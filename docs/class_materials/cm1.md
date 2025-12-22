# Class 1 — Actuarial Foundations Review

This lesson reviews key actuarial concepts that will be used throughout the
course. The goal is to establish a common language and notation for probability,
survival, life contingencies, and financial mathematics.

This session is a **review**, not a full re-teaching of preliminary actuarial
material. We focus on concepts and notation that will be referenced repeatedly
in later lessons.

---

## 1. Probability and Random Variables

### Random Variables

A random variable represents a numerical outcome of an uncertain future event.

In actuarial contexts, random variables are often used to represent:

- the timing of an event
- whether an event occurs within a period
- the value of a payment contingent on an event

| Term | Description |
|----|------------|
| Random variable | Numerical representation of an uncertain outcome |
| Event | A specific outcome or set of outcomes |
| Sample space | Set of all possible outcomes |

---

### Indicator Variables

Indicator variables are commonly used to model whether an event occurs.

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

---

### Expectation

Expectation is the primary probabilistic operator used in actuarial work.

$$
E[X] = \sum_x x \, P(X = x)
$$

Key points:

- expectation represents an average over all possible outcomes
- many actuarial quantities are expressed as expected values
- higher moments (variance, skewness) are not emphasized in this course

---

## 2. Survival and Mortality Concepts

### Basic Mortality Notation

Standard actuarial notation is assumed.

| Symbol | Meaning |
|----|--------|
| $q_x$ | Probability of death between ages $x$ and $x+1$ |
| $p_x$ | Probability of survival between ages $x$ and $x+1$ |
| ${}_t p_x$ | Probability of survival for $t$ years |

Relationship between one-year survival and death probabilities:

$$
p_x = 1 - q_x
$$

---

### Survival Probabilities

Survival probabilities over multiple periods are defined as:

$$
{}_t p_x = \prod_{k=0}^{t-1} \left( 1 - q_{x+k} \right)
$$

These probabilities form the basis for valuing payments that depend on survival
or death.

---

## 3. Life Contingencies

Life contingencies provide a framework for analyzing payments that depend on
human life events.

Life contingencies are used to:

- value benefits contingent on survival or death
- compare different payment structures
- support actuarial valuation and reserving

This course assumes familiarity with the **concepts**, not the derivations.

---

### Decrements

A decrement represents a cause by which a policy terminates.

Common decrements include:

| Decrement | Description |
|--------|------------|
| Death | Termination due to death |
| Withdrawal | Voluntary termination |
| Maturity | Termination at a specified time |

General assumptions:

- decrements are mutually exclusive within a period
- timing conventions must be defined
- assumptions must be applied consistently

---

## 4. Financial Mathematics

### Time Value of Money

The time value of money reflects the principle that payments at different times
are not directly comparable.

The discount factor is defined as:

$$
v = \frac{1}{1 + i}
$$

where $i$ is the annual effective interest rate.

---

### Present Value

Present value converts future payments into an equivalent value at time $0$.

For a sequence of cash flows $C_t$:

$$
PV = \sum_{t=1}^{n} C_t v^t
$$

Unless otherwise stated:

- time is measured in discrete periods
- payments occur at the end of each period
- interest rates are deterministic

---

## 5. Life Insurance

Life insurance contracts provide payments contingent on **death**.

### Cash Flow Timing (Conceptual)

- premiums are paid while the insured is alive
- a benefit is paid upon death
- the timing of the benefit payment is uncertain
- valuation emphasizes death probabilities and discounting

### Basic Cash Flow Structure

```
Time:     0     1     2     3     4     5
          |-----|-----|-----|-----|-----|
Premiums: P     P     P              
Death:                   X
Benefit:                   |B|
```

---

## 6. Annuities

Annuity contracts provide payments contingent on **survival**.

### Cash Flow Timing (Conceptual)

- payments are made while the annuitant is alive
- payments stop at death
- the duration of payments is uncertain
- valuation emphasizes survival probabilities and discounting

### Basic Cash Flow Structure

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
|------|----------------|---------|
| Primary risk addressed | Mortality (death) | Longevity (survival) |
| Cash flow trigger | Death | Survival |
| Benefit timing | Upon death | While alive |
| Payment uncertainty | Timing of payment | Duration of payments |
| Actuarial emphasis | Death probabilities | Survival probabilities |

---

## 8. Key Takeaways

After this session, you should be comfortable with:

1. Basic probability concepts and expectation
2. Actuarial mortality and survival notation
3. Core life contingency ideas
4. Time value of money and present value
5. Timing of cash flows for life insurance and annuity contracts

These foundational concepts will be referenced throughout the remainder of the course.