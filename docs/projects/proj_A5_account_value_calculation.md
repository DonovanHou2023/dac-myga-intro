## Step 5 — Account Value (AV) Roll-Forward

!!! abstract "Purpose of This Step"
    The purpose of this step is to roll the **Account Value (AV)** forward each month,
    applying withdrawal cash flows, penalty adjustments, and monthly interest crediting.

    This step produces the core projection values used throughout the illustration:

    - AV after withdrawal and penalties
    - interest credited for the month
    - end-of-period AV (EOP AV)

    Optionally, this step also supports applying an **end-of-period floor** based on
    guaranteed funds (e.g., `max(MFV, PFV)`), which is a common modeling simplification
    used to ensure AV does not fall below a guaranteed minimum track.

---

## What This Step Does

This step defines a deterministic account value update for a single month:

1. start with **AV at beginning of period** (BOP)
2. subtract **withdrawal amount**
3. subtract **penalty / adjustment** associated with withdrawal
4. credit monthly interest on the remaining balance
5. optionally apply an **EOP floor**

This step is intentionally a **pure roll-forward function**:
it does not decide how withdrawals or penalties were calculated.
Those are handled in earlier steps (Step 2–4).

---

## Business Requirements (BRD)

### 1. Timing and Ordering

AV roll-forward must follow the order below (this matters):

| Step | Operation | Reason |
|---|---|---|
| 1 | Start with \( AV_{BOP} \) | current available value |
| 2 | Subtract withdrawal | cash leaves the policy |
| 3 | Subtract penalty | charges reduce remaining balance |
| 4 | Credit interest | interest is earned on the remaining value |
| 5 | Apply floor (optional) | enforce guaranteed minimum (if used) |

---

### 2. Inputs (What the Function Needs)

| Input | Meaning |
|---|---|
| \( AV_{BOP} \) | beginning-of-month account value |
| withdrawal | cash withdrawn (gross, policyholder receipt basis) |
| penalty | combined adjustment for the transaction (surrender charge and/or MVA) |
| annual_rate | annual crediting rate applied for this month |
| floor_eop (optional) | end-of-period floor, e.g., max(MFV, PFV) |

!!! note
    This step does **not** compute the crediting rate selection — it receives `annual_rate`
    already determined by a rate-selection step (earlier or later depending on your build order).

---

### 3. Monthly Rate Conversion

Annual effective rate \( r \) must be converted to a monthly effective rate:

$$
r_m = (1 + r)^{1/12} - 1
$$

---

### 4. Core Roll-Forward Formula

The monthly roll-forward is:

$$
AV^{afterWD} = \max(0,\ AV_{BOP} - W - Pen)
$$

$$
Int = AV^{afterWD} \cdot r_m
$$

$$
AV_{EOP}^{raw} = AV^{afterWD} + Int
$$

If an end-of-period floor is provided:

$$
AV_{EOP} = \max(AV_{EOP}^{raw},\ Floor_{EOP})
$$

---

### 5. Penalty Interpretation (Important)

In the roll-forward function, `penalty` should be passed as the **total adjustment** that reduces AV.

In this project, it typically includes:

| Component | Typical Sign |
|---|---|
| surrender charge amount | reduces AV |
| MVA amount | can be positive or negative |

!!! warning "Implementation choice"
    In the simplest version, you can pass a single `penalty_total` from Step 3.
    However, be careful about sign conventions:
    - if MVA is **negative**, it increases the reduction
    - if MVA is **positive**, it offsets the reduction

    Your function should clearly document the expected sign convention and enforce it consistently.

---

## Inputs and Outputs

### Output Object

This step should return a small structured result:

| Field | Meaning |
|---|---|
| av_after_wd | AV after withdrawal and penalties |
| interest_credit | interest credited in the month |
| av_eop | AV at end of period |

---

## Starter Code (Expected Implementation)

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


def monthly_rate_from_annual(r_annual: float) -> float:
    return (1.0 + float(r_annual)) ** (1.0 / 12.0) - 1.0


@dataclass(frozen=True)
class AVResult:
    av_after_wd: float
    interest_credit: float
    av_eop: float


def roll_forward_account_value(
    av_bop: float,
    *,
    withdrawal: float,
    penalty: float,
    annual_rate: float,
    floor_eop: Optional[float] = None,
) -> AVResult:
    """
    AV roll-forward:

      av_after_wd = max(0, av_bop - withdrawal - penalty)
      interest    = av_after_wd * monthly_rate
      av_eop_raw  = av_after_wd + interest
      av_eop      = max(av_eop_raw, floor_eop) if floor_eop provided

    Notes:
    - penalty is intended to be the *total* penalty/adjustment from withdrawals.
    - floor_eop is applied after interest is credited (EOP floor).
    """
    av_bop_f = float(av_bop)
    wd = max(0.0, float(withdrawal))
    pen = max(0.0, float(penalty))

    av_after_wd = max(0.0, av_bop_f - wd - pen)

    r_m = monthly_rate_from_annual(float(annual_rate))
    interest = av_after_wd * r_m

    av_eop_raw = av_after_wd + interest

    if floor_eop is not None:
        floor_val = max(0.0, float(floor_eop))
        av_eop = max(av_eop_raw, floor_val)
    else:
        av_eop = av_eop_raw

    return AVResult(
        av_after_wd=av_after_wd,
        interest_credit=interest,
        av_eop=av_eop,
    )
```

---

## Deliverable for Step 5

By the end of this step, you should have:

- a tested monthly AV roll-forward function
- clear ordering consistent with product mechanics:
  - withdrawal / penalty first
  - interest credit second
  - optional floor last
- a structured `AVResult` output that can be stored to the final illustration table

This step will feed directly into the final assembly step that produces
the monthly output DataFrame and Cash Surrender Value fields.