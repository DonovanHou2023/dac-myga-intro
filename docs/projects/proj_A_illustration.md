## 1. Scope of the Illustration Tool

This project builds a **deterministic policy-level illustration engine** for a
**Multi-Year Guaranteed Annuity (MYGA)**.

The purpose is to understand:
- how MYGA product features interact,
- how calculation order affects outcomes,
- how illustration logic mirrors real insurer systems.

### Product Scope

| Feature | Included |
|---|---|
| Product Type | MYGA (fixed deferred annuity) |
| Crediting Rates | Initial guaranteed + renewal rates |
| Partial Withdrawals | Free withdrawal provision |
| Surrender Charges | Declining schedule |
| Market Value Adjustment (MVA) | Yes |
| Guaranteed Fund | Statutory nonforfeiture floor |
| Cash Surrender Value | Yes |

### Modeling Scope

- deterministic (no scenarios)
- single policy
- no behavior optimization
- annual time step (BOY / EOY)

---

## 2. Product Feature Definitions (Concise)

This section defines **what is modeled**, not implementation details.

### 2.1 Account Value (AV)

The **Account Value** represents accumulated premium and credited interest,
net of withdrawals and penalties.

$$
AV_{EOY} = (AV_{BOY} - W_t - \text{Penalty}_t) \times (1 + r_t)
$$

| Component | Description |
|---|---|
| \( AV_{BOY} \) | Account value at beginning of year |
| \( W_t \) | Withdrawal taken |
| \( r_t \) | Crediting rate for year |

---

### 2.2 Crediting Rates

| Period | Rate Type |
|---|---|
| Guarantee Period | Fixed, declared rate |
| Post-Guarantee | Renewal rates (year-specific) |

Rate selection depends on **policy year and guarantee term**.

---

### 2.3 Partial Withdrawal Provision

The contract defines a **free withdrawal limit**, while the policyholder determines
the **actual withdrawal taken**.

#### Free Withdrawal Limit

$$
\text{FreeLimit}_t = w \times AV_{BOY,t}
$$

| Rule | Assumption |
|---|---|
| Timing | Beginning of policy year |
| Year 1 | No withdrawals allowed |
| Excess | Allowed, but penalized |

#### Withdrawal Constraints

$$
W_t =
\begin{cases}
0, & t = 1 \\
\min(\text{UserInput}_t,\ AV_{BOY,t}), & t \ge 2
\end{cases}
$$

| Portion | Treatment |
|---|---|
| Free portion | No penalty |
| Excess portion | Subject to surrender charge and MVA |

---

### 2.4 Surrender Charges

Surrender charges apply to **amounts treated as surrender behavior**.

$$
\text{SC}_t = s_t \times W^{\text{excess}}_t
$$

| Characteristic | Description |
|---|---|
| Basis | Excess withdrawal |
| Pattern | Declining schedule |
| End State | Typically 0% |

---

### 2.5 Market Value Adjustment (MVA)

The **Market Value Adjustment** aligns liability payouts with asset market values
when withdrawals occur early.

#### Economic Interpretation

| Rate Movement | Asset Value | MVA |
|---|---|---|
| Rates ↑ | Values ↓ | Negative |
| Rates ↓ | Values ↑ | Positive |

#### MVA Factor

$$
\text{MVAFactor}_t =
\frac{(1 + x)^n}{(1 + y_t)^n} - 1
$$

| Symbol | Meaning |
|---|---|
| \( x \) | Issue reference rate |
| \( y_t \) | Current reference rate |
| \( n \) | Remaining guarantee duration |

#### Application Base

| Scenario | Amount Subject to MVA |
|---|---|
| Partial withdrawal | Excess portion after surrender charge |
| Full surrender | Entire surrenderable amount |

$$
\text{MVA}_t = \text{MVA Base}_t \times \text{MVAFactor}_t
$$

---

### 2.6 Guaranteed Fund

The **Guaranteed Fund** provides a statutory nonforfeiture floor.

$$
GF_t = \alpha P (1 + i_{min})^t - \text{Withdrawals}
$$

| Parameter | Meaning |
|---|---|
| \( \alpha \) | Guaranteed percentage (e.g., 87.5%) |
| \( i_{min} \) | Minimum guaranteed rate |

---

### 2.7 Cash Surrender Value

$$
CSV_t = \max(GF_t,\ AV_t - SC_t + \text{MVA}_t)
$$

Ensures compliance with statutory minimums.

---

## 3. Calculation Order (Key Principle)

Illustration results depend on **calculation order**.

Core dependencies:

| Step | Depends On |
|---|---|
| Withdrawals | BOY account value |
| Penalties | Excess withdrawal |
| MVA | Remaining duration, rates |
| Interest | Post-withdrawal balance |
| CSV | AV, SC, MVA, GF |

---

## 4. Illustration Calculation Flow

``` mermaid
flowchart TD
    A[Initialize Inputs] --> B[Set Projection Horizon]
    B --> C[Select Crediting Rate]
    C --> D[Compute MVA Factor]
    D --> E[Apply Withdrawal at BOY]
    E --> F[Update Guaranteed Fund]
    F --> G[Credit Interest]
    G --> H[Apply Surrender Charge]
    H --> I[Apply MVA]
    I --> J[Compute CSV]
    J --> C
```