from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Dict, Tuple

import pandas as pd

from dac_myga_intro.engine.catalog import ProductCatalog


WithdrawalMethod = Literal[
    "pct_of_boy_av",
    "fixed_amount",
    "prior_year_interest_credited",
]


@dataclass(frozen=True)
class IllustrationInputs:
    product_code: str
    premium: float
    initial_rate: float          # annual, e.g. 0.05
    renewal_rate: float          # annual, e.g. 0.045
    withdrawal_method: WithdrawalMethod
    withdrawal_value: float = 0.0  # pct (0.10) or fixed amount; ignored if prior_year_interest_credited


def penalty_amount_stub(withdrawal_excess: float, surrender_charge_pct: float) -> float:
    # TODO: implement later
    return 0.0


def monthly_rate_from_annual(r_annual: float) -> float:
    return (1.0 + r_annual) ** (1.0 / 12.0) - 1.0


def build_annual_rate_schedule(term_years: int, initial_rate: float, renewal_rate: float) -> Dict[int, float]:
    # Year 1 uses initial rate; years 2..term use renewal rate
    return {yr: (initial_rate if yr == 1 else renewal_rate) for yr in range(1, term_years + 1)}


def compute_free_withdrawal_limit(
    spec,
    policy_year: int,
    year_bop_av: float,
    prior_policy_year_interest: float,
) -> float:
    """
    Uses the product feature free_partial_withdrawal config.
    """
    fpw = spec.features.free_partial_withdrawal
    if not fpw.enabled:
        return 0.0

    if fpw.method == "pct_of_boy_account_value":
        pct = float(fpw.params.get("pct", 0.0))
        return max(0.0, pct * year_bop_av)

    if fpw.method == "prior_year_interest_credited":
        # For policy year 1 there is no prior year
        return max(0.0, prior_policy_year_interest if policy_year >= 2 else 0.0)

    # If new methods are added later, handle them here
    return 0.0


def compute_withdrawal_amount(
    inputs: IllustrationInputs,
    policy_year: int,
    year_bop_av: float,
    prior_policy_year_interest: float,
) -> float:
    """
    User-selected withdrawal instruction (single variable applied each year except year 1).
    Withdrawal occurs only in month 1 of the policy year (handled in projection loop).
    """
    if policy_year == 1:
        return 0.0

    if inputs.withdrawal_method == "pct_of_boy_av":
        return max(0.0, float(inputs.withdrawal_value) * year_bop_av)

    if inputs.withdrawal_method == "fixed_amount":
        return max(0.0, float(inputs.withdrawal_value))

    if inputs.withdrawal_method == "prior_year_interest_credited":
        return max(0.0, prior_policy_year_interest)

    return 0.0


def run_illustration(
    catalog: ProductCatalog,
    inputs: IllustrationInputs,
) -> pd.DataFrame:
    """
    Returns a pandas DataFrame for Streamlit display.

    Columns include:
    - policy_month (1..term_years*12)
    - policy_year (1..term_years)
    - month_in_policy_year (1..12)
    - annual_rate, monthly_rate
    - av_bop, withdrawal, free_limit, withdrawal_excess, penalty
    - interest_credit, av_eop
    """
    spec = catalog.get(inputs.product_code)
    term_years = spec.term_years
    total_months = term_years * 12

    rate_by_year = build_annual_rate_schedule(term_years, inputs.initial_rate, inputs.renewal_rate)

    # Track prior-year interest credited (needed for both free-withdrawal limit and user withdrawal method option)
    prior_year_interest = 0.0
    current_year_interest_accum = 0.0

    rows = []

    av = float(inputs.premium)  # initial deposit at time 0 => AV at BOP month 1

    for pm in range(1, total_months + 1):
        policy_year = (pm - 1) // 12 + 1
        month_in_year = (pm - 1) % 12 + 1

        annual_rate = float(rate_by_year[policy_year])
        m_rate = monthly_rate_from_annual(annual_rate)

        av_bop = av

        # Determine year BOP AV (used for % BOY withdrawal, free limits)
        # This is AV at month 1 BOP of the current year.
        # We can compute it on the fly: if month_in_year == 1, then av_bop is the year BOP.
        year_bop_av = av_bop if month_in_year == 1 else None

        withdrawal = 0.0
        free_limit = 0.0
        withdrawal_excess = 0.0
        surrender_charge_pct = 0.0
        penalty = 0.0

        # Withdrawal happens only at month 1 of each policy year except year 1
        if month_in_year == 1 and policy_year >= 2:
            # year_bop_av is av_bop in month 1
            year_bop_av = av_bop

            # product free-withdrawal limit
            free_limit = compute_free_withdrawal_limit(
                spec=spec,
                policy_year=policy_year,
                year_bop_av=year_bop_av,
                prior_policy_year_interest=prior_year_interest,
            )

            # user withdrawal amount
            withdrawal = compute_withdrawal_amount(
                inputs=inputs,
                policy_year=policy_year,
                year_bop_av=year_bop_av,
                prior_policy_year_interest=prior_year_interest,
            )

            # Cap withdrawal at available account value (can adjust later if you allow overdraft behavior)
            withdrawal = min(withdrawal, av_bop)

            # excess over free limit
            withdrawal_excess = max(0.0, withdrawal - free_limit)

            # Surrender charge percent for penalty logic (even though penalty is stubbed 0 now)
            surrender_charge_pct = catalog.surrender_charge(inputs.product_code, policy_year)

            penalty = penalty_amount_stub(withdrawal_excess, surrender_charge_pct)

        # Apply withdrawal + penalty (penalty is 0 for now)
        av_after_wd = av_bop - withdrawal - penalty

        # Monthly interest crediting (post-withdrawal)
        interest_credit = av_after_wd * m_rate
        av_eop = av_after_wd + interest_credit

        # Track interest by policy year for "prior_year_interest_credited"
        current_year_interest_accum += interest_credit
        if month_in_year == 12:
            prior_year_interest = current_year_interest_accum
            current_year_interest_accum = 0.0

        rows.append(
            {
                "policy_month": pm,
                "policy_year": policy_year,
                "month_in_policy_year": month_in_year,
                "annual_rate": annual_rate,
                "monthly_rate": m_rate,
                "av_bop": av_bop,
                "withdrawal": withdrawal,
                "free_limit": free_limit,
                "withdrawal_excess": withdrawal_excess,
                "surrender_charge_pct": surrender_charge_pct,
                "penalty": penalty,
                "interest_credit": interest_credit,
                "av_eop": av_eop,
            }
        )

        av = av_eop

    df = pd.DataFrame(rows)
    return df