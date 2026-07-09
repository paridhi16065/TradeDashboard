import plotly.express as px


def commodity_bar_chart(df):

    fig = px.bar(
        df,
        x="cmdDesc",
        y="primaryValue",
        title="Trade by Commodity"
    )

    return fig