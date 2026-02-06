# src/dac_myga_intro/carvm/styling.py
from __future__ import annotations

import pandas as pd


def highlight_winning_path_row(df: pd.DataFrame, winner_path: str) -> pd.io.formats.style.Styler:
    def _style(row):
        if str(row.get("Path", "")) == str(winner_path):
            return ["background-color: #fff3cd; font-weight: 700;"] * len(row)
        return [""] * len(row)

    return df.style.apply(_style, axis=1)


def highlight_winning_benefit_cells(df: pd.DataFrame) -> pd.io.formats.style.Styler:
    """
    Highlights the cell in the winning benefit set for each row
    (Death/Surrender/Annuitization/Continuation) based on "Winning Benefit".
    """
    benefit_cols = ["Death Benefit", "Surrender Benefit", "Annuitization Benefit", "Continuation Benefit"]

    def _row_style(row: pd.Series) -> list[str]:
        styles = [""] * len(row)
        win = str(row.get("Winning Benefit", ""))

        col_to_idx = {c: i for i, c in enumerate(df.columns)}
        for c in benefit_cols:
            if c in col_to_idx and c == win:
                styles[col_to_idx[c]] = "background-color: #d1fae5; font-weight: 700;"
        return styles

    return df.style.apply(_row_style, axis=1)