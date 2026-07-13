# import pandas as pd
# import requests
# import comtradeapicall

# import importlib.metadata
# version = importlib.metadata.version("comtradeapicall")
# print("comtradeapicall version:", version)

# #there are some free apis and some paid ones. I need to see which ones I need

# mydf = comtradeapicall.previewTarifflineData(typeCode='C', freqCode='M', clCode='HS', period='202205',
#                                              reporterCode='36', cmdCode='91,90', flowCode='M', partnerCode=36,
#                                              partner2Code=None,
#                                              customsCode=None, motCode=None, maxRecords=500, format_output='JSON',
#                                              countOnly=None, includeDesc=True)

# print(mydf.head(5))

import pandas as pd
import requests
import comtradeapicall
import streamlit as st

@st.cache_data(ttl=3600)
def fetch_trade_data(
    reporter,
    partner,
    years,
    flow
):

    all_years = []

    for year in years:

        data = comtradeapicall.previewFinalData(
            typeCode="C",
            freqCode="A",
            clCode="HS",

            period=str(year),

            reporterCode=reporter,
            partnerCode=partner,
            partner2Code=None,
            cmdCode="AG6",

            flowCode=flow,

            customsCode=None,
            motCode=None,

            maxRecords=500,

            format_output="JSON",

            aggregateBy=None,
            breakdownMode="classic",

            countOnly=None,
            includeDesc=True
        )
        df_year = pd.DataFrame(data)

        if not df_year.empty:
            all_years.append(df_year)


    if all_years:
        return pd.concat(
            all_years,
            ignore_index=True
        )

    return pd.DataFrame()