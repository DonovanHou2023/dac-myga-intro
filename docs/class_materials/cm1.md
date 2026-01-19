# Class 1 — Actuarial Foundations Review

This lesson reviews key actuarial concepts used throughout the course. The goal is to establish a common language and notation for:

- probability and random variables  
- survival and mortality notation  
- life contingencies  
- financial mathematics  

!!! note "How to use this lesson"
    This session is a **review**, not a full re-teaching of preliminary actuarial material.  
    Focus on **notation** and **interpretation** — these will appear repeatedly in later lessons.

---

## 1. Probability and Random Variables

### 1.1 Random Variables

A **random variable** represents a numerical outcome of an uncertain future event.

Common actuarial uses:

- the timing of an event
- whether an event occurs within a period
- the value of a payment contingent on an event

| Term | Description |
|---|---|
| Random variable | Numerical representation of an uncertain outcome |
| Event | A specific outcome or set of outcomes |
| Sample space | Set of all possible outcomes |

!!! tip "Actuarial intuition"
    In product modeling, random variables often show up as *time-to-event* (e.g., time to death) or *event indicators* (e.g., surrender happens vs doesn’t happen).

---

### 1.2 Indicator Variables

Indicator variables model whether an event occurs.

$$
I =
\begin{cases}
1 & \text{if the event occurs} \\
0 & \text{if the event does not occur}
\end{cases}
$$

Indicator variables are useful for:

- modeling survival or termination
- defining contingent payments
- simplifying expected value calculations

!!! info "Why actuaries love indicators"
    They allow you to write contingent cash flows as a single expression, then take expectations cleanly.

---

### 1.3 Expectation

Expectation is the primary probabilistic operator used in actuarial work.

$$
E[X] = \sum_x x \, P(X = x)
$$

Key points:

- expectation represents an average over all possible outcomes
- many actuarial quantities are expressed as expected values
- higher moments (variance, skewness) are not emphasized in this course

!!! note "Focus for this course"
    If you can set up the random variable and compute an expectation, you can model most of what we need.

---

## 2. Survival and Mortality Concepts

### 2.1 Basic Mortality Notation

Standard actuarial notation is assumed.

| Symbol | Meaning |
|---|---|
| $q_x$ | Probability of death between ages $x$ and $x+1$ |
| $p_x$ | Probability of survival between ages $x$ and $x+1$ |
| ${}_t p_x$ | Probability of survival for $t$ years from age $x$ |

Relationship between one-year survival and death probabilities:

$$
p_x = 1 - q_x
$$

!!! info "Interpretation"
    $q_x$ answers: “What is the probability the life **dies** in the next year?”  
    $p_x$ answers: “What is the probability the life **survives** the next year?”

---

### 2.2 Survival Probabilities

Survival probabilities over multiple years:

$$
{}_t p_x = \prod_{k=0}^{t-1} \left( 1 - q_{x+k} \right)
$$

These probabilities form the basis for valuing payments contingent on survival or death.

!!! tip "Mental model"
    Multi-year survival is the product of surviving each year along the path.

---

## 3. Life Contingencies

Life contingencies analyze payments that depend on human life events.

Used to:

- value benefits contingent on survival or death
- compare different payment structures
- support actuarial valuation and reserving

!!! note "Scope"
    This course assumes familiarity with the **concepts**, not derivations.  
    We care about applying notation consistently to real cash flows.

---

### 3.1 Decrements

A **decrement** is a cause by which a policy terminates.

| Decrement | Description |
|---|---|
| Death | Termination due to death |
| Withdrawal | Voluntary termination |
| Maturity | Termination at a specified time |

General assumptions:

- decrements are mutually exclusive within a period
- timing conventions must be defined
- assumptions must be applied consistently

!!! warning "Common modeling pitfall"
    Many errors come from inconsistent timing assumptions (BOP vs EOP).  
    Always define when events happen within the period.

---

## 4. Financial Mathematics

### 4.1 Time Value of Money

The time value of money reflects that payments at different times are not directly comparable.

Discount factor:

$$
v = \frac{1}{1 + i}
$$

where $i$ is the annual effective interest rate.

---

### 4.2 Present Value

Present value converts future payments into an equivalent value at time 0.

For cash flows $C_t$ paid at time $t$:

$$
PV = \sum_{t=1}^{n} C_t v^t
$$

Unless otherwise stated:

- time is measured in discrete periods
- payments occur at the end of each period
- interest rates are deterministic

!!! info "Course convention"
    We will be explicit when switching between annual vs monthly time steps.  
    In Python projects, we will mostly operate in **monthly** time.

---

## 5. Life Insurance

Life insurance provides payments contingent on **death**.

### 5.1 Cash Flow Timing

- premiums are paid while the insured is alive
- a benefit is paid upon death
- timing of the benefit payment is uncertain
- valuation emphasizes death probabilities and discounting

### 5.2 Basic Cash Flow Sketch

```
Time:     0     1     2     3     4     5
          |-----|-----|-----|-----|-----|
Premiums: P     P     P
Death:                   X
Benefit:                   |B|
```

---

## 6. Annuities

Annuities provide payments contingent on **survival**.

### 6.1 Cash Flow Timing

- payments are made while the annuitant is alive
- payments stop at death
- duration of payments is uncertain
- valuation emphasizes survival probabilities and discounting

### 6.2 Basic Cash Flow Sketch

```
Time:     0     1     2     3     4     5
          |-----|-----|-----|-----|-----|
Premiums: P
Death:                         X
Payments:      |A|   |A|   |A|   |A|
```

---

## 7. Life Insurance vs Annuities

| Aspect | Life Insurance | Annuity |
|---|---|---|
| Primary risk addressed | Mortality (death) | Longevity (survival) |
| Cash flow trigger | Death | Survival |
| Benefit timing | Upon death | While alive |
| Payment uncertainty | Timing of payment | Duration of payments |
| Actuarial emphasis | Death probabilities | Survival probabilities |

!!! tip "Practical takeaway"
    Life insurance hedges *dying too soon* (financial loss at death).  
    Annuities hedge *living too long* (outliving assets).

---

## 8. Key Takeaways

!!! success "After this lesson, you should be comfortable with:"
    1. Basic probability concepts and expectation  
    2. Actuarial mortality and survival notation  
    3. Core life contingency ideas and timing conventions  
    4. Time value of money and present value  
    5. Cash flow timing for life insurance vs annuity contracts  

These foundational concepts will be referenced throughout the remainder of the course.