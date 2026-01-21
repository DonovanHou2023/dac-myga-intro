# Homework 2 — Annuities, MYGA Features, and Python Illustration Framework

This assignment reinforces key ideas from **Class 2**:
- Deferred vs. immediate annuities (phases + risks)
- Product taxonomy (MYGA / FIA / RILA / VA)
- Interest crediting mechanics
- Triple compounding
- Guaranteed fund / MGSV concepts
- MYGA cash flow mechanics and cash surrender value logic

Unless otherwise stated:
- Time is measured in **policy months**
- Interest crediting is applied **monthly**
- Withdrawals (if any) occur at the **beginning of the policy year** (BOP of month 1, 13, 25, ...)

---

## Problem 1 — Deferred vs Immediate (Phases + Risks)

Answer in words (no calculations required).

1. In a **deferred annuity**, what happens during the **accumulation phase**?
2. In a **deferred annuity**, what happens during the **annuitization phase**?
3. Which phase primarily addresses **investment / interest-rate risk**?
4. Which phase primarily addresses **longevity risk**?
5. Why does an **immediate annuity** mainly target longevity risk?

---

## Problem 2 — Product Types (Conceptual Classification)

Fill out the table below.

| Product | What is credited? | Who bears market risk? | Is downside possible? |
|---|---|---|---|
| MYGA |  |  |  |
| FIA |  |  |  |
| RILA |  |  |  |
| VA |  |  |  |

Then answer:
1. Which products are most “bond-like” in behavior?
2. Which product is most similar to a mutual fund wrapper?

---

## Problem 3 — Triple Compounding (Conceptual + Numerical)

Explain “triple compounding” using:

- Compounding on **principal**
- Compounding on **credited interest**
- Compounding from **tax deferral**

Then compute:

Assume:
- Initial premium: \$10,000
- Annual credited rate: 5%
- Horizon: 3 years

1. Compute:
$$
AV_3 = 10{,}000 \times (1.05)^3
$$

2. In one paragraph: explain why tax deferral can increase long-run accumulation
even if the credited rate is the same as a taxable account.

---

## Problem 4 — Interest Crediting Examples (MYGA vs FIA vs RILA)

### Part A — MYGA

Assume:
- Premium: \$100,000
- MYGA credited rate: 4.2% annually
- One-year accumulation

Compute:
$$
AV_1 = 100{,}000 \times (1.042)
$$

### Part B — FIA (Cap)

Assume:
- Premium: \$100,000
- Index return: 7%
- Cap: 5%
- Floor: 0%

1. Compute the credited rate
2. Compute the end-of-year account value

### Part C — RILA (Buffer)

Assume:
- Premium: \$100,000
- Index return: –12%
- Buffer: 10%

1. Compute the credited return
2. Compute the end-of-year account value

---

## Problem 5 — Guaranteed Fund / MGSV (Floor Mechanics)

A MYGA includes a Minimum Guaranteed Surrender Value (MGSV) based on:

- 87.5% of single premium
- Accumulated at a minimum guaranteed rate
- Reduced by withdrawals

Assume:
- Single premium $P = 100{,}000$
- Minimum guaranteed rate $i_{min} = 1\%$ annually
- No withdrawals
- Duration: 5 years

Compute:
$$
MGSV_5 = 0.875 \times 100{,}000 \times (1.01)^5
$$

Then answer:
1. Why is MGSV important in statutory contexts?
2. How does MGSV relate to a “floor” on surrender values?

---

## Problem 6 — Monthly Mechanics (Order of Operations)

Define:

- $AV_t^{BOP}$ = account value at beginning of month $t$
- $W_t$ = withdrawal at beginning of month $t$ (**note**: for HW2, $W_t$ is non-zero only at the start of each policy year)
- $i_t$ = monthly credited interest rate
- $SC_t$ = surrender charge rate (by policy year)

Operations each month:

1. Start with $AV_t^{BOP}$
2. Withdraw at BOP:
$$
AV_t^{net} = AV_t^{BOP} - W_t
$$
3. Apply interest:
$$
AV_t^{EOP} = AV_t^{net} \times (1 + i_t)
$$
4. Cash surrender value at EOP:
$$
CSV_t = AV_t^{EOP} \times (1 - SC_t)
$$

