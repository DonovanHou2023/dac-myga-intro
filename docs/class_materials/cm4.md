# Class 4 — CARVM Reserve Fundamentals

This session introduces the **Commissioners Annuity Reserve Valuation Method (CARVM)**,
the statutory reserving framework historically used for **fixed and deferred annuity products**,
including **Multi-Year Guaranteed Annuities (MYGA)**.

The goal of this class is to build a **structural and algorithmic understanding**
of how statutory annuity reserves are determined under conservative assumptions.

!!! note "Scope of this class"
    This class focuses on **CARVM / AG 33** methodology only.
    VM-22 will be introduced in **Class 5** as an extension and modernization.

---

## 1. Regulatory Context: Where CARVM Comes From

### 1.1 What Is CARVM?

**CARVM** stands for:

> **Commissioners Annuity Reserve Valuation Method**

It is a **statutory reserving methodology** designed to determine the minimum reserve
required for certain annuity products under U.S. insurance regulation.

CARVM applies primarily to:

- Fixed deferred annuities
- MYGA and traditional fixed annuity contracts
- Products without equity-linked guarantees

---

### 1.2 Regulatory Source

CARVM is formally described and governed by:

- **Actuarial Guideline 33 (AG 33)**

AG 33 provides:

- the valuation framework
- permitted assumptions
- benefit definitions
- and methodology for determining reserves

---

## 2. Statutory Reserve Concept

### 2.1 Traditional Reserve Formula

$$
\text{Reserve} = PV(\text{Future Benefits}) - PV(\text{Future Considerations})
$$

This formulation works well for life insurance, but annuities require
additional structure due to embedded options.

---

### 2.2 Why Annuities Require a Different Method

Annuity contracts differ because:

- benefits are **path-dependent**
- policyholders have multiple **behavioral choices**
- future cash flows depend on **timing and actions**

!!! warning
    CARVM is not an expected value calculation.
    It is designed to capture the **worst-case benefit path**.

---

## 3. CARVM Core Philosophy

### 3.1 Worst-Case Valuation

CARVM assumes that:

> At each decision point, the policyholder will act in a manner that is
> most favorable to themselves and most adverse to the insurer.

This results in a **deterministic, conservative reserve**.

---

### 3.2 Time-First Logic

CARVM operates using a **time-first framework**:

- Fix a policy year
- Compare all allowable benefits at that time
- Select the maximum benefit
- Discount backward one period

Maximization occurs **within each time point**, not across time.

---

## 4. MYGA as the Base Product Example

### 4.1 MYGA Benefit Structure

| Benefit Type | Description |
|---|---|
| Accumulation Value (AV) | Account value with guaranteed interest |
| Nonforfeiture Value | Statutory minimum value |
| Guaranteed Fund | Floor under nonforfeiture rules |
| Surrender Benefit | AV minus charges ± MVA |
| Death Benefit | Typically AV |
| Maturity Benefit | Value at end of guarantee period |
| Annuitization Option | Conversion to income payments |

---

### 4.2 Annuitization Options Considered

| Option | Description |
|---|---|
| 15-Year Certain | Fixed payments for 15 years |
| Life Only | Payments contingent on survival |

Annuitization introduces mortality-contingent cash flows
and requires separate valuation logic.

---

## 5. CARVM Methodology: Integrated Path and Backward Framework

### 5.1 Two-Level Structure

CARVM is evaluated in two nested layers:

1. **Across policyholder paths**
2. **Within each path, backward induction over time**

---

### 5.2 Benefit Definition at a Given Time

At policy year $t$, allowable actions may include:

$$
B_t = \max \left(
\text{Surrender}_t,\ 
\text{Death}_t,\ 
\text{Annuitization}_t,\ 
\text{Maturity}_t,\ 
PV_t(\text{Continue})
\right)
$$

---

### 5.3 Backward Discounting

Within each path:

$$
R_{t-1} = \frac{B_t}{1 + i_v}
$$

where $i_v$ is the **valuation interest rate**.

---

### 5.4 CARVM Conceptual Algorithm Flow

``` mermaid
flowchart TD

    A[Start CARVM Valuation] --> B[Enumerate Policyholder Paths]

    B --> P1[Path 1: No Partial Withdrawal]
    B --> P2[Path 2: Full Free Partial Withdrawal]

    P1 --> C1A[Start at Final Duration]
    C1A --> C1B[Enumerate Allowed Benefits]
    C1B --> C1C[Calculate Value of Each Benefit]
    C1C --> C1D[Take Maximum Benefit]
    C1D --> C1E[Discount Back One Period]
    C1E --> C1F{Reached Time 0?}
    C1F -- No --> C1B
    C1F -- Yes --> R1[Reserve for Path 1]

    P2 --> C2A[Start at Final Duration]
    C2A --> C2B[Enumerate Allowed Benefits]
    C2B --> C2C[Calculate Value of Each Benefit]
    C2C --> C2D[Take Maximum Benefit]
    C2D --> C2E[Discount Back One Period]
    C2E --> C2F{Reached Time 0?}
    C2F -- No --> C2B
    C2F -- Yes --> R2[Reserve for Path 2]

    R1 --> M[Take Maximum Across Paths]
    R2 --> M
    M --> Z[CARVM Reserve at Issue]
```

---

## 6. Path-Dependent Behavior

Partial withdrawal behavior affects **future contract structure**, not just
current cash flows.

For MYGA products without GLWB, practice typically evaluates:

| Path | Description |
|---|---|
| No Partial Withdrawal | Maximizes accumulation |
| Full Free Partial Withdrawal | Maximizes early cash extraction |

The CARVM reserve is the **maximum across evaluated paths**.

---

## 7. Assumptions and Terminology

### 7.1 Interest Rates

| Term | Purpose |
|---|---|
| Guaranteed Rate | Builds AV |
| Nonforfeiture Rate | Guaranteed floor |
| Valuation Interest Rate | Backward discounting |
| Annuitization Rate | Income conversion |

These rates apply at **different layers** of the calculation.

---

### 7.2 Mortality

Mortality assumptions are used primarily for annuitization valuation.
For deferred MYGA contracts, mortality is secondary and prescribed
by statutory annuity tables.

---

## Section A — Looking Ahead: From CARVM to VM-22

This class established a **deterministic, worst-case framework** for annuity reserving
under statutory regulation.

In the next class, we will transition to **VM-22**, which extends these same ideas using
a **stochastic, distribution-based approach**.

Specifically, the next section will cover:

- Why CARVM is considered **overly conservative** for modern products
- How VM-22 replaces single-path worst-case logic with **scenario distributions**
- The role of **CTE (Conditional Tail Expectation)** in reserve determination
- How policyholder behavior is modeled probabilistically under VM-22
- The conceptual mapping:
  - CARVM paths ⟶ VM-22 stochastic scenarios
  - Worst-case path ⟶ Tail of the distribution

This transition will show that **VM-22 is not a replacement of CARVM logic**,
but a **generalization built on the same structural foundation**.