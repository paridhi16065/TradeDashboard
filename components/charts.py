import plotly.express as px


def commodity_bar_chart(df):


    commodities = (
        df.groupby("cmdDesc")["primaryValue"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )


    fig = px.bar(
        commodities,
        x="primaryValue",
        y="cmdDesc",
        orientation="h",
        title="Top 10 Traded Commodities"
    )

    return fig

def partner_bar_chart(df):

    fig = px.bar(
        df,
        x="TradeValue",
        y="Partner",
        orientation="h",
        title="Top Trade Partners"
    )

    fig.update_layout(
        yaxis={"categoryorder": "total ascending"}
    )

    return fig

def trade_trend_chart(df):

    import plotly.express as px

    yearly = (
        df.groupby("period")["primaryValue"]
        .sum()
        .reset_index()
    )

    fig = px.line(
        yearly,
        x="period",
        y="primaryValue",
        markers=True,
        title="Trade Trend Over Time"
    )

    return fig

def dgcis_commodity_chart(df):
    fig = px.bar(df, x="ValueUSD", y="Commodity", orientation="h", title="Top 10 Commodities")
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    return fig


def dgcis_country_chart(df):
    fig = px.bar(df, x="ValueUSD", y="Country", orientation="h", title="Top 10 Countries")
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    return fig


def dgcis_trend_chart(fy_totals_df, flow_label):
    fig = px.line(fy_totals_df, x="financial_year", y="ValueUSD", markers=True, title=f"{flow_label} by Financial Year")
    return fig