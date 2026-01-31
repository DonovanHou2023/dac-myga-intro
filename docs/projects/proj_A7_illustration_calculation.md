## Step 7 — Illustration Orchestration (Monthly Projection Runner)

!!! abstract "Purpose of This Step"
    The purpose of this step is to build the **top-level illustration runner** that
    orchestrates all engines you implemented in prior steps into a single monthly projection.

    This is the “glue layer” that:
    
    - loads product specs from the catalog
    - loops over policy months
    - calls each engine in the correct order
    - records outputs into a unified results table (DataFrame)

    The orchestration step is where the illustration becomes a complete system.

---

## What This Step Does

This step produces a **monthly projection DataFrame** that can be directly consumed by:

- Streamlit UI
- testing / validation
- export to CSV for exhibits

It connects the engines you built earlier:

| Engine | Module | What it provides |
|---|---|---|
| Product Specs | `catalog.py` | term, surrender charges, guarantee fund parameters |
| MVA Factor | `mva.py` | MVA factor \(D_t\) for month \(t\) |
| Withdrawal Engine | `withdrawals.py` | withdrawal amount + SC + MVA dollar amounts (excess-only) |
| Guarantee Funds | `guarantee_funds.py` | MFV/PFV roll-forward |
| Account Value Roll-Forward | `av.py` | monthly AV after WD/penalty + interest credit |
| Cash Surrender Value | `csv.py` | CSV payout and diagnostics |

---

## Business Requirements (BRD)

### 1. Projection Granularity

- Projection is **monthly**
- Policy year = \( \lfloor (pm-1)/12 \rfloor + 1 \)
- Month-in-year = \( ((pm-1) \bmod 12) + 1 \)

Where `pm` = policy month index starting at 1.

---

### 2. Crediting Rate Schedule

The orchestration layer must build the **annual crediting rate by policy year**:

- years 1..term_years: `initial_rate`
- years > term_years: `max(renewal_rate, minimum_guaranteed_rate)`

This ensures renewal rates never go below the minimum guaranteed.

$$
r_t =
\begin{cases}
r_{init}, & t \le Term \\
\max(r_{ren}, r_{min}), & t > Term
\end{cases}
$$

---

### 3. Monthly Operation Order (Critical)

The orchestration loop must follow this order each month:

1. **Compute MVA factor** (factor only)
2. **Snapshot BOP values** (AV, MFV, PFV)
3. **Withdrawals engine**
   
   - determines withdrawal amount (only month 1 of each policy year, year >= 2)
   - tracks free budget YTD
   - computes SC on excess
   - computes MVA on post-SC excess base
   - returns penalty_total

4. **Guarantee funds**
   
   - reduce MFV/PFV by withdrawal amount only
   - credit MFV/PFV monthly

5. **Account value roll-forward**
   
   - reduce by withdrawal + penalty_total
   - credit interest monthly
   - (optional) compute an NFF floor from guarantee funds

6. **Cash surrender value**
   
   - full surrender assumed each month for reporting
   - uses free budget remaining and SC/MVA rules
   - floors by guarantee funds

7. **Record outputs**
   
   - write one row of results for the month

!!! warning "Order matters"
    If you move these steps around, you will break the economics.
    For example:
    
    - Guarantee funds must be reduced by withdrawals before crediting
    - AV must be reduced before interest crediting
    - CSV requires post-floor AV if you are using AV floor behavior

---

### 4. State Management

Orchestration must maintain and update these states across months:

| State | Type | Why it exists |
|---|---|---|
| `av` | float | account value carried month to month |
| `wd_state` | WithdrawalState | tracks free withdrawal budget per policy year |
| `gf_state` | GuaranteeFundState | MFV/PFV balances |
| `prior_year_interest` | float | supports certain withdrawal methods and free limits |

Reset rule:
- when month_in_year == 12, set `prior_year_interest = sum(interest_credit over the year)` and reset accumulator.

---

### 5. Output Requirements (DataFrame)

The runner must produce a table that includes:

- time index fields
- rate fields
- withdrawal mechanics (including SC/MVA)
- AV fields (BOP, after WD, interest, EOP, floor)
- guarantee fund fields (MFV/PFV BOP/EOP)
- CSV fields (before floors, after floors, key diagnostics)

Suggested naming convention: prefix columns to keep things organized.

| Prefix | Meaning |
|---|---|
| `meta_` | time index, demographic fields, rate |
| `wd_` | withdrawal mechanics + charges |
| `mva_` | MVA factor (optional) |
| `av_` | account value roll-forward |
| `gf_` | guarantee fund roll-forward |
| `csv_` | cash surrender value fields |

---

## Inputs and Outputs

### Inputs

| Input | Source | Notes |
|---|---|---|
| `inputs` | `IllustrationInputs` | user-level controls (premium, rates, withdrawal method, etc.) |
| `catalog` | ProductCatalog | provides product features and parameters |

### Output

- `pd.DataFrame` with one row per month, ready for Streamlit.

---

## Starter Code (Expected Implementation)

The orchestration runner is expected to look like this:

- load `spec = catalog.get(product_code)`
- set projection length and total months
- initialize AV, withdrawal state, guarantee fund state
- loop months and call engines
- append a row dict each month
- return `pd.DataFrame(rows)`

