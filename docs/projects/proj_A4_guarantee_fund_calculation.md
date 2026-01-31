## Step 4 — Guaranteed Funds (MFV / PFV) Projection

!!! abstract "Purpose of This Step"
    The purpose of this step is to project the **Guaranteed Fund tracks** that establish
    statutory / contractual minimum surrender values.

    In MYGA products, the account value (AV) is not the only value that matters.
    Many contracts include a **nonforfeiture floor** that guarantees a minimum value
    even if credited rates change over time.

    This step builds the guarantee fund mechanics so later steps can compute:

    - Minimum Fund Value (**MFV**) and Prospective Fund Value (**PFV**)
    - A guaranteed floor for surrender value (used in Cash Surrender Value logic)

---

## What This Step Does

This step introduces a deterministic guarantee-fund engine that:

1. initializes MFV and PFV at issue (as a % of premium)
2. reduces MFV/PFV when a withdrawal happens (dollar-for-dollar)
3. credits MFV/PFV monthly using product-defined annual rates (converted to monthly)

This step focuses only on the guarantee-fund balances — it does **not** decide cash surrender value yet.

---

## Business Requirements (BRD)

### 1. Why Guaranteed Funds Exist

Guaranteed funds represent a **minimum value floor** that protects the policyholder.

| Concept | Meaning | Why it matters |
|---|---|---|
| AV | current account value | driven by credited rate + withdrawals |
| MFV / PFV | guaranteed floor tracks | protects against low credited outcomes |
| CSV | cash surrender value | later computed as max(guarantee floor, net AV) |

The illustration engine must compute MFV/PFV so that CSV can be computed correctly.

---

### 2. Two Guarantee Tracks: MFV and PFV

This project includes two guarantee tracks that behave similarly but use different parameters.

| Track | Initialization | Crediting Rule | Typical Purpose |
|---|---|---|---|
| MFV | \( \alpha_{mfv} \cdot Premium \) | credits at initial rate during term, then minimum rate | minimum floor tied to term dynamics |
| PFV | \( \alpha_{pfv} \cdot Premium \) | credits at PFV rate for N years, then another rate | prospective-style nonforfeiture floor |

(Exact naming varies by company; the goal here is to practice the mechanics.)

---

### 3. Required Inputs

All guarantee fund parameters must come from **product specs** (Step 1B) and not be hardcoded.

| Input | Source | Notes |
|---|---|---|
| MFV base % | product YAML | `mfv.base_pct_of_premium` |
| PFV base % | product YAML | `pfv.base_pct_of_premium` |
| PFV rate | product YAML | `pfv.rate_annual`, `rate_years`, `rate_after_years_annual` |
| Minimum guaranteed rate | product YAML | `minimum_guaranteed_rate` |
| Initial crediting rate | illustration inputs | used for MFV during term |
| Term years | product YAML | determines MFV rate switch |

---

### 4. Initialization at Issue

Guarantee funds are initialized as a % of premium:

$$
\begin{aligned}
MFV_0 &= \alpha_{mfv}\cdot P \\
PFV_0 &= \alpha_{pfv}\cdot P
\end{aligned}
$$

Where:
- \( P \) is the single premium
- \( \alpha_{mfv}, \alpha_{pfv} \) are product parameters

---

### 5. Withdrawal Impact on Guarantee Funds

Withdrawals reduce guarantee funds **dollar-for-dollar**, floored at 0.

!!! warning "Important"
    The surrendered amount applied to MFV/PFV should be the **gross withdrawal amount**
    (policyholder takes this cash out). It should **not** include surrender charges or MVA.

$$
GF_{t}^{afterWD} = \max(GF_{t}^{beforeWD} - W_t,\ 0)
$$

This rule applies to both MFV and PFV.

---

### 6. Monthly Crediting

Guarantee funds are credited monthly, based on annual rates converted to monthly:

Annual-to-monthly conversion:

$$
r_m = (1+r_{annual})^{1/12} - 1
$$

Monthly update:

$$
GF_{t,m}^{EOP} = GF_{t,m}^{BOP}\cdot (1+r_m)
$$

---

### 7. MFV Annual Rate Rule

MFV credits at:

