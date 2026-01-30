from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import pandas as pd


Sex = Literal["male", "female"]
AnnuityOption = Literal["installment", "life_income_no_guarantee"]


@dataclass(frozen=True)
class AnnuityTables:
    installment: pd.DataFrame
    life_income: pd.DataFrame


def load_annuity_tables(base_dir: Path) -> AnnuityTables:
    """
    Loads CSV tables from src/dac_myga_intro/data/annuity_tables/.
    """
    inst = pd.read_csv(base_dir / "installment_option.csv")
    life = pd.read_csv(base_dir / "life_income_no_guarantee.csv")

    # normalize columns
    inst["years"] = inst["years"].astype(int)
    life["age"] = life["age"].astype(int)

    return AnnuityTables(installment=inst, life_income=life)


def _lookup_installment_factor(inst_df: pd.DataFrame, years: int) -> float:
    row = inst_df.loc[inst_df["years"] == int(years)]
    if row.empty:
        raise ValueError(f"Installment table does not contain years={years}")
    return float(row.iloc[0]["monthly_per_1000"])


def _lookup_life_income_factor(life_df: pd.DataFrame, age: int, sex: Sex) -> float:
    """
    Simple lookup:
    - exact age match required for v0
    Later you can add interpolation.
    """
    row = life_df.loc[life_df["age"] == int(age)]
    if row.empty:
        raise ValueError(f"Life income table does not contain age={age}")

    col = "male_per_1000" if sex == "male" else "female_per_1000"
    return float(row.iloc[0][col])


def monthly_annuity_payment(
    *,
    proceeds: float,
    option: AnnuityOption,
    tables: AnnuityTables,
    installment_years: int | None = None,
    age: int | None = None,
    sex: Sex | None = None,
) -> float:
    """
    Returns monthly payment given proceeds (account value at annuitization).

    Payment formula: (proceeds / 1000) * factor

    Required inputs:
    - installment: installment_years
    - life_income_no_guarantee: age, sex
    """
    proceeds = float(proceeds)
    if proceeds <= 0:
        return 0.0

    if option == "installment":
        if installment_years is None:
            raise ValueError("installment_years is required for installment option")
        factor = _lookup_installment_factor(tables.installment, installment_years)

    elif option == "life_income_no_guarantee":
        if age is None or sex is None:
            raise ValueError("age and sex are required for life income option")
        factor = _lookup_life_income_factor(tables.life_income, age, sex)

    else:
        raise ValueError(f"Unknown option: {option}")

    return (proceeds / 1000.0) * factor