from __future__ import annotations

from pathlib import Path
from typing import Dict, Any, Optional

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

# NEW: annuity benefits
from dac_myga_intro.engine.annuity_benefits import (
    load_annuity_tables,
    annuity_monthly_payment,
)


# -----------------------
# Outputs: column grouping
# -----------------------
# meta_* : time index & rate info (NOW includes meta_attained_age)
# wd_*   : withdrawals mechanics (includes SC + MVA + penalty_total)
# mva_*  : factor only
# av_*   : account value projection
# gf_*   : guarantee fund projection (MFV/PFV)
# csv_*  : cash surrender values + diagnostics
# ann_*  : annuity benefit outputs (only populated at year-end months)


def build_annual_rate_schedule(
    *,
    term_years: int,
    projection_years: int,
    initial_rate: float,
    renewal_rate: float,
    minimum_guaranteed_rate: float,
) -> Dict[int, float]:
    """
    Crediting schedule by policy year:
      - years 1..term_years: initial_rate (guaranteed period)
      - years term_years+1..projection_years: renewal_rate (if projecting beyond term)
    """
    sched: Dict[int, float] = {}
    for yr in range(1, projection_years + 1):
        sched[yr] = (
            float(initial_rate)
            if yr <= term_years
            else max(float(renewal_rate), float(minimum_guaranteed_rate))
        )
    return sched


