import streamlit as st

from services.comtrade import fetch_trade_data
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

if st.button("Load Trade Data"):

    df = fetch_trade_data(
    reporter=countries[country],
    partner=partners[partner],
    years=years,
    flow=flows[trade_flow]
    )

    st.write("Columns returned:")
    st.write(df.columns)

    st.write("Preview:")
    st.dataframe(df.head())
    # -------------------
    # KPI Cards
    # -------------------

    col1, col2, col3 = st.columns(3)

    if df.empty:

        st.warning(
        "No trade data found for this selection."
        )

        st.stop()

    total_trade = df["primaryValue"].sum()


    col1.metric(
        "Total Trade",
        f"${total_trade:,.0f}"
    )


    col2.metric(
        "Records",
        len(df)
    )


    col3.metric(
        "Reporter",
        country
    )


    # -------------------
    # Chart
    # -------------------

    st.subheader("Trade Trend")

    trend_fig = trade_trend_chart(df)

    st.plotly_chart(
        trend_fig,
        use_container_width=True
    )

    st.subheader("Trade by Commodity")


    fig = commodity_bar_chart(df)


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # -------------------
    # Raw Data
    # -------------------

    st.subheader("Raw Data")


    st.dataframe(df)


else:

    st.info(
        "Select filters and click Load Trade Data."
    )