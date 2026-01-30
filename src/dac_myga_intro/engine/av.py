from __future__ import annotations

from dataclasses import dataclass


def monthly_rate_from_annual(r_annual: float) -> float:
    return (1.0 + r_annual) ** (1.0 / 12.0) - 1.0


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
) -> AVResult:
    """
    AV roll-forward:
      av_after_wd = av_bop - withdrawal - penalty
      interest = av_after_wd * monthly_rate
      av_eop = av_after_wd + interest
    """
    av_after_wd = max(0.0, float(av_bop) - max(0.0, float(withdrawal)) - max(0.0, float(penalty)))
    r_m = monthly_rate_from_annual(float(annual_rate))
    interest = av_after_wd * r_m
    av_eop = av_after_wd + interest
    return AVResult(av_after_wd=av_after_wd, interest_credit=interest, av_eop=av_eop)