def run_illustration(catalog: ProductCatalog, inputs: IllustrationInputs) -> pd.DataFrame:
    """
    Monthly projection orchestrator.

    Adds:
      - meta_attained_age = issue_age + policy_year
      - annuity benefits computed ONLY at year-end months (month_in_year == 12)
        using ann_amount_applied = AV_EOP (post-floor)

    NOTE: installment certain requires a "years" input. Since you haven't added it to
    IllustrationInputs yet, we pull it with getattr and default to 10.
    Recommended: add `annuitization_years: Optional[int]` to IllustrationInputs
    and pass it from Streamlit.
    """

    spec = catalog.get(inputs.product_code)
    term_years = int(spec.term_years)

    # Projection length (years)
    proj_years_raw = getattr(inputs, "projection_years", None)
    if proj_years_raw is None or int(proj_years_raw) <= 0:
        projection_years = term_years
    else:
        projection_years = int(proj_years_raw)

    total_months = projection_years * 12
    term_months = term_years * 12

    # Crediting schedule for AV
    rate_by_year = build_annual_rate_schedule(
        term_years=term_years,
        projection_years=projection_years,
        initial_rate=float(inputs.initial_rate),
        renewal_rate=float(inputs.renewal_rate),
        minimum_guaranteed_rate=float(spec.features.minimum_guaranteed_rate),
    )

    # Prior-year interest credited tracking
    prior_year_interest = 0.0
    current_year_interest_accum = 0.0

    # Initialize AV at issue
    av = float(inputs.premium)

    # Withdrawal state
    wd_state: WithdrawalState = init_withdrawal_state()

    # Guarantee fund params from YAML
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

    # -----------------------
    # NEW: Load annuity payout tables once
    # Adjust path as needed to match your repo layout.
    # You said: src/data/annuity_tables/...
    # -----------------------
    annuity_tables_root = Path("src/dac_myga_intro/data/annuity_tables")
    ann_tables = load_annuity_tables(annuity_tables_root)

    installment_years = int(inputs.installment_years)

    rows: list[dict[str, Any]] = []

    for pm in range(1, total_months + 1):
        policy_year = (pm - 1) // 12 + 1
        month_in_year = (pm - 1) % 12 + 1
        annual_rate = float(rate_by_year[policy_year])

        # meta attained age = issue_age + policy_year
        attained_age = float(inputs.issue_age) + float(policy_year)

        # (0) MVA factor
        mva_enabled = bool(spec.features.mva.enabled)
        have_mva_rates = (
            inputs.mva_initial_index_rate is not None
            and inputs.mva_current_index_rate is not None
        )

        mva_factor = 0.0
        if mva_enabled and have_mva_rates:
            if inputs.mva_months_remaining_override is not None:
                n_remaining = int(inputs.mva_months_remaining_override)
            else:
                n_remaining = max(0, term_months - pm)

            mva_factor = calculate_mva_factor(
                MVAInputs(
                    x_initial_index_rate=float(inputs.mva_initial_index_rate),
                    y_current_index_rate=float(inputs.mva_current_index_rate),
                    n_months_remaining=int(n_remaining),
                )
            ).mva_factor

        # (1) BOP snapshots
        av_bop = float(av)
        gf_mfv_bop = float(gf_state.mfv)
        gf_pfv_bop = float(gf_state.pfv)

        year_bop_av = av_bop  # ok for v0

        # (2) Withdrawals
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

        # (3) Guarantee funds roll-forward
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

        # (4) Account Value roll-forward
        av_result = roll_forward_account_value(
            av_bop=av_bop,
            withdrawal=float(wd_res.withdrawal_amount),
            penalty=float(wd_res.penalty_total),
            annual_rate=float(annual_rate),
        )

        av_eop = float(av_result.av_eop)

        # AV floor to guarantee funds
        nff_floor = max(gf_mfv_eop, gf_pfv_eop)
        av_eop_floored = max(av_eop, nff_floor)

        av = av_eop_floored  # carry forward

        # Prior-year interest credited tracking
        current_year_interest_accum += float(av_result.interest_credit)
        if month_in_year == 12:
            prior_year_interest = float(current_year_interest_accum)
            current_year_interest_accum = 0.0

        # (5) CSV calculation
        sc_pct_override = 0.0 if pm == term_months else None

        csv_out = calculate_cash_surrender_value(
            av_eop=float(av),
            surrender_amount=float(av),
            free_remaining_at_calc=float(wd_res.free_remaining_eop),
            surrender_charge_pct=float(
                catalog.surrender_charge(inputs.product_code, policy_year)
            ),
            surrender_charge_pct_override=sc_pct_override,
            mva_factor=float(mva_factor),
            gf_mfv_eop=float(gf_mfv_eop),
            gf_pfv_eop=float(gf_pfv_eop),
        )

        # -----------------------
        # NEW: Annuity benefits at YEAR END ONLY
        # - A amount = AV_EOP (post-floor) at month 12
        # -----------------------
        ann_is_year_end = bool(month_in_year == 12)
        ann_amount_applied: Optional[float] = None
        ann_installment_monthly_payment: Optional[float] = None
        ann_single_life_monthly_payment: Optional[float] = None

        if ann_is_year_end:
            ann_amount_applied = float(av)

            # Option 1: installment certain
            ann_installment_monthly_payment = float(
                annuity_monthly_payment(
                    amount_applied=float(ann_amount_applied),
                    option="installment_certain",
                    tables=ann_tables,
                    years=int(installment_years),
                )
            )

            # Option 2: single life no guarantee
            # Use attained_age (issue_age + policy_year) and inputs.gender
            ann_single_life_monthly_payment = float(
                annuity_monthly_payment(
                    amount_applied=float(ann_amount_applied),
                    option="single_life_no_guarantee",
                    tables=ann_tables,
                    attained_age=float(attained_age),
                    gender=str(inputs.gender),
                )
            )

        # Assemble row
        rows.append(
            {
                # META
                "meta_policy_month": int(pm),
                "meta_policy_year": int(policy_year),
                "meta_month_in_policy_year": int(month_in_year),
                "meta_annual_rate": float(annual_rate),
                "meta_issue_age": int(inputs.issue_age),
                "meta_attained_age": float(attained_age),
                "meta_gender": str(inputs.gender),
                "meta_projection_years": int(projection_years),

                # MVA
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

                "csv_amount_subject_to_sc": float(
                    csv_out.amount_subject_to_surrender_charge
                ),
                "csv_sc_pct_used": float(csv_out.surrender_charge_pct_used),
                "csv_sc_amt_used": float(csv_out.surrender_charge_amount_used),
                "csv_amount_subject_to_mva": float(csv_out.amount_subject_to_mva),
                "csv_mva_factor_used": float(csv_out.mva_factor_used),
                "csv_mva_amt_used": float(csv_out.mva_amount_used),

                # ANNUITY outputs (mostly None except year-end months)
                "ann_is_year_end": bool(ann_is_year_end),
                "ann_amount_applied": float(ann_amount_applied) if ann_amount_applied is not None else None,
                "ann_installment_years": int(installment_years) if ann_is_year_end else None,
                "ann_installment_monthly_payment": float(ann_installment_monthly_payment) if ann_installment_monthly_payment is not None else None,
                "ann_single_life_monthly_payment": float(ann_single_life_monthly_payment) if ann_single_life_monthly_payment is not None else None,
            }
        )

    return pd.DataFrame(rows)