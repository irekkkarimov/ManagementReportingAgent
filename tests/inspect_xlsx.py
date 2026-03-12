"""Inspect Excel structure."""
import pandas as pd
from pathlib import Path

xlsx = Path("tests/test_results/balance_sheet_full.xlsx")
xl = pd.ExcelFile(xlsx)
print("Sheets:", xl.sheet_names)
for sheet in xl.sheet_names:
    df = pd.read_excel(xlsx, sheet_name=sheet, header=None)
    print(f"\n--- {sheet} ---")
    print(f"Shape: {df.shape}")
    pd.set_option("display.max_columns", 20)
    pd.set_option("display.width", 200)
    pd.set_option("display.max_colwidth", 40)
    print(df.head(30).to_string())
