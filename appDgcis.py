import streamlit as st
import pandas as pd

from utils.formatters import format_currency
import services.dgcis as dgcis
from components.charts import (
    dgcis_commodity_chart,
    dgcis_country_chart,
    dgcis_trend_chart,
)

st.set_page_config(page_title="India Trade Dashboard (DGCI&S)", layout="wide")

st.title("🇮🇳 India Trade Dashboard — Official DGCI&S Data")
st.caption("Source: DGCI&S Foreign Trade Data Dissemination Portal • By Financial Year (Apr–Mar)")

with st.spinner("Loading DGCI&S data..."):
    imports_df = dgcis.get_all_data("import")
    exports_df = dgcis.get_all_data("export")

if imports_df.empty and exports_df.empty:
    st.warning("No DGCI&S data found — check RAW_DIR in services/dgcis.py")
    st.stop()

import_fys = set(imports_df["financial_year"].unique()) if not imports_df.empty else set()
export_fys = set(exports_df["financial_year"].unique()) if not exports_df.empty else set()
common_fys = sorted(import_fys & export_fys)

st.info(
    f"""
    **Import data covers:** {', '.join(sorted(import_fys)) if import_fys else 'none'}

    **Export data covers:** {', '.join(sorted(export_fys)) if export_fys else 'none'}

    ⚠️ Coverage differs between imports and exports (import data has a shorter history) — trade balance is only shown for financial years present in both.
    """
)

st.sidebar.header("Filters")
trade_flow = st.sidebar.radio("Trade Flow", ["Export", "Import"])
active_df = exports_df if trade_flow == "Export" else imports_df
active_fys = sorted(active_df["financial_year"].unique())
selected_fy = st.sidebar.selectbox("Financial Year", active_fys, index=len(active_fys) - 1)
country_options = ["All Countries"] + sorted(active_df["Country"].unique().tolist())
selected_country = st.sidebar.selectbox("Country Partner", country_options)

country_filter = None if selected_country == "All Countries" else selected_country

tab_analysis, tab_data = st.tabs(["Analysis", "Raw Data"])

with tab_analysis:
    fy_df = active_df[active_df["financial_year"] == selected_fy]
    if country_filter:
        fy_df = fy_df[fy_df["Country"] == country_filter]

    fy_total = fy_df["ValueUSD"].sum()
    hhi = dgcis.compute_hhi(active_df, selected_fy, country=country_filter)
    yoy = dgcis.compute_yoy_growth(active_df, selected_fy, country=country_filter)

    col1, col2, col3, col4 = st.columns(4)
    label_suffix = f" ({selected_country})" if country_filter else ""
    col1.metric(f"Total {trade_flow}s{label_suffix}", format_currency(fy_total))
    col2.metric("Commodity Concentration (HHI)", f"{hhi:.3f}" if hhi is not None else "N/A")
    col3.metric("YoY Growth", f"{yoy:+.1f}%" if yoy is not None else "N/A")

    if selected_fy in common_fys:
        exp_scope = exports_df[exports_df["financial_year"] == selected_fy]
        imp_scope = imports_df[imports_df["financial_year"] == selected_fy]
        if country_filter:
            exp_scope = exp_scope[exp_scope["Country"] == country_filter]
            imp_scope = imp_scope[imp_scope["Country"] == country_filter]
        exp_total = exp_scope["ValueUSD"].sum()
        imp_total = imp_scope["ValueUSD"].sum()
        col4.metric("Trade Balance", format_currency(exp_total - imp_total))
    else:
        col4.metric("Trade Balance", "N/A (incomplete coverage)")

    st.subheader(f"{trade_flow} Trend by Financial Year{label_suffix}")
    trend_scope = active_df if not country_filter else active_df[active_df["Country"] == country_filter]
    fy_totals = dgcis.get_fy_totals(trend_scope)
    st.plotly_chart(dgcis_trend_chart(fy_totals, trade_flow), use_container_width=True)

    st.subheader(f"Top Commodities — {selected_fy}{label_suffix}")
    commodity_source = active_df if not country_filter else active_df[active_df["Country"] == country_filter]
    st.plotly_chart(dgcis_commodity_chart(dgcis.get_commodity_breakdown(commodity_source, selected_fy)), use_container_width=True)

    if not country_filter:
        st.subheader(f"Top Countries — {selected_fy}")
        st.plotly_chart(dgcis_country_chart(dgcis.get_country_breakdown(active_df, selected_fy)), use_container_width=True)

with tab_data:
    st.dataframe(fy_df)