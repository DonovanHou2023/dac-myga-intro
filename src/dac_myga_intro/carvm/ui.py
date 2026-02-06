# src/dac_myga_intro/carvm/ui.py
from __future__ import annotations

from typing import Optional

import streamlit as st


def pct_slider(
    label: str,
    default_pct: float,
    *,
    min_pct: float = 0.0,
    max_pct: float = 15.0,
    step_pct: float = 0.05,
    key: str | None = None,
) -> float:
    """UI shows %; returns decimal."""
    v = st.slider(
        label,
        min_value=float(min_pct),
        max_value=float(max_pct),
        value=float(default_pct),
        step=float(step_pct),
        format="%.2f%%",
        key=key,
    )
    return float(v) / 100.0


def safe_get_free_pct(spec) -> Optional[float]:
    """
    Extract "free partial withdrawal %" from YAML spec object.
    Supports method 'pct_of_boy_account_value' with params {'pct': ...}.
    """
    try:
        fpw = spec.features.free_partial_withdrawal
        if not bool(fpw.enabled):
            return None
        if str(fpw.method) not in (
            "pct_of_boy_account_value",
            "pct_of_boy_av",
            "pct_of_boy_account_value_yearly",
        ):
            return None
        params = getattr(fpw, "params", {}) or {}
        pct = params.get("pct", None)
        return float(pct) if pct is not None else None
    except Exception:
        return None