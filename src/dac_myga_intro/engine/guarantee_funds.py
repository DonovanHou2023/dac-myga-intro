from __future__ import annotations

from dataclasses import dataclass


def monthly_rate_from_annual(r_annual: float) -> float:
    return (1.0 + float(r_annual)) ** (1.0 / 12.0) - 1.0


@dataclass(frozen=True)
class MinimumFundValueParams:
    """
    Minimum Fund Value (MFV) track.

    Caller MUST supply base_pct_of_premium (from product YAML).
    """
    base_pct_of_premium: float  # no defaults on purpose


@dataclass(frozen=True)
class ProspectiveFundValueParams:
    """
    Prospective Fund Value (PFV) track.

    Caller MUST supply all fields (from product YAML).
    """
    base_pct_of_premium: float  # no defaults on purpose
    rate_annual: float
    rate_years: int
    rate_after_years_annual: float


@dataclass(frozen=True)
class GuaranteeFundState:
    """Stores current balances for the guarantee tracks."""
    mfv: float
    pfv: float


def mfv_annual_rate_for_policy_year(
    policy_year: int,
    term_years: int,
    initial_rate: float,
    min_guaranteed_rate: float,
) -> float:
    """MFV credits at initial_rate during the guaranteed term, then min_guaranteed_rate thereafter."""
    return float(initial_rate) if int(policy_year) <= int(term_years) else float(min_guaranteed_rate)


def pfv_annual_rate_for_policy_year(
    policy_year: int,
    params: ProspectiveFundValueParams,
) -> float:
    """PFV credits at params.rate_annual for first params.rate_years years, then rate_after_years_annual."""
    return float(params.rate_annual) if int(policy_year) <= int(params.rate_years) else float(params.rate_after_years_annual)


def initialize_guarantee_funds(
    premium: float,
    mfv_params: MinimumFundValueParams,
    pfv_params: ProspectiveFundValueParams,
) -> GuaranteeFundState:
    """Initialize MFV and PFV balances at issue."""
    p = float(premium)

    # Light validation (optional but helpful)
    if mfv_params.base_pct_of_premium < 0.0:
        raise ValueError("MFV base_pct_of_premium must be >= 0")
    if pfv_params.base_pct_of_premium < 0.0:
        raise ValueError("PFV base_pct_of_premium must be >= 0")
    if pfv_params.rate_years < 0:
        raise ValueError("PFV rate_years must be >= 0")

    mfv0 = float(mfv_params.base_pct_of_premium) * p
    pfv0 = float(pfv_params.base_pct_of_premium) * p
    return GuaranteeFundState(mfv=mfv0, pfv=pfv0)


def apply_surrender_to_guarantee_funds(
    state: GuaranteeFundState,
    surrender_amount: float,
) -> GuaranteeFundState:
    """
    Reduce both MFV and PFV by the surrendered amount (withdrawal), dollar-for-dollar, floored at 0.

    NOTE: surrender_amount should NOT include surrender charges, MVA, penalties.
    """
    wd = max(0.0, float(surrender_amount))
    return GuaranteeFundState(
        mfv=max(0.0, float(state.mfv) - wd),
        pfv=max(0.0, float(state.pfv) - wd),
    )


def credit_guarantee_funds_monthly(
    state: GuaranteeFundState,
    policy_year: int,
    *,
    term_years: int,
    initial_rate: float,
    min_guaranteed_rate: float,
    pfv_params: ProspectiveFundValueParams,
) -> GuaranteeFundState:
    """Apply one month of interest crediting to both MFV and PFV."""
    mfv_r_annual = mfv_annual_rate_for_policy_year(
        policy_year=policy_year,
        term_years=term_years,
        initial_rate=initial_rate,
        min_guaranteed_rate=min_guaranteed_rate,
    )
    mfv_r_m = monthly_rate_from_annual(mfv_r_annual)

    pfv_r_annual = pfv_annual_rate_for_policy_year(policy_year, pfv_params)
    pfv_r_m = monthly_rate_from_annual(pfv_r_annual)

    return GuaranteeFundState(
        mfv=float(state.mfv) * (1.0 + mfv_r_m),
        pfv=float(state.pfv) * (1.0 + pfv_r_m),
    )