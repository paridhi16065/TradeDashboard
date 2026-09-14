# scripts/build_dgcis_cache.py
import sys
from pathlib import Path

# Add the project root (one level up from scripts/) to Python's search path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


import services.dgcis as dgcis

for flow in ["import", "export"]:
    df = dgcis.load_all_months(flow)
    df.to_parquet(f"scripts/raw/{flow}_processed.parquet")
    print(f"{flow}: {len(df)} rows saved")