```python
from __future__ import annotations

from typing import Dict, Any
import pandas as pd

from dac_myga_intro.engine.catalog import ProductCatalog
from dac_myga_intro.engine.inputs import IllustrationInputs

from dac_myga_intro.engine.withdrawals import (
    WithdrawalState,
    init_withdrawal_state,
    calc_withdrawal_for_month,
)
from dac_myga_intro.engine.mva import MVAInputs, calculate_mva_factor
from dac_myga_intro.engine.av import roll_forward_account_value
from dac_myga_intro.engine.guarantee_funds import (
    MinimumFundValueParams,
    ProspectiveFundValueParams,
    GuaranteeFundState,
    initialize_guarantee_funds,
    apply_surrender_to_guarantee_funds,
    credit_guarantee_funds_monthly,
)
from dac_myga_intro.engine.csv import calculate_cash_surrender_value


def run_illustration(catalog: ProductCatalog, inputs: IllustrationInputs) -> pd.DataFrame:
    spec = catalog.get(inputs.product_code)
    term_years = int(spec.term_years)

    # Determine projection length
    projection_years = int(inputs.projection_years) if inputs.projection_years and inputs.projection_years > 0 else term_years
    total_months = projection_years * 12
    term_months = term_years * 12

    # Initialize AV and states
    av = float(inputs.premium)
    wd_state: WithdrawalState = init_withdrawal_state()

    gf_spec = spec.features.guarantee_funds
    mfv_params = MinimumFundValueParams(base_pct_of_premium=float(gf_spec.mfv.base_pct_of_premium))
    pfv_params = ProspectiveFundValueParams(
        base_pct_of_premium=float(gf_spec.pfv.base_pct_of_premium),
        rate_annual=float(gf_spec.pfv.rate_annual),
        rate_years=int(gf_spec.pfv.rate_years),
        rate_after_years_annual=float(gf_spec.pfv.rate_after_years_annual),
    )
    gf_state: GuaranteeFundState = initialize_guarantee_funds(inputs.premium, mfv_params, pfv_params)

    prior_year_interest = 0.0
    current_year_interest_accum = 0.0

    rows: list[dict[str, Any]] = []

    for pm in range(1, total_months + 1):
        policy_year = (pm - 1) // 12 + 1
        month_in_year = (pm - 1) % 12 + 1

        # (0) MVA factor
        mva_factor = 0.0
        # ... compute using MVAInputs if enabled and rates provided ...

        # (1) Snapshot BOP
        av_bop = float(av)

        # (2) Withdrawals
        wd_state, wd_res = calc_withdrawal_for_month(
            catalog=catalog,
            inputs=inputs,
            state=wd_state,
            policy_year=policy_year,
            month_in_policy_year=month_in_year,
            av_bop=av_bop,
            year_bop_av=av_bop,
            prior_policy_year_interest=float(prior_year_interest),
            mva_factor=float(mva_factor),
        )

        # (3) Guarantee funds
        gf_state = apply_surrender_to_guarantee_funds(gf_state, float(wd_res.withdrawal_amount))
        gf_state = credit_guarantee_funds_monthly(
            gf_state,
            policy_year=policy_year,
            term_years=term_years,
            initial_rate=float(inputs.initial_rate),
            min_guaranteed_rate=float(spec.features.minimum_guaranteed_rate),
            pfv_params=pfv_params,
        )

        # (4) AV roll-forward
        av_res = roll_forward_account_value(
            av_bop=av_bop,
            withdrawal=float(wd_res.withdrawal_amount),
            penalty=float(wd_res.penalty_total),
            annual_rate=float(inputs.initial_rate),
        )
        av = float(av_res.av_eop)

        # (5) CSV
        csv_out = calculate_cash_surrender_value(
            av_eop=float(av),
            surrender_amount=float(av),
            free_remaining_at_calc=float(wd_res.free_remaining_eop),
            surrender_charge_pct=float(catalog.surrender_charge(inputs.product_code, policy_year)),
            mva_factor=float(mva_factor),
            gf_mfv_eop=float(gf_state.mfv),
            gf_pfv_eop=float(gf_state.pfv),
        )

        # (6) Record row
        rows.append(
            {
                "meta_policy_month": pm,
                "meta_policy_year": policy_year,
                "meta_month_in_policy_year": month_in_year,
                "av_bop": av_bop,
                "wd_withdrawal_amount": float(wd_res.withdrawal_amount),
                "av_interest_credit": float(av_res.interest_credit),
                "av_eop": float(av),
                "csv_final": float(csv_out.csv),
            }
        )

        # (7) year-end bookkeeping
        current_year_interest_accum += float(av_res.interest_credit)
        if month_in_year == 12:
            prior_year_interest = float(current_year_interest_accum)
            current_year_interest_accum = 0.0

    return pd.DataFrame(rows)
```

---

## Things to Consider (Common Pitfalls)

### 1. AV floor vs CSV floor (do not mix)

- If you floor AV by guarantee funds, you are effectively making AV “guaranteed”
  in the projection itself.
- If you only floor CSV, AV can stay below GF but surrender payout is floored.

!!! note
    Your current implementation floors AV **and** floors CSV. That is fine for a learning tool,
    but be aware this may not represent how all production systems separate AV vs NFF floors.

---

### 2. Term-end surrender charge override

You included a hook:

- override surrender charge to 0% at `pm == term_months`

This is a reasonable simplification but must be documented clearly.

---

### 3. MVA indexing assumptions

Right now:

- MVA factor is computed only if the benchmark rates are provided

Later you may extend:

- use an index curve by month
- use term-dependent rate selection

---

## Deliverable for Step 7

By the end of this step you should have:

- `run_illustration(catalog, inputs) -> DataFrame`
- correct monthly orchestration order
- stable column naming for Streamlit
- internal state handling:
  - free withdrawal budget
  - guarantee fund state
  - prior-year interest tracking

This completes Project A: a modular MYGA illustration engine built from reusable components.