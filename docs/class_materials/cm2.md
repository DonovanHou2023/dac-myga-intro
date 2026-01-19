# Class 2 — Annuities and MYGA Product Fundamentals

This session introduces **annuities as insurance contracts**, focusing on how
different annuity types allocate risk, credit interest, and define benefits.
We then narrow the scope to **Multi-Year Guaranteed Annuities (MYGA)**, which will
serve as the core product for later **policy illustration and CARVM / VM-22 reserving** work.

!!! note "Learning objective"
    The goal of this class is **structural understanding**, not memorization.
    Focus on *how products work* and *why features exist* — not on marketing language.

---

## 1. What Is an Annuity?

An **annuity** is an insurance contract that exchanges money across time.

At a high level:

- The policyholder pays a **lump sum** or **series of premiums**
- The insurer promises **future benefits**, which may include:
  - account value accumulation
  - guaranteed minimum values
  - periodic income payments

!!! info "Key idea"
    Annuities primarily exist to **transfer financial risk**,  
    not to maximize investment returns.

---

## 2. Deferred vs. Immediate Annuities

Annuities are commonly classified by **when income payments begin**.

### 2.1 Lifecycle View

| Phase | Deferred Annuity | Immediate Annuity |
|---|---|---|
| Accumulation | Yes | No |
| Annuitization | Optional / Later | Immediate |
| Liquidity | Limited | None |
| Primary purpose | Growth + optional income | Guaranteed income |

!!! tip "Think in phases"
    Almost all annuity discussions become clearer once you explicitly separate
    **accumulation** from **income** phases.

---

### 2.2 Deferred Annuities

A **deferred annuity** consists of two conceptual phases:

1. **Accumulation phase**
   - premiums earn interest or indexed returns
   - account value evolves over time
2. **Annuitization phase (optional)**
   - account value may be converted into income

**Primary risks addressed by phase**

| Phase | Risk focus |
|---|---|
| Accumulation | Investment risk, interest rate risk |
| Annuitization | Longevity risk (if elected) |

!!! example "Accumulation example"
    - Premium: \$100,000  
    - Crediting rate: 4%  
    - Duration: 5 years  

    $$
    AV_5 = 100{,}000 \times (1.04)^5 \approx 121{,}665
    $$

---

### 2.3 Immediate Annuities

An **immediate annuity** skips the accumulation phase.

- Premium is exchanged directly for income
- Payments typically begin within 12 months

**Primary risk addressed**

| Phase | Risk focus |
|---|---|
| Income phase | Longevity risk |

!!! example "Income example"
    - Premium: \$100,000  
    - Payment period: 180 months  

    $$
    \text{Monthly Income} = \frac{100{,}000}{180} \approx 556
    $$

---

## 3. Types of Annuities (Industry Classification)

Annuities differ primarily by:

- **interest crediting methodology**
- **who bears market risk**

### 3.1 Product Taxonomy

| Product | Full name | Market risk |
|---|---|---|
| MYGA | Multi-Year Guaranteed Annuity | Insurer |
| FIA | Fixed Indexed Annuity | Insurer |
| RILA | Registered Index-Linked Annuity | Shared |
| VA | Variable Annuity | Policyholder |

!!! info "Why this matters"
    Product classification determines:
    - volatility of account values
    - complexity of modeling
    - statutory reserving treatment

---

## 4. Interest Crediting Methodology

### 4.1 MYGA — Fixed Guaranteed Crediting

- Declared rate locked for multiple years
- Simple and deterministic growth

!!! example "MYGA crediting"
    - Premium: \$100,000  
    - Rate: 4.5%  
    - Term: 3 years  

    $$
    AV_3 = 100{,}000 \times (1.045)^3 \approx 114{,}144
    $$

!!! tip "Modeling intuition"
    MYGA behaves like a **book-value instrument** with contractual guarantees.

---

### 4.2 FIA — Indexed Crediting with Downside Protection

- Interest linked to an external index
- Subject to caps, participation rates, or spreads
- Floor typically at 0%

!!! example "FIA with cap"
    - Index return: 8%  
    - Cap: 5%  

    $$
    \text{Credited Rate} = \min(8\%, 5\%) = 5\%
    $$

    $$
    AV_1 = AV_0 \times 1.05
    $$

