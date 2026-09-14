import zipfile
from pathlib import Path
import pandas as pd
import streamlit as st

# Point this at wherever your fetch.py log said "ALL DATA WILL BE SAVED UNDER: ..."
RAW_DIR = Path(r"C:\Users\RISC-5PARIDHI\Desktop\TradeDashboard\scripts\raw")

VALUE_COL_SUBSTRING = "Value(US $)"


def to_financial_year(year, month):
    """India's FY runs April–March. E.g. (2026, 6) -> 'FY2026-27'."""
    if month >= 4:
        return f"FY{year}-{str(year + 1)[-2:]}"
    return f"FY{year - 1}-{str(year)[-2:]}"


def load_month_zip(zip_path, flow):
    frames = []
    with zipfile.ZipFile(zip_path) as z:
        for name in z.namelist():
            with z.open(name) as f:
                df = pd.read_excel(f, engine="xlrd", header=1)
                frames.append(df)
    combined = pd.concat(frames, ignore_index=True)

    country_col = "Country of Consignment" if flow == "import" else "Country of Destination"
    value_col = next(c for c in combined.columns if VALUE_COL_SUBSTRING in c)

    grouped = (
        combined.groupby(["Commodity", country_col], as_index=False)
        .agg(QTY=("QTY", "sum"), ValueUSD=(value_col, "sum"))
        .rename(columns={country_col: "Country"})
    )
    grouped["flow"] = flow
    return grouped


def load_all_months(flow):
    flow_dir = RAW_DIR / flow
    empty = pd.DataFrame(columns=["Commodity", "Country of Consignment", "QTY", "ValueUSD", "flow", "year", "month", "financial_year"])
    if not flow_dir.exists():
        return empty

    all_months = []
    for year_dir in sorted(flow_dir.iterdir()):
        if not year_dir.is_dir():
            continue
        year = int(year_dir.name)
        for zip_file in sorted(year_dir.glob("*.zip")):
            month = int(zip_file.stem)
            df = load_month_zip(zip_file, flow)
            df["year"] = year
            df["month"] = month
            df["financial_year"] = to_financial_year(year, month)
            all_months.append(df)

    return pd.concat(all_months, ignore_index=True) if all_months else empty


# @st.cache_data(ttl=None, show_spinner=False)
# def get_all_data(flow):
#     return load_all_months(flow)

@st.cache_data(ttl=None, show_spinner=False)
def get_all_data(flow):
    parquet_path = RAW_DIR / f"{flow}_processed.parquet"
    if parquet_path.exists():
        return pd.read_parquet(parquet_path)
    return load_all_months(flow)  # fallback if parquet doesn't exist yet


def get_fy_totals(df):
    return (
        df.groupby("financial_year", as_index=False)["ValueUSD"]
        .sum()
        .sort_values("financial_year")
        .reset_index(drop=True)
    )


def get_commodity_breakdown(df, financial_year, top_n=10):
    fy_df = df[df["financial_year"] == financial_year]
    return (
        fy_df.groupby("Commodity", as_index=False)["ValueUSD"]
        .sum()
        .sort_values("ValueUSD", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )


def get_country_breakdown(df, financial_year, top_n=10):
    fy_df = df[df["financial_year"] == financial_year]
    return (
        fy_df.groupby("Country", as_index=False)["ValueUSD"]
        .sum()
        .sort_values("ValueUSD", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )

def compute_hhi(df, financial_year, country=None):
    fy_df = df[df["financial_year"] == financial_year]
    if country:
        fy_df = fy_df[fy_df["Country"] == country]
    by_commodity = fy_df.groupby("Commodity")["ValueUSD"].sum()
    if by_commodity.sum() == 0:
        return None
    shares_squared = (by_commodity / by_commodity.sum()) ** 2
    return shares_squared.sum()


def compute_yoy_growth(df, financial_year, country=None):
    all_fys = sorted(df["financial_year"].unique())
    if financial_year not in all_fys:
        return None
    idx = all_fys.index(financial_year)
    if idx == 0:
        return None
    prev_fy = all_fys[idx - 1]

    scope = df if not country else df[df["Country"] == country]
    current_total = scope[scope["financial_year"] == financial_year]["ValueUSD"].sum()
    prev_total = scope[scope["financial_year"] == prev_fy]["ValueUSD"].sum()
    if prev_total == 0:
        return None
    return (current_total - prev_total) / prev_total * 100

