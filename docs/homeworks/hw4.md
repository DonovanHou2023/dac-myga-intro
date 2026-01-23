# Homework 4 — CARVM Basics: Paths, Backward Induction, and Annuity Options (Python)

This assignment is tied to **Class 4 (CARVM Reserve Fundamentals)**.

The objectives are to:

- understand the **CARVM calculation order** (time-first, benefit max, backward discounting)
- understand **path-dependent reserving** (no PW vs full free PW)
- implement Python tools to value **annuitization options**
- extend your MYGA illustration engine to produce **CARVM-style reserves by path**

!!! note "Structure"
    Homework 4 contains:
    1) Concept questions (Problems 1–5)  
    2) Python Exercise A: annuitization option valuation (PV at different times \(t\))  
    3) Python Exercise B: CARVM-style reserve by path using your MYGA illustration (extend HW2 Problem 7)

---

## Problem 1 — What CARVM Is (Conceptual)

Answer in words.

1. What is CARVM designed to measure in statutory reserving?
2. Why is CARVM considered a **worst-case** framework rather than an expected value framework?
3. What is the regulatory reference for CARVM (name the guideline)?

---

## Problem 2 — CARVM Calculation Order (Conceptual)

Answer in words and/or short formulas.

CARVM does **not** work by taking maximum values across years first.

1. Describe the correct CARVM order of operations, using the terms:
   - time point
   - allowable benefits
   - maximum benefit
   - backward discounting / recursion

2. In one sentence: where does the “max” operator occur, and why?

---

## Problem 3 — Benefit Set for MYGA (Conceptual)

Consider a simplified MYGA product.

1. List at least **five** benefit types that may be considered in CARVM (examples: surrender, death, maturity, etc.).
2. Explain why annuitization options are treated differently from lump-sum benefits in valuation.

---

## Problem 4 — Path Dependence (Conceptual)

Answer in words.

1. Why does partial withdrawal behavior require evaluating **multiple paths**?
2. For a MYGA product without GLWB, why are two paths often sufficient as representative extremes?
3. Define the two paths used in this course:
   - No Partial Withdrawal
   - Full Free Partial Withdrawal

---

## Problem 5 — Column Reserve (Conceptual)

Answer in words.

1. Define **Column Reserve** in the context of CARVM path testing.
2. If Path 1 produces reserve 12,000 and Path 2 produces reserve 14,500, what is the column reserve and why?
3. Explain how the reserve relates to the idea of “worst-case for the insurer”.

---

# Python Exercise A — Annuitization Option Value at Time \(t\)

In CARVM, annuitization options may be compared against other benefits at a given policy year \(t\).
In this exercise, you will build a small Python tool to compute the **present value of annuity payments**
at different valuation times \(t\), using provided mortality and discount assumptions.

---

## A.1 Definitions

Let:

- \( t \) = policy year (valuation time)
- \( v = \frac{1}{1+i} \) where \(i\) is the annual effective discount rate
- \( {}_k p_{x+t} \) = probability that a life age \(x+t\) survives \(k\) more years
- Payments occur at the **end of each year**

You will value two annuitization options:

1. **15-year certain** annuity-immediate
2. **single life** annuity-immediate (life only)

---

## A.2 Inputs Provided (Example Assumptions)

Use these default inputs for your testing. Your code should accept them as inputs.

### Mortality (Annual \(q\) rates)

We provide a simplified mortality table for attained ages 60–90.
Interpretation: \( q_{age} \) is the probability of death during the year.

| Age | \(q_{age}\) |
|---:|---:|
| 60 | 0.0100 |
| 61 | 0.0106 |
| 62 | 0.0113 |
| 63 | 0.0121 |
| 64 | 0.0130 |
| 65 | 0.0140 |
| 66 | 0.0152 |
| 67 | 0.0165 |
| 68 | 0.0180 |
| 69 | 0.0196 |
| 70 | 0.0214 |
| 71 | 0.0234 |
| 72 | 0.0256 |
| 73 | 0.0280 |
| 74 | 0.0306 |
| 75 | 0.0334 |
| 76 | 0.0365 |
| 77 | 0.0398 |
| 78 | 0.0435 |
| 79 | 0.0475 |
| 80 | 0.0520 |
| 81 | 0.0569 |
| 82 | 0.0624 |
| 83 | 0.0684 |
| 84 | 0.0751 |
| 85 | 0.0824 |
| 86 | 0.0906 |
| 87 | 0.0995 |
| 88 | 0.1095 |
| 89 | 0.1205 |
| 90 | 0.1325 |