Answer:

1. Why do we take withdrawals at BOP (modeling convention)?
2. If $AV_t^{BOP} = 50{,}000$, $W_t = 1{,}000$, and $i_t = 0.003$, compute $AV_t^{EOP}$.
3. If $SC_t = 0.06$, compute $CSV_t$.

---

## Problem 7 — Python Project: MYGA Illustration Engine (Core Build)

You will build a **beginner-friendly** MYGA illustration engine that produces a
**monthly projection** for 10 years (120 months).

### 7.1 What You’re Building

A function or class that:
- accepts MYGA inputs (rates, schedules, withdrawal %)
- projects month-by-month account values
- produces a clean table of outputs (DataFrame)

You should be able to:
- change inputs (duration, withdrawal %, etc.)
- rerun projection instantly
- inspect the output columns for auditability

---

## 7.2 Provided Product Specs (Known Inputs)

Use these as provided constants for this homework (still pass them as inputs in code).

### Minimum Guaranteed Rate (all products)

- $i_{min} = 1\%$ annual effective

### Surrender Charge Schedules (policy year → charge)

**5-year MYGA**
- 1: 0.10
- 2: 0.09
- 3: 0.08
- 4: 0.07
- 5: 0.06
- 6: 0.05
- 7: 0.00

**7-year MYGA**
- 1: 0.10
- 2: 0.09
- 3: 0.08
- 4: 0.07
- 5: 0.06
- 6: 0.05
- 7: 0.04
- 8: 0.00

**10-year MYGA**
- 1: 0.10
- 2: 0.09
- 3: 0.08
- 4: 0.07
- 5: 0.06
- 6: 0.05
- 7: 0.04
- 8: 0.03
- 9: 0.02
- 10: 0.01
- 11: 0.00

---

## 7.3 Withdrawal Provision (Policy-Year BOP Only)

Withdrawals in HW2 occur **only once per policy year**, at the **beginning of the policy year**:

- Withdrawal months are: 1, 13, 25, 37, ...
- In all other months, withdrawal is 0.

Free withdrawal limit each policy year:

$$
\text{FreeLimit}_y = 10\% \times AV_{\text{(start of policy year } y)}
$$

For HW2:
- withdrawal input is a **fixed annual percentage** between **0% and 10%**
- assume it will **not exceed** the free limit (so **no penalties** in HW2)

Withdrawal amount applied at the beginning of policy year $y$:

$$
W_{y,\text{BOP}} = AV_{\text{(start of policy year } y)} \times w_{annual}
$$

**Order of operations at the start of the policy year:**
1. Start with $AV^{BOP}$
2. Subtract withdrawal $W_{y,\text{BOP}}$
3. Then proceed with monthly interest crediting

---

## 7.4 Required Inputs (Your Code Must Accept)

At minimum:

- `premium` (float)
- `projection_months` (int), default 120
- `product_term_years` (int): 5, 7, or 10
- `initial_rate_annual` (float): rate during term
- `renewal_rates_annual` (dict): renewal rate by policy year (year > term)
- `min_guarantee_rate_annual` (float): set to 0.01
- `surrender_charge_schedule` (dict): given above
- `withdrawal_pct_annual` (float): between 0.00 and 0.10

---

## 7.5 Required Output Columns

Your projection must return a DataFrame with these columns:

- `month`
- `policy_year`
- `av_bop`
- `withdrawal_bop`
- `av_after_withdrawal`
- `interest_rate_monthly`
- `interest_credit`
- `av_eop`
- `surrender_charge_rate`
- `cash_surrender_value_eop`
- `free_withdrawal_limit_py` (10% × AV at start of policy year)
- `withdrawals_ytd_py` (for auditability)
- `guaranteed_fund_value_eop` (MGSV-style floor)

---

## 7.6 Projection Rules (Step-by-Step)

For each month:

1. Determine `policy_year`
2. Determine the annual crediting rate:
   - if `policy_year <= product_term_years`: use `initial_rate_annual`
   - else use `renewal_rates_annual[policy_year]` if available, otherwise keep last known rate
3. Convert annual rate to monthly effective:
$$
i_m = (1 + i_{annual})^{1/12} - 1
$$
4. Compute withdrawal at BOP:
   - If month $t$ is the first month of a policy year (1, 13, 25, ...):
