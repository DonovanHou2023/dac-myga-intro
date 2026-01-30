from pathlib import Path

import streamlit as st
import pandas as pd

from dac_myga_intro.engine.catalog import ProductCatalog
from dac_myga_intro.engine.errors import ProductCatalogError


# -----------------------
# Page config
# -----------------------
st.set_page_config(
    page_title="Donovan's MYGA Illustration Tool",
    layout="wide",
)

# -----------------------
# Header / Branding
# -----------------------
logo_path = Path("assets") / "logo_black.png"
col_logo, col_title = st.columns([1, 5], vertical_alignment="center")

with col_logo:
    if logo_path.exists():
        st.image(str(logo_path), use_container_width=True)
    else:
        st.caption("Logo not found. Put it at: assets/logo.png")

with col_title:
    st.title("Donovan’s MYGA Illustration Tool")
    st.write(
        "This app is part of the assets for **Donovan’s MYGA Intro class**. "
        "It demonstrates how product specs (YAML) feed into an illustration engine."
    )

st.divider()

# -----------------------
# Load product catalog
# -----------------------
products_dir = Path("src") / "dac_myga_intro" / "data" / "products"
catalog = ProductCatalog(products_dir)

# -----------------------
# Layout: left = controls, right = display
# -----------------------
left, right = st.columns([2, 3], vertical_alignment="top")

with left:
    st.subheader("Product Selection")

    # If YAML files exist, list them; otherwise fallback to the known list.
    try:
        available_products = catalog.list_products()
        if not available_products:
            available_products = ["MYGA5", "MYGA7", "MYGA10"]
    except Exception:
        available_products = ["MYGA5", "MYGA7", "MYGA10"]

    selected_product = st.selectbox(
        "Choose a product",
        options=available_products,
        index=0,
    )

    st.caption(f"Looking for YAML at: `{products_dir}`")

with right:
    st.subheader("Product Features")

    try:
        spec = catalog.get(selected_product)

        # ---- Flatten into a key/value table for display ----
        # (Keep it simple now; later you can make it prettier.)
        rows = []

        rows.append(("Product Code", spec.product_code))
        rows.append(("Term (years)", spec.term_years))
        rows.append(("Minimum Guaranteed Rate", f"{spec.features.minimum_guaranteed_rate:.2%}"))

        rows.append(("MVA Enabled", "Yes" if spec.features.mva.enabled else "No"))
        if spec.features.mva.benchmark_index is not None:
            rows.append(("Benchmark Index Code", spec.features.mva.benchmark_index.code))
            if spec.features.mva.benchmark_index.description:
                rows.append(("Benchmark Index Description", spec.features.mva.benchmark_index.description))

        fpw = spec.features.free_partial_withdrawal
        rows.append(("Free Partial Withdrawal Enabled", "Yes" if fpw.enabled else "No"))
        rows.append(("Free Partial Withdrawal Method", fpw.method))
        if fpw.params:
            rows.append(("Free Partial Withdrawal Params", str(fpw.params)))

        # Show key/value table
        kv_df = pd.DataFrame(rows, columns=["Feature", "Value"])
        st.dataframe(kv_df, use_container_width=True, hide_index=True)

        st.markdown("### Surrender Charge Schedule")
        sched = spec.features.surrender_charge.schedule
        sched_rows = [{"Policy Year": int(y), "Surrender Charge": f"{float(p):.2%}"} for y, p in sorted(sched.items())]

        # Add an explicit "After Term" row so it’s obvious
        sched_rows.append(
            {
                "Policy Year": f">{spec.term_years}",
                "Surrender Charge": f"{spec.features.surrender_charge.after_term_default_charge_pct:.2%}",
            }
        )

        sched_df = pd.DataFrame(sched_rows)
        st.dataframe(sched_df, use_container_width=True, hide_index=True)

        # Optional: show assumptions keys (placeholders)
        with st.expander("Assumptions Keys (placeholders)"):
            a_rows = [
                ("mortality_table_key", spec.mortality_table_key),
                ("lapse_model_key", spec.lapse_model_key),
                ("withdrawal_behavior_key", spec.withdrawal_behavior_key),
                ("expense_assumption_key", spec.expense_assumption_key),
            ]
            a_df = pd.DataFrame(a_rows, columns=["Assumption", "Key"])
            st.dataframe(a_df, use_container_width=True, hide_index=True)

    except ProductCatalogError as e:
        st.error(f"Could not load product '{selected_product}'. {e}")
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        st.exception(e)