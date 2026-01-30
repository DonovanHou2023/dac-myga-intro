from pathlib import Path

import pandas as pd

from dac_myga_intro.engine.catalog import ProductCatalog
from dac_myga_intro.engine.illustration import run_illustration
from dac_myga_intro.engine.inputs import IllustrationInputs


def test_run_illustration_smoke():
    # Adjust this path to wherever your product YAML files live
    products_dir = Path("src/dac_myga_intro/data/products")
    catalog = ProductCatalog(products_dir)

    inputs = IllustrationInputs(
        product_code="MYGA5",          # must exist in your YAML
        premium=100_000.0,
        initial_rate=0.05,
        renewal_rate=0.04,             # not used if projecting only term
        withdrawal_method="fixed_amount",
        withdrawal_value=5_000.0,
        # keep MVA off for now (None rates)
        mva_initial_index_rate=None,
        mva_current_index_rate=None,
    )

    df = run_illustration(catalog, inputs)

    # 1) Must return a DataFrame
    assert isinstance(df, pd.DataFrame)

    # 2) Expected row count = term_years * 12
    assert len(df) == 5 * 12

    # 3) Must include key columns
    expected_cols = [
        "meta_policy_month",
        "meta_policy_year",
        "meta_month_in_policy_year",
        "av_bop",
        "av_eop",
        "wd_withdrawal_amount",
        "csv",
        "gf_mfv_eop",
        "gf_pfv_eop",
    ]
    for c in expected_cols:
        assert c in df.columns