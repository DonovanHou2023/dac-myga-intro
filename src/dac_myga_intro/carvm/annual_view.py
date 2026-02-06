# src/dac_myga_intro/carvm/annual_view.py
from __future__ import annotations

import pandas as pd


def build_annual_view(df: pd.DataFrame) -> pd.DataFrame:
    """
    Reduce monthly projection to annual (BOY/EOY).

    WD (your rule):
      - WD is the BOY withdrawal amount (month 1), not sum of months.

    Requires:
      - meta_policy_year, meta_month_in_policy_year
      - av_bop, av_eop
      - wd_withdrawal_amount (optional)
      - csv_final (optional)
      - meta_attained_age (optional)
    """
    if "meta_policy_year" not in df.columns or "meta_month_in_policy_year" not in df.columns:
        raise ValueError("Missing meta columns: need meta_policy_year and meta_month_in_policy_year.")

    boy = df[df["meta_month_in_policy_year"] == 1].copy()
    eoy = df[df["meta_month_in_policy_year"] == 12].copy()

    boy_cols = ["meta_policy_year", "av_bop"]
    if "meta_attained_age" in boy.columns:
        boy_cols.append("meta_attained_age")
    if "wd_withdrawal_amount" in boy.columns:
        boy_cols.append("wd_withdrawal_amount")

    boy = boy[boy_cols].rename(
        columns={
            "av_bop": "AV_BOY",
            "meta_attained_age": "Attained Age",
            "wd_withdrawal_amount": "WD",
        }
    )

    eoy_cols = ["meta_policy_year"]
    if "av_eop" in eoy.columns:
        eoy_cols.append("av_eop")
    if "csv_final" in eoy.columns:
        eoy_cols.append("csv_final")

    eoy = eoy[eoy_cols].rename(columns={"av_eop": "AV_EOY", "csv_final": "CSV_EOY"})

    out = (
        boy.merge(eoy, on="meta_policy_year", how="inner")
        .rename(columns={"meta_policy_year": "Policy Year"})
        .sort_values("Policy Year")
        .reset_index(drop=True)
    )

    if "WD" not in out.columns:
        out["WD"] = 0.0

    # numeric cleanup
    for c in ["AV_BOY", "AV_EOY", "CSV_EOY", "WD", "Attained Age"]:
        if c in out.columns:
            out[c] = pd.to_numeric(out[c], errors="coerce")

    return out


def truncate_to_term_years(annual_df: pd.DataFrame, *, term_years: int) -> pd.DataFrame:
    """For Max FPW path: show years through surrender-charge period (term)."""
    df = annual_df.copy().sort_values("Policy Year").reset_index(drop=True)
    return df[df["Policy Year"] <= int(term_years)].reset_index(drop=True)