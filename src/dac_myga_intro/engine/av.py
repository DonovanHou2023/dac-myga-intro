from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


def monthly_rate_from_annual(r_annual: float) -> float:
    return (1.0 + float(r_annual)) ** (1.0 / 12.0) - 1.0


@dataclass(frozen=True)
class AVResult:
    av_after_wd: float
    interest_credit: float
    av_eop: float


def roll_forward_account_value(
    av_bop: float,
    *,
    withdrawal: float,
    penalty: float,
    annual_rate: float,
    # NEW: optional floor (e.g., max(MFV_eop, PFV_eop))
    floor_eop: Optional[float] = None,
) -> AVResult:
    """
    AV roll-forward:

      av_after_wd = max(0, av_bop - withdrawal - penalty)
      interest    = av_after_wd * monthly_rate
      av_eop_raw  = av_after_wd + interest
      av_eop      = max(av_eop_raw, floor_eop) if floor_eop provided

    Notes:
    - penalty is intended to be the *total* penalty/adjustment from withdrawals
      (e.g., surrender charge + MVA amount) for this month.
    - floor_eop is applied after interest is credited (EOP floor).
    """
    av_bop_f = float(av_bop)
    wd = max(0.0, float(withdrawal))
    pen = max(0.0, float(penalty))

    av_after_wd = max(0.0, av_bop_f - wd - pen)

    r_m = monthly_rate_from_annual(float(annual_rate))
    interest = av_after_wd * r_m

    av_eop_raw = av_after_wd + interest

    if floor_eop is not None:
        floor_val = max(0.0, float(floor_eop))
        av_eop = max(av_eop_raw, floor_val)
    else:
        av_eop = av_eop_raw

    return AVResult(
        av_after_wd=av_after_wd,
        interest_credit=interest,
        av_eop=av_eop,
    )