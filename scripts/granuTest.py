from services.comtrade import fetch_trade_data

df = fetch_trade_data(
    reporter=699,
    partner=None,
    years=[2023],
    flow="X"
)

print(df.columns)
print(df["partnerDesc"].unique())