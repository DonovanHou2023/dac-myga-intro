# Homework 3 — Bond Pricing, ALM, MVA, and Annuitization (Python + Concepts)

This assignment builds on **Class 3** and continues your development from **Homework 2**.

The objectives are to:

- reinforce bond cash flows, pricing, and interest rate sensitivity
- connect asset values to MYGA liabilities through ALM and spread
- formalize the economic logic behind **Market Value Adjustment (MVA)**
- introduce Python utilities for:
  - bond pricing under yield shocks
  - MVA factor calculation
  - annuitization present value under mortality + discounting

!!! note "Important structure for Homework 3"
    Homework 3 contains:
    1) Conceptual and numerical questions (Problems 1–8)  
    2) **Three separate Python exercises** (Python Exercise A–C)  
    3) A continuation task: **keep improving HW2 Problem 7** based on instructor feedback

---

## Problem 1 — Bond Cash Flows (Conceptual)

Answer in words.

1. For a standard fixed-rate coupon bond:
   - what cash flow occurs at time 0?
   - what cash flows occur during the life of the bond?
   - what cash flow occurs at maturity?

2. Why are coupon bonds considered predictable cash flow instruments?

3. Why are fixed-income assets a natural match for MYGA liabilities?

---

## Problem 2 — Bond Pricing and Market Value (Conceptual)

Answer in words and formulas.

1. Define the **market value** of a bond.
2. How does market value depend on:
   - the coupon rate?
   - the current market yield?
3. What does it mean for a bond to trade:
   - at par?
   - at a premium?
   - at a discount?

---

## Problem 3 — Interest Rates and Bond Prices (Conceptual)

Answer conceptually.

1. What happens to bond prices when interest rates increase?
2. What happens to bond prices when interest rates decrease?
3. Why is this relationship critical for understanding MYGA surrender risk?

---

## Problem 4 — Duration (Conceptual)

Answer in words.

1. What does **duration** measure?
2. How should duration be interpreted economically?
3. If a bond has duration of 6, what is the approximate impact of a 1% increase
   in interest rates on the bond’s price?

---

## Problem 5 — ALM and Spread (Numerical + Conceptual)

Consider a MYGA product with:

- Asset earned rate (AER): 5.75%
- Policy credited rate: 4.25%

1. Compute the **spread**.
2. List at least three uses of spread within an insurance company.
3. Why do renewal rates often decrease after the initial guarantee period?

---

## Problem 6 — Why MVA Exists (Conceptual)

Answer in words.

1. Describe what happens economically if:
   - interest rates rise
   - a policyholder surrenders early
2. Why does selling assets early potentially create a loss?
3. How does MVA protect insurers from disintermediation risk?

---

## Problem 7 — Annuitization Basics (Conceptual)

Answer in words.

1. What does it mean to **annuitize** an account value?
2. Give three common annuitization options and briefly describe each:
   - life only
   - life with period certain
   - period certain
3. Why does annuitization shift the insurer’s risk profile?

---

## Problem 8 — Quick Income Illustration (Simple Numerical)

Assume a policyholder annuitizes:

- Account value: \$120,000
- Payout horizon: 20 years (240 months)

Compute the approximate monthly payment under a simplified “level payment for 240 months” assumption:

$$
\text{Payment} \approx \frac{120{,}000}{240}
$$

Then answer:
1. Why is this not a complete actuarial annuity calculation?
2. What additional inputs are needed for a real actuarial annuitization quote?

---

## Python Exercise A — Bond Pricing Engine (Market Value Under Yield Shocks)

You will implement a reusable function to compute the **market value of a bond**
under different interest rate scenarios.

### A.1 Required Function

```
def price_bond(
    face_value: float,
    coupon_rate_annual: float,
    maturity_years: int,
    yield_rate_annual: float,
    coupon_frequency: int = 2
) -> float:
    """
    Returns the market value of a fixed-rate coupon bond.

    Assumptions:
    - level coupons
    - coupon_frequency payments per year (default: semiannual)
    - discount rate equals the provided yield_rate_annual
    """
    ...
```

### A.2 Pricing Rules

- Number of coupon periods:
$$
N = \text{Maturity}\_\text{years} \times m
$$
where $m$ is coupon_frequency.

- Coupon per period:
$$
C = \frac{FV \times c}{m}
$$
where:
- $FV$ = face value
- $c$ = annual coupon rate
- $m$ = payments per year

- Yield per period:
$$
y = \frac{y_{annual}}{m}
$$

- Market value:
$$
MV = \sum_{t=1}^{N} \frac{C}{(1+y)^t} + \frac{FV}{(1+y)^N}
$$

!!! tip "Implementation hint"
    Use a for-loop over periods 1..N.  
    Discount each cash flow and sum.

### A.3 Required Test Scenario

Use the following bond:

- Face value: 100
- Coupon rate: 4%
- Maturity: 5 years
- Coupon frequency: semiannual

Compute the market value under:

| Market Yield (annual) | Expected Relationship |
|---:|---|
| 4% | ≈ 100 (par) |
| 5% | < 100 (discount) |
| 3% | > 100 (premium) |

Answer (short):
1. Why do these results make sense economically?

### A.4 Yield Shock Analysis (Required)

Using the same bond:

1. Compute $MV$ at yield = 4%
2. Recompute:
   - yield increases to 6%
   - yield decreases to 2%

