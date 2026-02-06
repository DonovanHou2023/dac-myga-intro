# src/dac_myga_intro/carvm/annuity_pv.py
from __future__ import annotations

from typing import Dict, Tuple

import numpy as np

from dac_myga_intro.engine.annuity_benefits import annuity_monthly_payment


def pv_installment_certain_monthly(
    monthly_payment: float,
    years: int,
    annual_discount_rate: float,
) -> float:
    """PV of level monthly payment for N years (no mortality)."""
    years = int(years)
    if years <= 0 or monthly_payment <= 0:
        return 0.0

    im = (1.0 + float(annual_discount_rate)) ** (1.0 / 12.0) - 1.0
    v = 1.0 / (1.0 + im)
    n = years * 12
    m = np.arange(1, n + 1, dtype=float)
    return float(np.sum(monthly_payment * (v ** m)))


def pv_single_life_monthly(
    monthly_payment: float,
    attained_age: int,
    annual_discount_rate: float,
    qx_by_age: Dict[int, float],
    *,
    max_age: int = 121,
) -> float:
    """
    PV of level monthly payment contingent on survival (approx):
      - annual qx at integer ages from table
      - monthly survival: p_month(age) = (1 - qx(age))^(1/12)
      - payment at end of month m occurs if alive at end of that month
    """
    if monthly_payment <= 0:
        return 0.0

    im = (1.0 + float(annual_discount_rate)) ** (1.0 / 12.0) - 1.0
    v = 1.0 / (1.0 + im)

    age0 = max(0, int(attained_age))
    pv = 0.0
    s = 1.0

    max_months = max(0, (int(max_age) - age0) * 12)
    last_age = max(qx_by_age.keys()) if qx_by_age else 120

    for m in range(1, max_months + 1):
        age = age0 + (m - 1) // 12
        qx = float(qx_by_age.get(age, qx_by_age.get(last_age, 1.0)))
        qx = max(0.0, min(1.0, qx))
        p_month = (1.0 - qx) ** (1.0 / 12.0)

        s_end = s * p_month
        pv += monthly_payment * s_end * (v ** m)
        s = s_end

        if s < 1e-10:
            break

    return float(pv)


def compute_annuitization_pvs(
    *,
    amount_applied: float,
    attained_age: int,
    gender: str,
    installment_years: int,
    ann_tables: dict,
    qx_by_age: Dict[int, float],
    annuity_discount_rate: float,
) -> Tuple[float, float, float]:
    """
    Returns:
      (installment_pv, single_life_pv, annuitization_benefit=max(pvs))

    Payout amounts come from your payout tables via annuity_monthly_payment().
    """
    if amount_applied <= 0:
        return 0.0, 0.0, 0.0

    m_inst = float(
        annuity_monthly_payment(
            amount_applied=float(amount_applied),
            option="installment_certain",
            tables=ann_tables,
            years=int(installment_years),
        )
    )
    pv_inst = pv_installment_certain_monthly(
        monthly_payment=m_inst,
        years=int(installment_years),
        annual_discount_rate=float(annuity_discount_rate),
    )

    m_life = float(
        annuity_monthly_payment(
            amount_applied=float(amount_applied),
            option="single_life_no_guarantee",
            tables=ann_tables,
            attained_age=float(attained_age),
            gender=str(gender),
        )
    )
    pv_life = pv_single_life_monthly(
        monthly_payment=m_life,
        attained_age=int(attained_age),
        annual_discount_rate=float(annuity_discount_rate),
        qx_by_age=qx_by_age,
        max_age=121,
    )

    ann_ben = max(float(pv_inst), float(pv_life))
    return float(pv_inst), float(pv_life), float(ann_ben)