!!! warning "Important distinction"
    Index return ≠ credited return.  
    Contract features determine what the policyholder actually earns.

---

### 4.3 RILA — Buffered / Leveraged Index Exposure

- Partial downside protection (buffer)
- Partial upside participation
- Losses possible beyond the buffer

!!! example "RILA buffer example"
    - Index return: –12%  
    - Buffer: 10%  

    $$
    \text{Credited Return} = -2\%
    $$

---

## 5. Triple Compounding (Conceptual)

Annuities often benefit from **three distinct layers of compounding**:

1. Compounding on **principal**
2. Compounding on **credited interest**
3. Compounding from **tax deferral** (tax not paid annually)

!!! note "Important clarification"
    Only the first two are *financial* compounding.
    Tax deferral is not mathematical compounding, but it materially affects outcomes.

---

## 6. MYGA Benefits Overview

MYGA benefits define **allowable cash flow events** under the contract.

### 6.1 Surrender Benefits

Upon surrender, the policyholder typically receives:

$$
\text{Surrender Value} = AV - \text{Surrender Charge} \pm \text{MVA}
$$

!!! info "Economic meaning"
    Surrender charges and MVA protect the insurer from early disintermediation.

---

### 6.2 Death Benefits

Common structure:

- Death benefit = Account Value
- Surrender charges often **waived**
- MVA may or may not apply (product-specific)

---

### 6.3 Maturity Benefits

At the end of the guarantee period, the policyholder may:

- Withdraw funds
- Renew at a new rate
- Annuitize

---

### 6.4 Annuitization Benefits

- Converts account value into income
- Common options:
  - life only
  - period certain
  - joint life

---

### 6.5 Partial Withdrawal Benefits

- Free withdrawal allowance (e.g., 10% annually)
- Excess withdrawals subject to surrender charges and/or MVA

!!! tip "Design intuition"
    Partial withdrawal provisions balance **liquidity for policyholders**
    against **persistency protection for insurers**.

---

## 7. Guaranteed Fund / Minimum Guaranteed Surrender Value (MGSV)

MYGA contracts include a **Guaranteed Fund**, providing a statutory floor.

Typical structure:

- 87.5% of single premium
- Accumulated at a minimum guaranteed interest rate
- Reduced for withdrawals

!!! example "Conceptual MGSV formula"
    $$
    \text{MGSV}_t = 0.875 \times P \times (1 + i_{min})^t - \text{Withdrawals}
    $$

!!! info "Why MGSV matters"
    MGSV ensures a **non-forfeiture minimum**, regardless of credited rates,
    and plays a critical role in statutory reserving.

---

## 8. Key MYGA Product Features (Summary)

| Feature | Description |
|---|---|
| Interest crediting | Fixed, guaranteed for term |
| Surrender charge | Declining schedule |
| Free withdrawal | Limited liquidity without penalty |
| MVA | Economic adjustment for rate changes |
| Guaranteed fund | Statutory minimum surrender value |
| Premium bonus | Optional upfront enhancement |

---

## 9. Looking Ahead

!!! success "Next steps"
    In the next class, we will extend MYGA analysis beyond the policy level and begin
    connecting **product mechanics to insurer balance sheet management**.

Specifically, we will cover:

- **Market Value Adjustment (MVA) in depth**
  - Why MVA exists economically
  - How interest rate movements affect asset values
  - Why you cannot understand surrender behavior or asset sizing without MVA

- **Asset–Liability Management (ALM) for MYGA products**
  - How MYGA liabilities are supported by fixed-income assets
  - Duration matching and cash flow matching concepts
  - How surrender provisions and MVA influence asset strategy
  - Practical constraints faced by insurers in real portfolios

- **Annuitization options and income conversion**
  - What annuitization actually means operationally
  - Common annuitization forms (life only, period certain, joint life)
  - How annuitization changes the insurer’s risk profile
  - Why annuitization assumptions matter even if few policyholders elect it

!!! info "Why this matters"
    MYGA products cannot be analyzed in isolation.  
    Their design is tightly linked to:
    - asset duration
    - interest rate risk
    - liquidity management
    - and long-term income guarantees

Understanding **MVA, ALM, and annuitization** is essential to understanding
how MYGA products are managed inside an insurance company.