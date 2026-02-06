# src/dac_myga_intro/carvm/mortality.py
from __future__ import annotations

from pathlib import Path
from typing import Dict

import pandas as pd


def _read_iam_table(path: Path) -> Dict[int, float]:
    """
    Reads a CSV shaped like:
      Row\Column,1
      0,0.001801
      1,0.00045
      ...

    Returns: {age: qx_annual}
    """
    df = pd.read_csv(path)

    age_col = df.columns[0]
    qx_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]

    out: Dict[int, float] = {}
    for _, r in df.iterrows():
        try:
            age = int(float(r[age_col]))
            qx = float(r[qx_col])
            out[age] = max(0.0, min(1.0, qx))
        except Exception:
            continue
    return out


def load_mortality_table(gender: str, *, mort_root: Path) -> Dict[int, float]:
    """
    Loads 2012 IAM from:
      mort_root/2012IAM_M.csv
      mort_root/2012IAM_F.csv
    """
    gender = str(gender).upper().strip()
    f = mort_root / ("2012IAM_M.csv" if gender == "M" else "2012IAM_F.csv")
    if not f.exists():
        raise FileNotFoundError(f"Mortality table not found: {f}")
    return _read_iam_table(f)