Provide a small table:

| Yield | Market Value |
|---:|---:|
| 4% |  |
| 6% |  |
| 2% |  |

Then answer:
- Which direction creates a loss?
- How does this connect to early surrender risk in MYGA?

---

## Python Exercise B — MVA Factor Calculator (Treasury-Based)

You will implement a simplified MVA calculator based on treasury rates.

### B.1 MVA Rate Definitions (For This Homework)

- **Initial MVA rate**:
  - 5-year Treasury rate at issue: $r_0$
- **Current MVA rate**:
  - current 5-year Treasury rate minus 25 bps: $r_t = r_{5y,current} - 0.25\%$

!!! note "Interpretation"
    The -25 bps adjustment is a simplified proxy for product design (e.g., spread offsets).
    Real products may use more complex reference yields and offsets.

### B.2 MVA Factor Methodology (Simplified)

Let:
- $r_0$ = initial MVA rate
- $r_t$ = current MVA rate
- $D$ = remaining duration (years)

Define the MVA factor:

$$
\text{MVA Factor} = \left( \frac{1 + r_0}{1 + r_t} \right)^D
$$

- If factor < 1 → negative MVA (reduces payout)
- If factor > 1 → positive MVA (increases payout)

### B.3 Required Function

```
def calculate_mva_factor(
    initial_mva_rate: float,
    current_mva_rate: float,
    remaining_years: float
) -> float:
    """
    Returns the MVA factor multiplier.
    """
    ...
```

### B.4 Required Scenario (Compute MVA Factor)

Assume:
- Initial 5-year Treasury at issue: 3.50%
- Current 5-year Treasury: 5.00%
- Current MVA rate: 5.00% – 0.25% = 4.75%
- Remaining duration: 3 years

Tasks:
1. Compute MVA factor
2. Is MVA positive or negative?
3. Explain the result in 2–3 sentences

---

## Python Exercise C — Annuitization Present Value (Mortality + Discounting)

In this exercise, you will calculate the **present value of life-contingent annuity payments**
using:
- a mortality input (survival probabilities)
- a discount rate input

This is a foundational building block for annuitization pricing.

---

### C.1 Required Inputs and Definitions

Assume:
- payments occur at the **end of each year**
- payment amount is level: $A$ per year
- annuity pays while the annuitant is alive (life-only style)

Define:
- ${}_t p_x$ = probability a life age $x$ survives $t$ years
- $v = \frac{1}{1+i}$ where $i$ is annual effective discount rate

Then the present value is:

$$
PV = \sum_{t=1}^{n} A \cdot v^t \cdot {}_t p_x
$$

Where $n$ is the maximum projection horizon (e.g., 10 years for this homework).

---

### C.2 Required Function

```
from typing import List

def pv_life_annuity_immediate(
    payment: float,
    discount_rate_annual: float,
    survival_probs: List[float]
) -> float:
    """
    Computes PV of a life-contingent annuity-immediate using provided survival probabilities.

    Inputs:
    - payment: level payment amount A
    - discount_rate_annual: annual effective discount rate i
    - survival_probs: list where survival_probs[t-1] = {}_t p_x for t = 1..n

    Returns:
    - present value PV
    """
    ...
```

!!! tip "Implementation hint"
    - Compute v = 1/(1+i)
    - Loop t = 1..n
    - Add payment * (v**t) * survival_prob[t-1]

---

### C.3 Example Data (Provided)

Use:

- Payment: \$10,000 per year
- Discount rate: 4% annual effective
- Survival probabilities (for t = 1..10):

| t | ${}_t p_x$ |
|---:|---:|
| 1 | 0.990 |
| 2 | 0.979 |
| 3 | 0.967 |
| 4 | 0.954 |
| 5 | 0.940 |
| 6 | 0.925 |
| 7 | 0.909 |
| 8 | 0.892 |
| 9 | 0.874 |
| 10 | 0.855 |

Tasks:
1. Compute PV using your function
2. Provide the numeric result (rounded to nearest dollar)
3. In 2–3 sentences: explain how mortality changes PV relative to a certain annuity

---

## Continuation Task — Homework 2 Problem 7 (MYGA Illustration Engine)

You must continue improving your **Homework 2 Problem 7** MYGA illustration engine.

!!! note "What to do"
    You will receive instructor feedback during/after Class 3.  
    Your job is to incorporate that feedback and resubmit an improved version.

Minimum expectations for the updated submission:
- cleaner structure (functions/classes organized clearly)
- consistent column outputs
- correct policy-year withdrawal logic (withdrawal at policy-year start only)
- readable code + comments sufficient for a beginner to follow

---

## Deliverables

Submit:

1. Updated HW2 Problem 7 MYGA illustration engine (post-feedback version)
2. Python Exercise A:
   - bond pricing function
   - yield shock table results
3. Python Exercise B:
   - MVA factor function
   - required scenario result + interpretation
4. Python Exercise C:
   - PV annuitization function
   - PV result + interpretation
5. Short write-up (10–15 sentences):
   - bond pricing intuition
   - why MVA exists
   - how PV under mortality differs from fixed-term annuity PV

!!! success "What this homework accomplishes"
    This homework completes the conceptual bridge from:
    **bond pricing → ALM spread → MVA → annuitization PV**.

It prepares you for **Class 4**, where we shift fully into **CARVM and statutory reserving**.