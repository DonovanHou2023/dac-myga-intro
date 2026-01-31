from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import numpy as np
import pandas as pd
import streamlit as st
import numpy_financial as npf 


import sys
# Make "src/" importable on Streamlit Community Cloud
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if SRC.exists():
    sys.path.insert(0, str(SRC))

from dac_myga_intro.engine.catalog import ProductCatalog
from dac_myga_intro.engine.inputs import IllustrationInputs
from dac_myga_intro.engine.illustration import run_illustration


# -----------------------
# Helpers
# -----------------------
def select_columns_by_prefix(df: pd.DataFrame, prefixes: List[str]) -> pd.DataFrame:
    cols = [c for c in df.columns if any(c.startswith(p) for p in prefixes)]
    return df[cols]


def style_by_prefix(df: pd.DataFrame) -> pd.io.formats.style.Styler:
    """
    Background color by segment prefix.
    """
    def color_for_col(col_name: str) -> str:
        if col_name.startswith("mva_"):
            return "background-color: #ffe5e5;"  # light red
        if col_name.startswith("wd_"):
            return "background-color: #e8f5ff;"  # light blue
        if col_name.startswith("csv_"):
            return "background-color: #eefbea;"  # light green
        if col_name.startswith("meta_"):
            return "background-color: #f2f2f2;"  # light gray
        if col_name.startswith("gf_"):
            return "background-color: #efe9ff;"  # soft light purple
        if col_name.startswith("av_"):
            return "background-color: #fff7e6;"  # light warm tint
        return ""

    def style_col(s: pd.Series) -> list[str]:
        css = color_for_col(str(s.name))
        return [css] * len(s)

    return df.style.apply(style_col, axis=0)


def _is_rate_col(col: str) -> bool:
    """
    Heuristics: stored as decimals, displayed as % with 2 decimals.
    """
    explicit = {
        "meta_annual_rate",
        "wd_surrender_charge_pct",
        "mva_factor",
        "wd_mva_factor",
        "csv_sc_pct_used",
        "csv_mva_factor_used",
    }
    if col in explicit:
        return True

    if col.endswith("_pct"):
        return True
    if col.endswith("_factor"):
        return True
    if "rate" in col and not col.startswith(("meta_policy_", "meta_projection_")):
        return True

    return False


def build_format_map(df: pd.DataFrame) -> dict[str, str]:
    """
    Column name -> format spec for pandas Styler.format
    """
    fmt: dict[str, str] = {}
    amount_prefixes = ("av_", "wd_", "gf_", "csv_")

    for c in df.columns:
        # Percent formatting
        if _is_rate_col(c):
            fmt[c] = "{:.2%}"
            continue

        # Integer-ish metadata: show as int without decimals
        if c.startswith("meta_") and pd.api.types.is_integer_dtype(df[c]):
            fmt[c] = "{:d}"
            continue

        # Amount formatting
        if c.startswith(amount_prefixes):
            if pd.api.types.is_bool_dtype(df[c]):
                continue
            if pd.api.types.is_numeric_dtype(df[c]):
                fmt[c] = "{:,.2f}"
            continue

        # Other floats default
        if pd.api.types.is_float_dtype(df[c]):
            fmt[c] = "{:,.2f}"

    return fmt


def style_and_format(df: pd.DataFrame) -> pd.io.formats.style.Styler:
    styler = style_by_prefix(df)
    styler = styler.format(build_format_map(df))
    return styler


def dict_to_markdown_table(d: dict, key_col: str = "Field", val_col: str = "Value") -> str:
    rows = [f"| {k} | {v} |" for k, v in d.items()]
    header = f"| {key_col} | {val_col} |\n|---|---|\n"
    return header + "\n".join(rows)


def pct_slider_sidebar(
    label: str,
    *,
    default_pct: float,
    min_pct: float = 0.0,
    max_pct: float = 10.0,
    step_pct: float = 0.05,
    help_text: str | None = None,
    key: str | None = None,
) -> float:
    """Shows percent with 2 decimals, returns decimal (e.g., 4.65% -> 0.0465)."""
    v_pct = st.slider(
        label,
        min_value=float(min_pct),
        max_value=float(max_pct),
        value=float(default_pct),
        step=float(step_pct),
        format="%.2f%%",
        help=help_text,
        key=key,
    )
    return v_pct / 100.0


