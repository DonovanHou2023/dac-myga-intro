## Step 6 — Cash Surrender Value (CSV) Calculation

!!! abstract "Purpose of This Step"
    The purpose of this step is to calculate the **Cash Surrender Value (CSV)** payable
    when the policyholder surrenders (fully or partially).

    CSV is the “payout number” most people care about — but it is **not** simply Account Value.
    It reflects:

    - free withdrawal allowance remaining (if applicable)
    - surrender charges (SC)
    - Market Value Adjustment (MVA)
    - statutory / product minimum floors (guarantee funds)

    This step produces CSV in a way that is transparent and audit-friendly, with
    intermediate fields returned for debugging and exhibits.

---

## What This Step Does

Given **end-of-period account value** \( AV_{EOP} \), this step:

1. determines the surrender amount \( A \) (default = full surrender)
2. applies remaining free withdrawal budget (portion exempt from SC/MVA)
3. computes surrender charges on the excess portion
4. computes MVA on the remaining excess portion (after SC)
5. calculates CSV before floors
6. applies floors (e.g., max(MFV, PFV), optional GMV)

This step is intentionally separate from AV roll-forward (Step 5):
- Step 5 updates values inside the contract
- Step 6 computes the payout upon surrender

---

## Business Requirements (BRD)

### 1. Key Inputs

| Input | Meaning |
|---|---|
| \( AV_{EOP} \) | Account value after monthly roll-forward |
| free_remaining_at_calc | free withdrawal budget remaining YTD (at time of CSV calc) |
| surrender_charge_pct | surrender charge % for policy year |
| mva_factor | MVA factor from Step 2 (dollar amount computed here) |
| guarantee floors | MFV/PFV (and optional GMV) at time of surrender |

---

### 2. Core Methodology (A–B–C Structure)

We use the A–B–C structure you defined:

- **A** = surrender amount
- **B** = free portion used (not subject to SC/MVA)
- **C** = surrender charge amount

Then:

- excess portion = \( A - B \)
- surrender charge = \( (A - B) \cdot s \)
- amount subject to MVA = \( (A - B) - C \)
- MVA amount = subject \(\times\) MVA factor

---

### 3. Full Surrender vs Partial Surrender

This step supports both, but defaults to full surrender:

| Case | Surrender Amount \(A\) |
|---|---|
| Full surrender | \( A = AV_{EOP} \) |
| Partial surrender | \( A = \text{surrender\_amount input} \) |

---

### 4. Mathematical Definition

Let:

- \( A \) = surrender amount (gross)
- \( F \) = free remaining at time of calculation
- \( s \) = surrender charge %
- \( D \) = MVA factor

**Free portion used:**

$$
B = \min(A,\ F)
$$

**Amount subject to surrender charge:**

$$
Excess = \max(A - B,\ 0)
$$

**Surrender charge:**

$$
SC = Excess \cdot s
$$

**Amount subject to MVA:**

$$
MVA_{base} = \max(Excess - SC,\ 0)
$$

**MVA amount:**

$$
MVA = MVA_{base} \cdot D
$$

**CSV before floors:**

$$
CSV_{raw} = \max(A - SC + MVA,\ 0)
$$

---

### 5. Floors (Guarantee Funds)

CSV must be floored by the guarantee fund minimums.

For this project:

- **NFF floor** is the maximum of the two guarantee fund tracks:

$$
NFF = \max(MFV_{EOP}, PFV_{EOP})
$$

Final CSV:

$$
CSV = \max(CSV_{raw},\ NFF,\ GMV\ \text{(optional)})
$$

---

### 6. Contract Variation Note (Important)

!!! warning "Free withdrawal treatment on full surrender can vary by product"
    Some products may not allow a “free portion” to reduce surrender charges on a full surrender.
    In that case, set:

    - `free_remaining_at_calc = 0.0` when the event is a full surrender.

    For this project, we assume the free remaining amount **does apply** unless you override it.

---

## Inputs and Outputs

