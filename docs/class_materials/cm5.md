# Class 5 — VM-22 Framework and Asset–Liability Reserve Methodology

This session introduces **VM-22**, the modern statutory reserving framework
for life and annuity products under the NAIC Valuation Manual.

VM-22 extends traditional deterministic reserve concepts by explicitly modeling:

- asset cash flows
- liability cash flows
- policyholder behavior
- economic uncertainty

The goal of this class is to understand **how VM-22 reserves are constructed,
what assumptions are used, and how VM-22 differs from CARVM and cash flow testing**.

---

## 1. What Is VM-22?

**VM-22** refers to **Valuation Manual, Section 22**, which governs statutory reserves
for many life and annuity products.

At a high level, VM-22 requires insurers to:

- project **future asset and liability cash flows**
- under prescribed **economic and actuarial assumptions**
- across **deterministic and stochastic scenarios**
- and determine a reserve sufficient to support those cash flows

VM-22 is fundamentally a **cash-flow–based valuation framework**.

---

## 2. VM-22 High-Level Reserve Structure

VM-22 consists of two primary reserve components:

| Component | Description |
|---|---|
| Deterministic Reserve (DR) | Baseline reserve under prescribed adverse scenarios |
| Stochastic Reserve (SR) | Tail-based reserve using multiple economic scenarios |

The statutory reserve is defined as:

$$
\text{VM-22 Reserve} = \max(\text{Deterministic Reserve}, \text{Stochastic Reserve})
$$

---

## 3. Deterministic Scenario Framework

### 3.1 Purpose of the Deterministic Reserve

The deterministic reserve answers the question:

> Under a prescribed adverse economic scenario,  
> what initial asset amount is required to fully support projected liability cash flows?

This reserve establishes **baseline adequacy** without relying on probability-weighted outcomes.

---

### 3.2 Deterministic Projection Mechanics

Under a deterministic scenario, the insurer performs:

1. Projection of **liability cash flows**
2. Projection of **asset cash flows**
3. Calculation of **period-by-period surplus**
4. Discounting of surplus to time 0
5. Iterative calibration of initial assets (reserve)

---

### 3.3 Surplus Definition

At projection time $t$:

$$
\text{Surplus}_t = \text{Asset Inflows}_t - \text{Liability Outflows}_t
$$

Examples of cash flows:

- **Asset inflows**
  - coupon income
  - maturities
  - reinvestment proceeds
- **Liability outflows**
  - withdrawals
  - annuity payments
  - death benefits
  - expenses

---

## 4. Finding the Deterministic Reserve (Iterative Process)

### 4.1 Why Iteration Is Required

The deterministic reserve is **not known in advance**.

- asset cash flows depend on the starting asset amount
- reinvestment patterns are nonlinear
- liability cash flows are path-dependent

Therefore, VM-22 requires solving an **implicit equation**:

$$
PV(\text{Surplus}) = 0
$$

---

### 4.2 Conceptual Iteration Logic

The insurer:

- guesses an initial asset amount
- projects assets and liabilities
- computes surplus
- discounts surplus
- adjusts the initial asset amount
- repeats until convergence

---

### 4.3 Deterministic Reserve Iteration Flow

``` mermaid
flowchart TD

    A[Initial Asset Guess] --> B[Project Asset Cash Flows]
    B --> C[Project Liability Cash Flows]
    C --> D[Compute Period Surplus]
    D --> E[Discount Surplus to Time 0]
    E --> F{PV Surplus ≈ 0?}
    F -- Yes --> G[Accept Deterministic Reserve]
    F -- No --> H[Adjust Initial Assets]
    H --> A
```

---

## 5. PV Surplus vs Interim Surplus

### 5.1 Binding Condition in VM-22

In VM-22, the **binding reserve condition** is:

$$
PV(\text{Surplus}) = 0
$$

This condition determines reserve sufficiency.

---

### 5.2 Interim Surplus Behavior

VM-22 does **not require** surplus to be positive in every projection year.

