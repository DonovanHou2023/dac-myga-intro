# carvm_app.py
from __future__ import annotations

from pathlib import Path
from typing import Optional

import sys
import pandas as pd
import streamlit as st

# =========================================================
# Make "src/" importable on Streamlit Community Cloud
# =========================================================
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if SRC.exists():
    sys.path.insert(0, str(SRC))

from dac_myga_intro.engine.catalog import ProductCatalog
from dac_myga_intro.engine.inputs import IllustrationInputs
from dac_myga_intro.engine.illustration import run_illustration
from dac_myga_intro.engine.annuity_benefits import load_annuity_tables

# CARVM helpers (your refactor)
from dac_myga_intro.carvm.ui import pct_slider, safe_get_free_pct
from dac_myga_intro.carvm.annual_view import build_annual_view, truncate_to_term_years
from dac_myga_intro.carvm.mortality import load_mortality_table
from dac_myga_intro.carvm.reserve import compute_carvm_reserve_reverse_induction
from dac_myga_intro.carvm.styling import highlight_winning_path_row, highlight_winning_benefit_cells


# =========================================================
# App setup (match Illustration app style)
# =========================================================
st.set_page_config(page_title="Donovan's MYGA Intro Toolkit — CARVM", layout="wide")

st.markdown(
    """
    <style>
      /* Keep this minimal + consistent with your other app.
         Paste your shared CSS here if you maintain a common block. */

      /* Sidebar spacing tweaks */
      section[data-testid="stSidebar"] .stMarkdown h3 { margin-bottom: 0.25rem; }
      section[data-testid="stSidebar"] .stMarkdown h2 { margin-top: 0.25rem; }

      /* Make metrics a bit tighter */
      div[data-testid="stMetric"] { padding: 8px 10px; border-radius: 10px; }

      /* Dataframe container */
      .stDataFrame { border-radius: 12px; overflow: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

catalog = ProductCatalog(Path("src/dac_myga_intro/data/products"))

# Payout + mortality table roots
annuity_tables_root = Path("src/dac_myga_intro/data/annuity_tables")
ann_tables = load_annuity_tables(annuity_tables_root)
mort_root = Path("src/dac_myga_intro/data/annuity_tables")


# =========================================================
# Sidebar: brand header (match Illustration app)
# =========================================================
logo_black_path = Path("assets/logo_black.png")
cols = st.sidebar.columns([1, 3], vertical_alignment="center")
with cols[0]:
    if logo_black_path.exists():
        st.image(str(logo_black_path), width=64)
with cols[1]:
    st.markdown("### 多师的精算禅院")

st.sidebar.divider()


# =========================================================
# Sidebar: Inputs (LEFT = inputs only)
# =========================================================
st.sidebar.markdown("## CARVM Inputs")

product = st.sidebar.selectbox("Product", ["MYGA5", "MYGA7", "MYGA10"], index=0)
spec = catalog.get(product)

with st.sidebar.expander("Policy Inputs", expanded=True):
    premium = st.number_input("Premium", min_value=0.0, value=100000.0, step=1000.0)
    issue_age = st.number_input("Issue age", min_value=0, max_value=120, value=40, step=1)
    gender = st.selectbox("Gender", ["M", "F"], index=0)

with st.sidebar.expander("Rates", expanded=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        initial_rate = pct_slider("Init rate", 5.00, min_pct=0.0, max_pct=10.0, step_pct=0.05, key="init_rate")
    with c2:
        carvm_discount_rate = pct_slider("CARVM disc", 4.50, min_pct=0.0, max_pct=15.0, step_pct=0.05, key="disc_rate")
    with c3:
        annuity_discount_rate = pct_slider("Ann disc", 4.50, min_pct=0.0, max_pct=15.0, step_pct=0.05, key="ann_disc_rate")

with st.sidebar.expander("Annuitization Option", expanded=False):
    installment_years = st.number_input(
        "Installment years",
        min_value=1,
        max_value=30,
        value=10,
        step=1,
        help="Used for installment-certain annuitization PV (Option 1).",
    )

run_btn = st.sidebar.button("Run CARVM", type="primary")


# =========================================================
# Main header + consistent top description
# =========================================================
st.title("CARVM Reserve (MYGA) — POC")
st.caption("Toolkit module: CARVM reserve via two deterministic behavior paths + reverse induction.")


# =========================================================
# Right side descriptions (match your newer style)
# =========================================================
term_years = int(spec.term_years)
min_guar = float(spec.features.minimum_guaranteed_rate)

# For this phase you fixed the projection horizon to age 100
max_age = 100
projection_years = max(1, int(max_age - int(issue_age)))

free_pct = safe_get_free_pct(spec)
free_pct_note = "Read from YAML." if free_pct is not None else "Could not read from YAML; defaulted to 10%."
if free_pct is None:
    free_pct = 0.10

st.markdown(
    f"""
**Configuration**
- Projection horizon: **to age {max_age}** ⇒ **{projection_years} years**
- After term: illustration credits at **minimum guaranteed rate** from YAML: **{min_guar:.2%}**
- Paths used for CARVM max test: **No PW** and **Max FPW**
"""
)

with st.expander("Path definitions (for this POC)", expanded=False):
    st.markdown(
        f"""
- **No PW**: 0 partial withdrawals every year.
- **Max FPW**: free-withdrawal % = **{free_pct:.2%}** ({free_pct_note}), taken at **BOY** each year while surrender charges apply (1..{term_years}).
- Benefits (death/surrender/annuitization/continuation) use **EOY** values.
- Annuitization is reported as PVs:
  - `Installment PV` (no mortality)
  - `Single Life PV` (2012 IAM mortality)
  - `Annuitization Benefit` = max of the two PVs
"""
    )

st.divider()


# =========================================================
# Run (store in session_state)
# =========================================================
if run_btn:
    qx_by_age = load_mortality_table(str(gender), mort_root=mort_root)

    # No PW
    inp_no_pw = IllustrationInputs(
        product_code=product,
        premium=float(premium),
        issue_age=int(issue_age),
        gender=str(gender),
        initial_rate=float(initial_rate),
        renewal_rate=float(min_guar),  # post-term uses min guar (no renewal input)
        projection_years=int(projection_years),
        withdrawal_method="pct_of_boy_av",
        withdrawal_value=0.0,
        mva_initial_index_rate=None,
        mva_current_index_rate=None,
        mva_months_remaining_override=None,
        installment_years=int(installment_years),
    )

    # Max FPW
    inp_max_fpw = IllustrationInputs(
        product_code=product,
        premium=float(premium),
        issue_age=int(issue_age),
        gender=str(gender),
        initial_rate=float(initial_rate),
        renewal_rate=float(min_guar),
        projection_years=int(projection_years),
        withdrawal_method="pct_of_boy_av",
        withdrawal_value=float(free_pct),
        mva_initial_index_rate=None,
        mva_current_index_rate=None,
        mva_months_remaining_override=None,
        installment_years=int(installment_years),
    )

    df_a = run_illustration(catalog, inp_no_pw)
    df_b = run_illustration(catalog, inp_max_fpw)

    st.session_state["carvm_df_a"] = df_a
    st.session_state["carvm_df_b"] = df_b
    st.session_state["carvm_qx_by_age"] = qx_by_age
    st.session_state["carvm_inputs"] = {
        "product": product,
        "premium": float(premium),
        "issue_age": int(issue_age),
        "gender": str(gender),
        "initial_rate": float(initial_rate),
        "carvm_discount_rate": float(carvm_discount_rate),
        "annuity_discount_rate": float(annuity_discount_rate),
        "projection_years": int(projection_years),
        "installment_years": int(installment_years),
        "term_years": int(term_years),
        "free_pct": float(free_pct),
        "max_age": int(max_age),
        "min_guar": float(min_guar),
    }


# =========================================================
# Display (if results exist)
# =========================================================
df_a = st.session_state.get("carvm_df_a")
df_b = st.session_state.get("carvm_df_b")
inp_state = st.session_state.get("carvm_inputs")
qx_by_age = st.session_state.get("carvm_qx_by_age")

if df_a is None or df_b is None or inp_state is None or qx_by_age is None:
    st.info("Set inputs in the left sidebar and click **Run CARVM**.")
    st.stop()

# Annualize projections
annual_a = build_annual_view(df_a)

# Max FPW shown only through surrender charge period (term)
annual_b_full = build_annual_view(df_b)
annual_b = truncate_to_term_years(annual_b_full, term_years=inp_state["term_years"])

# Compute reserves by reverse induction
carvm_a = compute_carvm_reserve_reverse_induction(
    annual_a,
    issue_age=inp_state["issue_age"],
    carvm_discount_rate=inp_state["carvm_discount_rate"],
    annuity_discount_rate=inp_state["annuity_discount_rate"],
    installment_years=inp_state["installment_years"],
    ann_tables=ann_tables,
    qx_by_age=qx_by_age,
    gender=inp_state["gender"],
    last_year_continuation_basis="AV",
)

carvm_b = compute_carvm_reserve_reverse_induction(
    annual_b,
    issue_age=inp_state["issue_age"],
    carvm_discount_rate=inp_state["carvm_discount_rate"],
    annuity_discount_rate=inp_state["annuity_discount_rate"],
    installment_years=inp_state["installment_years"],
    ann_tables=ann_tables,
    qx_by_age=qx_by_age,
    gender=inp_state["gender"],
    last_year_continuation_basis="CSV",
)

reserve_a = float(carvm_a.loc[0, "Reserve (BOY)"]) if len(carvm_a) else 0.0
reserve_b = float(carvm_b.loc[0, "Reserve (BOY)"]) if len(carvm_b) else 0.0
reserve = max(reserve_a, reserve_b)
winner_path = "No PW" if reserve_a >= reserve_b else "Max FPW"


# ---- KPIs (consistent block style) ----
k1, k2, k3, k4 = st.columns(4)
k1.metric("Winning Path", winner_path)
k2.metric("Init rate", f"{inp_state['initial_rate']:.2%}")
k3.metric("CARVM disc", f"{inp_state['carvm_discount_rate']:.2%}")
k4.metric("CARVM Reserve (BOY Y1)", f"{reserve:,.2f}")

st.divider()


# ---- Reserve by path (highlight winner) ----
st.subheader("Reserve by Path (reverse induction)")
summary_tbl = pd.DataFrame(
    [
        {"Path": "No PW", "Reserve (BOY Y1)": reserve_a},
        {"Path": "Max FPW", "Reserve (BOY Y1)": reserve_b},
    ]
)
st.dataframe(
    highlight_winning_path_row(summary_tbl, winner_path).format({"Reserve (BOY Y1)": "{:,.2f}"}),
    width="stretch",
    height=120,
)

st.divider()


# ---- Path details ----
st.subheader("Path Details (annual projection + benefits + reserve)")
path_choice = st.selectbox("Select a path to view", ["No PW", "Max FPW"], index=0)
show = carvm_a.copy() if path_choice == "No PW" else carvm_b.copy()

# Clean attained age formatting
if "Attained Age" in show.columns:
    show["Attained Age"] = pd.to_numeric(show["Attained Age"], errors="coerce").round().astype("Int64")

default_cols = [
    "Policy Year",
    "Attained Age" if "Attained Age" in show.columns else None,
    "AV_BOY",
    "AV_EOY",
    "CSV_EOY" if "CSV_EOY" in show.columns else None,
    "WD",
    "Death Benefit",
    "Surrender Benefit",
    "Installment PV",
    "Single Life PV",
    "Annuitization Benefit",
    "Continuation Benefit",
    "Maximum Benefit",
    "Winning Benefit",
    "Reserve (BOY)",
]
default_cols = [c for c in default_cols if c is not None and c in show.columns]

cols_to_show = st.multiselect(
    "Columns to display",
    options=list(show.columns),
    default=default_cols,
)

fmt_map = {
    "AV_BOY": "{:,.2f}",
    "AV_EOY": "{:,.2f}",
    "CSV_EOY": "{:,.2f}",
    "WD": "{:,.2f}",
    "Death Benefit": "{:,.2f}",
    "Surrender Benefit": "{:,.2f}",
    "Installment PV": "{:,.2f}",
    "Single Life PV": "{:,.2f}",
    "Annuitization Benefit": "{:,.2f}",
    "Continuation Benefit": "{:,.2f}",
    "Maximum Benefit": "{:,.2f}",
    "Reserve (BOY)": "{:,.2f}",
}

view = show[cols_to_show].copy()
styler = highlight_winning_benefit_cells(view).format({k: v for k, v in fmt_map.items() if k in view.columns})
st.dataframe(styler, width="stretch", height=520)

# ---- Chart ----
st.subheader("Quick chart")
y_series = st.multiselect(
    "Select series to plot",
    options=[
        c
        for c in [
            "Reserve (BOY)",
            "Maximum Benefit",
            "Annuitization Benefit",
            "Surrender Benefit",
            "Death Benefit",
            "AV_EOY",
            "WD",
        ]
        if c in show.columns
    ],
    default=[c for c in ["Reserve (BOY)", "Maximum Benefit"] if c in show.columns],
)
if y_series:
    chart_df = show[["Policy Year"] + y_series].set_index("Policy Year")
    st.line_chart(chart_df, height=320)

st.divider()

with st.expander("Notes / Implementation assumptions", expanded=False):
    st.markdown(
        f"""
- Projection horizon fixed to age **{inp_state["max_age"]}** ⇒ `{inp_state["projection_years"]}` years.
- Rate after term uses product minimum guaranteed rate from YAML: **{inp_state["min_guar"]:.2%}**.
- `WD` is the **BOY** withdrawal amount (month 1), not the annual sum.
- Max FPW view is truncated to **term** `{inp_state["term_years"]}` years.
- Winning benefit cell highlight is based on: Death vs Surrender vs Annuitization vs Continuation.
"""
    )