$$
W_t = AV_t^{BOP} \times w_{annual}
$$
   - Otherwise:
$$
W_t = 0
$$
5. Apply interest to the net amount:
$$
AV_t^{EOP} = (AV_t^{BOP} - W_t)\times (1+i_m)
$$
6. Cash surrender value:
$$
CSV_t = AV_t^{EOP}\times(1-SC_y)
$$
7. Guaranteed fund value (simplified monthly floor):
   - Start at $0.875 \times \text{premium}$
   - Reduce by withdrawals
   - Accumulate at $i_{min}$ monthly effective
$$
GF_t^{EOP} = (GF_t^{BOP} - W_t)\times (1+i_{min,m})
$$

---

## 7.7 Suggested Starter Code Skeleton (Class Version)

``` Python
from dataclasses import dataclass
from typing import Dict, Optional
import pandas as pd

@dataclass
class MYGAInputs:
    premium: float
    product_term_years: int
    projection_months: int = 120

    initial_rate_annual: float = 0.04
    renewal_rates_annual: Optional[Dict[int, float]] = None

    min_guarantee_rate_annual: float = 0.01
    surrender_charge_schedule: Optional[Dict[int, float]] = None

    withdrawal_pct_annual: float = 0.00  # between 0.00 and 0.10


class MYGAPolicy:
    def __init__(self, inputs: MYGAInputs):
        self.inputs = inputs

    def _annual_to_monthly(self, i_annual: float) -> float:
        return (1 + i_annual) ** (1/12) - 1

    def _policy_year(self, month: int) -> int:
        return (month - 1) // 12 + 1

    def _crediting_rate_annual(self, policy_year: int) -> float:
        inp = self.inputs
        if policy_year <= inp.product_term_years:
            return inp.initial_rate_annual
        if inp.renewal_rates_annual and policy_year in inp.renewal_rates_annual:
            return inp.renewal_rates_annual[policy_year]
        return inp.initial_rate_annual

    def _surrender_charge_rate(self, policy_year: int) -> float:
        inp = self.inputs
        if inp.surrender_charge_schedule and policy_year in inp.surrender_charge_schedule:
            return inp.surrender_charge_schedule[policy_year]
        return 0.0

    def project(self) -> pd.DataFrame:
        inp = self.inputs

        i_min_m = self._annual_to_monthly(inp.min_guarantee_rate_annual)

        av = inp.premium
        gf = 0.875 * inp.premium  # guaranteed fund starts here

        rows = []
        withdrawals_ytd = 0.0
        free_limit = 0.0

        for m in range(1, inp.projection_months + 1):
            py = self._policy_year(m)

            # reset policy year trackers at month 1, 13, 25, ...
            if (m - 1) % 12 == 0:
                withdrawals_ytd = 0.0
                free_limit = 0.10 * av  # 10% of AV at start of policy year

            av_bop = av

            # withdrawal occurs only at the beginning of the policy year
            is_policy_year_start = ((m - 1) % 12 == 0)
            w = av_bop * inp.withdrawal_pct_annual if is_policy_year_start else 0.0
            withdrawals_ytd += w

            i_annual = self._crediting_rate_annual(py)
            i_m = self._annual_to_monthly(i_annual)

            av_after = av_bop - w
            interest_credit = av_after * i_m
            av_eop = av_after + interest_credit

            sc = self._surrender_charge_rate(py)
            csv_eop = av_eop * (1 - sc)

            # guaranteed fund floor (simplified)
            gf_after = gf - w
            gf_eop = gf_after * (1 + i_min_m)
            gf = gf_eop

            rows.append({
                "month": m,
                "policy_year": py,
                "av_bop": av_bop,
                "withdrawal_bop": w,
                "av_after_withdrawal": av_after,
                "interest_rate_monthly": i_m,
                "interest_credit": interest_credit,
                "av_eop": av_eop,
                "surrender_charge_rate": sc,
                "cash_surrender_value_eop": csv_eop,
                "free_withdrawal_limit_py": free_limit,
                "withdrawals_ytd_py": withdrawals_ytd,
                "guaranteed_fund_value_eop": gf_eop,
            })

            av = av_eop

        return pd.DataFrame(rows)
```

