import zipfile
import pandas as pd

with zipfile.ZipFile(r"C:\Users\RISC-5PARIDHI\Desktop\TradeDashboard\scripts\raw\export\2026\01.zip") as z:
    with z.open(z.namelist()[0]) as f:
        df = pd.read_excel(f, engine="xlrd", header=1)

print(df.columns.tolist())
print(df.head(5))