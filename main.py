import json
from dataclasses import asdict
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from agent.excel.base import SHEET_PARSED
from agent.excel.parse_financial_results_xlsx import parse_financial_results_xlsx

load_dotenv()

if __name__ == "__main__":
    path = Path("excel_input/delta_ofr.xlsx")
    df = pd.read_excel(path, sheet_name=SHEET_PARSED)
    report = parse_financial_results_xlsx(df)
    d = asdict(report)
    print(json.dumps(d, indent=2, ensure_ascii=False))
