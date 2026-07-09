import streamlit as st

from services.comtrade import fetch_trade_data
from components.charts import commodity_bar_chart


st.set_page_config(
    page_title="Trade Dashboard",
    layout="wide"
)


# -------------------
# Header
# -------------------

st.title("🌍 Trade Intelligence Dashboard")

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


year = st.sidebar.slider(
    "Year",
    2010,
    2025,
    2023
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
        year=year,
        flow=flows[trade_flow]
    )


    # -------------------
    # KPI Cards
    # -------------------

    col1, col2, col3 = st.columns(3)


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