- initial rate during the guarantee term
- minimum guaranteed rate after the term

$$
r^{MFV}_{annual}(t)=
\begin{cases}
r_{initial}, & t \le term \\
r_{min}, & t > term
\end{cases}
$$

---

### 8. PFV Annual Rate Rule

PFV credits at:

- PFV rate for first `rate_years`
- then `rate_after_years_annual` afterwards

$$
r^{PFV}_{annual}(t)=
\begin{cases}
r_{pfv}, & t \le Y \\
r_{after}, & t > Y
\end{cases}
$$

---

## Inputs and Outputs

### Inputs

| Input | Type | Meaning |
|---|---|---|
| premium | float | single premium |
| policy_year | int | used for annual rate selection |
| term_years | int | MFV rate switch |
| initial_rate | float | MFV in-term crediting |
| min_guaranteed_rate | float | MFV after-term crediting |
| mfv_params | MFVSpec | base % |
| pfv_params | PFVSpec | base %, PFV rate rules |
| surrender_amount | float | gross withdrawal amount |

### Outputs

| Output | Type | Meaning |
|---|---|---|
| GuaranteeFundState.mfv | float | updated MFV balance |
| GuaranteeFundState.pfv | float | updated PFV balance |

---

## Starter Code (Expected Implementation)

Students are expected to implement this guarantee-fund module with:

- parameter dataclasses
- state dataclass
- initialization function
- withdrawal application
- monthly crediting

```python
from __future__ import annotations

from dataclasses import dataclass


def monthly_rate_from_annual(r_annual: float) -> float:
    return (1.0 + float(r_annual)) ** (1.0 / 12.0) - 1.0


@dataclass(frozen=True)
class MinimumFundValueParams:
    base_pct_of_premium: float


@dataclass(frozen=True)
class ProspectiveFundValueParams:
    base_pct_of_premium: float
    rate_annual: float
    rate_years: int
    rate_after_years_annual: float


@dataclass(frozen=True)
class GuaranteeFundState:
    mfv: float
    pfv: float


def initialize_guarantee_funds(
    premium: float,
    mfv_params: MinimumFundValueParams,
    pfv_params: ProspectiveFundValueParams,
) -> GuaranteeFundState:
    p = float(premium)
    mfv0 = float(mfv_params.base_pct_of_premium) * p
    pfv0 = float(pfv_params.base_pct_of_premium) * p
    return GuaranteeFundState(mfv=mfv0, pfv=pfv0)


def apply_surrender_to_guarantee_funds(
    state: GuaranteeFundState,
    surrender_amount: float,
) -> GuaranteeFundState:
    wd = max(0.0, float(surrender_amount))
    return GuaranteeFundState(
        mfv=max(0.0, float(state.mfv) - wd),
        pfv=max(0.0, float(state.pfv) - wd),
    )


def credit_guarantee_funds_monthly(
    state: GuaranteeFundState,
    policy_year: int,
    *,
    term_years: int,
    initial_rate: float,
    min_guaranteed_rate: float,
    pfv_params: ProspectiveFundValueParams,
) -> GuaranteeFundState:
    # MFV annual rate rule
    mfv_r_annual = float(initial_rate) if policy_year <= term_years else float(min_guaranteed_rate)
    mfv_r_m = monthly_rate_from_annual(mfv_r_annual)

    # PFV annual rate rule
    pfv_r_annual = float(pfv_params.rate_annual) if policy_year <= pfv_params.rate_years else float(pfv_params.rate_after_years_annual)
    pfv_r_m = monthly_rate_from_annual(pfv_r_annual)

    return GuaranteeFundState(
        mfv=float(state.mfv) * (1.0 + mfv_r_m),
        pfv=float(state.pfv) * (1.0 + pfv_r_m),
    )
```

---

## Deliverable for Step 4

By the end of this step, you should have:

- a guarantee fund module that supports MFV and PFV
- a state object containing both balances
- correct handling of:
  - initialization at issue
  - reduction by gross withdrawals
  - monthly crediting using policy-year-dependent rates

This step will be consumed by the next step where we compute:

- net account value after withdrawal
- cash surrender value \( CSV = \max(\text{guarantee floor},\ \text{net AV}) \)