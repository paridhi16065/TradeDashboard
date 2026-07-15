from services.comtrade import fetch_trade_data
df = fetch_trade_data(
    reporter=699,
    partner=0,
    years=[2023],
    flow="X"
)

print(df.head())


df.to_parquet(
    "cache/exports/India_2023.parquet",
    index=False
)