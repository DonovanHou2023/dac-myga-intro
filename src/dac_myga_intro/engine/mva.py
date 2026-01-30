from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


# ============================================================
# MVA FACTOR ONLY
# ============================================================

@dataclass(frozen=True)
class MVAInputs:
    """
    Contract-style MVA factor inputs.

    D = ((1 + X) / (1 + Y))^(N / 12) - 1

    where:
      X = initial benchmark index rate (annual)
      Y = current benchmark index rate (annual)
      N = months remaining in MVA period
    """
    x_initial_index_rate: float   # X
    y_current_index_rate: float   # Y
    n_months_remaining: int       # N (>= 0)


@dataclass(frozen=True)
class MVAResult:
    """
    Pure MVA factor output.
    """
    mva_factor: float


def compute_mva_factor(
    *,
    x: float,
    y: float,
    n_months_remaining: int,
) -> float:
    """
    Computes the MVA factor:

        D = ((1 + X) / (1 + Y))^(N / 12) - 1

    Guardrails:
    - If N <= 0 → factor = 0.0
    - Require (1 + X) > 0 and (1 + Y) > 0
    """
    n = int(n_months_remaining)
    if n <= 0:
        return 0.0

    one_plus_x = 1.0 + float(x)
    one_plus_y = 1.0 + float(y)

    if one_plus_x <= 0.0 or one_plus_y <= 0.0:
        raise ValueError(
            f"Invalid MVA rates: require 1+X > 0 and 1+Y > 0. "
            f"Got X={x}, Y={y}"
        )

    return (one_plus_x / one_plus_y) ** (n / 12.0) - 1.0


def calculate_mva_factor(inputs: MVAInputs) -> MVAResult:
    """
    Public API: compute and return ONLY the MVA factor.

    Dollar impact is intentionally handled elsewhere.
    """
    factor = compute_mva_factor(
        x=inputs.x_initial_index_rate,
        y=inputs.y_current_index_rate,
        n_months_remaining=inputs.n_months_remaining,
    )

    return MVAResult(mva_factor=float(factor))