- interim deficits are permitted
- timing mismatches are allowed
- liquidity stress is not directly constrained

However:

- interim surplus patterns must be **documented**
- negative periods require **explanation**
- regulators may review projection diagnostics

---

### 5.3 Comparison with Cash Flow Testing

| Aspect | VM-22 | Cash Flow Testing |
|---|---|---|
| Binding constraint | PV surplus | Multiple metrics |
| Interim deficits | Allowed | Closely monitored |
| Liquidity focus | Secondary | Primary |
| Earnings emergence | Secondary | Primary |

---

## 6. VM-22 Assumption Framework

VM-22 assumptions are governed by **explicit regulatory guidance**.
Not all assumptions are best estimate.

---

### 6.1 Liability Assumptions

| Assumption | Governance | Notes |
|---|---|---|
| Mortality | Prescribed | VM tables |
| Lapse / Withdrawal | Company-specific | With margins |
| Annuitization Election | Company-specific | Subject to limits |
| Expenses | Company-specific | Prudent estimate |
| Premiums | Contractual | Fixed |

---

### 6.2 Asset Assumptions

| Assumption | Governance | Notes |
|---|---|---|
| Initial Asset Portfolio | Company-specific | Actual holdings |
| Default Rates | Prescribed / conservative | VM guidance |
| Reinvestment Strategy | Company-defined | Constrained |
| Reinvestment Yield | Scenario-driven | Prescribed scenarios |
| Asset Expenses | Company-specific | Prudent estimate |

---

### 6.3 Best Estimate vs Prescribed Summary

| Category | Best Estimate Allowed |
|---|---|
| Policyholder behavior | Yes (with margin) |
| Asset strategy | Yes |
| Mortality | No |
| Economic scenarios | No |

---

## 7. Stochastic Reserve Framework

### 7.1 Purpose of the Stochastic Reserve

The stochastic reserve captures **tail risk** arising from:

- adverse interest rate paths
- unfavorable reinvestment outcomes
- behavior sensitivity under stress

---

### 7.2 Scenario-Based Projection

VM-22 specifies:

- a prescribed number of economic scenarios
- stochastic interest rate and equity paths

Each scenario produces a **scenario-specific reserve requirement**.

---

### 7.3 CTE Measure

The stochastic reserve is calculated using **Conditional Tail Expectation (CTE)**:

$$
\text{CTE}_\alpha = \text{average of the worst } (1-\alpha)\% \text{ outcomes}
$$

The required CTE level depends on product type.

---

### 7.4 Stochastic Exclusion Test (SET)

Some products may qualify for a **Stochastic Exclusion Test**.

If passed:

- stochastic reserve may be waived
- deterministic reserve becomes binding

---

## 8. VM-22 vs CARVM

| Aspect | CARVM | VM-22 |
|---|---|---|
| Core focus | Worst-case benefit | Asset–liability cash flows |
| Time logic | Backward recursion | Forward projection |
| Assets | Implicit | Explicit |
| Behavior | Deterministic paths | Probabilistic |
| Tail risk | Implicit | Explicit (CTE) |

---

## 9. VM-22 vs Cash Flow Testing

VM-22 shares conceptual roots with traditional **cash flow testing**, but differs in purpose.

| Dimension | VM-22 | Cash Flow Testing |
|---|---|---|
| Objective | Statutory reserve | Risk management |
| Output | Binding reserve | Diagnostics |
| Scenario governance | Prescribed | Company-defined |
| Liquidity stress | Secondary | Central |
| Earnings analysis | Secondary | Central |

---

## 10. Conceptual Summary

VM-22 can be viewed as:

- a regulatory extension of cash flow testing
- a generalization of CARVM
- a framework that explicitly prices economic tail risk

**Key intuition**:

- CARVM asks: *What is the worst benefit path?*
- VM-22 asks: *What initial asset level supports liabilities under adverse distributions?*
- Cash flow testing asks: *Will the company survive through time?*

This class completes the transition from deterministic reserving
to modern asset–liability valuation.