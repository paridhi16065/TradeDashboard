import pandas as pd
import requests
import comtradeapicall

import importlib.metadata
version = importlib.metadata.version("comtradeapicall")
print("comtradeapicall version:", version)

#there are some free apis and some paid ones. I need to see which ones I need

mydf = comtradeapicall.previewTarifflineData(typeCode='C', freqCode='M', clCode='HS', period='202205',
                                             reporterCode='36', cmdCode='91,90', flowCode='M', partnerCode=36,
                                             partner2Code=None,
                                             customsCode=None, motCode=None, maxRecords=500, format_output='JSON',
                                             countOnly=None, includeDesc=True)

print(mydf.head(5))
