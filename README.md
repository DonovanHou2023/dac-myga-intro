# Donovan’s Actuarial Class — MYGA Foundation

This repository contains the **course materials, homework assignments, and supporting tools**
for *Donovan’s Actuarial Class: Multi-Year Guaranteed Annuity (MYGA) Foundation*.

The project is designed as a **hands-on, practitioner-level introduction** to MYGA products,
policy illustration mechanics, and statutory reserving frameworks, progressing from
foundational concepts to modern valuation methodologies.

The materials are organized to support **self-study, guided instruction, and applied modeling**.

---

## Repository Contents

### 1. Class Materials

The `class_materials/` directory contains structured lecture notes written in Markdown
and compiled into a documentation site using **MkDocs Material**.

Each class builds on the previous one:

| Class | Topic |
|---|---|
| Class 1 | Actuarial foundations review (probability, life contingencies, financial math) |
| Class 2 | Annuities and MYGA product fundamentals |
| Class 3 | Fixed income basics, ALM, and Market Value Adjustment (MVA) |
| Class 4 | CARVM reserving methodology and path-based valuation |
| Class 5 | VM-22 framework: deterministic and stochastic reserves |

The emphasis is on **structure, intuition, and calculation flow**, not memorization.

---

### 2. Homework Assignments

The `homeworks/` directory contains assignments corresponding to each class.

Homework focuses on:

- conceptual understanding of reserving frameworks
- numerical reasoning
- progressive Python modeling exercises

Key modeling themes include:

- MYGA policy illustration engines
- partial withdrawal mechanics
- annuitization option valuation
- CARVM-style path testing and column reserves
- VM-22 deterministic reserve logic
- structural understanding of stochastic reserves and CTE

Each assignment builds toward a reusable modeling framework.

---

### 3. Streamlit Applications

This repository also includes **Streamlit applications** developed alongside the coursework.

These applications:

- visualize MYGA policy illustrations
- demonstrate reserve mechanics interactively
- connect theoretical concepts to applied tools

The Streamlit apps correspond directly to:

- policy illustration engines
- CARVM reserve logic
- VM-22 deterministic reserve concepts

They are intended as **educational and exploratory tools**, not production systems.

---

## Learning Objectives

By completing the materials in this repository, a student should be able to:

- understand MYGA product mechanics and benefit structures
- build a policy illustration engine in Python
- explain and implement CARVM reserving logic
- understand the motivation and structure of VM-22
- distinguish CARVM, VM-22, and cash flow testing
- reason about asset–liability interactions
- communicate valuation logic using diagrams and code

This repository is **not exam-prep focused**.
It reflects how actuaries reason about products and reserves in practice.

---

## Documentation Site

The documentation site is built with:

- MkDocs
- MkDocs Material theme
- MathJax for mathematical notation
- Mermaid for flowcharts and structural diagrams

Local development typically follows:

```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
mkdocs serve
```

The site is deployed using **GitHub Pages**.

---

## Intended Audience

This repository is suitable for:

- actuarial students transitioning from exams to applied work
- early-career actuaries working with annuity products
- analysts interested in insurance asset–liability modeling
- practitioners seeking a structured refresher on CARVM and VM-22

A basic familiarity with actuarial concepts and Python is helpful but not required.

---

## Disclaimer

All materials in this repository are for **educational purposes only**.

- Product structures are simplified
- Assumptions are illustrative
- Models are not production-ready
- Regulatory interpretations are instructional, not legal guidance

This repository does **not** represent the views, methods, or models of any insurer or employer.

---

## Author

**Donovan Hou, FSA, MAAA, MBA (Chicago Booth)**  
Actuarial and analytics practitioner focused on annuity products,
valuation frameworks, and actuarial modernization.

---

## License

This project is licensed for educational use.
See the `LICENSE` file for full terms.