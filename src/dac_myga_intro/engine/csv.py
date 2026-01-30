from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CSVResult:
    csv: float
    csv_before_floors: float

    # Debug / transparency (optional but useful for exhibits)
    amount_subject_to_surrender_charge: float
    surrender_charge_pct_used: float
    surrender_charge_amount_used: float


def _calc_surrender_charge_amount(
    *,
    withdrawal_amount: float,
    free_used_this_txn: float,
    surrender_charge_pct: float,
    surrender_charge_amount_override: Optional[float] = None,
    surrender_charge_pct_override: Optional[float] = None,
) -> tuple[float, float, float]:
    """
    Returns:
      (amount_subject_to_sc, pct_used, sc_amount)

    Contract intent (your simplified model):
      - free_used_this_txn is not subject to surrender charge
      - only the excess portion is subject to surrender charge
    """
    w = max(0.0, float(withdrawal_amount))
    free_used = max(0.0, float(free_used_this_txn))

    amount_subject = max(0.0, w - free_used)

    # Override rules (used for term-end or special waiver conditions)
    if surrender_charge_amount_override is not None:
        sc_amt = max(0.0, float(surrender_charge_amount_override))
        pct_used = float(surrender_charge_pct_override) if surrender_charge_pct_override is not None else float(surrender_charge_pct)
        return amount_subject, pct_used, sc_amt

    pct_used = float(surrender_charge_pct_override) if surrender_charge_pct_override is not None else float(surrender_charge_pct)
    pct_used = max(0.0, pct_used)

    sc_amt = amount_subject * pct_used
    return amount_subject, pct_used, sc_amt


def calculate_cash_surrender_value(
    av: float,
    *,
    # Option A (recommended): pass the already-computed surrender charge amount
    surrender_charge_amount: Optional[float] = None,

    # Option B (alternative): let CSV compute surrender charge amount from mechanics
    withdrawal_amount: float = 0.0,
    free_used_this_txn: float = 0.0,
    surrender_charge_pct: float = 0.0,

    # Term-end / waiver overrides
    # Example: if month == term_month, pass surrender_charge_pct_override=0.0
    surrender_charge_amount_override: Optional[float] = None,
    surrender_charge_pct_override: Optional[float] = None,

    # MVA (optional)
    mva_amount: float = 0.0,

    # Floors (future)
    gmv_floor: Optional[float] = None,
    nff_floor: Optional[float] = None,
) -> CSVResult:
    """
    Base (v0):
      csv_before_floors = max(0, av - surrender_charge_amount_used + mva_amount)

    Notes:
    - If surrender_charge_amount is provided, we use it (unless override is provided).
    - Otherwise we compute SC from withdrawal mechanics:
        amount_subject = max(0, withdrawal_amount - free_used_this_txn)
        SC = amount_subject * surrender_charge_pct
    - Override hooks:
        * surrender_charge_pct_override = 0.0 for term-end month (month 60 etc.)
        * surrender_charge_amount_override = 0.0 for waivers
    """
    av = float(av)
    mva_amount = float(mva_amount)

    # Decide how to source surrender charge amount
    if surrender_charge_amount is not None and surrender_charge_amount_override is None:
        # Use precomputed amount
        sc_amt_used = max(0.0, float(surrender_charge_amount))
        # Still produce diagnostics consistent with that approach
        amount_subject = max(0.0, float(withdrawal_amount) - float(free_used_this_txn))
        pct_used = float(surrender_charge_pct_override) if surrender_charge_pct_override is not None else float(surrender_charge_pct)
    else:
        amount_subject, pct_used, sc_amt_used = _calc_surrender_charge_amount(
            withdrawal_amount=withdrawal_amount,
            free_used_this_txn=free_used_this_txn,
            surrender_charge_pct=surrender_charge_pct,
            surrender_charge_amount_override=surrender_charge_amount_override,
            surrender_charge_pct_override=surrender_charge_pct_override,
        )

    base = max(0.0, av - sc_amt_used + mva_amount)

    floors = [base]
    if gmv_floor is not None:
        floors.append(float(gmv_floor))
    if nff_floor is not None:
        floors.append(float(nff_floor))

    final_csv = max(floors)

    return CSVResult(
        csv=final_csv,
        csv_before_floors=base,
        amount_subject_to_surrender_charge=float(amount_subject),
        surrender_charge_pct_used=float(pct_used),
        surrender_charge_amount_used=float(sc_amt_used),
    )