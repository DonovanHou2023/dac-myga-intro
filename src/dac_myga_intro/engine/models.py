from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Literal


FreeWithdrawalMethod = Literal[
    "prior_year_interest_credited",
    "pct_of_boy_account_value",
]


@dataclass(frozen=True)
class BenchmarkIndex:
    type: str
    code: str
    description: str = ""


@dataclass(frozen=True)
class MVAFeature:
    enabled: bool
    benchmark_index: Optional[BenchmarkIndex] = None


@dataclass(frozen=True)
class SurrenderChargeFeature:
    schedule: Dict[int, float]              # policy_year -> pct
    after_term_default_charge_pct: float    # e.g., 0.0


@dataclass(frozen=True)
class FreePartialWithdrawalFeature:
    enabled: bool
    method: FreeWithdrawalMethod
    params: Dict[str, float]                # e.g., {"pct": 0.10}
    description: str = ""


# -----------------------
# Guarantee fund specs (NEW)
# -----------------------
@dataclass(frozen=True)
class MFVSpec:
    base_pct_of_premium: float  # e.g. 0.875


@dataclass(frozen=True)
class PFVSpec:
    base_pct_of_premium: float        # e.g. 0.907
    rate_annual: float                # e.g. 0.0191
    rate_years: int                   # e.g. 10
    rate_after_years_annual: float    # e.g. 0.0


@dataclass(frozen=True)
class GuaranteeFundsSpec:
    mfv: MFVSpec
    pfv: PFVSpec


# -----------------------
# Product features
# -----------------------
@dataclass(frozen=True)
class ProductFeatures:
    minimum_guaranteed_rate: float
    mva: MVAFeature
    surrender_charge: SurrenderChargeFeature
    free_partial_withdrawal: FreePartialWithdrawalFeature

    # NEW: guarantee funds are product-driven features
    guarantee_funds: GuaranteeFundsSpec


@dataclass(frozen=True)
class ProductSpec:
    schema_version: int
    product_code: str
    term_years: int
    features: ProductFeatures

    # Assumptions placeholders (keys to external tables)
    mortality_table_key: Optional[str] = None
    lapse_model_key: Optional[str] = None
    withdrawal_behavior_key: Optional[str] = None
    expense_assumption_key: Optional[str] = None