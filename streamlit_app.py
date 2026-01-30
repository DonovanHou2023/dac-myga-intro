from __future__ import annotations

from pathlib import Path
from typing import List

import streamlit as st
import pandas as pd

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
            return "background-color: #f2f2f2;"  # light gray (NEW)
        if col_name.startswith("gf_"):
            return "background-color: #efe9ff;"  # soft light purple (NEW)
        return ""

    def style_col(s: pd.Series) -> list[str]:
        css = color_for_col(str(s.name))
        return [css] * len(s)

    return df.style.apply(style_col, axis=0)


def build_format_map(df: pd.DataFrame) -> dict[str, str]:
    """
    Column name -> format spec for pandas Styler.format

    Rules:
      - rate-type columns (decimal stored) -> percent with 2 decimals
      - amount-type columns -> commas + 2 decimals
    """
    fmt: dict[str, str] = {}

    # Columns that are stored as decimals but should be displayed as %
    explicit_rate_cols = {
        "meta_annual_rate",
        "wd_surrender_charge_pct",
        "mva_factor",
    }

    amount_prefixes = ("av_", "csv_", "gf_", "wd_")  # most wd_* are dollars except wd_surrender_charge_pct above

    for c in df.columns:
        # Percent formatting
        if c in explicit_rate_cols:
            fmt[c] = "{:.2%}"
            continue

        # Amount formatting (commas + 2dp)
        if c.startswith(amount_prefixes):
            fmt[c] = "{:,.2f}"
            continue

        # Other floats default to 2dp with commas
        if pd.api.types.is_float_dtype(df[c]):
            fmt[c] = "{:,.2f}"

    return fmt


def style_and_format(df: pd.DataFrame) -> pd.io.formats.style.Styler:
    """
    Apply background colors + number formatting.
    """
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


# -----------------------
# App setup
# -----------------------
st.set_page_config(page_title="Donovan's MYGA Intro Toolkit", layout="wide")