### Discount Rate

- Annual effective discount rate: \( i = 4.00\% \)

### Annuity Rates / Payment Levels (Example)

To keep the exercise straightforward, assume the contract specifies a level annual payment:

- 15-year certain payment: \$8,500 per year
- Single life payment: \$7,000 per year

!!! note "Why different payments?"
    Real products determine payout rates from pricing assumptions.  
    Here, we provide payment levels so you can focus on valuation mechanics.

---

## A.3 Required Functions

### Function 1 — Convert \(q\) table to survival probabilities

Write a function that builds survival probabilities from a given starting age.

- Input: mortality table \(q\), starting age, horizon \(n\)
- Output: list of survival probabilities \([{}_1 p, {}_2 p, \dots, {}_n p]\)

```
from typing import Dict, List

def build_survival_probs(
    q_table: Dict[int, float],
    start_age: int,
    n_years: int
) -> List[float]:
    """
    Returns survival probabilities for k = 1..n_years.

    survival[k-1] = {}_k p_{start_age}

    Hint:
    - p_age = 1 - q_age
    - {}_k p = product of p over each year
    """
    ...
```

---

### Function 2 — PV of 15-year certain annuity at time \(t\)

```
def pv_annuity_certain(
    payment: float,
    discount_rate: float,
    term_years: int
) -> float:
    """
    PV at valuation time t for an annuity-immediate paying 'payment' for 'term_years' years.
    Payments are at end of each year.
    """
    ...
```

Formula reference:

$$
PV_{\text{certain}}(t) = \sum_{k=1}^{n} payment \cdot v^k
$$

---

### Function 3 — PV of single life annuity at time \(t\)

```
def pv_annuity_single_life(
    payment: float,
    discount_rate: float,
    survival_probs: List[float]
) -> float:
    """
    PV at valuation time t for a life-only annuity-immediate.
    survival_probs[k-1] should represent {}_k p_{x+t}.
    """
    ...
```

Formula reference:

$$
PV_{\text{life}}(t) = \sum_{k=1}^{n} payment \cdot v^k \cdot {}_k p_{x+t}
$$

---

## A.4 Required Tasks

Assume:

- Issue age \(x = 60\)
- Compute option values at policy years:
  - \(t = 0\)
  - \(t = 5\)
  - \(t = 10\)

For each \(t\):

1. Determine attained age \(x+t\)
2. Build survival probabilities from age \(x+t\) for a chosen horizon \(n\)
   - for this homework, use \(n = 30\) years (or until your table ends)
3. Compute:
   - PV of 15-year certain option
   - PV of single life option
4. Output a table like:

| \(t\) | Attained Age | PV (15Y Certain) | PV (Single Life) |
|---:|---:|---:|---:|
| 0 | 60 |  |  |
| 5 | 65 |  |  |
| 10 | 70 |  |  |

---

# Python Exercise B — CARVM-Style Reserve by Path (Extend HW2 Problem 7)

In this exercise, you will extend your **Homework 2 Problem 7** MYGA illustration engine
to support **two paths** and produce a **path-level reserve** using backward discounting.

!!! note "Key idea"
    CARVM involves:
    - computing values over time under a given path
    - discounting from a far duration back to time 0 (backward induction / recursion)
    - taking the maximum reserve across paths to produce a column reserve

---

## B.1 Two Paths to Project

For each policy, project two paths:

| Path | Definition |
|---|---|
| Path 1 | **No Partial Withdrawal** (withdrawal rate = 0%) |
| Path 2 | **Full Free Partial Withdrawal** (withdrawal rate = 10% annually, starting policy year 2) |