### Outputs (Audit-Friendly)

This step should return not only CSV, but also key intermediate fields to make it easy to explain results.

| Output Field | Meaning |
|---|---|
| csv | final cash surrender value after floors |
| csv_before_floors | value after SC/MVA but before floors |
| nff_floor_used | max(MFV, PFV) used as guarantee floor |
| surrender_amount | amount surrendered (A) |
| free_portion_used | portion exempt from SC/MVA (B) |
| amount_subject_to_surrender_charge | excess portion |
| surrender_charge_amount_used | SC dollar amount |
| amount_subject_to_mva | post-SC base for MVA |
| mva_amount_used | MVA dollar amount |

---

## Starter Code (Expected Implementation)

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CSVResult:
    csv: float
    csv_before_floors: float
    nff_floor_used: float

    # Debug transparency
    av_eop: float
    surrender_amount: float
    free_remaining_at_calc: float
    free_portion_used: float

    amount_subject_to_surrender_charge: float
    surrender_charge_pct_used: float
    surrender_charge_amount_used: float

    amount_subject_to_mva: float
    mva_factor_used: float
    mva_amount_used: float


def _clamp_nonneg(x: float) -> float:
    return max(0.0, float(x))


def calculate_cash_surrender_value(
    av_eop: float,
    *,
    surrender_amount: Optional[float] = None,
    free_remaining_at_calc: float = 0.0,
    surrender_charge_pct: float = 0.0,
    surrender_charge_pct_override: Optional[float] = None,
    mva_factor: float = 0.0,
    gf_mfv_eop: Optional[float] = None,
    gf_pfv_eop: Optional[float] = None,
    gmv_floor: Optional[float] = None,
) -> CSVResult:

    av_eop_f = _clamp_nonneg(av_eop)
    A = av_eop_f if surrender_amount is None else _clamp_nonneg(surrender_amount)

    free_rem = _clamp_nonneg(free_remaining_at_calc)
    free_portion_used = min(A, free_rem)

    amount_subject_sc = _clamp_nonneg(A - free_portion_used)

    pct_used = float(surrender_charge_pct_override) if surrender_charge_pct_override is not None else float(surrender_charge_pct)
    pct_used = _clamp_nonneg(pct_used)

    sc_amt = amount_subject_sc * pct_used

    amount_subject_mva = _clamp_nonneg(amount_subject_sc - sc_amt)
    mva_amt = float(amount_subject_mva) * float(mva_factor)

    csv_before_floors = _clamp_nonneg(A - sc_amt + mva_amt)

    mfv = _clamp_nonneg(gf_mfv_eop) if gf_mfv_eop is not None else 0.0
    pfv = _clamp_nonneg(gf_pfv_eop) if gf_pfv_eop is not None else 0.0
    nff_floor = max(mfv, pfv)

    floors = [csv_before_floors, nff_floor]
    if gmv_floor is not None:
        floors.append(_clamp_nonneg(gmv_floor))

    final_csv = max(floors)

    return CSVResult(
        csv=float(final_csv),
        csv_before_floors=float(csv_before_floors),
        nff_floor_used=float(nff_floor),
        av_eop=float(av_eop_f),
        surrender_amount=float(A),
        free_remaining_at_calc=float(free_rem),
        free_portion_used=float(free_portion_used),
        amount_subject_to_surrender_charge=float(amount_subject_sc),
        surrender_charge_pct_used=float(pct_used),
        surrender_charge_amount_used=float(sc_amt),
        amount_subject_to_mva=float(amount_subject_mva),
        mva_factor_used=float(mva_factor),
        mva_amount_used=float(mva_amt),
    )
```

---

## Deliverable for Step 6

By the end of this step, you should have:

- a CSV function that correctly applies:
  - free remaining amount (if applicable)
  - surrender charge on excess
  - MVA on post-SC base
  - guarantee fund floors
- a structured `CSVResult` that exposes intermediate values for transparency

This is the final “payout layer” needed before assembling the full monthly illustration table.