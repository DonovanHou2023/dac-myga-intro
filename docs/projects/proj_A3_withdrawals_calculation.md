## Step 3 — Withdrawal Application Logic

!!! abstract "Purpose of This Step"
    The purpose of this step is to apply **policyholder withdrawals** in a way that is:

    - contractually correct
    - economically consistent
    - compatible with downstream MVA and surrender charge logic

    This step determines **how much is withdrawn**, **what portion is free**, and
    **what portion is subject to penalties** — but does **not** update account value yet.
    Account value updates occur in a later step.

---

## What This Step Does

This step translates **policyholder intent** into a structured withdrawal result.

Specifically, it:

- enforces **timing rules** (year, month)
- enforces **account value constraints**
- separates withdrawals into:
  - free portion
  - excess portion
- prepares inputs for:
  - surrender charge calculation
  - MVA application
- tracks **year-to-date free withdrawal usage**

This step is intentionally stateful at the **policy-year level**.

---

## Business Requirements (BRD)

### 1. Timing Rules

| Rule | Requirement |
|---|---|
| Policy Year 1 | No withdrawals allowed |
| Month of withdrawal | First month only |
| Timing | Beginning of policy year (BOY) |

These rules ensure deterministic and reproducible illustrations.

---

### 2. Withdrawal Constraints

Withdrawals must satisfy **all** of the following:

| Constraint | Description |
|---|---|
| Non-negative | No negative withdrawals |
| AV-limited | Cannot exceed BOY account value |
| Free-limited | Free portion capped by provision |
| Excess allowed | Excess permitted but penalized |

Formally:

$$
W_t = \min(\text{UserInput}_t,\ AV_{BOY,t})
$$

---

### 3. Free Partial Withdrawal Provision

The product defines a **maximum free withdrawal allowance** for each policy year.

| Provision Type | Free Limit Definition |
|---|---|
| % of BOY AV | $w \times AV_{BOY}$ |
| Prior-year interest | Interest credited in prior year |

No free withdrawal is available in policy year 1.

---

### 4. Withdrawal Decomposition

Each withdrawal is decomposed into **free** and **excess** portions:

$$
\begin{aligned}
W^{\text{free}}_t &= \min(W_t,\ \text{FreeRemaining}_t) \\
W^{\text{excess}}_t &= \max(W_t - W^{\text{free}}_t,\ 0)
\end{aligned}
$$

| Component | Meaning |
|---|---|
| Free portion | Not subject to charges or MVA |
| Excess portion | Subject to surrender charge and MVA |

---

### 5. Year-to-Date Free Withdrawal Tracking

Free withdrawal usage must be tracked **within each policy year**.

| Field | Meaning |
|---|---|
| Free limit YTD | Annual free allowance |
| Free used YTD | Cumulative usage |
| Free remaining YTD | Available free amount |

This tracking enables:

- correct handling of multiple transactions
- transparent illustration output
- compatibility with future UI extensions

---

## Inputs and Outputs

### Inputs

| Input | Source |
|---|---|
| IllustrationInputs | Policyholder withdrawal method |
| ProductCatalog | Free withdrawal rules |
| Account Value (BOY) | Prior projection step |
| Prior-year interest | For certain methods |
| MVA factor | From Step 2 |

---

### Outputs

| Output | Meaning |
|---|---|
| Withdrawal amount | Total withdrawal applied |
| Free used | Free portion used |
| Excess amount | Subject to penalties |
| Surrender charge | Applied to excess |
| MVA amount | Applied to excess (net) |
| Updated state | Free usage tracking |

---

## Starter Code (Expected Implementation)

Below is a **reference structure** for implementing withdrawal application.
Students are expected to match the **logic and ordering**, not copy line-for-line.

```python
@dataclass(frozen=True)
class WithdrawalState:
    policy_year: int
    month_in_policy_year: int
    free_limit_ytd: float
    free_used_ytd: float
    free_remaining_ytd: float


@dataclass(frozen=True)
class WithdrawalResult:
    withdrawal_amount: float
    free_used_this_txn: float
    excess_amount: float
    surrender_charge_amount: float
    mva_amount: float
    penalty_total: float


def calc_withdrawal_for_month(
    *,
    catalog,
    inputs,
    state,
    policy_year,
    month_in_policy_year,
    av_bop,
    year_bop_av,
    prior_policy_year_interest,
    mva_factor,
):
    # 1. Enforce timing rules
    if policy_year <= 1 or month_in_policy_year != 1:
        return state, WithdrawalResult(
            withdrawal_amount=0.0,
            free_used_this_txn=0.0,
            excess_amount=0.0,
            surrender_charge_amount=0.0,
            mva_amount=0.0,
            penalty_total=0.0,
        )

    # 2. Determine requested withdrawal
    requested = compute_user_withdrawal_amount(
        inputs, policy_year, month_in_policy_year,
        year_bop_av, prior_policy_year_interest
    )

    withdrawal = min(requested, av_bop)

    # 3. Split free vs excess
    free_used = min(withdrawal, state.free_remaining_ytd)
    excess = max(withdrawal - free_used, 0.0)

    # 4. Apply surrender charge
    sc_pct = catalog.surrender_charge(inputs.product_code, policy_year)
    sc_amt = excess * sc_pct

    # 5. Apply MVA to net excess
    mva_subject = max(excess - sc_amt, 0.0)
    mva_amt = mva_subject * mva_factor

    penalty_total = sc_amt - mva_amt

    return updated_state, WithdrawalResult(
        withdrawal_amount=withdrawal,
        free_used_this_txn=free_used,
        excess_amount=excess,
        surrender_charge_amount=sc_amt,
        mva_amount=mva_amt,
        penalty_total=penalty_total,
    )
```

---

## Deliverable for Step 3

By the end of this step, you should have:

- a deterministic withdrawal engine
- correct handling of free vs excess withdrawals
- stateful tracking of free usage
- clean separation between **withdrawal logic** and **account value updates**

This output will be consumed by the **account value projection step** next.