def np_irr_monthly(cashflows: list[float]) -> Optional[float]:
    """
    Returns monthly IRR (decimal), or None if IRR cannot be computed.
    """
    try:
        r = npf.irr(np.array(cashflows, dtype=float))
        if r is None or np.isnan(r):
            return None
        return float(r)
    except Exception as e:
        # TEMPORARY: surface the error while debugging
        print("IRR error:", e)
        return None


def annualize_monthly_rate(r_m: float) -> float:
    return (1.0 + r_m) ** 12 - 1.0


# -----------------------
# App setup
# -----------------------
st.set_page_config(page_title="Donovan's MYGA Intro Toolkit", layout="wide")

st.markdown(
    """
    <style>
    /* --- Sidebar background --- */
    section[data-testid="stSidebar"]{
        background: #eef4ff !important;              /* soft blue wash */
        border-right: 1px solid #dbe7ff !important;
    }

    /* --- Make each expander look like a card (big visual win) --- */
    section[data-testid="stSidebar"] div[data-testid="stExpander"] details {
        background: #f5f9ff !important;              /* slightly lighter than sidebar */
        border: 1px solid #dbe7ff !important;
        border-radius: 14px !important;
        box-shadow: 0 1px 0 rgba(15, 23, 42, 0.03) !important;
        margin-bottom: 10px !important;
        overflow: hidden;
    }

    /* Expander header */
    section[data-testid="stSidebar"] div[data-testid="stExpander"] summary {
        padding: 10px 12px !important;
        font-weight: 800 !important;
        color: #0f172a !important;
    }

    /* Expander content padding */
    section[data-testid="stSidebar"] div[data-testid="stExpander"] details > div {
        padding: 8px 12px 12px 12px !important;
    }

    /* --- Widgets: soft tinted, not white blocks --- */
    section[data-testid="stSidebar"] input,
    section[data-testid="stSidebar"] textarea,
    section[data-testid="stSidebar"] select,
    section[data-testid="stSidebar"] [data-baseweb="select"] > div,
    section[data-testid="stSidebar"] [data-baseweb="input"] > div {
        background: #f2f7ff !important;              /* soft tint */
        border: 1px solid #cfe0ff !important;
        border-radius: 12px !important;
        color: #0f172a !important;
    }

    /* Hover */
    section[data-testid="stSidebar"] input:hover,
    section[data-testid="stSidebar"] textarea:hover,
    section[data-testid="stSidebar"] [data-baseweb="select"] > div:hover,
    section[data-testid="stSidebar"] [data-baseweb="input"] > div:hover {
        border-color: #b7d0ff !important;
    }

    /* Focus ring (primary blue) */
    section[data-testid="stSidebar"] input:focus,
    section[data-testid="stSidebar"] textarea:focus,
    section[data-testid="stSidebar"] [data-baseweb="select"] > div:focus-within,
    section[data-testid="stSidebar"] [data-baseweb="input"] > div:focus-within {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15) !important;
        outline: none !important;
    }

    /* Sidebar divider softer */
    section[data-testid="stSidebar"] hr {
        border-top: 1px solid #dbe7ff !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

catalog = ProductCatalog(Path("src/dac_myga_intro/data/products"))

# -----------------------
# Sidebar: brand header
# -----------------------
logo_black_path = Path("assets/logo_black.png")
cols = st.sidebar.columns([1, 3], vertical_alignment="center")
with cols[0]:
    if logo_black_path.exists():
        st.image(str(logo_black_path), width=44)
with cols[1]:
    st.markdown("### 多师的精算禅院")

st.sidebar.divider()

# -----------------------
# Sidebar: Product selection
# -----------------------
st.sidebar.markdown("## Product Selection")
product = st.sidebar.selectbox("Product", ["MYGA5", "MYGA7", "MYGA10"], index=0)

spec = catalog.get(product)

default_projection_years = 15
default_issue_age = 40
default_initial_rate = 5.00
default_renewal_rate = 2.00

# -----------------------
# Sidebar: Illustration parameters
# -----------------------
st.sidebar.markdown("## Illustration Parameters")

with st.sidebar.expander("Generic Parameters", expanded=True):
    premium = st.number_input("Premium", min_value=0.0, value=100000.0, step=1000.0)

    projection_years = st.number_input(
        "Projection length (years)",
        min_value=1,
        max_value=50,
        value=int(default_projection_years),
        step=1,
        help="How many years to project. If greater than term, renewal rate applies after term.",
    )

    issue_age = st.number_input(
        "Issue age",
        min_value=0,
        max_value=120,
        value=default_issue_age,
        step=1,
        help="Used for annuitization calculations later.",
    )

    gender = st.selectbox("Gender", ["M", "F"], index=0)

with st.sidebar.expander("Crediting Rate", expanded=False):
    initial_rate = pct_slider_sidebar("Initial crediting rate (annual)", default_pct=default_initial_rate, key="initial_rate")
    renewal_rate = pct_slider_sidebar(
        "Renewal rate (annual)",
        default_pct=default_renewal_rate,
        help_text="Used after term if projection length exceeds term.",
        key="renewal_rate",
    )

with st.sidebar.expander("Withdrawals", expanded=False):
    wd_method = st.selectbox(
        "Partial withdrawal method",
        ["pct_of_boy_av", "fixed_amount", "prior_year_interest_credited"],
        index=1,
        key="wd_method",
    )
    if wd_method == "pct_of_boy_av":
        wd_value_pct = st.slider(
            "Withdrawal % of BOY AV (each year, starting year 2)",
            min_value=0.0, max_value=30.0, value=10.0, step=0.5, format="%.1f%%", key="wd_pct",
        )
        wd_value = wd_value_pct / 100.0
    elif wd_method == "fixed_amount":
        wd_value = st.number_input(
            "Withdrawal amount (each year, starting year 2)",
            min_value=0.0, value=0.0, step=500.0, key="wd_amt",
        )
    else:
        wd_value = 0.0
        st.caption("Uses prior-year interest credited (no value input).")

with st.sidebar.expander("MVA", expanded=False):
    enable_mva = st.checkbox("Enable MVA inputs", value=True, key="enable_mva")

    mva_initial_index_rate = None
    mva_current_index_rate = None
    mva_months_remaining_override = None

    if enable_mva:
        mva_initial_index_rate = pct_slider_sidebar("MVA initial index rate X (annual)", default_pct=2.00, key="mva_x")
        mva_current_index_rate = pct_slider_sidebar("MVA current index rate Y (annual)", default_pct=4.00, key="mva_y")

        use_override = st.checkbox("Override months remaining N", value=False, key="mva_override_flag")
        if use_override:
            mva_months_remaining_override = st.number_input("N months remaining", min_value=0, value=12, step=1, key="mva_n")


def run_and_store() -> None:
    inp = IllustrationInputs(
        product_code=product,
        premium=float(premium),
        issue_age=int(issue_age),
        gender=str(gender),

        initial_rate=float(initial_rate),
        renewal_rate=float(renewal_rate),

        projection_years=int(projection_years),

        withdrawal_method=wd_method,
        withdrawal_value=float(wd_value),

        mva_initial_index_rate=mva_initial_index_rate,
        mva_current_index_rate=mva_current_index_rate,
        mva_months_remaining_override=mva_months_remaining_override,
    )
    df = run_illustration(catalog, inp)
    st.session_state["illustration_df"] = df


# -----------------------
# Main area tabs
# -----------------------
tab_product, tab_illustration, tab_summary = st.tabs(["Product", "Illustration", "Summary"])


# =========================================================
# PRODUCT TAB (expanded / complete)
# =========================================================
with tab_product:
    st.header(f"Product Specification: {product}")

    # -----------------------
    # 1) Top summary table
    # -----------------------
    st.markdown(
        "| Field | Value | Explanation |\n"
        "|---|---:|---|\n"
        f"| Schema Version | {spec.schema_version} | YAML schema version used by the engine to validate/parse product specs. |\n"
        f"| Product Code | {spec.product_code} | Product identifier. |\n"
        f"| Term (years) | {spec.term_years} | Guaranteed term length. |\n"
        f"| Minimum Guaranteed Rate | {spec.features.minimum_guaranteed_rate:.2%} | Contract minimum rate used in floor logic (e.g., NFF/GMV style). |\n",
        unsafe_allow_html=True,
    )

    st.divider()

    # -----------------------
    # 2) Product Features (from YAML)
    # -----------------------
    st.subheader("Product Features (from YAML)")

    # ---- MVA ----
    mva = spec.features.mva
    st.markdown("### MVA (Market Value Adjustment)")
    st.markdown(
        "| Field | Value |\n"
        "|---|---|\n"
        f"| enabled | `{bool(mva.enabled)}` |\n"
        f"| benchmark_index | `{None if mva.benchmark_index is None else mva.benchmark_index.code}` |\n"
        f"| benchmark_type | `{None if mva.benchmark_index is None else mva.benchmark_index.type}` |\n"
        f"| benchmark_description | `{None if mva.benchmark_index is None else (mva.benchmark_index.description or '—')}` |\n",
        unsafe_allow_html=True,
    )

    with st.expander("MVA factor formula (engine)", expanded=False):
        st.latex(r"D = \left(\frac{1+X}{1+Y}\right)^{N/12} - 1")
        st.markdown(
            """
- **X** = initial benchmark index rate (input)  
- **Y** = current benchmark index rate (input)  
- **N** = months remaining in MVA period (computed or overridden)  

The engine computes **factor only** in `mva.py`; dollar impact is applied later in CSV.
"""
        )

    st.divider()

    # ---- Surrender Charge ----
    sc = spec.features.surrender_charge
    st.markdown("### Surrender Charge")

    sched = getattr(sc, "schedule", None) or {}
    if sched:
        sched_rows = "\n".join([f"| {yr} | {pct:.2%} |" for yr, pct in sorted(sched.items())])
        st.markdown("| Policy Year | Surrender Charge % |\n|---:|---:|\n" + sched_rows)
    else:
        st.info("No surrender charge schedule found in YAML (schedule is empty).")

    # after-term behavior (your YAML has after_term.default_charge_pct)
    after_term_pct = getattr(sc, "after_term_default_charge_pct", None)
    if after_term_pct is None and hasattr(sc, "after_term"):
        # fallback if your spec object stores it nested
        after_term_pct = getattr(sc.after_term, "default_charge_pct", 0.0)

    st.markdown(
        f"- After-term default charge %: `{float(after_term_pct):.2%}`",
        unsafe_allow_html=True,
    )

    st.caption(
        "Implementation note: surrender charge % is treated as **policy-year based** (constant across months in that policy year), "
        "with a **term-end month override to 0%** (e.g., month 60 for MYGA5)."
    )

    st.divider()

    # ---- Free Partial Withdrawal ----
    fpw = spec.features.free_partial_withdrawal
    st.markdown("### Free Partial Withdrawal")

    st.markdown(
        "| Field | Value |\n"
        "|---|---|\n"
        f"| enabled | `{bool(fpw.enabled)}` |\n"
        f"| method | `{fpw.method}` |\n"
        f"| params | `{fpw.params}` |\n"
        f"| description | `{fpw.description if fpw.description else '—'}` |\n",
        unsafe_allow_html=True,
    )

    if fpw.enabled:
        with st.expander("Free withdrawal formula (engine)", expanded=False):
            if fpw.method == "pct_of_boy_account_value":
                pct = float(fpw.params.get("pct", 0.0))
                st.latex(r"FL_y = p \cdot AV_{y}^{BOY}")
                st.markdown(f"Where $$p = {pct:.2%}$$.")
            elif fpw.method == "prior_year_interest_credited":
                st.latex(r"FL_y = IC_{y-1}^{\\text{total}} \\quad (FL_1 = 0)")
            else:
                st.warning(f"Unknown free withdrawal method in YAML: `{fpw.method}`")

    st.divider()

    # ---- Guarantee Funds ----
    gf = spec.features.guarantee_funds
    st.markdown("### Guarantee Funds")

    # Protect against missing nodes
    mfv = gf.mfv
    pfv = gf.pfv

    st.markdown(
        "| Track | Base % of Premium | Rate (annual) | Rate years | Rate after years (annual) | Notes |\n"
        "|---|---:|---:|---:|---:|---|\n"
        f"| MFV | `{float(mfv.base_pct_of_premium):.2%}` | `initial_rate during term; min guaranteed after term` | — | — | Floor track (reduces by withdrawals only) |\n"
        f"| PFV | `{float(pfv.base_pct_of_premium):.2%}` | `{float(pfv.rate_annual):.2%}` | `{int(pfv.rate_years)}` | `{float(pfv.rate_after_years_annual):.2%}` | {pfv.description if getattr(pfv, 'description', None) else '—'} |\n",
        unsafe_allow_html=True,
    )

    st.caption(
        "Implementation note: MFV/PFV reduce by **withdrawal amount only** (not surrender charges or MVA), "
        "then credit monthly using their respective rate rules."
    )

    st.divider()

    # -----------------------
    # 3) Methodology quick reference (matches your engine)
    # -----------------------
    st.subheader("Methodology Quick Reference (Engine Order)")

    st.markdown(
        r"""
This is the monthly ordering used in `illustration.py`:

1) **MVA factor** (factor only)  
2) Snapshot BOP values  
3) **Withdrawals** (updates free budget; computes withdrawal penalty components)  
4) **Guarantee funds** (reduce by withdrawal only; then credit)  
5) **Account Value** (subtract withdrawal + penalty; then interest; then apply AV floor vs guarantee funds)  
6) **CSV** (full surrender at time t; uses free remaining; applies surrender charge then MVA; floors by guarantee funds)
"""
    )

    with st.expander("Core formulas (summary)", expanded=False):
        st.markdown("**Monthly interest conversion**")
        st.latex(r"i_t = (1+r_y)^{1/12} - 1")

        st.markdown("**Account Value roll-forward**")
        st.latex(r"AV_t^{post} = \max(0, AV_t^{B} - W_t - Penalty_t)")
        st.latex(r"IC_t = AV_t^{post} \cdot i_t")
        st.latex(r"AV_t^{E} = AV_t^{post} + IC_t")
        st.latex(r"AV_t^{E, floored} = \max(AV_t^{E}, \max(MFV_t^{E}, PFV_t^{E}))")

        st.markdown("**CSV calculation (full surrender)**")
        st.latex(r"A = AV_t^{E, floored}")
        st.latex(r"B = \min(A, FreeRemaining_t)")
        st.latex(r"Excess = \max(0, A - B)")
        st.latex(r"SC = Excess \cdot s_y")
        st.latex(r"S = \max(0, Excess - SC)")
        st.latex(r"MVA = S \cdot D(X,Y,N)")
        st.latex(r"CSV = \max(0, A - SC + MVA)")
        st.latex(r"CSV_{final} = \max(CSV, MFV_t^{E}, PFV_t^{E})")

    st.divider()

    # -----------------------
    # 4) Assumption keys
    # -----------------------
    st.subheader("Assumption Keys")

    keys_table = {
        "mortality_table_key": spec.mortality_table_key,
        "lapse_model_key": spec.lapse_model_key,
        "withdrawal_behavior_key": spec.withdrawal_behavior_key,
        "expense_assumption_key": spec.expense_assumption_key,
    }
    st.markdown(dict_to_markdown_table(keys_table), unsafe_allow_html=True)

# =========================================================
# ILLUSTRATION TAB
# =========================================================
with tab_illustration:
    
    st.header("Illustration Results")
    run = st.button("Run Illustration", type="primary", key="run_illustration_btn")
    if run:
        run_and_store()

    df = st.session_state.get("illustration_df", None)

    if df is None:
        st.info("Click **Run Illustration** to generate results.")
    else:
        with st.expander("Exhibits / Columns to show", expanded=True):
            st.caption("Default view shows Account Value + CSV. Add more exhibits below.")
            show_withdrawals = st.checkbox("Add withdrawal exhibits (wd_*)", value=False, key="show_wd")
            show_mva_cols = st.checkbox("Add MVA exhibits (mva_*)", value=False, key="show_mva")
            show_guarantee = st.checkbox("Add guarantee fund exhibits (gf_*)", value=False, key="show_gf")
            show_meta = st.checkbox("Add meta/time exhibits (meta_*)", value=False, key="show_meta")

        # IMPORTANT: your CSV is csv_* but final is `csv_final`
        prefixes = ["av_", "csv_"]
        if show_meta:
            prefixes += ["meta_"]
        if show_withdrawals:
            prefixes += ["wd_"]
        if show_mva_cols:
            prefixes += ["mva_"]
        if show_guarantee:
            prefixes += ["gf_"]

        view_df = select_columns_by_prefix(df, prefixes)

        st.dataframe(
            style_and_format(view_df),
            width="stretch",
            height=560,
        )

        st.download_button(
            "Download current view (CSV)",
            data=view_df.to_csv(index=False).encode("utf-8"),
            file_name=f"{product.lower()}_illustration_view.csv",
            mime="text/csv",
        )


# =========================================================
# SUMMARY TAB (NEW)
# =========================================================
with tab_summary:
    st.header("Summary")

    # Run button in Summary tab triggers the same run as Illustration tab
    run2 = st.button("Run Illustration", type="primary", key="run_summary_btn")
    if run2:
        run_and_store()

    df = st.session_state.get("illustration_df", None)

    if df is None:
        st.info("Run the illustration to populate summary charts.")
    else:
        xcol = "meta_policy_month"
        if xcol not in df.columns:
            st.warning("Expected `meta_policy_month` not found. Check illustration outputs.")
        else:
            # -----------------------------
            # 2x2 layout
            # -----------------------------
            top_left, top_right = st.columns(2, vertical_alignment="top")
            bot_left, bot_right = st.columns(2, vertical_alignment="top")

            # =========================
            # (A) Line chart: multi-select series
            # =========================
            with top_left:
                st.subheader("Value over time")

                SERIES_MAP = {
                    "Account Value (AV EOP)": "av_eop",
                    "Cash Surrender Value (CSV final)": "csv_final",
                    "CSV before floors": "csv_before_floors",
                    "Guarantee Fund 1 (MFV EOP)": "gf_mfv_eop",
                    "Guarantee Fund 2 (PFV EOP)": "gf_pfv_eop",
                }

                # Only keep series that exist in df
                available_series = [k for k, v in SERIES_MAP.items() if v in df.columns]
                default_series = [s for s in ["Account Value (AV EOP)", "Cash Surrender Value (CSV final)"] if s in available_series]

                line_choices = st.multiselect(
                    "Select series (multi-select)",
                    available_series,
                    default=default_series if default_series else available_series[:1],
                    key="summary_line_choices",
                )

                if not line_choices:
                    st.info("Select at least one series to plot.")
                else:
                    cols = [xcol] + [SERIES_MAP[c] for c in line_choices]
                    chart_df = df[cols].copy()
                    chart_df = chart_df.rename(columns={xcol: "Policy Month"})
                    # Rename y cols to friendly labels
                    for friendly in line_choices:
                        chart_df = chart_df.rename(columns={SERIES_MAP[friendly]: friendly})

                    st.line_chart(chart_df, x="Policy Month", y=line_choices, height=320)

            # =========================
            # (B) Bar chart: multi-select metrics
            # =========================
            with top_right:
                st.subheader("Monthly cash impacts (bars)")

                # Convention:
                # - withdrawal and penalty shown NEGATIVE (reduce AV)
                # - interest credit shown POSITIVE
                BAR_MAP = {
                    "Partial withdrawal taken (negative)": ("wd_withdrawal_amount", -1.0),
                    "Penalty on withdrawal (negative)": ("wd_penalty_total", -1.0),
                    "Interest credit (positive)": ("av_interest_credit", 1.0),
                }

                available_bars = [k for k, (col, _) in BAR_MAP.items() if col in df.columns]
                default_bars = [b for b in available_bars if "Interest" in b or "withdrawal" in b.lower()]
                default_bars = default_bars[:2] if default_bars else available_bars[:1]

                bar_choices = st.multiselect(
                    "Select metrics (multi-select)",
                    available_bars,
                    default=default_bars,
                    key="summary_bar_choices",
                    help="Withdrawals/penalties shown as negative; interest as positive.",
                )

                if not bar_choices:
                    st.info("Select at least one metric to plot.")
                else:
                    bar_df = pd.DataFrame({"Policy Month": df[xcol].astype(int)})

                    for label in bar_choices:
                        col, sign = BAR_MAP[label]
                        bar_df[label] = df[col].astype(float) * float(sign)

                    # Streamlit bar_chart expects index for x-axis
                    st.bar_chart(bar_df.set_index("Policy Month"), height=320)

            # =========================
            # (C) Outcome table at termination (5/10/15 years)
            # =========================
            with bot_left:
                st.subheader("Contract value at termination dates")

                prem = float(premium)
                proj_years = int(projection_years)
                max_month = proj_years * 12

                wd_col = "wd_withdrawal_amount"
                csv_col = "csv_final"

                years_to_show = [5, 10, 15]
                years_to_show = [y for y in years_to_show if y * 12 <= max_month]

                rows = []
                for y in years_to_show:
                    m = y * 12
                    sub = df[df[xcol] == m]
                    if sub.empty:
                        continue

                    r = sub.iloc[-1]
                    total_wd = float(df.loc[df[xcol] <= m, wd_col].sum()) if wd_col in df.columns else 0.0
                    csv_at = float(r[csv_col]) if csv_col in df.columns else float("nan")
                    total_received = total_wd + csv_at

                    rows.append(
                        {
                            "Horizon (years)": y,
                            "Premium (outflow)": -prem,
                            "Total withdrawals (inflow)": total_wd,
                            "CSV at termination (inflow)": csv_at,
                            "Total value received": total_received,
                        }
                    )

                if not rows:
                    st.info("No horizon rows available (projection too short or missing columns).")
                else:
                    out_df = pd.DataFrame(rows)
                    st.dataframe(style_and_format(out_df), width="stretch", height=260)

            # =========================
            # (D) Annualized IRR only (5/10/15 years)
            # =========================
            with bot_right:
                st.subheader("Annualized IRR at termination dates")

                prem = float(premium)
                proj_years = int(projection_years)
                max_month = proj_years * 12

                wd_col = "wd_withdrawal_amount"
                csv_col = "csv_final"

                years_to_show = [5, 10, 15]
                years_to_show = [y for y in years_to_show if y * 12 <= max_month]

                irr_rows = []
                for y in years_to_show:
                    m_end = y * 12
                    sub_end = df[df[xcol] == m_end]
                    if sub_end.empty:
                        continue
                    r_end = sub_end.iloc[-1]

                    # Monthly cashflows: month0=-premium; month1..m_end=+withdrawals; last month += csv_final
                    cashflows = [-prem]
                    if wd_col in df.columns:
                        for mm in range(1, m_end + 1):
                            amt = float(df.loc[df[xcol] == mm, wd_col].sum())
                            cashflows.append(amt)
                    else:
                        cashflows.extend([0.0] * m_end)

                    csv_at = float(r_end[csv_col]) if csv_col in df.columns else 0.0
                    cashflows[-1] = float(cashflows[-1]) + csv_at

                    # IRR monthly -> annualize
                    irr_m = np_irr_monthly(cashflows)
                    irr_a = annualize_monthly_rate(irr_m) if irr_m is not None else None

                    irr_rows.append(
                        {
                            "Horizon (years)": y,
                            "Annualized IRR": irr_a if irr_a is not None else np.nan,
                        }
                    )

                if not irr_rows:
                    st.info("IRR cannot be computed (missing columns or insufficient projection).")
                else:
                    irr_df = pd.DataFrame(irr_rows)
                    st.dataframe(
                        irr_df.style.format({"Annualized IRR": "{:.2%}"}),
                        width="stretch",
                        height=260,
                    )