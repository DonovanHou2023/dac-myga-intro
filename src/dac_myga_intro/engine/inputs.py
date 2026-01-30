from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Literal

# Keep WithdrawalMethod definition here too (shared)
WithdrawalMethod = Literal[
    "pct_of_boy_av",
    "fixed_amount",
    "prior_year_interest_credited",
]

GenderCategory = Literal[
    "M",
    "F",
]


@dataclass(frozen=True)
class IllustrationInputs:
    product_code: str
    premium: float
    issue_age: int
    gender: GenderCategory

    initial_rate: float
    renewal_rate: float

    withdrawal_method: WithdrawalMethod
    withdrawal_value: float = 0.0

    # MVA assumptions (optional)
    mva_initial_index_rate: Optional[float] = None
    mva_current_index_rate: Optional[float] = None
    mva_months_remaining_override: Optional[int] = None
