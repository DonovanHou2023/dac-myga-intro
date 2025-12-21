# Lesson 1 — Actuarial Foundations Review

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

\[
I =
\begin{cases}
1 & \text{if the event occurs} \\
0 & \text{if the event does not occur}
\end{cases}
\]

Indicator variables are useful for:
- modeling survival or termination
- defining contingent payments
- simplifying expected value calculations

---

### Expectation

Expectation is the primary probabilistic operator used in actuarial work.

\[
E[X] = \sum x \cdot P(X = x)
\]

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
| \( q_x \) | Probability of death between ages \( x \) and \( x+1 \) |
| \( p_x \) | Probability of survival between ages \( x \) and \( x+1 \) |
| \( {}_tp_x \) | Probability of survival for \( t \) years |

Relationship:
\[
p_x = 1 - q_x
\]

---

### Survival Probabilities

Survival probabilities over multiple periods are defined as:

\[
{}_tp_x = \prod_{k=0}^{t-1} (1 - q_{x+k})
\]

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

\[
v = \frac{1}{1 + i}
\]

where:
- \( i \) is the annual effective interest rate

---

### Present Value

Present value converts future payments into an equivalent value at time 0.

For a sequence of cash flows \( C_t \):

\[
PV = \sum_{t=1}^{n} C_t \cdot v^t
\]

Unless otherwise stated:
- time is measured in discrete periods
- payments occur at the end of each period
- interest rates are deterministic

---

### Example: Present Value Calculation

```python
def present_value(cashflows, discount_rate):
    """
    cashflows: list of cash flows by period
    discount_rate: annual effective interest rate
    """
    return sum(
        cf / (1 + discount_rate) ** t
        for t, cf in enumerate(cashflows, start=1)
    )

print(present_value([100, 100, 100], 0.05))
```

This example illustrates the standard discounting convention used throughout the course.

## 5. Life Insurance vs Annuity Contracts (High-Level Comparison)

Before moving on, it is helpful to conceptually distinguish between life
insurance and annuity contracts. This comparison is intended to provide
high-level context only; detailed product mechanics are not covered in this
lesson.

| Aspect | Life Insurance | Annuity |
|------|----------------|---------|
| Primary risk addressed | Mortality (death) | Longevity (survival) |
| Typical triggering event | Death of the insured | Survival of the annuitant |
| Cash flow orientation | Protection-oriented | Income or accumulation-oriented |
| Benefit timing | Generally uncertain | Often contingent on survival |
| Actuarial emphasis | Death probabilities | Survival probabilities |

This distinction will be useful background for later lessons when annuity
products are discussed in greater detail.

---

## 6. Key Takeaways

After this session, you should be comfortable with:

- Basic probability concepts and expectation
- Actuarial mortality and survival notation
- Core life contingency ideas
- Present value and discounting concepts
- High-level differences between life insurance and annuity contracts

These foundational concepts will be referenced throughout the remainder of the course.