---

## 7.8 Sample Output (First 12 Months Example)

This section shows an **example projection output** so you understand what your
illustration engine should produce.

> **Important**
> - Your numbers may differ depending on assumptions
> - Column names and structure should closely resemble this
> - Order of operations must follow the rules in Section 7.6

### Example Assumptions (Illustration Only)

- Premium: 100,000
- Product term: 5-year MYGA
- Initial annual rate: 4.5%
- Minimum guarantee rate: 1.0%
- Annual withdrawal percentage: 6%  
  - Withdrawal occurs **once per policy year**, at policy year start (month 1, 13, ...)
  - In other months, withdrawal is 0
- Surrender charge (policy year 1): 10%

### Example Output — First 12 Months

| month | policy_year | av_bop | withdrawal_bop | interest_rate_monthly | interest_credit | av_eop | surrender_charge_rate | cash_surrender_value_eop | guaranteed_fund_value_eop |
|-----:|------------:|-------:|---------------:|----------------------:|----------------:|-------:|----------------------:|--------------------------:|---------------------------:|
| 1 | 1 | 100000.00 | 6000.00 | 0.003675 | 345.45 | 94345.45 | 0.10 | 84910.91 | 82062.69 |
| 2 | 1 | 94345.45 | 0.00 | 0.003675 | 346.40 | 94691.85 | 0.10 | 85222.67 | 82130.56 |
| 3 | 1 | 94691.85 | 0.00 | 0.003675 | 347.67 | 95039.52 | 0.10 | 85535.57 | 82198.49 |
| 4 | 1 | 95039.52 | 0.00 | 0.003675 | 348.95 | 95388.47 | 0.10 | 85849.62 | 82266.48 |
| 5 | 1 | 95388.47 | 0.00 | 0.003675 | 350.23 | 95738.70 | 0.10 | 86164.83 | 82334.53 |
| 6 | 1 | 95738.70 | 0.00 | 0.003675 | 351.52 | 96090.22 | 0.10 | 86481.20 | 82402.64 |
| 7 | 1 | 96090.22 | 0.00 | 0.003675 | 352.81 | 96443.03 | 0.10 | 86800.73 | 82470.81 |
| 8 | 1 | 96443.03 | 0.00 | 0.003675 | 354.11 | 96797.14 | 0.10 | 87117.43 | 82539.04 |
| 9 | 1 | 96797.14 | 0.00 | 0.003675 | 355.41 | 97152.55 | 0.10 | 87437.30 | 82607.33 |
| 10 | 1 | 97152.55 | 0.00 | 0.003675 | 356.71 | 97509.26 | 0.10 | 87758.33 | 82675.67 |
| 11 | 1 | 97509.26 | 0.00 | 0.003675 | 358.02 | 97867.28 | 0.10 | 88080.55 | 82744.08 |
| 12 | 1 | 97867.28 | 0.00 | 0.003675 | 359.34 | 98226.62 | 0.10 | 88403.96 | 82812.55 |

### Notes on the Table

- Withdrawal is applied at **policy year start only** (month 1, 13, 25, ...)
- In months without withdrawal, the projection step is just interest crediting
- Cash surrender value reflects the surrender charge for that policy year
- Guaranteed fund value:
  - starts at 87.5% of premium
  - reduced by withdrawal at policy year start
  - accumulates monthly at the minimum guaranteed rate

### Required Display in Submission

In your submission, you must include:

- The **first 24 months** of output for at least one scenario  
  (e.g., `df.head(24)`)

---

## Deliverables

Submit the following:

1. Your Python code (`.py` or Jupyter notebook)
2. Projection results for:
   - 5-year MYGA
   - 7-year MYGA
   - 10-year MYGA  
   (show at least the first 24 months for each)
3. A short written explanation (5–10 sentences) describing:
   - How you handled initial vs renewal rates
   - How withdrawals were applied (policy-year start only)
   - How the guaranteed fund floor was calculated
   - Any simplifying assumptions you made

---

This homework establishes the **core illustration engine** that will later be
extended to:
- multi-path projections
- policyholder behavior modeling
- CARVM and VM-22 reserve calculations