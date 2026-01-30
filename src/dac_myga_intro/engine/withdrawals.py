from __future__ import annotations

from dataclasses import dataclass

from dac_myga_intro.engine.catalog import ProductCatalog
from dac_myga_intro.engine.inputs import IllustrationInputs


@dataclass(frozen=True)
class WithdrawalState:
    """
    Tracks the free withdrawal budget for the CURRENT policy year.
    """
    policy_year: int
    month_in_policy_year: int
    free_limit_ytd: float
    free_used_ytd: float
    free_remaining_ytd: float


@dataclass(frozen=True)
class WithdrawalResult:
    withdrawal_amount: float

    # Free withdrawal mechanics
    free_limit_ytd: float
    free_used_this_txn: float
    free_used_ytd_eop: float
    free_remaining_eop: float

    # Amount subject to charges/MVA
    excess_amount: float

    # Surrender charge outputs
    surrender_charge_pct: float
    surrender_charge_amount: float

    # MVA outputs (factor passed in from illustration)
    mva_factor: float
    mva_amount_subject: float
    mva_amount: float

    # Convenience: combined “penalty/adjustment” on the excess portion
    penalty_total: float


def init_withdrawal_state() -> WithdrawalState:
    return WithdrawalState(
        policy_year=1,
        month_in_policy_year=1,
        free_limit_ytd=0.0,
        free_used_ytd=0.0,
        free_remaining_ytd=0.0,
    )


def compute_free_limit_for_year(
    spec,
    policy_year: int,
    year_bop_av: float,
    prior_policy_year_interest: float,
) -> float:
    fpw = spec.features.free_partial_withdrawal
    if not fpw.enabled or policy_year <= 1:
        return 0.0

    if fpw.method == "pct_of_boy_account_value":
        pct = float(fpw.params.get("pct", 0.0))
        return max(0.0, pct * float(year_bop_av))

    if fpw.method == "prior_year_interest_credited":
        return max(0.0, float(prior_policy_year_interest))

    return 0.0


def compute_user_withdrawal_amount(
    inputs: IllustrationInputs,
    policy_year: int,
    year_bop_av: float,
    prior_policy_year_interest: float,
) -> float:
    if policy_year <= 1:
        return 0.0

    if inputs.withdrawal_method == "pct_of_boy_av":
        return max(0.0, float(inputs.withdrawal_value) * float(year_bop_av))

    if inputs.withdrawal_method == "fixed_amount":
        return max(0.0, float(inputs.withdrawal_value))

    if inputs.withdrawal_method == "prior_year_interest_credited":
        return max(0.0, float(prior_policy_year_interest))

    return 0.0


def _refresh_year_state_if_needed(
    *,
    catalog: ProductCatalog,
    inputs: IllustrationInputs,
    state: WithdrawalState,
    policy_year: int,
    month_in_policy_year: int,
    year_bop_av: float,
    prior_policy_year_interest: float,
) -> WithdrawalState:
    spec = catalog.get(inputs.product_code)

    if policy_year != state.policy_year and month_in_policy_year == 1:
        free_limit = compute_free_limit_for_year(
            spec=spec,
            policy_year=policy_year,
            year_bop_av=year_bop_av,
            prior_policy_year_interest=prior_policy_year_interest,
        )
        return WithdrawalState(
            policy_year=policy_year,
            month_in_policy_year=month_in_policy_year,
            free_limit_ytd=float(free_limit),
            free_used_ytd=0.0,
            free_remaining_ytd=float(free_limit),
        )

    if month_in_policy_year != state.month_in_policy_year:
        return WithdrawalState(
            policy_year=state.policy_year,
            month_in_policy_year=month_in_policy_year,
            free_limit_ytd=state.free_limit_ytd,
            free_used_ytd=state.free_used_ytd,
            free_remaining_ytd=state.free_remaining_ytd,
        )

    return state


