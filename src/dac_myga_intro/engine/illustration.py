from __future__ import annotations

from typing import Dict, Any

import pandas as pd

from dac_myga_intro.engine.catalog import ProductCatalog
from dac_myga_intro.engine.inputs import IllustrationInputs

# Component modules
from dac_myga_intro.engine.withdrawals import (
    WithdrawalState,
    init_withdrawal_state,
    calc_withdrawal_for_month,
)

from dac_myga_intro.engine.mva import MVAInputs, calculate_mva_factor

from dac_myga_intro.engine.av import roll_forward_account_value
from dac_myga_intro.engine.guarantee_funds import (
    MinimumFundValueParams,
    ProspectiveFundValueParams,
    GuaranteeFundState,
    initialize_guarantee_funds,
    apply_surrender_to_guarantee_funds,
    credit_guarantee_funds_monthly,
)
from dac_myga_intro.engine.csv import calculate_cash_surrender_value


# -----------------------
# Outputs: column grouping
# -----------------------
# meta_* : time index & rate info
# wd_*   : withdrawals mechanics (includes SC + MVA + penalty_total)
# mva_*  : factor only (optional; you can keep this minimal)
# av_*   : account value projection
# gf_*   : guarantee fund projection (MFV/PFV)
# csv_*  : cash surrender values + diagnostics


def build_annual_rate_schedule(
    *,
    term_years: int,
    projection_years: int,
    initial_rate: float,
    renewal_rate: float,
) -> Dict[int, float]:
    """
    Crediting schedule by policy year:
      - years 1..term_years: initial_rate (guaranteed period)
      - years term_years+1..projection_years: renewal_rate (if projecting beyond term)
    """
    sched: Dict[int, float] = {}
    for yr in range(1, projection_years + 1):
        sched[yr] = float(initial_rate) if yr <= term_years else float(renewal_rate)
    return sched


