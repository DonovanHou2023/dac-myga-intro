## Step 1A — Define Illustration Inputs

!!! abstract "Purpose of This Step"
    Before any illustration logic can be written, we must define a **single, consistent
    input object** that represents all assumptions needed to run a MYGA illustration.

    In production systems, this input layer is critical for:
    - standardization
    - validation
    - separation of concerns

    This step establishes the **contract** between the user interface and the
    illustration engine.

---

### What This Step Does

This step defines an `IllustrationInputs` structure that:

- captures all **policy- and product-level assumptions**
- standardizes **withdrawal behavior inputs**
- optionally supports **MVA-related inputs**
- validates inputs before projection begins

All downstream steps (projection, withdrawals, MVA, surrender value, reserves)
will depend on this object.

---

### Business Requirements (BRD)

#### 1. Input Categories

The illustration inputs must cover the following categories:

| Category | Fields | Purpose |
|---|---|---|
| Policy Info | premium, issue_age, gender | drives duration and future extensions |
| Product ID | product_code | selects default schedules / terms |
| Crediting | initial_rate, renewal_rate | MYGA growth mechanics |
| Withdrawals | method + value | models policyholder behavior |
| Projection Control | projection_years | determines output horizon |
| MVA Controls | index rates, overrides | supports MVA calculation |

---

#### 2. Required vs Optional Fields

**Required fields (no defaults):**

| Field | Description |
|---|---|
| product_code | identifies MYGA product |
| premium | single premium amount |
| issue_age | age at issue |
| gender | used for later extensions |
| initial_rate | guaranteed rate |
| renewal_rate | post-guarantee rate |
| withdrawal_method | behavior model |

**Optional fields (with defaults):**

| Field | Default | Notes |
|---|---|---|
| projection_years | 15 | 0 means “use product default” later |
| withdrawal_value | 0.0 | interpreted by withdrawal method |
| mva_* fields | None | optional for early steps |

---

#### 3. Withdrawal Method Standardization

Withdrawal behavior must be expressed using **standardized methods**.

| Method | Meaning | Example |
|---|---|---|
| pct_of_boy_av | % of BOY account value | 5% of AV |
| fixed_amount | fixed dollar withdrawal | $2,000 |
| prior_year_interest_credited | interest-only withdrawal | last year’s interest |

This avoids hardcoding behavior into the engine.

---

#### 4. Validation Rules (Minimum)

The input object must enforce basic validity:

| Rule | Reason |
|---|---|
| premium > 0 | avoid invalid policies |
| issue_age ∈ [0,120] | realistic bounds |
| rates ≥ 0 | no negative rates |
| projection_years ≥ 0 | 0 = product default |
| withdrawal_value ≥ 0 | no negative withdrawals |
| pct_of_boy_av ≤ 10% | align with free withdrawal |

Validation should occur **before** any projection logic runs.

---

#### 5. Role in the Illustration Engine

The illustration engine will later use these inputs as follows:

| Input | Used For |
|---|---|
| initial_rate / renewal_rate | crediting logic |
| withdrawal_method / value | BOY withdrawal calculation |
| projection_years | number of rows |
| mva_* | MVA factor and adjustment |

This makes Step 1A the **foundation layer** of the entire project.

---

### Starter Code (What You Are Expected to Write)

Below is a **starter implementation** you can build on.
You are encouraged to extend validation and structure over time.

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Literal

WithdrawalMethod = Literal[
    "pct_of_boy_av",
    "fixed_amount",
    "prior_year_interest_credited",
]

GenderCategory = Literal["M", "F"]


@dataclass(frozen=True)
class IllustrationInputs:
    # --- required fields ---
    product_code: str
    premium: float
    issue_age: int
    gender: GenderCategory

    initial_rate: float
    renewal_rate: float

    withdrawal_method: WithdrawalMethod

    # --- optional / default fields ---
    projection_years: int = 15
    withdrawal_value: float = 0.0

    # optional MVA inputs
    mva_initial_index_rate: Optional[float] = None
    mva_current_index_rate: Optional[float] = None
    mva_months_remaining_override: Optional[int] = None

    def validate(self) -> None:
        if self.premium <= 0:
            raise ValueError("premium must be > 0")
        if not (0 <= self.issue_age <= 120):
            raise ValueError("issue_age must be between 0 and 120")
        if self.initial_rate < 0 or self.renewal_rate < 0:
            raise ValueError("rates must be >= 0")
        if self.projection_years < 0:
            raise ValueError("projection_years must be >= 0")
        if self.withdrawal_value < 0:
            raise ValueError("withdrawal_value must be >= 0")

        if self.withdrawal_method == "pct_of_boy_av":
            if not (0.0 <= self.withdrawal_value <= 0.10):
                raise ValueError(
                    "pct_of_boy_av withdrawal_value must be between 0 and 0.10"
                )
```

---

### Example Usage

```python
inputs = IllustrationInputs(
    product_code="MYGA_5",
    premium=100_000,
    issue_age=60,
    gender="M",
    initial_rate=0.045,
    renewal_rate=0.035,
    withdrawal_method="pct_of_boy_av",
    withdrawal_value=0.05,
)

inputs.validate()
```

---

### Deliverable for Step 1A

By the end of this step, you should have:

- a validated `IllustrationInputs` object
- standardized withdrawal methods
- basic input validation
- a reproducible way to pass assumptions into the illustration engine

This object will be reused in **every subsequent step** of the project.