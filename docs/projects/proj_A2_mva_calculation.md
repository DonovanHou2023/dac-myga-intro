## Step 2 — Market Value Adjustment (MVA) Calculation

!!! abstract "Purpose of This Step"
    The purpose of this step is to calculate the **Market Value Adjustment (MVA) factor**
    used in MYGA illustrations.

    The MVA reflects **economic gains or losses** on assets when funds are withdrawn
    before the end of the guarantee period.

    This step focuses on **calculating the MVA factor only** — not the dollar impact.
    Applying the factor to withdrawals or surrender values will be handled in later steps.

---

## What This Step Does

This step introduces a **pure, reusable MVA calculation module** that:

- takes benchmark interest rates as rate input
- converts remaining duration into a discount exponent
- produces a single **dimensionless MVA factor**
- applies guardrails for edge cases

The output of this step will later be used to calculate:

- MVA on excess partial withdrawals
- MVA on full surrender values

---

## Business Requirements (BRD)

### 1. Scope of the MVA Calculation

| Item | Included | Notes |
|---|---|---|
| MVA factor | ✅ | pure factor only |
| Dollar impact | ❌ | handled later |
| Compounding | Annual rates, fractional years | months / 12 |
| Product-specific caps | ❌ | ignored for now |

This separation ensures the MVA logic is:

- testable
- reusable
- independent of policy cash flows

---

### 2. Economic Interpretation

The MVA compares two yield environments:

| Concept | Meaning |
|---|---|
| Issue environment | When the MYGA was priced |
| Current environment | When funds are withdrawn |

| Rate Movement | Asset Value | MVA |
|---|---|---|
| Rates ↑ | Decrease | Negative |
| Rates ↓ | Increase | Positive |

---

### 3. Required Inputs

The MVA factor calculation requires three inputs.

| Symbol | Name | Description |
|---|---|---|
| $X$ | Initial index rate | Benchmark rate at issue |
| $Y$ | Current index rate | Benchmark rate at withdrawal |
| $N$ | Months remaining | Remaining guarantee months |

!!! note
    The benchmark index (e.g., UST 5Y) is defined at the **product level**
    and supplied to this step via earlier configuration.

---

### 4. Mathematical Definition

The MVA factor is defined as:

$$
D = \left(\frac{1 + X}{1 + Y}\right)^{N / 12} - 1
$$

Where:

- $X$ and $Y$ are **annualized rates**
- $N/12$ converts remaining months to fractional years

---

### 5. Guardrails and Edge Cases

The implementation must enforce the following rules:

| Case | Required Behavior |
|---|---|
| $N < 0$ | return factor = 0 |
| $1 + X < 0$ | raise error |
| $1 + Y < 0$ | raise error |

These guardrails prevent mathematically invalid or misleading results.

---

## Inputs and Outputs

### Input Object

| Field | Type | Meaning |
|---|---|---|
| x_initial_index_rate | float | $X$, issue benchmark rate |
| y_current_index_rate | float | $Y$, current benchmark rate |
| n_months_remaining | int | $N$, months remaining |

### Output Object

| Field | Type | Meaning |
|---|---|---|
| mva_factor | float | dimensionless MVA factor |

---

## Starter Code (Expected Implementation)

Below is a **reference implementation** for this step.
Students are expected to understand and reproduce this structure,
not necessarily copy it verbatim.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class MVA```:
    """
    Contract-style MVA factor ```.

    D = ((1 + X) / (1 + Y))^(N / 12) - 1
    """
    x_initial_index_rate: float
    y_current_index_rate: float
    n_months_remaining: int


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
    Computes the MVA factor.

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
            "Invalid MVA rates: require 1 + X > 0 and 1 + Y > 0"
        )

    return (one_plus_x / one_plus_y) ** (n / 12.0) - 1.0


def calculate_mva_factor(```: MVA```) -> MVAResult:
    """
    Public API: compute and return ONLY the MVA factor.
    """
    factor = compute_mva_factor(
        x=```.x_initial_index_rate,
        y=```.y_current_index_rate,
        n_months_remaining=```.n_months_remaining,
    )

    return MVAResult(mva_factor=float(factor))
```

---

## Deliverable for Step 2

By the end of this step, you should have:

- a standalone MVA calculation module
- clear separation between **factor** and **dollar impact**
- guardrails for invalid ```
- unit-testable logic independent of the illustration engine

This MVA factor will be **consumed by later steps** when calculating:

- penalties on excess partial withdrawals
- cash surrender values