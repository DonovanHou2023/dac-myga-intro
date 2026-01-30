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
from dac_myga_intro.engine.av import roll_forward_account_value
from dac_myga_intro.engine.mva import MVAInputs, calculate_mva
from dac_myga_intro.engine.guarantee_funds import (
    MinimumFundValueParams,
    ProspectiveFundValueParams,
    GuaranteeFundState,
    initialize_guarantee_funds,
    apply_surrender_to_guarantee_funds,
    credit_guarantee_funds_monthly,
)
from dac_myga_intro.engine.csv import calculate_cash_surrender_value


def build_annual_rate_schedule(term_years: int, initial_rate: float, renewal_rate: float) -> Dict[int, float]:
    """
    For v0, project only through the guaranteed term.

    MYGA assumption:
      - initial_rate applies through term_years (guaranteed period)
      - renewal_rate becomes relevant only if you later extend projection beyond term
    """
    return {yr: float(initial_rate) for yr in range(1, term_years + 1)}


def _round_output(df: pd.DataFrame, decimals: int = 2) -> pd.DataFrame:
    """
    Round all float columns for presentation.
    Keeps ints/strings unchanged.
    """
    out = df.copy()

    float_cols = out.select_dtypes(include=["float"]).columns
    if len(float_cols) > 0:
        out[float_cols] = out[float_cols].round(decimals)

    return out


