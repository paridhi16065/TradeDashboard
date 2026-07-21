import time
import requests
import pandas as pd
import xml.etree.ElementTree as ET
import streamlit as st

WITS_BASE = "https://wits.worldbank.org/API/V1/SDMX/V21/datasource/tradestats-trade"

FLOW_TO_INDICATOR = {
    "X": "XPRT-TRD-VL",
    "M": "MPRT-TRD-VL",
}

REQUIRED_COLUMNS = ["primaryValue", "cmdCode", "cmdDesc", "period", "partnerCode", "reporterCode", "flowCode"]

HS_SECTOR_CODES = [
    "01-05_Animal", "06-15_Vegetable", "16-24_FoodProd", "25-26_Minerals",
    "27-27_Fuels", "28-38_Chemicals", "39-40_PlastiRub", "41-43_HidesSkin",
    "44-49_Wood", "50-63_TextCloth", "64-67_Footwear", "68-71_StoneGlas",
    "72-83_Metals", "84-85_MachElec", "86-89_Transport", "90-99_Miscellan",
]

def get_sector_breakdown(df):
    return df[df["cmdCode"].isin(HS_SECTOR_CODES)]

_last_call = 0.0


def _throttle():
    global _last_call
    elapsed = time.time() - _last_call
    if elapsed < 0.3:
        time.sleep(0.3 - elapsed)
    _last_call = time.time()


def _strip_ns(tag):
    return tag.split("}")[-1] if "}" in tag else tag


def _parse_wits_xml(xml_text):
    """Handles both the flat 'structure specific' schema and the nested
    'generic' SDMX schema WITS may return."""
    root = ET.fromstring(xml_text)

    # Bail out cleanly on an explicit WITS error payload
    for el in root.iter():
        if _strip_ns(el.tag) == "error":
            return pd.DataFrame()

    rows = []
    for series in root.iter():
        if _strip_ns(series.tag) != "Series":
            continue

        # Series-level dimensions (flat attrs in both schema variants,
        # or nested under a SeriesKey in the generic schema)
        series_attrs = dict(series.attrib)
        for child in series:
            if _strip_ns(child.tag) == "SeriesKey":
                for val in child:
                    if _strip_ns(val.tag) == "Value":
                        series_attrs[val.attrib.get("id")] = val.attrib.get("value")

        for obs in series:
            tag = _strip_ns(obs.tag)
            if tag == "Obs":
                # Flat structure-specific style: attributes directly on <Obs>
                if obs.attrib.get("TIME_PERIOD") is not None:
                    row = dict(series_attrs)
                    row.update(obs.attrib)
                    rows.append(row)
                else:
                    # Generic style: <ObsDimension id="TIME_PERIOD" value="..."/>
                    # and <ObsValue value="..."/> as children
                    row = dict(series_attrs)
                    for child in obs:
                        ctag = _strip_ns(child.tag)
                        if ctag == "ObsDimension":
                            row[child.attrib.get("id")] = child.attrib.get("value")
                        elif ctag == "ObsValue":
                            row["OBS_VALUE"] = child.attrib.get("value")
                    rows.append(row)

    return pd.DataFrame(rows)


def _to_comtrade_schema(df, flow):
    df = df.rename(columns={
        "OBS_VALUE": "primaryValue",
        "PRODUCTCODE": "cmdCode",
        "TIME_PERIOD": "period",
        "PARTNER": "partnerCode",
        "REPORTER": "reporterCode",
    })
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            df[col] = pd.Series(dtype="object")
    df["primaryValue"] = pd.to_numeric(df["primaryValue"], errors="coerce").fillna(0)*1000
    df["cmdDesc"] = df["cmdCode"]
    df["flowCode"] = flow
    return df[REQUIRED_COLUMNS]


@st.cache_data(ttl=None, show_spinner=False)
def fetch_trade_data(reporter, partner, years, flow):
    indicator = FLOW_TO_INDICATOR[flow]
    all_years = []
    for year in years:
        url = (
            f"{WITS_BASE}/reporter/{reporter}/year/{year}"
            f"/partner/{partner}/product/all/indicator/{indicator}"
        )
        _throttle()
        try:
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            df_year = _parse_wits_xml(resp.text)
        except (requests.RequestException, ET.ParseError):
            df_year = pd.DataFrame()
        if not df_year.empty:
            all_years.append(df_year)
    if not all_years:
        return pd.DataFrame(columns=REQUIRED_COLUMNS)
    df = pd.concat(all_years, ignore_index=True)
    return _to_comtrade_schema(df, flow)

def get_yearly_totals(df):
    return df[df["cmdCode"] == "Total"]

@st.cache_data(ttl=None, show_spinner=False)
def get_country_names():
    url = "https://wits.worldbank.org/API/V1/wits/datasource/tradestats-trade/country/ALL"
    _throttle()
    resp = requests.get(url, timeout=30)
    root = ET.fromstring(resp.text)
    names = {}
    for c in root.iter():
        if _strip_ns(c.tag) == "country":
            iso3 = c.attrib.get("iso3Code") or c.attrib.get("countrycode")
            for child in c:
                if _strip_ns(child.tag) == "name":
                    names[iso3] = child.text
    return names

def fetch_all_partners(reporter, year, flow):
    indicator = FLOW_TO_INDICATOR[flow]
    url = (
        f"{WITS_BASE}/reporter/{reporter}/year/{year}"
        f"/partner/all/product/Total/indicator/{indicator}"
    )
    _throttle()
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        df = _parse_wits_xml(resp.text)
    except (requests.RequestException, ET.ParseError):
        df = pd.DataFrame()
    if df.empty:
        return pd.DataFrame(columns=REQUIRED_COLUMNS)
    return _to_comtrade_schema(df, flow)

def fetch_partner_trade_data(reporter, years, flow, partners):
    results = []
    for partner_name, partner_code in partners.items():
        if partner_name == "World":
            continue
        df = fetch_trade_data(reporter, partner_code, years, flow)
        totals = get_yearly_totals(df)
        if totals.empty:
            continue
        results.append({"Partner": partner_name, "TradeValue": totals["primaryValue"].sum()})
    return (
        pd.DataFrame(results)
        .sort_values("TradeValue", ascending=False)
        .reset_index(drop=True)
    )