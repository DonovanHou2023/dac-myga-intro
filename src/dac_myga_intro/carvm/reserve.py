# src/dac_myga_intro/carvm/reserve.py
from __future__ import annotations

from typing import Dict

import numpy as np
import pandas as pd

from dac_myga_intro.carvm.annuity_pv import compute_annuitization_pvs


def compute_carvm_reserve_reverse_induction(
    annual_df: pd.DataFrame,
    *,
    issue_age: int,
    carvm_discount_rate: float,
    annuity_discount_rate: float,
    installment_years: int,
    ann_tables: dict,
    qx_by_age: Dict[int, float],
    gender: str,
    last_year_continuation_basis: str = "CSV",  # "CSV" or "AV"
) -> pd.DataFrame:
    """
    Reverse induction (your current intended logic):

    - WD: BOY withdrawal amount (column "WD").
    - Year-end benefits:
        Death = AV_EOY
        Surrender = CSV_EOY (fallback AV_EOY)
        Installment PV / Single Life PV computed from amount_applied = AV_EOY
        Annuitization Benefit = max(Installment PV, Single Life PV)
    - Continuation:
        Last year = CSV_EOY (or AV_EOY)
        Prior years: Continuation_y = WD_(y+1) + MaximumBenefit_(y+1)/(1+i_carvm)
    - Maximum Benefit = max(Death, Surrender, Annuitization, Continuation)
    - Reserve (BOY) = MaximumBenefit/(1+i_carvm) + WD
    - Winning Benefit = argmax among the 4 benefits (for row-level highlight)
    """
    df = annual_df.copy().reset_index(drop=True)

    # Attained Age as int
    if "Attained Age" not in df.columns or df["Attained Age"].isna().all():
        df["Attained Age"] = (int(issue_age) + df["Policy Year"]).astype(int)
    else:
        df["Attained Age"] = pd.to_numeric(df["Attained Age"], errors="coerce").round().astype("Int64")

    if "WD" not in df.columns:
        df["WD"] = 0.0

    df["Death Benefit"] = df.get("AV_EOY", np.nan)
    if "CSV_EOY" in df.columns and df["CSV_EOY"].notna().any():
        df["Surrender Benefit"] = df["CSV_EOY"]
    else:
        df["Surrender Benefit"] = df.get("AV_EOY", np.nan)

    # annuitization PVs per year
    inst_pvs = []
    life_pvs = []
    ann_bens = []

    for _, r in df.iterrows():
        amt = float(r["AV_EOY"]) if pd.notna(r.get("AV_EOY", np.nan)) else 0.0
        age_i = int(r["Attained Age"]) if pd.notna(r.get("Attained Age", np.nan)) else int(issue_age) + int(r["Policy Year"])

        pv_inst, pv_life, ann_ben = compute_annuitization_pvs(
            amount_applied=amt,
            attained_age=age_i,
            gender=str(gender),
            installment_years=int(installment_years),
            ann_tables=ann_tables,
            qx_by_age=qx_by_age,
            annuity_discount_rate=float(annuity_discount_rate),
        )
        inst_pvs.append(pv_inst)
        life_pvs.append(pv_life)
        ann_bens.append(ann_ben)

    df["Installment PV"] = inst_pvs
    df["Single Life PV"] = life_pvs
    df["Annuitization Benefit"] = ann_bens

    # reverse induction
    i = float(carvm_discount_rate)
    disc = 1.0 / (1.0 + i)

    df["Continuation Benefit"] = 0.0
    df["Maximum Benefit"] = 0.0
    df["Reserve (BOY)"] = 0.0
    df["Winning Benefit"] = ""

    n = len(df)
    next_max_benefit = 0.0
    next_wd = 0.0

    for idx in range(n - 1, -1, -1):
        death = float(df.loc[idx, "Death Benefit"]) if pd.notna(df.loc[idx, "Death Benefit"]) else 0.0
        surr = float(df.loc[idx, "Surrender Benefit"]) if pd.notna(df.loc[idx, "Surrender Benefit"]) else 0.0
        annb = float(df.loc[idx, "Annuitization Benefit"]) if pd.notna(df.loc[idx, "Annuitization Benefit"]) else 0.0
        wd = float(df.loc[idx, "WD"]) if pd.notna(df.loc[idx, "WD"]) else 0.0

        if idx == n - 1:
            if str(last_year_continuation_basis).upper() == "AV":
                cont = float(df.loc[idx, "AV_EOY"]) if pd.notna(df.loc[idx, "AV_EOY"]) else 0.0
            else:
                cont = float(df.loc[idx, "Surrender Benefit"]) if pd.notna(df.loc[idx, "Surrender Benefit"]) else 0.0
        else:
            cont = float(next_wd) + float(next_max_benefit) * disc

        df.loc[idx, "Continuation Benefit"] = cont

        max_ben = max(death, surr, annb, cont)
        df.loc[idx, "Maximum Benefit"] = max_ben

        # Reserve at BOY (your current implementation): discounted max + WD at BOY
        df.loc[idx, "Reserve (BOY)"] = max_ben * disc + wd

        candidates = {
            "Death Benefit": death,
            "Surrender Benefit": surr,
            "Annuitization Benefit": annb,
            "Continuation Benefit": cont,
        }
        df.loc[idx, "Winning Benefit"] = max(candidates, key=candidates.get)

        next_max_benefit = max_ben
        next_wd = wd

    return df