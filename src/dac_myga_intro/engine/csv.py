from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CSVResult:
    # Final values
    csv: float
    csv_before_floors: float
    nff_floor_used: float

    # Transparency / exhibits (debug)
    av_eop: float
    surrender_amount: float

    free_remaining_at_calc: float
    free_portion_used: float

    amount_subject_to_surrender_charge: float
    surrender_charge_pct_used: float
    surrender_charge_amount_used: float

    amount_subject_to_mva: float
    mva_factor_used: float
    mva_amount_used: float


def _clamp_nonneg(x: float) -> float:
    return max(0.0, float(x))


def calculate_cash_surrender_value(
    av_eop: float,
    *,
    # Full surrender by default; allow partial surrender if you ever want it.
    surrender_amount: Optional[float] = None,

    # Free withdrawal budget remaining at the time of CSV calculation
    # (this is the “free portion left” you described)
    free_remaining_at_calc: float = 0.0,

    # Surrender charge mechanics
    surrender_charge_pct: float = 0.0,
    surrender_charge_pct_override: Optional[float] = None,  # e.g., set 0.0 at term-end month

    # MVA mechanics (factor only; dollar amount computed here)
    mva_factor: float = 0.0,

    # Guarantee fund floor (you said “floored by both guarantee funds”)
    gf_mfv_eop: Optional[float] = None,
    gf_pfv_eop: Optional[float] = None,

    # Other floors (optional, future hooks)
    gmv_floor: Optional[float] = None,
) -> CSVResult:
    """
    CSV computed at time t (v0+):

    Given AV at EOP (already rolled forward), compute surrender payout:

      A = surrender_amount (default = AV_EOP for full surrender)
      B = free_portion_used = min(A, free_remaining_at_calc)
      Excess = max(0, A - B)

      SC = Excess * s_y   (s_y may be overridden to 0 at term end)
      AmountSubjectToMVA = max(0, Excess - SC)   (your A-B-C structure)
      MVA = AmountSubjectToMVA * mva_factor

      CSV_before_floors = max(0, A - SC + MVA)

    Floors:
      NFF floor = max(gf_mfv_eop, gf_pfv_eop) if provided
      CSV = max(CSV_before_floors, NFF floor, GMV floor if provided)

    Notes:
    - This function assumes the free portion remaining applies to surrender/CSV calc
      the same way it applies to withdrawals (not subject to SC or MVA).
    - If your contract treats free withdrawal as NOT applicable to full surrender,
      you'd set free_remaining_at_calc=0 for surrender events.
    """

    av_eop_f = _clamp_nonneg(av_eop)

    # Full surrender by default
    A = av_eop_f if surrender_amount is None else _clamp_nonneg(surrender_amount)

    free_rem = _clamp_nonneg(free_remaining_at_calc)
    free_portion_used = min(A, free_rem)

    amount_subject_sc = _clamp_nonneg(A - free_portion_used)

    pct_used = float(surrender_charge_pct_override) if surrender_charge_pct_override is not None else float(surrender_charge_pct)
    pct_used = _clamp_nonneg(pct_used)

    sc_amt = amount_subject_sc * pct_used

    # MVA subject after SC per your structure
    mva_factor_used = float(mva_factor)
    amount_subject_mva = _clamp_nonneg(amount_subject_sc - sc_amt)
    mva_amt = amount_subject_mva * mva_factor_used

    csv_before_floors = _clamp_nonneg(A - sc_amt + mva_amt)

    # Guarantee fund floor (NFF-style): floor by BOTH funds (max)
    mfv = _clamp_nonneg(gf_mfv_eop) if gf_mfv_eop is not None else 0.0
    pfv = _clamp_nonneg(gf_pfv_eop) if gf_pfv_eop is not None else 0.0
    nff_floor = max(mfv, pfv)

    floors = [csv_before_floors, nff_floor]
    if gmv_floor is not None:
        floors.append(_clamp_nonneg(gmv_floor))

    final_csv = max(floors)

    return CSVResult(
        csv=float(final_csv),
        csv_before_floors=float(csv_before_floors),
        nff_floor_used=float(nff_floor),

        av_eop=float(av_eop_f),
        surrender_amount=float(A),

        free_remaining_at_calc=float(free_rem),
        free_portion_used=float(free_portion_used),

        amount_subject_to_surrender_charge=float(amount_subject_sc),
        surrender_charge_pct_used=float(pct_used),
        surrender_charge_amount_used=float(sc_amt),

        amount_subject_to_mva=float(amount_subject_mva),
        mva_factor_used=float(mva_factor_used),
        mva_amount_used=float(mva_amt),
    )