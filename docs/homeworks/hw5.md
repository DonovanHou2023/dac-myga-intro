# Homework 5 — VM-22 Framework Understanding and Structural Modeling

This assignment is tied to **Class 5 (VM-22 Framework and Asset–Liability Reserve Methodology)**.

The goal of this homework is **conceptual mastery**, not numerical sophistication.

You should demonstrate that you understand:

- what VM-22 is designed to do
- how deterministic and stochastic reserves are constructed
- how assumptions are classified and governed
- how VM-22 differs from CARVM and cash flow testing
- how the overall VM-22 calculation framework is structured

---

## Problem 1 — What Problem Does VM-22 Solve? (Conceptual)

Answer in words.

1. What regulatory or economic problem is VM-22 designed to address?
2. Why is a purely deterministic reserve framework (such as CARVM) insufficient for many modern annuity products?
3. In one sentence, explain the key difference between:
   - “worst-case benefit” reserving
   - “asset–liability cash flow” reserving

---

## Problem 2 — Deterministic Reserve Logic (Conceptual)

Answer in words. No calculations are required.

1. What is the purpose of the **deterministic reserve** in VM-22?
2. Why is the deterministic reserve **not known in advance** and must be solved iteratively?
3. Define **surplus** in the context of VM-22 deterministic projections.
4. What condition must be satisfied at time 0 for the deterministic reserve to be considered sufficient?

---

## Problem 3 — PV Surplus vs Interim Surplus (Conceptual)

Answer in words.

1. In VM-22, is the binding condition based on:
   - surplus being positive in every projection year, or
   - the present value of surplus?
2. Can interim (year-by-year) surplus be negative in VM-22 projections?
3. Why might regulators or auditors still care about interim surplus patterns, even if they are not binding?

---

## Problem 4 — Assumptions in VM-22 (Conceptual)

VM-22 uses a mix of prescribed and company-specific assumptions.

### 4.1 Liability Assumptions

For each of the following, state whether it is typically:
- prescribed by regulation, or
- company-specific (with margins)

| Assumption | Prescribed or Company-Specific? |
|---|---|
| Mortality | |
| Lapse / Withdrawal | |
| Annuitization Election | |
| Expenses | |
| Premiums | |

---

### 4.2 Asset Assumptions

For each item below, briefly explain how it is governed under VM-22.

| Assumption | Description |
|---|---|
| Initial Asset Portfolio | |
| Reinvestment Strategy | |
| Reinvestment Yield | |
| Default Rates | |

---

## Problem 5 — Deterministic vs Stochastic Reserve (Conceptual)

Answer in words.

1. What additional risk does the **stochastic reserve** capture that the deterministic reserve does not?
2. What is a **CTE (Conditional Tail Expectation)** measure, in general terms?
3. Why does VM-22 require taking the **maximum** of deterministic and stochastic reserves?

---

## Problem 6 — VM-22 vs CARVM vs Cash Flow Testing (Conceptual)

Complete the table below.

| Aspect | CARVM | VM-22 | Cash Flow Testing |
|---|---|---|---|
| Primary objective | | | |
| Treatment of assets | | | |
| Treatment of behavior | | | |
| Tail risk | | | |
| Interim liquidity focus | | | |

Then answer:

- In one paragraph, explain how VM-22 can be viewed as a bridge between CARVM and cash flow testing.

---

# Problem 7 — VM-22 Structural Flowchart (Required)

This problem tests your understanding of the **overall VM-22 calculation architecture**.

You may complete this problem using **either Mermaid or Python visualization tools**.

---

## 7.1 Objective

Create a **flowchart** that clearly shows:

- how VM-22 reserves are calculated
- how deterministic and stochastic components fit together
- where assumptions and scenarios enter the process
- how the final reserve is determined

The emphasis is on **structure and logic**, not artistic detail.

---

## 7.2 Required Elements

Your flowchart should include **at least** the following components:

1. Assumption setup
   - liability assumptions
   - asset assumptions
2. Deterministic projection
   - asset cash flows
   - liability cash flows
   - surplus calculation
   - iterative solving for initial reserve
3. Stochastic projection
   - multiple economic scenarios
   - scenario-specific reserves
   - CTE aggregation
4. Final reserve determination
   - comparison of deterministic vs stochastic reserves

---

## 7.3 Option A — Mermaid Flowchart

If you choose Mermaid, include a diagram similar in spirit to:

``` mermaid
flowchart TD
    A[Set VM-22 Assumptions] --> B[Deterministic Scenario Projection]
    B --> C[Project Assets]
    B --> D[Project Liabilities]
    C --> E[Compute Surplus]
    D --> E
    E --> F[Discount Surplus]
    F --> G{PV Surplus ≈ 0?}
    G -- No --> H[Adjust Initial Assets]
    H --> B
    G -- Yes --> I[Deterministic Reserve]

    A --> J[Stochastic Scenarios]
    J --> K[Scenario Projections]
    K --> L[Scenario Reserves]
    L --> M[CTE Calculation]

    I --> N[Compare Reserves]
    M --> N
    N --> O[VM-22 Reserve]
```

You may modify, expand, or reorganize this diagram as long as the logic is correct.

---

## 7.4 Option B — Python Visualization (Optional)

Alternatively, you may use Python packages such as:

- graphviz
- networkx
- matplotlib (diagrammatic representation)

In this case:

- include your Python code
- briefly explain how each part of the diagram maps to VM-22 concepts

```
# Example (structure only)
from graphviz import Digraph

dot = Digraph()
dot.node("A", "Assumption Setup")
dot.node("B", "Deterministic Projection")
dot.node("C", "Stochastic Projection")
dot.node("D", "Final Reserve")

dot.edges([("A","B"), ("A","C"), ("B","D"), ("C","D")])
```

---

## Deliverables

Submit:

1. Written answers for Problems 1–6
2. A VM-22 flowchart (Mermaid or Python)
3. A short explanation (6–10 sentences) describing your flowchart and how it represents VM-22 logic

---

!!! success "What this homework demonstrates"
    - You understand the purpose and structure of VM-22
    - You can distinguish deterministic and stochastic reserves
    - You can explain how assumptions are governed
    - You can clearly communicate VM-22 architecture using diagrams