import plotly.express as px


def commodity_bar_chart(df):

    fig = px.bar(
        df,
        x="cmdDesc",
        y="primaryValue",
        title="Trade by Commodity"
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