st.markdown(
    """
    <style>
    /* Make Streamlit tab labels larger */
    button[data-baseweb="tab"] > div[data-testid="stMarkdownContainer"] > p {
        font-size: 24px !important;
        font-weight: 700 !important;
    }

    /* Make dataframe text larger */
    div[data-testid="stDataFrame"] * {
        font-size: 16px !important;
    }

    /* Slightly larger/bolder dataframe header */
    div[data-testid="stDataFrame"] thead tr th {
        font-size: 16px !important;
        font-weight: 700 !important;
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

# -----------------------
# Sidebar: Illustration parameters
# -----------------------
st.sidebar.markdown("## Illustration Parameters")

with st.sidebar.expander("Generic Parameters", expanded=True):
    premium = st.number_input("Premium", min_value=0.0, value=100000.0, step=1000.0)
    issue_age = st.number_input(
        "Issue age", min_value=0, max_value=120, value=60, step=1,
        help="Used for annuitization calculations later (and any age-based features).",
    )
    gender = st.selectbox("Gender", ["M", "F"], index=0, help="Used for annuitization factors later.")

with st.sidebar.expander("Crediting Rate", expanded=False):
    initial_rate = pct_slider_sidebar("Initial crediting rate (annual)", default_pct=5.00, key="initial_rate")
    renewal_rate = pct_slider_sidebar(
        "Renewal rate (annual)",
        default_pct=4.50,
        help_text="Used after the term if/when you extend projection beyond term.",
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
            min_value=0.0, value=5000.0, step=500.0, key="wd_amt",
        )
    else:
        wd_value = 0.0
        st.caption("Uses prior-year interest credited (no value input).")

with st.sidebar.expander("MVA", expanded=False):
    enable_mva = st.checkbox("Enable MVA inputs", value=False, key="enable_mva")

    mva_initial_index_rate = None
    mva_current_index_rate = None
    mva_months_remaining_override = None

    if enable_mva:
        mva_initial_index_rate = pct_slider_sidebar("MVA initial index rate X (annual)", default_pct=4.00, key="mva_x")
        mva_current_index_rate = pct_slider_sidebar("MVA current index rate Y (annual)", default_pct=5.00, key="mva_y")

        use_override = st.checkbox("Override months remaining N", value=False, key="mva_override_flag")
        if use_override:
            mva_months_remaining_override = st.number_input(
                "N months remaining", min_value=0, value=12, step=1, key="mva_n",
            )

# -----------------------
# Main area tabs
# -----------------------
tab_product, tab_illustration = st.tabs(["Product", "Illustration"])

with tab_product:
    spec = catalog.get(product)

    # =========================================================
    # MAIN SUMMARY TABLE (Field / Value / Explanation)
    # =========================================================
    st.markdown(
        "| Field | Value | Explanation |\n"
        "|---|---:|---|\n"
        f"| Schema Version | {spec.schema_version} | YAML schema version used by the engine to validate/parse product specs. |\n"
        f"| Product Code | {spec.product_code} | Product identifier (e.g., MYGA5 = 5-year guaranteed term). |\n"
        f"| Term (years) | {spec.term_years} | Guaranteed term length used for the base illustration horizon. |\n"
        f"| Minimum Guaranteed Rate | {spec.features.minimum_guaranteed_rate:.2%} | Contract minimum credited rate used in guarantee/floor logic (e.g., nonforfeiture). |\n",
        unsafe_allow_html=True,
    )

    st.divider()

    # =========================================================
    # MONTHLY ROLL-FORWARD METHODOLOGY
    # =========================================================
    st.subheader("Monthly Roll-Forward Methodology")

    st.markdown(
        r"""
Let:

- $$AV_{t}^{B}$$ = Account Value at beginning of month $$t$$  
- $$W_t$$ = Withdrawal taken in month $$t$$ (non-zero only for month 1 of each policy year, year $$\ge 2$$)  
- $$SC_t$$ = Surrender charge amount in month $$t$$  
- $$MVA_t$$ = Market value adjustment amount in month $$t$$ (optional)  
- $$r_y$$ = annual crediting rate applicable for the policy year containing month $$t$$  
- $$i_t$$ = monthly crediting rate derived from annual rate $$r_y$$

Monthly rate conversion:
""")
    st.latex(r"i_t = (1+r_y)^{1/12} - 1")

    st.markdown("Roll-forward equations:")
    st.latex(r"AV_t^{\text{post}} = AV_t^{B} - W_t - SC_t")
    st.latex(r"IC_t = AV_t^{\text{post}} \cdot i_t")
    st.latex(r"AV_t^{E} = AV_t^{\text{post}} + IC_t")

    st.markdown(
        r"""
Cash Surrender Value (v0 structure; floors added later):
""")
    st.latex(r"CSV_t = AV_t^{E} - SC_t + MVA_t")

    with st.expander("Numerical example (roll-forward)", expanded=False):
        st.markdown(
            r"""
Assume:

- $$AV_t^{B} = 100{,}000$$  
- $$W_t = 12{,}000$$  
- Excess portion subject to surrender charge = 2,000  
- Surrender charge rate = 6%  $$\Rightarrow SC_t = 2{,}000 \times 0.06 = 120$$  
- Annual rate $$r_y = 5\%$$

Monthly rate:
"""
        )
        st.latex(r"i_t = (1.05)^{1/12}-1 \approx 0.004074")

        st.markdown("Then:")
        st.latex(r"AV_t^{\text{post}} = 100{,}000 - 12{,}000 - 120 = 87{,}880")
        st.latex(r"IC_t = 87{,}880 \cdot 0.004074 \approx 358")
        st.latex(r"AV_t^{E} \approx 87{,}880 + 358 = 88{,}238")

    st.divider()

    # =========================================================
    # SURRENDER CHARGE
    # =========================================================
    st.subheader("Surrender Charge")

    st.markdown(
        r"""
Define:

- $$FL_y$$ = free withdrawal limit for policy year $$y$$  
- $$W_y$$ = withdrawal amount taken at the start of policy year $$y$$  
- $$E_y = \max(0, W_y - FL_y)$$ = excess amount  
- $$s_y$$ = surrender charge rate for policy year $$y$$

Surrender charge amount:
"""
    )
    st.latex(r"SC_y = E_y \cdot s_y")

    sched = spec.features.surrender_charge.schedule
    sched_rows = "\n".join([f"| {yr} | {pct:.2%} |" for yr, pct in sorted(sched.items())])
    st.markdown(
        "| Policy Year | Surrender Charge % |\n|---:|---:|\n" + sched_rows
    )
    st.markdown(
        f"- After-term default charge %: {spec.features.surrender_charge.after_term_default_charge_pct:.2%}"
    )

    with st.expander("Numerical example (surrender charge)", expanded=False):
        st.markdown(
            r"""
Assume:

- $$FL_y = 10{,}000$$
- $$W_y = 12{,}000$$  $$\Rightarrow E_y = 2{,}000$$
- $$s_y = 7\%$$

Then:
"""
        )
        st.latex(r"SC_y = 2{,}000 \cdot 0.07 = 140")

    st.divider()

    # =========================================================
    # FREE PARTIAL WITHDRAWAL
    # =========================================================
    st.subheader("Free Partial Withdrawal")

    fpw = spec.features.free_partial_withdrawal

    st.markdown(
        r"""
This provision defines the annual free limit $$FL_y$$ used to split withdrawals into free vs excess.

Supported methods (current):
"""
    )
    st.markdown(
        f"- enabled: {fpw.enabled}\n"
        f"- method: {fpw.method}\n"
        f"- params: {fpw.params}\n"
        f"- description: {fpw.description if fpw.description else '—'}"
    )

    if fpw.method == "pct_of_boy_account_value":
        pct = float(fpw.params.get("pct", 0.0))
        st.markdown("Formula (percent of BOY AV):")
        st.latex(r"FL_y = p \cdot AV_{y}^{BOY}")
        st.markdown(f"Where $$p = {pct:.2%}$$.")
    elif fpw.method == "prior_year_interest_credited":
        st.markdown("Formula (prior-year interest credited):")
        st.latex(r"FL_y = IC_{y-1}^{\text{total}} \quad\text{(and } FL_1=0\text{)}")

    with st.expander("Numerical example (free withdrawal split)", expanded=False):
        st.markdown(
            r"""
Assume percent-of-BOY method:

- $$AV_{y}^{BOY} = 100{,}000$$
- $$p=10\%$$  $$\Rightarrow FL_y = 10{,}000$$
- $$W_y = 12{,}000$$

Then:
"""
        )
        st.latex(r"E_y = \max(0, 12{,}000 - 10{,}000) = 2{,}000")

    st.divider()

    # =========================================================
    # MVA
    # =========================================================
    st.subheader("MVA (Market Value Adjustment)")

    mva = spec.features.mva
    st.markdown(
        f"- enabled: {mva.enabled}\n"
        f"- benchmark_index: {None if mva.benchmark_index is None else mva.benchmark_index.code}"
    )

    st.markdown(
        r"""
Let:

- $$X$$ = initial benchmark index rate  
- $$Y$$ = current benchmark index rate  
- $$N$$ = months remaining in the MVA period  
- $$S$$ = amount subject to MVA

A common structure is:

1) derive an MVA factor $$F(X,Y,N)$$  
2) apply it to the amount subject to MVA:

"""
    )

    st.latex(r"MVA = S \cdot F(X,Y,N)")

    st.markdown(
        r"""
In your implementation, the **amount subject** is determined by contract components:

- $$A$$ = surrendered amount  
- $$B$$ = portion not subject to surrender charge (free portion)  
- $$C$$ = surrender charge amount  

Then a typical structure is:
"""
    )
    st.latex(r"S = \max(0, A - B - C)")

    with st.expander("Numerical example (MVA structure)", expanded=False):
        st.markdown(
            r"""
Assume:
- $$A=12{,}000$$, $$B=10{,}000$$, $$C=120$$

Then:
"""
        )
        st.latex(r"S=\max(0, 12{,}000-10{,}000-120)=1{,}880")
        st.markdown(
            r"Then $$MVA = 1{,}880 \cdot F(X,Y,N)$$ once $$F$$ is computed."
        )

    st.divider()

    # =========================================================
    # GUARANTEE FUNDS
    # =========================================================
    st.subheader("Guarantee Funds")

    gf = spec.features.guarantee_funds

    st.markdown(
        "| Track | Base % of Premium | Rate (annual) | Rate years | Rate after years (annual) |\n"
        "|---|---:|---:|---:|---:|\n"
        f"| MFV | {gf.mfv.base_pct_of_premium:.2%} | (term: initial rate; after term: min guaranteed) | — | — |\n"
        f"| PFV | {gf.pfv.base_pct_of_premium:.2%} | {gf.pfv.rate_annual:.2%} | {gf.pfv.rate_years} | {gf.pfv.rate_after_years_annual:.2%} |\n",
        unsafe_allow_html=True,
    )

    st.markdown(
        r"""
