from pathlib import Path
import streamlit as st

from dac_myga_intro.engine.catalog import ProductCatalog
from dac_myga_intro.engine.illustration import IllustrationInputs, run_illustration

catalog = ProductCatalog(Path("src/dac_myga_intro/data/products"))

# Example UI inputs
product = st.selectbox("Product", ["MYGA5", "MYGA7", "MYGA10"])
premium = st.number_input("Premium", value=100000.0, step=1000.0)
initial_rate = st.number_input("Initial crediting rate", value=0.05, step=0.001, format="%.4f")
renewal_rate = st.number_input("Renewal rate", value=0.045, step=0.001, format="%.4f")

wd_method = st.selectbox(
    "Partial withdrawal method",
    ["pct_of_boy_av", "fixed_amount", "prior_year_interest_credited"]
)
wd_value = 0.0
if wd_method in ("pct_of_boy_av", "fixed_amount"):
    wd_value = st.number_input("Partial withdrawal value", value=0.10 if wd_method == "pct_of_boy_av" else 0.0)

if st.button("Run Illustration"):
    inp = IllustrationInputs(
        product_code=product,
        premium=premium,
        initial_rate=initial_rate,
        renewal_rate=renewal_rate,
        withdrawal_method=wd_method,   # type: ignore
        withdrawal_value=wd_value,
    )
    df = run_illustration(catalog, inp)
    st.dataframe(df, use_container_width=True)