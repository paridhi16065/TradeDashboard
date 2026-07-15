import streamlit as st

from utils.formatters import format_currency
import pandas as pd

import services.comtrade as comtrade
from components.charts import (
    commodity_bar_chart,
    trade_trend_chart
)


st.set_page_config(
    page_title="Trade Dashboard",
    layout="wide"
)


# -------------------
# Header
# -------------------

st.title("🌏 Trade Intelligence Dashboard")

st.write(
    """
    Explore trade flows, partners, and commodities using UN Comtrade data.
    """
)

st.caption(
    "Source: UN Comtrade API • Annual merchandise trade statistics"
)


# -------------------
# Sidebar filters
# -------------------

st.sidebar.header("Filters")


countries = {
    "India": 699,
    "China": 156,
    "United States": 842
}


partners = {
    "World": 0,
    "China": 156,
    "United States": 842
}


flows = {
    "Exports": "X",
    "Imports": "M"
}


country = st.sidebar.selectbox(
    "Reporter Country",
    list(countries.keys())
)


partner = st.sidebar.selectbox(
    "Partner Country",
    list(partners.keys())
)


year_range = st.sidebar.slider(
    "Years",
    2010,
    2025,
    (2015, 2023)
)

years = list(
    range(
        year_range[0],
        year_range[1] + 1
    )
)

trade_flow = st.sidebar.radio(
    "Trade Flow",
    list(flows.keys())
)

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

    # Prefetch both flows to speed up balance calculation later
    try:
        exports_all = comtrade.fetch_trade_data(
            reporter=countries[country],
            partner=partners[partner],
            years=years,
            flow=flows["Exports"]
        )
    except Exception:
        exports_all = pd.DataFrame()

    try:
        imports_all = comtrade.fetch_trade_data(
            reporter=countries[country],
            partner=partners[partner],
            years=years,
            flow=flows["Imports"]
        )
    except Exception:
        imports_all = pd.DataFrame()

    exports_total = exports_all["primaryValue"].sum() if not exports_all.empty else 0
    imports_total = imports_all["primaryValue"].sum() if not imports_all.empty else 0

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

        total_trade = df["primaryValue"].sum()

        trade_balance = exports_total - imports_total
        print(trade_balance)
        total_label = f"Total {trade_flow}"

        col1.metric(
            total_label,
            format_currency(total_trade)
        )

        col2.metric(
            "Records",
            len(df)
        )

        col3.metric(
            "Reporter",
            country
        )

        col4.metric(
            "Trade Balance",
            format_currency(trade_balance)
        )

        # Color-coded label for surplus/deficit
        if trade_balance > 0:
            bal_label = "Surplus"
            bal_color = "#138000"
        elif trade_balance < 0:
            bal_label = "Deficit"
            bal_color = "#d62828"
        else:
            bal_label = "Balanced"
            bal_color = "#6c757d"

        col4.markdown(
            f'<div style="display:inline-block;padding:6px 10px;border-radius:8px;color:#fff;background:{bal_color};font-weight:600">{bal_label}</div>',
            unsafe_allow_html=True,
        )

        st.subheader( f"{trade_flow} Trend")

        trend_fig = trade_trend_chart(df)
        st.plotly_chart(
            trend_fig,
            use_container_width=True
        )

        st.subheader(f"{trade_flow} by Commodity")
        fig = commodity_bar_chart(df)
        st.plotly_chart(
            fig,
            use_container_width=True
        )