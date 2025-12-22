# Homework 1 — Actuarial Foundations

This assignment reinforces the foundational concepts introduced in **Class 1**.
Show all formulas used. Numerical answers should be clearly labeled.

Unless otherwise stated:
- Time is measured in discrete annual periods
- Payments occur at the end of each period
- Interest rates are annual effective rates

---

## Problem 1 — Probability (Indicator Variables)

Let $I$ be an indicator variable equal to $1$ if a policyholder dies during the
year and $0$ otherwise.

1. Write the definition of $I$ using a piecewise function.
2. If $P(\text{death}) = 0.02$, compute $E[I]$.

---

## Problem 2 — Probability (Expectation)

Let $X$ represent the benefit payment in a one-year term life insurance contract:

- $X = 100{,}000$ if the insured dies during the year
- $X = 0$ otherwise

If the probability of death during the year is $q = 0.01$:

1. Write the probability distribution of $X$
2. Compute $E[X]$

---

## Problem 3 — Mortality and Survival (Single Period)

At age $x$, the probability of death during the year is $q_x = 0.015$.

1. Compute the one-year survival probability $p_x$
2. Interpret $p_x$ in words

---

## Problem 4 — Mortality and Survival (Multiple Periods)

Suppose the following mortality rates apply:

- $q_9 = 0.10$
- $q_{10} = 0.20$

An individual is alive at the **beginning of age 9**.

1. Compute the probability that the individual survives to the end of age 10
2. Clearly show the formula used for ${}_2 p_9$

---

## Problem 5 — Time Value of Money (Present Value)

Assume an annual effective interest rate of $i = 5\%$.

A payment of $1{,}000$ will be made at the end of each of the next 3 years.

1. Write the present value formula
2. Compute the numerical present value

---

## Problem 6 — Time Value of Money (Changing Interest Rates)

Suppose interest rates vary by year:

- Year 1: $i_1 = 4\%$
- Year 2: $i_2 = 5\%$
- Year 3: $i_3 = 6\%$

A payment of $500$ is made at the end of each year.

1. Write the present value formula using year-specific discount factors
2. Compute the present value

---

## Problem 7 — Life Insurance (Expected Present Value)

Consider a one-year term life insurance contract that pays a benefit $B$ at the
end of the year of death.

Assume:
- $q_x = 0.01$
- $i = 5\%$

1. Write the expected present value (EPV) of the benefit
2. Express the EPV in terms of $B$

(No need to solve for a numerical value of $B$.)

---

## Problem 8 — Life Insurance (Premium Calculation)

Using the setup from **Problem 7**, suppose the level premium $P$ is paid at the
end of the year **only if the insured is alive**.

Under the equivalence principle:

1. Write the equation that equates the EPV of premiums to the EPV of benefits
2. Solve for the premium $P$ in terms of $B$

---

## Problem 9 — Annuity (Expected Present Value)

Consider a life annuity-immediate that pays $A$ at the end of the year
if the annuitant survives the year.

Assume:
- $p_x = 0.98$
- $i = 5\%$

1. Write the expected present value of the annuity payment
2. Express the EPV in terms of $A$

---

## Problem 10 — Life Insurance vs Annuity (Conceptual)

Answer the following in **words**, no calculations required.

1. Which probability is central to valuing life insurance contracts?
2. Which probability is central to valuing annuity contracts?
3. Explain why life insurance and annuities hedge opposite risks.

---

## Problem 11 — Python Exercise (Required)

Write a Python function that computes the present value of a sequence of cash
flows given a constant annual effective interest rate.

Your function should:
- Take a list of cash flows
- Take a discount rate as input
- Return the present value

Test your function using:
- Cash flows: `[100, 100, 100]`
- Discount rate: `0.05`

Include:
- The Python code
- The numerical output

---

### Submission Notes

- Show formulas clearly before substituting values
- Clearly label all answers
- Python code should be readable and commented

This assignment prepares you for valuation techniques used in later classes.