def run_illustration(catalog: ProductCatalog, inputs: IllustrationInputs) -> pd.DataFrame:
    """
    Main orchestrator.

    Deterministic order each month:
      (1) Snapshot BOP values
      (2) Withdrawal + surrender charge
      (3) MVA (optional, if enabled and input rates provided)
      (4) Account Value roll-forward (withdrawal + surrender charge as penalty, then interest)
      (5) Guarantee fund roll-forward (reduce by withdrawal, then credit monthly)
      (6) CSV calculation (v0: AV - surrender charge + MVA; floors later)

    Returns: monthly pandas DataFrame ready for Streamlit.
    """

    spec = catalog.get(inputs.product_code)
    term_years = int(spec.term_years)
    total_months = term_years * 12

    # AV crediting schedule (during term)
    rate_by_year = build_annual_rate_schedule(term_years, inputs.initial_rate, inputs.renewal_rate)

    # Prior-year interest credited tracking (used for free withdrawal method and withdrawal method)
    prior_year_interest = 0.0
    current_year_interest_accum = 0.0

    # Initialize AV at issue
    av = float(inputs.premium)

    # Initialize withdrawal state
    wd_state: WithdrawalState = init_withdrawal_state()

    # -----------------------
    # Guarantee fund params come from PRODUCT FEATURES (YAML), not user inputs
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
        # (1) BOP snapshots
        # -----------------------
        av_bop = av
        gf_mfv_bop = gf_state.mfv
        gf_pfv_bop = gf_state.pfv

        # BOY AV is only meaningful at month 1; but withdrawals module can accept av_bop safely
        year_bop_av = av_bop if month_in_year == 1 else av_bop

        # -----------------------
        # (2) Withdrawals + surrender charge
        # -----------------------
        wd_state, wd_res = calc_withdrawal_for_month(
            catalog=catalog,
            inputs=inputs,
            state=wd_state,
            policy_year=policy_year,
            month_in_policy_year=month_in_year,
            av_bop=av_bop,
            year_bop_av=year_bop_av,
            prior_policy_year_interest=prior_year_interest,
        )

        # -----------------------
        # (3) MVA (optional)
        # Contract notation:
        #   A = amount surrendered (withdrawal)
        #   B = amount not subject to surrender charge (free portion)
        #   C = surrender charge amount ($)
        # -----------------------
        mva_factor = 0.0
        mva_amount_subject = 0.0
        mva_adjustment = 0.0

        mva_enabled = bool(spec.features.mva.enabled)
        have_mva_rates = (
            inputs.mva_initial_index_rate is not None
            and inputs.mva_current_index_rate is not None
        )

        if mva_enabled and have_mva_rates and wd_res.excess_amount > 0.0:
            # N: months remaining to end of MVA period
            # v0 assumption: MVA period ends at term end
            if inputs.mva_months_remaining_override is not None:
                n_remaining = int(inputs.mva_months_remaining_override)
            else:
                n_remaining = max(0, total_months - pm + 1)

            A = float(wd_res.withdrawal_amount)
            B = float(wd_res.free_used_this_txn)
            C = float(wd_res.surrender_charge_amount)

            mva_out = calculate_mva(
                MVAInputs(
                    x_initial_index_rate=float(inputs.mva_initial_index_rate),
                    y_current_index_rate=float(inputs.mva_current_index_rate),
                    n_months_remaining=int(n_remaining),
                ),
                A=A,
                B=B,
                C=C,
                # Hook for contract caps/floors later
                fund_value_after_surrender_charge=None,
                minimum_fund_value=None,
            )

            mva_factor = float(mva_out.mva_factor)
            mva_amount_subject = float(mva_out.amount_subject_to_mva)
            mva_adjustment = float(mva_out.mva_adjustment_capped)

        # -----------------------
        # (4) Account Value roll-forward
        # v0: treat surrender charge as "penalty" deducted from AV before interest credit
        # -----------------------
        av_result = roll_forward_account_value(
            av_bop=av_bop,
            withdrawal=float(wd_res.withdrawal_amount),
            penalty=float(wd_res.surrender_charge_amount),
            annual_rate=annual_rate,
        )
        av = float(av_result.av_eop)

        # Track prior-year interest credited
        current_year_interest_accum += float(av_result.interest_credit)
        if month_in_year == 12:
            prior_year_interest = float(current_year_interest_accum)
            current_year_interest_accum = 0.0

        # -----------------------
        # (5) Guarantee fund roll-forward
        # Reduce by withdrawal ONLY; then credit monthly per MFV/PFV rules
        # -----------------------
        gf_state = apply_surrender_to_guarantee_funds(gf_state, float(wd_res.withdrawal_amount))

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
        # (6) CSV calculation
        # v0: CSV = AV - surrender charge + MVA (floors optional later)
        # -----------------------
        csv_out = calculate_cash_surrender_value(
            av=float(av_result.av_eop),
            surrender_charge_amount=float(wd_res.surrender_charge_amount),
            mva_amount=float(mva_adjustment),
            gmv_floor=None,
            nff_floor=None,
        )

        rows.append(
            {
                # META
                "meta_policy_month": pm,
                "meta_policy_year": policy_year,
                "meta_month_in_policy_year": month_in_year,
                "meta_annual_rate": annual_rate,

                # INPUT META (kept for later use; not used in v0 math)
                "meta_issue_age": int(inputs.issue_age),
                "meta_gender": str(inputs.gender),

                # WITHDRAWALS
                "wd_withdrawal_amount": float(wd_res.withdrawal_amount),
                "wd_free_limit_ytd": float(wd_res.free_limit_ytd),
                "wd_free_used_this_txn": float(wd_res.free_used_this_txn),
                "wd_free_used_ytd_eop": float(wd_res.free_used_ytd_eop),
                "wd_free_remaining_eop": float(wd_res.free_remaining_eop),
                "wd_excess_amount": float(wd_res.excess_amount),
                "wd_surrender_charge_pct": float(wd_res.surrender_charge_pct),
                "wd_surrender_charge_amount": float(wd_res.surrender_charge_amount),

                # MVA
                "mva_enabled": bool(mva_enabled and have_mva_rates),
                "mva_factor": float(mva_factor),
                "mva_amount_subject": float(mva_amount_subject),
                "mva_adjustment": float(mva_adjustment),

                # ACCOUNT VALUE
                "av_bop": float(av_bop),
                "av_after_withdrawal_and_penalty": float(av_result.av_after_wd),
                "av_interest_credit": float(av_result.interest_credit),
                "av_eop": float(av_result.av_eop),

                # GUARANTEE FUNDS
                "gf_mfv_bop": float(gf_mfv_bop),
                "gf_mfv_eop": float(gf_mfv_eop),
                "gf_pfv_bop": float(gf_pfv_bop),
                "gf_pfv_eop": float(gf_pfv_eop),

                # CSV
                "csv_before_floors": float(csv_out.csv_before_floors),
                "csv": float(csv_out.csv),
            }
        )

    df = pd.DataFrame(rows)
    return _round_output(df, decimals=2)