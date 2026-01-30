from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Literal

WithdrawalMethod = Literal[
    "pct_of_boy_av",
    "fixed_amount",
    "prior_year_interest_credited",
]

GenderCategory = Literal["M", "F"]


@dataclass(frozen=True)
class IllustrationInputs:
    # --- required (no defaults) must come first ---
    product_code: str
    premium: float
    issue_age: int
    gender: GenderCategory

    initial_rate: float
    renewal_rate: float

    withdrawal_method: WithdrawalMethod

    # --- optional/default fields below ---
    projection_years: int = 15  # 0 => default to product term in illustration.py
    withdrawal_value: float = 0.0

    mva_initial_index_rate: Optional[float] = None
    mva_current_index_rate: Optional[float] = None
    mva_months_remaining_override: Optional[int] = None