def calc_withdrawal_for_month(
    *,
    catalog: ProductCatalog,
    inputs: IllustrationInputs,
    state: WithdrawalState,
    policy_year: int,
    month_in_policy_year: int,
    av_bop: float,
    year_bop_av: float,
    prior_policy_year_interest: float,
    # NEW: factor passed in from illustration (0.0 means “no MVA”)
    mva_factor: float = 0.0,
) -> tuple[WithdrawalState, WithdrawalResult]:
    """
    v0 assumption:
    - only allow withdrawal at month 1 of each policy year (year >= 2)
    - state tracks remaining free amount through the year for downstream CSV/UI usage

    MVA:
    - applies to the excess portion (net of surrender charge amount per your A-B-C structure)
    """

    # Ensure state is initialized for the current policy year/month
    state = _refresh_year_state_if_needed(
        catalog=catalog,
        inputs=inputs,
        state=state,
        policy_year=policy_year,
        month_in_policy_year=month_in_policy_year,
        year_bop_av=year_bop_av,
        prior_policy_year_interest=prior_policy_year_interest,
    )

    # Default: no withdrawal this month — but still return free-budget info from state
    if not (month_in_policy_year == 1 and policy_year >= 2):
        res = WithdrawalResult(
            withdrawal_amount=0.0,
            free_limit_ytd=float(state.free_limit_ytd),
            free_used_this_txn=0.0,
            free_used_ytd_eop=float(state.free_used_ytd),
            free_remaining_eop=float(state.free_remaining_ytd),
            excess_amount=0.0,
            surrender_charge_pct=0.0,
            surrender_charge_amount=0.0,
            mva_factor=float(mva_factor),
            mva_amount_subject=0.0,
            mva_amount=0.0,
            penalty_total=0.0,
        )
        return state, res

    # Requested withdrawal per user instruction
    wd_req = compute_user_withdrawal_amount(
        inputs=inputs,
        policy_year=policy_year,
        year_bop_av=year_bop_av,
        prior_policy_year_interest=prior_policy_year_interest,
    )
    wd = min(max(0.0, float(wd_req)), max(0.0, float(av_bop)))

    # Split into free vs excess
    free_used_this_txn = min(wd, max(0.0, float(state.free_remaining_ytd)))
    excess_amount = max(0.0, wd - free_used_this_txn)

    # Update free-used YTD
    free_used_ytd_eop = float(state.free_used_ytd) + float(free_used_this_txn)
    free_remaining_eop = max(0.0, float(state.free_limit_ytd) - free_used_ytd_eop)

    # Surrender charge applies to excess portion
    surrender_charge_pct = float(catalog.surrender_charge(inputs.product_code, policy_year))
    surrender_charge_amount = float(excess_amount) * float(surrender_charge_pct)

    # MVA applies to “amount subject” per your A-B-C structure:
    # A=wd, B=free_used_this_txn, C=surrender_charge_amount
    # subject = max(0, A-B-C) = max(0, excess_amount - surrender_charge_amount)
    mva_factor = float(mva_factor)
    mva_amount_subject = max(0.0, float(excess_amount) - float(surrender_charge_amount))
    mva_amount = float(mva_amount_subject) * float(mva_factor)

    # “Penalty / adjustment total” per your request
    penalty_total = float(surrender_charge_amount) + float(mva_amount)

    new_state = WithdrawalState(
        policy_year=policy_year,
        month_in_policy_year=month_in_policy_year,
        free_limit_ytd=float(state.free_limit_ytd),
        free_used_ytd=float(free_used_ytd_eop),
        free_remaining_ytd=float(free_remaining_eop),
    )

    res = WithdrawalResult(
        withdrawal_amount=float(wd),
        free_limit_ytd=float(state.free_limit_ytd),
        free_used_this_txn=float(free_used_this_txn),
        free_used_ytd_eop=float(free_used_ytd_eop),
        free_remaining_eop=float(free_remaining_eop),
        excess_amount=float(excess_amount),
        surrender_charge_pct=float(surrender_charge_pct),
        surrender_charge_amount=float(surrender_charge_amount),
        mva_factor=float(mva_factor),
        mva_amount_subject=float(mva_amount_subject),
        mva_amount=float(mva_amount),
        penalty_total=float(penalty_total),
    )

    return new_state, res