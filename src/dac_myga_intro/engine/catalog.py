from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Dict, List, Optional

import yaml  # pyyaml

from .errors import ProductNotFoundError, ProductSpecValidationError
from .models import (
    BenchmarkIndex,
    FreePartialWithdrawalFeature,
    MVAFeature,
    ProductFeatures,
    ProductSpec,
    SurrenderChargeFeature,
    MFVSpec,
    PFVSpec,
    GuaranteeFundsSpec,
)


class ProductCatalog:
    """
    Loads product specs from YAML files and provides typed access + helper getters.
    Caches loaded specs in memory for fast repeated access.
    """

    def __init__(self, products_dir: Path):
        self.products_dir = products_dir
        self._cache: Dict[str, ProductSpec] = {}

    def list_products(self) -> List[str]:
        return sorted([p.stem.upper() for p in self.products_dir.glob("*.yml")])

    def get(self, product_code: str) -> ProductSpec:
        code = product_code.strip().upper()
        if code in self._cache:
            return self._cache[code]

        path = self.products_dir / f"{code}.yml"
        if not path.exists():
            raise ProductNotFoundError(f"Product '{code}' not found: {path}")

        raw = yaml.safe_load(path.read_text())
        spec = self._parse_spec(raw)
        self._cache[code] = spec
        return spec

    # -----------------------
    # Convenience getters
    # -----------------------
    def term_years(self, product_code: str) -> int:
        return self.get(product_code).term_years

    def minimum_guaranteed_rate(self, product_code: str) -> float:
        return self.get(product_code).features.minimum_guaranteed_rate

    def mva_enabled(self, product_code: str) -> bool:
        return self.get(product_code).features.mva.enabled

    def benchmark_index_code(self, product_code: str) -> Optional[str]:
        idx = self.get(product_code).features.mva.benchmark_index
        return None if idx is None else idx.code

    def surrender_charge(self, product_code: str, policy_year: int) -> float:
        spec = self.get(product_code)
        sched = spec.features.surrender_charge.schedule
        if policy_year <= spec.term_years:
            if policy_year not in sched:
                raise ProductSpecValidationError(
                    f"{product_code}: surrender_charge.schedule missing policy year {policy_year}"
                )
            return float(sched[policy_year])
        return float(spec.features.surrender_charge.after_term_default_charge_pct)

    def free_partial_withdrawal_method(self, product_code: str) -> str:
        return self.get(product_code).features.free_partial_withdrawal.method

    def free_partial_withdrawal_params(self, product_code: str) -> Dict[str, float]:
        return dict(self.get(product_code).features.free_partial_withdrawal.params)

    # -----------------------
    # Internal parsing / validation
    # -----------------------
    def _parse_spec(self, raw: dict) -> ProductSpec:
        try:
            schema_version = int(raw["schema_version"])
            product_code = str(raw["product_code"]).upper()
            term_years = int(raw["term_years"])

            f = raw["features"]

            # -----------------------
            # MVA
            # -----------------------
            mva_raw = f["mva"]
            mva_enabled = bool(mva_raw["enabled"])
            benchmark_index = None
            if mva_raw.get("benchmark_index"):
                bi = mva_raw["benchmark_index"]
                benchmark_index = BenchmarkIndex(
                    type=str(bi.get("type", "")),
                    code=str(bi.get("code", "")),
                    description=str(bi.get("description", "")),
                )

            # -----------------------
            # Surrender charge
            # -----------------------
            sc_raw = f["surrender_charge"]
            schedule = {int(k): float(v) for k, v in sc_raw["schedule"].items()}
            after_term_default = float(sc_raw["after_term"]["default_charge_pct"])

            # -----------------------
            # Free partial withdrawal
            # -----------------------
            fpw_raw = f["free_partial_withdrawal"]
            method = str(fpw_raw["method"])
            params = {str(k): float(v) for k, v in (fpw_raw.get("params") or {}).items()}

            allowed = {"prior_year_interest_credited", "pct_of_boy_account_value"}
            if method not in allowed:
                raise ProductSpecValidationError(
                    f"{product_code}: free_partial_withdrawal.method must be one of {sorted(allowed)}; got '{method}'"
                )
            if method == "pct_of_boy_account_value" and "pct" not in params:
                raise ProductSpecValidationError(
                    f"{product_code}: free_partial_withdrawal.params.pct is required when method == pct_of_boy_account_value"
                )

            free_partial_withdrawal = FreePartialWithdrawalFeature(
                enabled=bool(fpw_raw.get("enabled", True)),
                method=method,  # type: ignore
                params=params,
                description=str(fpw_raw.get("description", "")),
            )

            # -----------------------
            # Guarantee funds (NEW)
            # -----------------------
            gf_raw = f.get("guarantee_funds")

            default_mfv = {"base_pct_of_premium": 0.875}
            default_pfv = {
                "base_pct_of_premium": 0.907,
                "rate_annual": 0.0191,
                "rate_years": 10,
                "rate_after_years_annual": 0.0,
            }

            if gf_raw is None:
                gf_raw = {"mfv": default_mfv, "pfv": default_pfv}
            else:
                gf_raw = gf_raw or {}
                gf_raw.setdefault("mfv", default_mfv)
                gf_raw.setdefault("pfv", default_pfv)

            mfv_raw = gf_raw["mfv"]
            pfv_raw = gf_raw["pfv"]

            guarantee_funds = GuaranteeFundsSpec(
                mfv=MFVSpec(
                    base_pct_of_premium=float(
                        mfv_raw.get("base_pct_of_premium", default_mfv["base_pct_of_premium"])
                    )
                ),
                pfv=PFVSpec(
                    base_pct_of_premium=float(
                        pfv_raw.get("base_pct_of_premium", default_pfv["base_pct_of_premium"])
                    ),
                    rate_annual=float(pfv_raw.get("rate_annual", default_pfv["rate_annual"])),
                    rate_years=int(pfv_raw.get("rate_years", default_pfv["rate_years"])),
                    rate_after_years_annual=float(
                        pfv_raw.get(
                            "rate_after_years_annual",
                            default_pfv["rate_after_years_annual"],
                        )
                    ),
                ),
            )

            # -----------------------
            # Product features
            # -----------------------
            features = ProductFeatures(
                minimum_guaranteed_rate=float(f["minimum_guaranteed_rate"]),
                mva=MVAFeature(enabled=mva_enabled, benchmark_index=benchmark_index),
                surrender_charge=SurrenderChargeFeature(
                    schedule=schedule,
                    after_term_default_charge_pct=after_term_default,
                ),
                free_partial_withdrawal=free_partial_withdrawal,
                guarantee_funds=guarantee_funds,
            )

            # -----------------------
            # Assumptions placeholders
            # -----------------------
            a = raw.get("assumptions", {}) or {}

            return ProductSpec(
                schema_version=schema_version,
                product_code=product_code,
                term_years=term_years,
                features=features,
                mortality_table_key=a.get("mortality_table_key"),
                lapse_model_key=a.get("lapse_model_key"),
                withdrawal_behavior_key=a.get("withdrawal_behavior_key"),
                expense_assumption_key=a.get("expense_assumption_key"),
            )

        except KeyError as e:
            raise ProductSpecValidationError(f"Missing required field: {e}") from e
        except ValueError as e:
            raise ProductSpecValidationError(f"Invalid value type: {e}") from e