Withdrawal convention:

- withdrawal occurs at **beginning of policy year**
- withdrawal amount is a % of account value at BOP of that policy year
- free withdrawal provision:
  - max 10% each year
  - not available in policy year 1

---

## B.2 Projection Horizon and Timing

- Projection horizon: **30 policy years**
- Projection frequency: **annual** (policy year steps are sufficient for this homework)

Your projection should output, for each path and each year:

| Column | Description |
|---|---|
| Policy Year \(t\) | 1..30 |
| AV\_BOP | Account value at beginning of year |
| Withdrawal | Withdrawal taken at beginning of year (0% or 10% rule) |
| Interest Credit | Interest credited during year |
| AV\_EOP | Account value at end of year |
| (Optional) Surrender Value | AV adjusted for surrender charges/MVA if you already have it |

---

## B.3 Reserve Calculation (Per Path)

For this homework, define **path reserve** as the discounted value of future worst-case benefits under that path.

To keep this exercise tractable, use this simplified benefit for reserve:

- Benefit at year \(t\): **account value at end of year** \(AV\_EOP(t)\)

Then the reserve at time 0 for a given path is:

$$
R^{(path)}_0 = \sum_{t=1}^{30} \frac{AV\_EOP(t)}{(1+i_v)^t}
$$

Where:

- valuation discount rate \( i_v \) is an input
- use \( i_v = 4.00\% \) for your default run

!!! warning "Simplification"
    True CARVM compares multiple benefits at each time point and uses backward recursion with max operators.
    For Homework 4, we focus on:
    - path projection mechanics
    - discounting mechanics
    - structure needed for future CARVM enhancement

---

## B.4 Required Functions (Suggested Structure)

### Function 1 — Project a single path

```
from typing import Dict, List, Any

def project_myga_path(
    initial_premium: float,
    crediting_rate_schedule: List[float],
    withdrawal_rate: float,
    projection_years: int = 30,
) -> List[Dict[str, Any]]:
    """
    Projects annual policy values for one path.

    Inputs:
    - initial_premium: starting AV at issue
    - crediting_rate_schedule: list of annual crediting rates by policy year (length >= projection_years)
    - withdrawal_rate: 0.0 for no PW path, 0.10 for full free PW path
    - projection_years: default 30

    Output:
    - list of rows (dicts) with year-by-year values
    """
    ...
```

### Function 2 — Discount projected benefits to get reserve

```
def calculate_path_reserve(
    projected_rows: List[Dict[str, Any]],
    valuation_discount_rate: float
) -> float:
    """
    Computes reserve at time 0 by discounting AV_EOP values.

    Output:
    - reserve value at time 0
    """
    ...
```

### Function 3 — Column reserve (max across paths)

```
def calculate_column_reserve(
    reserve_path_1: float,
    reserve_path_2: float
) -> float:
    """
    Returns max of the two path reserves.
    """
    ...
```

---

## B.5 Required Output

Your final output should allow the instructor to access:

1. projected year-by-year rows for Path 1 and Path 2
2. reserve for each path
3. column reserve (max across paths)

Provide:

- a printed summary:

| Metric | Value |
|---|---:|
| Path 1 Reserve |  |
| Path 2 Reserve |  |
| Column Reserve |  |

- and show the first 10 rows of each projected path table

---

## Deliverables

Submit:

1. Answers to Problems 1–5 (written)
2. Python Exercise A code and the PV output table for \(t = 0, 5, 10\)
3. Python Exercise B code including:
   - two path projections (30 years)
   - each path reserve at time 0
   - column reserve
4. A short write-up (8–12 sentences):
   - explain the CARVM order of operations
   - explain why we test paths (no PW vs full free PW)
   - explain how annuitization PV fits into benefit valuation at time \(t\)

!!! success "What this homework accomplishes"
    - You can value annuitization options at different policy years \(t\)
    - You can generate two MYGA projection paths
    - You can compute path reserves and a column reserve structure
    - You have the scaffolding needed for a full CARVM max-benefit recursion in later classes