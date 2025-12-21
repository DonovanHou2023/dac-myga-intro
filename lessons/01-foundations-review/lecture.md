# Lesson 1 — Foundations Review

Welcome to Lesson 1. This example lecture contains a short outline and a sample code block.

## Outline

- Introduction to MYGA
- Product structure
- Key math concepts

## Example Code

```python
def present_value(cashflows, discount_rate):
    return sum(cf / (1 + discount_rate) ** t for t, cf in enumerate(cashflows, start=1))

print(present_value([100, 100, 100], 0.05))
```

Feel free to edit this file and push changes to `main` — the site will rebuild automatically.
