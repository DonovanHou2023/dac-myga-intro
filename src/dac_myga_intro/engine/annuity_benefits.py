from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional

import pandas as pd

GenderCategory = Literal["M", "F"]


@dataclass(frozen=True)
class InstallmentTable:
    """years -> monthly_per_1000"""
    df: pd.DataFrame  # columns: years, monthly_per_1000

    def monthly_per_1000(self, years: int) -> float:
        if years < 1 or years > 30:
            raise ValueError(f"installment years must be 1..30, got {years}")
        row = self.df.loc[self.df["years"] == years]
        if row.empty:
            raise ValueError(f"installment table missing years={years}")
        return float(row.iloc[0]["monthly_per_1000"])


@dataclass(frozen=True)
class LifeIncomeTable:
    """age -> male_per_1000, female_per_1000; supports linear interpolation."""
    df: pd.DataFrame  # columns: age, male_per_1000, female_per_1000

    def monthly_per_1000(self, age: float, gender: GenderCategory) -> float:
        if age < 50:
            return 0.0

        col = "male_per_1000" if gender == "M" else "female_per_1000"
        x = self.df["age"].astype(float).to_numpy()
        y = self.df[col].astype(float).to_numpy()

        # clamp above max age to last point (or you can raise instead; your choice)
        if age <= float(x.min()):
            return float(y[x.argmin()])
        if age >= float(x.max()):
            return float(y[x.argmax()])

        # find neighbors
        # x is sparse but sorted in your data; ensure sort anyway
        d = self.df.sort_values("age")
        x = d["age"].astype(float).to_numpy()
        y = d[col].astype(float).to_numpy()

        # locate interval
        import numpy as np
        idx = int(np.searchsorted(x, age))
        x0, x1 = float(x[idx - 1]), float(x[idx])
        y0, y1 = float(y[idx - 1]), float(y[idx])

        # linear interpolation
        w = (age - x0) / (x1 - x0)
        return y0 + w * (y1 - y0)


@dataclass(frozen=True)
class AnnuityPayoutTables:
    installment: InstallmentTable
    life_no_guarantee: LifeIncomeTable


def load_annuity_tables(root: Path) -> AnnuityPayoutTables:
    """
    root should be something like: Path("src/data/annuity_tables")
    """
    inst_path = root / "installment_option.csv"
    life_path = root / "life_income_no_guarantee.csv"

    inst = pd.read_csv(inst_path)
    life = pd.read_csv(life_path)

    # basic schema validation
    for c in ["years", "monthly_per_1000"]:
        if c not in inst.columns:
            raise ValueError(f"installment table missing column: {c}")

    for c in ["age", "male_per_1000", "female_per_1000"]:
        if c not in life.columns:
            raise ValueError(f"life income table missing column: {c}")

    return AnnuityPayoutTables(
        installment=InstallmentTable(df=inst),
        life_no_guarantee=LifeIncomeTable(df=life),
    )


def annuity_monthly_payment(
    *,
    amount_applied: float,
    option: Literal["installment_certain", "single_life_no_guarantee"],
    tables: AnnuityPayoutTables,
    years: Optional[int] = None,
    attained_age: Optional[float] = None,
    gender: Optional[GenderCategory] = None,
) -> float:
    """
    Converts amount_applied into monthly payout using table factors.

    Tables are per $1,000, so:
      monthly_payment = (amount_applied / 1000) * monthly_per_1000
    """
    amt = max(0.0, float(amount_applied))

    if option == "installment_certain":
        if years is None:
            raise ValueError("installment_certain requires years")
        f = tables.installment.monthly_per_1000(int(years))
        return (amt / 1000.0) * float(f)

    if option == "single_life_no_guarantee":
        if attained_age is None or gender is None:
            raise ValueError("single_life_no_guarantee requires attained_age and gender")
        f = tables.life_no_guarantee.monthly_per_1000(float(attained_age), gender)
        return (amt / 1000.0) * float(f)

    raise ValueError(f"unknown option: {option}")