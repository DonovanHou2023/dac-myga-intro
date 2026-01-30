from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


def monthly_rate_from_annual(r_annual: float) -> float:
    return (1.0 + r_annual) ** (1.0 / 12.0) - 1.0


@dataclass(frozen=True)
class MinimumFundValueParams:
    """
    Minimum Fund Value (MFV) track.

    Your spec (simplified):
      - base = 87.5% * premium
      - reduce by amounts surrendered (withdrawals), not including charges/MVA/penalties
      - credit:
          * initial_rate for years 1..term_years
          * min_guaranteed_rate after term_years
    """
    base_pct_of_premium: float = 0.875


@dataclass(frozen=True)
class ProspectiveFundValueParams:
    """
    Prospective Fund Value (PFV) track.

    Your spec (fixed interest account example):
      - base = 90.7% * premium
      - reduce by amounts surrendered (withdrawals only)
      - credit at a contract-specified rate for a certain number of years,
        then possibly a different rate (often 0%).
    """
    base_pct_of_premium: float = 0.907
    rate_annual: float = 0.0191
    rate_years: int = 10
    rate_after_years_annual: float = 0.0


@dataclass(frozen=True)
class GuaranteeFundState:
    """
    Stores current balances for the guarantee tracks.
    """
    mfv: float
    pfv: float


def mfv_annual_rate_for_policy_year(
    policy_year: int,
    term_years: int,
    initial_rate: float,
    min_guaranteed_rate: float,
) -> float:
    """
    MFV credits at initial_rate during the guaranteed term, then min_guaranteed_rate thereafter.
    """
    return initial_rate if policy_year <= term_years else min_guaranteed_rate


def pfv_annual_rate_for_policy_year(
    policy_year: int,
    params: ProspectiveFundValueParams,
) -> float:
    """
    PFV credits at params.rate_annual for first params.rate_years years,
    then params.rate_after_years_annual afterward.
    """
    return params.rate_annual if policy_year <= params.rate_years else params.rate_after_years_annual


def initialize_guarantee_funds(
    premium: float,
    mfv_params: MinimumFundValueParams,
    pfv_params: ProspectiveFundValueParams,
) -> GuaranteeFundState:
    """
    Initialize MFV and PFV balances at issue.
    """
    premium = float(premium)
    mfv0 = mfv_params.base_pct_of_premium * premium
    pfv0 = pfv_params.base_pct_of_premium * premium
    return GuaranteeFundState(mfv=mfv0, pfv=pfv0)


def apply_surrender_to_guarantee_funds(
    state: GuaranteeFundState,
    surrender_amount: float,
) -> GuaranteeFundState:
    """
    Reduce both MFV and PFV by the surrendered amount (withdrawal),
    dollar-for-dollar, floored at 0.

    NOTE: surrender_amount should NOT include surrender charges, MVA, penalties.
    """
    wd = max(0.0, float(surrender_amount))
    return GuaranteeFundState(
        mfv=max(0.0, state.mfv - wd),
        pfv=max(0.0, state.pfv - wd),
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
    """
    Apply one month of interest crediting to both MFV and PFV.
    """
    # MFV rate depends on term vs post-term
    mfv_r_annual = mfv_annual_rate_for_policy_year(
        policy_year=policy_year,
        term_years=term_years,
        initial_rate=initial_rate,
        min_guaranteed_rate=min_guaranteed_rate,
    )
    mfv_r_m = monthly_rate_from_annual(mfv_r_annual)

    # PFV rate depends on PFV schedule
    pfv_r_annual = pfv_annual_rate_for_policy_year(policy_year, pfv_params)
    pfv_r_m = monthly_rate_from_annual(pfv_r_annual)

    return GuaranteeFundState(
        mfv=state.mfv * (1.0 + mfv_r_m),
        pfv=state.pfv * (1.0 + pfv_r_m),
    )