Let:

- $$P$$ = premium
- $$SU_t$$ = surrendered amount at time $$t$$ (withdrawal)
- $$MFV_t$$, $$PFV_t$$ = guarantee fund balances at time $$t$$
- $$j_t$$ = monthly rate for the guarantee fund track

Initialization:
"""
    )
    st.latex(r"MFV_0 = \alpha \cdot P")
    st.latex(r"PFV_0 = \beta \cdot P")

    st.markdown(
        r"""
Monthly roll-forward (conceptual):
"""
    )
    st.latex(r"MFV_t^{\text{post}} = \max(0, MFV_t - SU_t)")
    st.latex(r"PFV_t^{\text{post}} = \max(0, PFV_t - SU_t)")
    st.latex(r"MFV_{t+1} = MFV_t^{\text{post}} \cdot (1 + j_t^{MFV})")
    st.latex(r"PFV_{t+1} = PFV_t^{\text{post}} \cdot (1 + j_t^{PFV})")

    with st.expander("Numerical example (guarantee funds)", expanded=False):
        st.markdown(
            r"""
Assume:
- Premium $$P=100{,}000$$
- $$\alpha=87.5\%\Rightarrow MFV_0=87{,}500$$
- $$\beta=90.7\%\Rightarrow PFV_0=90{,}700$$
- First month surrender $$SU_1=5{,}000$$
- Monthly rate $$j=0.15\%$$

Then:
"""
        )
        st.latex(r"MFV_1 = (87{,}500-5{,}000)\cdot(1+0.0015)")
        st.latex(r"PFV_1 = (90{,}700-5{,}000)\cdot(1+0.0015)")

    st.divider()

    # =========================================================
    # ASSUMPTION KEYS
    # =========================================================
    st.subheader("Assumption Keys")

    keys_table = {
        "mortality_table_key": spec.mortality_table_key,
        "lapse_model_key": spec.lapse_model_key,
        "withdrawal_behavior_key": spec.withdrawal_behavior_key,
        "expense_assumption_key": spec.expense_assumption_key,
    }
    st.markdown(dict_to_markdown_table(keys_table), unsafe_allow_html=True)


with tab_illustration:
    st.header("Product Illustration")

    # Run button
    run = st.button("Run Illustration", type="primary")

    if run:
        inp = IllustrationInputs(
            product_code=product,
            premium=float(premium),
            initial_rate=float(initial_rate),
            renewal_rate=float(renewal_rate),
            withdrawal_method=wd_method,
            withdrawal_value=float(wd_value),
            mva_initial_index_rate=mva_initial_index_rate,
            mva_current_index_rate=mva_current_index_rate,
            mva_months_remaining_override=mva_months_remaining_override,
            issue_age=int(issue_age),
            gender=str(gender),
        )
        df = run_illustration(catalog, inp)
        st.session_state["illustration_df"] = df

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
            use_container_width=True,
            height=560,
        )

        st.download_button(
            "Download current view (CSV)",
            data=view_df.to_csv(index=False).encode("utf-8"),
            file_name=f"{product.lower()}_illustration_view.csv",
            mime="text/csv",
        )