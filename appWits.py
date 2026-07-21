import streamlit as st

from utils.formatters import format_currency
import pandas as pd

import services.wits as comtrade
from components.charts import (
    commodity_bar_chart,
    trade_trend_chart,
    partner_bar_chart
)


st.set_page_config(
    page_title="Trade Dashboard",
    layout="wide"
)

st.title("🌏 Trade Intelligence Dashboard")

st.write(
    """
    Explore trade flows, partners, and commodities using WITS (World Bank) trade data.
    """
)

st.caption(
    "Source: WITS (World Integrated Trade Solution) • Annual merchandise trade statistics"
)

# -------------------
# Sidebar filters
# -------------------

st.sidebar.header("Filters")

countries = {
    "India": "ind",
    # "China": "chn",
    # "United States": "usa"
}

partners = {
    "World": "wld",
    "China": "chn",
    "United States": "usa",
    "United Arab Emirates": "are",
    "Singapore": "sgp",
    "Germany": "deu",
    "United Kingdom": "gbr",
    "Japan": "jpn",
    "Netherlands": "nld",
    "Bangladesh": "bgd",
    "Saudi Arabia": "sau",
    "Australia": "aus",
    "France": "fra",
    "Italy": "ita",
    "South Korea": "kor",
    "Malaysia": "mys",
    "Brazil": "bra",
    "Vietnam": "vnm"
}

flows = {
    "Exports": "X",
    "Imports": "M"
}

#country = st.sidebar.selectbox("Reporter Country", list(countries.keys()))
country = "India"
partner = st.sidebar.selectbox("Partner Country", list(partners.keys()))

year_range = st.sidebar.slider("Years", 2010, 2025, (2015, 2023))
years = list(range(year_range[0], year_range[1] + 1))

trade_flow = st.sidebar.radio("Trade Flow", list(flows.keys()))

# -------------------
# Load data
# -------------------

spinner_msg = f"Loading exports & imports for {country} ({year_range[0]}–{year_range[1]})..."
with st.spinner(spinner_msg):
    df = comtrade.fetch_trade_data(
        reporter=countries[country],
        partner=partners[partner],
        years=years,
        flow=flows[trade_flow]
    )

    # Split the raw (mixed-classification) data immediately —
    # everything below this line uses totals_df or sector_df, never raw df
    totals_df = comtrade.get_yearly_totals(df)
    sector_df = comtrade.get_sector_breakdown(df)

    partner_df = comtrade.fetch_partner_trade_data(
        reporter=countries[country],
        years=years,
        flow=flows[trade_flow],
        partners=partners
    )

    # Prefetch both flows for the trade balance calculation
    try:
        exports_all = comtrade.fetch_trade_data(
            reporter=countries[country], partner=partners[partner],
            years=years, flow=flows["Exports"]
        )
        exports_totals_df = comtrade.get_yearly_totals(exports_all)
    except Exception:
        exports_totals_df = pd.DataFrame()

    try:
        imports_all = comtrade.fetch_trade_data(
            reporter=countries[country], partner=partners[partner],
            years=years, flow=flows["Imports"]
        )
        imports_totals_df = comtrade.get_yearly_totals(imports_all)
    except Exception:
        imports_totals_df = pd.DataFrame()

    exports_total = exports_totals_df["primaryValue"].sum() if not exports_totals_df.empty else 0
    imports_total = imports_totals_df["primaryValue"].sum() if not imports_totals_df.empty else 0

st.info(
    f"""
    **Reporter:** {country}

    **Partner:** {partner}

    **Trade Flow:** {trade_flow}

    **Years:** {year_range[0]}–{year_range[1]}
    """
)

if df.empty:
    st.warning("No trade data found for this selection.")

tab_data, tab_analysis = st.tabs(["Data", "Analysis"])

with tab_data:
    st.subheader("Preview")
    st.dataframe(df.head())

    st.subheader("Raw Data")
    st.dataframe(df)

with tab_analysis:
    if df.empty:
        st.warning("No trade data found for this selection.")
    else:
        col1, col2, col3, col4 = st.columns(4)

        total_trade = totals_df["primaryValue"].sum()   # was df["primaryValue"].sum()
        trade_balance = exports_total - imports_total
        total_label = f"Total {trade_flow}"

        col1.metric(total_label, format_currency(total_trade))
        col2.metric("Years of Data", totals_df["period"].nunique())  # was raw len(df)
        col3.metric("Reporter", country)
        col4.metric("Trade Balance", format_currency(trade_balance))

        if trade_balance > 0:
            bal_label, bal_color = "Surplus", "#138000"
        elif trade_balance < 0:
            bal_label, bal_color = "Deficit", "#d62828"
        else:
            bal_label, bal_color = "Balanced", "#6c757d"

        col4.markdown(
            f'<div style="display:inline-block;padding:6px 10px;border-radius:8px;color:#fff;background:{bal_color};font-weight:600">{bal_label}</div>',
            unsafe_allow_html=True,
        )

        st.subheader(f"{trade_flow} Trend")
        trend_fig = trade_trend_chart(totals_df)   # was trade_trend_chart(df)
        st.plotly_chart(trend_fig, use_container_width=True)

        st.subheader(f"{trade_flow} by Commodity")
        commodity_fig = commodity_bar_chart(sector_df)   # was fetch_commodity_breakdown(...) — that function never existed
        st.plotly_chart(commodity_fig, use_container_width=True)

        st.subheader("Top Export Destinations" if trade_flow == "Exports" else "Top Import Sources")
        partner_fig = partner_bar_chart(partner_df)   # already safe, no change needed
        st.plotly_chart(partner_fig, use_container_width=True)