import plotly.express as px


def commodity_bar_chart(df):

    import plotly.express as px

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