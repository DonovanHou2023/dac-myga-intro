# Class 3 — Bond Pricing, ALM, and Market Value Adjustment (MVA)

This session connects **MYGA product mechanics** to the **asset side of the balance sheet**.
We begin with a refresh on **bond cash flows and pricing**, then extend those ideas to
**asset–liability management (ALM)**, **spread-based earnings**, and the economic logic
behind **Market Value Adjustment (MVA)**.

We conclude with a deeper look at **annuitization options** and what income conversion
means in practice.

!!! note "Big picture"
    You cannot understand MYGA products without understanding:
    - how assets are priced
    - how assets earn returns
    - and what happens when interest rates change

---

## 1. Bond Cash Flows (Refresher)

Fixed-income assets are the primary backing for MYGA liabilities.
We start with a standard **coupon bond**.

### 1.1 Bond Cash Flow Structure

Consider a bond with:
- Face value: \$100
- Coupon rate: 4% annually
- Coupon frequency: semiannual
- Maturity: 5 years

**Cash flows**

- At purchase (time 0): investor pays market price
- Every 6 months: coupon payment
- At maturity: final coupon + principal repayment

!!! example "Bond cash flow timeline (semiannual)"

```
Time:   0    0.5    1.0    1.5    2.0    ...    5.0
        |-----|------|------|------|------|------|
Cash:  -P     C      C      C      C      ...   C+100
```

Where:
- $C = 100 \times 4\% / 2 = 2$

---

## 2. Bond Pricing and Market Value

### 2.1 Market Value of a Bond

The **market value** of a bond is the present value of its future cash flows,
discounted at the **current market yield**.

$$
MV = \sum_{t=1}^{n} \frac{C_t}{(1+y)^t}
$$

Where:
- $C_t$ = cash flow at time $t$
- $y$ = market yield per period

!!! info "Key point"
    Market value depends on **current interest rates**, not the coupon rate.

---

### 2.2 Par, Premium, and Discount Bonds

| Price vs Par | Description |
|---|---|
| $MV = 100$ | Bond trades at par |
| $MV > 100$ | Bond trades at a premium |
| $MV < 100$ | Bond trades at a discount |

!!! tip "Economic intuition"
    - Coupon > market yield → premium bond  
    - Coupon < market yield → discount bond  

At time 0:
- buying a **premium bond** means paying more than face value
- buying a **discount bond** means paying less than face value

---

### 2.3 Book Value vs Market Value

| Concept | Meaning |
|---|---|
| Market value | Price if bond is sold today |
| Book value | Amortized cost on insurer’s books |

For insurers:
- assets are often held at **book value**
- gains and losses are realized when assets are sold

!!! warning "Important distinction"
    Market value drives **economic reality**.
    Book value drives **accounting presentation**.

---

## 3. Interest Rate Sensitivity

### 3.1 Interest Rate Movements

- When interest rates **rise** → bond prices **fall**
- When interest rates **fall** → bond prices **rise**

This inverse relationship is fundamental to MVA design.

---

### 3.2 Duration (Conceptual)

**Duration** measures a bond’s sensitivity to interest rate changes.

!!! info "What duration tells you"
    Approximate % change in price for a 1% change in yield.

Example:
- Duration = 5
- Rates increase by 1%
- Bond price decreases by ≈ 5%

We will focus on **effective duration intuition**, not formal derivations.

---

## 4. Asset–Liability Management (ALM) for MYGA

### 4.1 Asset Portfolio for MYGA

MYGA premiums are typically invested in **fixed-income assets**, such as:

- corporate bonds
- structured notes
- mortgage-backed securities
- commercial mortgage loans
- select CLO tranches

!!! note "Unifying idea"
    Regardless of asset type, the goal is the same:
    earn a predictable return to support guaranteed liabilities.

---

### 4.2 Net Earned Rate and Spread

Define:

- **Asset Earned Rate (AER)**: yield earned on assets
- **Credited Rate**: interest credited to policyholders
- **Spread** = AER – Credited Rate

!!! example "Typical spread economics"
    - Asset earned rate: 5.5%
    - MYGA credited rate: 4.0%
    - Spread: 1.5% (150 bps)

The spread is used to:
- cover expenses
- absorb risks
- generate profit

!!! info "Industry reality"
    Typical long-run spreads:
    - ~100–200 bps
    - renewal rates are often **lower** than initial rates
    - spreads generally widen after the guarantee period

---

## 5. Why Market Value Adjustment (MVA) Exists

### 5.1 The Economic Problem

Suppose:
- Insurer purchased assets when rates were low
- Interest rates rise
- Policyholder surrenders early

To pay the surrender value:
- insurer may need to **sell assets**
- assets now have **lower market value**

This creates a **market value loss**.

---

### 5.2 MVA as a Risk-Sharing Mechanism

**Market Value Adjustment (MVA)** passes part of the asset gain/loss
to the policyholder.

!!! info "Key principle"
    MVA aligns the **liability payout** with the **economic value of assets**.

---

### 5.3 Simple MVA Example

Assume:
- Initial credited rate: 4%
- Current market rate: 6%
- Remaining duration: 3 years

Rates increased → asset value declined.

Simplified intuition:
- higher current rates → **negative MVA**
- lower current rates → **positive MVA**

!!! note "Product design detail"
    Many MVAs are calculated using:
    - reference yields
    - spread offsets
    - duration-based formulas

Exact formulas vary by product.

---

## 6. Annuitization Options

Annuitization converts **account value** into a stream of income payments.

### 6.1 Common Annuitization Forms

| Option | Description |
|---|---|
| Life only | Payments for life, stop at death |
| Life with period certain | Minimum guaranteed payment period |
| Period certain | Payments for fixed number of years |
| Joint life | Payments continue while either life is alive |

---

### 6.2 Numerical Illustration

Assume:
- Account value at annuitization: \$100,000
- Life expectancy: 20 years (240 months)
- Simplified payout factor

**Life only (illustrative)**

$$
\text{Monthly Payment} \approx \frac{100{,}000}{240} \approx 417
$$

**Life with 15-year certain**

- Payments guaranteed for at least 180 months
- Monthly payment slightly lower due to guarantee

!!! tip "Why this matters"
    Annuitization changes the insurer’s risk from:
    - accumulation risk
    - to longevity and payout risk

---

## 7. Key Takeaways

!!! success "After this class, you should understand:"
    - how bond cash flows and pricing work
    - the difference between market value and book value
    - why interest rate changes create gains and losses
    - how MYGA products earn spread through ALM
    - why MVA is economically necessary
    - how annuitization options reshape cash flows

---

## 8. Looking Ahead

!!! success "Next class"
    In **Class 4**, we will shift from product economics to **statutory reserving**.

We will introduce:

- **CARVM (Commissioners Annuity Reserve Valuation Method)**
- Relevant NAIC guidance (including **AG 33** and VM-22 context)
- How CARVM translates product guarantees into reserves
- Step-by-step reserve calculation intuition

This will complete the bridge from:
**product → assets → economics → statutory reserves**.