def run_illustration(catalog: ProductCatalog, inputs: IllustrationInputs) -> pd.DataFrame:
    """
    Monthly projection orchestrator.

    Monthly order (per your latest design):
      (0) compute MVA factor for the month (factor only)
      (1) snapshot BOP values
      (2) withdrawals (updates free budget; computes SC and MVA on excess; returns penalty_total)
      (3) guarantee funds roll-forward (reduce by withdrawal only; then credit)
      (4) account value roll-forward (withdrawal + penalty_total; then interest)
          + optional AV floor vs guarantee funds (added here)
      (5) CSV calculation at time t:
          - full surrender assumed: surrender_amount = AV_EOP
          - uses free_remaining_at_calc to exempt part from SC and MVA
          - computes SC, then applies MVA factor on post-SC subject amount
          - floors by max(MFV_EOP, PFV_EOP)

    Returns: pandas DataFrame ready for Streamlit.
    """

    spec = catalog.get(inputs.product_code)
    term_years = int(spec.term_years)

    # -----------------------
    # Projection length (years)
    # - If inputs.projection_years is absent/None or <=0, default to term_years
    # - Allow projecting beyond term_years if you want (renewal_rate matters then)
    # -----------------------
    proj_years_raw = getattr(inputs, "projection_years", None)
    if proj_years_raw is None or int(proj_years_raw) <= 0:
        projection_years = term_years
    else:
        projection_years = int(proj_years_raw)

    total_months = projection_years * 12
    term_months = term_years * 12  # used for term-end surrender charge override hook

    # Crediting schedule for AV
    rate_by_year = build_annual_rate_schedule(
        term_years=term_years,
        projection_years=projection_years,
        initial_rate=float(inputs.initial_rate),
        renewal_rate=float(inputs.renewal_rate),
    )

    # Prior-year interest credited tracking (for withdrawal method / free rule option)
    prior_year_interest = 0.0
    current_year_interest_accum = 0.0

    # Initialize AV at issue
    av = float(inputs.premium)

    # Withdrawal state
    wd_state: WithdrawalState = init_withdrawal_state()

    # -----------------------
    # Guarantee fund params MUST come from YAML product features
    # -----------------------
    gf_spec = spec.features.guarantee_funds

    mfv_params = MinimumFundValueParams(
        base_pct_of_premium=float(gf_spec.mfv.base_pct_of_premium)
    )
    pfv_params = ProspectiveFundValueParams(
        base_pct_of_premium=float(gf_spec.pfv.base_pct_of_premium),
        rate_annual=float(gf_spec.pfv.rate_annual),
        rate_years=int(gf_spec.pfv.rate_years),
        rate_after_years_annual=float(gf_spec.pfv.rate_after_years_annual),
    )

    gf_state: GuaranteeFundState = initialize_guarantee_funds(
        inputs.premium, mfv_params, pfv_params
    )

    rows: list[dict[str, Any]] = []

    for pm in range(1, total_months + 1):
        policy_year = (pm - 1) // 12 + 1
        month_in_year = (pm - 1) % 12 + 1
        annual_rate = float(rate_by_year[policy_year])

        # -----------------------
        # (0) MVA factor first (factor only)
        # -----------------------
        mva_enabled = bool(spec.features.mva.enabled)
        have_mva_rates = (
            inputs.mva_initial_index_rate is not None
            and inputs.mva_current_index_rate is not None
        )

        mva_factor = 0.0
        if mva_enabled and have_mva_rates:
            # N months remaining: v0 assumption -> MVA period ends at term end
            if inputs.mva_months_remaining_override is not None:
                n_remaining = int(inputs.mva_months_remaining_override)
            else:
                n_remaining = max(0, term_months - pm + 1)

            mva_factor = calculate_mva_factor(
                MVAInputs(
                    x_initial_index_rate=float(inputs.mva_initial_index_rate),
                    y_current_index_rate=float(inputs.mva_current_index_rate),
                    n_months_remaining=int(n_remaining),
                )
            ).mva_factor

        # -----------------------
        # (1) BOP snapshots
        # -----------------------
        av_bop = float(av)
        gf_mfv_bop = float(gf_state.mfv)
        gf_pfv_bop = float(gf_state.pfv)

        # BOY AV: meaningful at month 1 (but safe to pass av_bop for now)
        year_bop_av = av_bop if month_in_year == 1 else av_bop

        # -----------------------
        # (2) Withdrawals (includes SC + MVA on excess; returns penalty_total)
        # -----------------------
        wd_state, wd_res = calc_withdrawal_for_month(
            catalog=catalog,
            inputs=inputs,
            state=wd_state,
            policy_year=policy_year,
            month_in_policy_year=month_in_year,
            av_bop=av_bop,
            year_bop_av=year_bop_av,
            prior_policy_year_interest=float(prior_year_interest),
            mva_factor=float(mva_factor),
        )

        # -----------------------
        # (3) Guarantee funds roll-forward
        # - reduce by withdrawal ONLY (not SC/MVA/penalties)
        # - then credit monthly based on MFV/PFV rules
        # -----------------------
        gf_state = apply_surrender_to_guarantee_funds(
            gf_state, float(wd_res.withdrawal_amount)
        )

        gf_state = credit_guarantee_funds_monthly(
            gf_state,
            policy_year=policy_year,
            term_years=term_years,
            initial_rate=float(inputs.initial_rate),
            min_guaranteed_rate=float(spec.features.minimum_guaranteed_rate),
            pfv_params=pfv_params,
        )

        gf_mfv_eop = float(gf_state.mfv)
        gf_pfv_eop = float(gf_state.pfv)

        # -----------------------
        # (4) Account Value roll-forward
        # - penalty should include SC + MVA portions on excess (wd_res.penalty_total)
        # - optional floor: AV_EOP floored by max(MFV_EOP, PFV_EOP)
        # -----------------------
        av_result = roll_forward_account_value(
            av_bop=av_bop,
            withdrawal=float(wd_res.withdrawal_amount),
            penalty=float(wd_res.penalty_total),
            annual_rate=float(annual_rate),
        )

        av_eop = float(av_result.av_eop)

        # AV floor to guarantee funds (as you requested)
        nff_floor = max(gf_mfv_eop, gf_pfv_eop)
        av_eop_floored = max(av_eop, nff_floor)

        # If floored, update the result "in-place" for downstream CSV + next month AV
        # (keep interest_credit as originally calculated for transparency; adjust av_eop only)
        av = av_eop_floored

        # Prior-year interest credited tracking (based on interest credit, not floor bump)
        current_year_interest_accum += float(av_result.interest_credit)
        if month_in_year == 12:
            prior_year_interest = float(current_year_interest_accum)
            current_year_interest_accum = 0.0

        # -----------------------
        # (5) CSV calculation at time t (full surrender)
        # - use AV_EOP AFTER floor
        # - use free remaining at calc to exempt part from SC/MVA
        # - SC pct override example at term-end month (month 60 for 5-year)
        # - floor by guarantee funds
        # -----------------------
        sc_pct_override = 0.0 if pm == term_months else None

        csv_out = calculate_cash_surrender_value(
            av_eop=float(av),
            surrender_amount=float(av),  # full surrender at time t
            free_remaining_at_calc=float(wd_res.free_remaining_eop),
            surrender_charge_pct=float(catalog.surrender_charge(inputs.product_code, policy_year)),
            surrender_charge_pct_override=sc_pct_override,
            mva_factor=float(mva_factor),
            gf_mfv_eop=float(gf_mfv_eop),
            gf_pfv_eop=float(gf_pfv_eop),
        )

        # -----------------------
        # Assemble row
        # -----------------------
        rows.append(
            {
                # META
                "meta_policy_month": int(pm),
                "meta_policy_year": int(policy_year),
                "meta_month_in_policy_year": int(month_in_year),
                "meta_annual_rate": float(annual_rate),
                "meta_issue_age": int(inputs.issue_age),
                "meta_gender": str(inputs.gender),
                "meta_projection_years": int(projection_years),

                # MVA FACTOR (optional columns)
                "mva_enabled": bool(mva_enabled and have_mva_rates),
                "mva_factor": float(mva_factor),

                # WITHDRAWALS / CHARGES
                "wd_withdrawal_amount": float(wd_res.withdrawal_amount),
                "wd_free_limit_ytd": float(wd_res.free_limit_ytd),
                "wd_free_used_this_txn": float(wd_res.free_used_this_txn),
                "wd_free_used_ytd_eop": float(wd_res.free_used_ytd_eop),
                "wd_free_remaining_eop": float(wd_res.free_remaining_eop),
                "wd_excess_amount": float(wd_res.excess_amount),

                "wd_surrender_charge_pct": float(wd_res.surrender_charge_pct),
                "wd_surrender_charge_amount": float(wd_res.surrender_charge_amount),

                "wd_mva_factor": float(wd_res.mva_factor),
                "wd_mva_amount_subject": float(wd_res.mva_amount_subject),
                "wd_mva_amount": float(wd_res.mva_amount),

                "wd_penalty_total": float(wd_res.penalty_total),

                # ACCOUNT VALUE
                "av_bop": float(av_bop),
                "av_after_withdrawal_and_penalty": float(av_result.av_after_wd),
                "av_interest_credit": float(av_result.interest_credit),
                "av_eop_before_floor": float(av_eop),
                "av_nff_floor": float(nff_floor),
                "av_eop": float(av),

                # GUARANTEE FUNDS
                "gf_mfv_bop": float(gf_mfv_bop),
                "gf_mfv_eop": float(gf_mfv_eop),
                "gf_pfv_bop": float(gf_pfv_bop),
                "gf_pfv_eop": float(gf_pfv_eop),

                # CSV + diagnostics
                "csv_before_floors": float(csv_out.csv_before_floors),
                "csv_nff_floor_used": float(csv_out.nff_floor_used),
                "csv_final": float(csv_out.csv),

                "csv_amount_subject_to_sc": float(csv_out.amount_subject_to_surrender_charge),
                "csv_sc_pct_used": float(csv_out.surrender_charge_pct_used),
                "csv_sc_amt_used": float(csv_out.surrender_charge_amount_used),
                "csv_amount_subject_to_mva": float(csv_out.amount_subject_to_mva),
                "csv_mva_factor_used": float(csv_out.mva_factor_used),
                "csv_mva_amt_used": float(csv_out.mva_amount_used),
            }
        )

    return pd.DataFrame(rows)