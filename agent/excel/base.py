"""
Общая логика парсинга Excel-отчётов с листом "parsed" (код строки + значения по годам/датам).
"""

import json
from datetime import datetime
from typing import Dict

import pandas as pd

SHEET_PARSED = "parsed"


def date_key(col: object) -> str:
    """Ключ даты для dict: из datetime берём год ("2025"), остальное — str(col)."""
    if isinstance(col, datetime):
        return str(col.year)
    return str(col)


def normalize_code(raw: object) -> str:
    """Код строки отчёта как строка без десятичной части (1110.0 -> '1110')."""
    if raw is None or (isinstance(raw, float) and pd.isna(raw)):
        return ""
    s = str(raw).strip()
    if "." in s and s.replace(".", "").isdigit():
        return str(int(float(s)))
    return s


def value_columns(df: pd.DataFrame) -> list:
    """Колонки с числовыми значениями по годам: либо годы (2023, 2024), либо current_year и т.д."""
    result = []
    for c in df.columns:
        if c in ("name", "code"):
            continue
        if c == "values":
            continue
        result.append(c)
    return result


def parse_rows_from_df(df: pd.DataFrame) -> Dict[str, Dict[str, int]]:
    """Собирает по строкам Excel словарь код -> {дата: значение}."""
    rows: Dict[str, Dict[str, int]] = {}
    for _, row in df.iterrows():
        code = normalize_code(row["code"])
        if not code:
            continue
        if "values" in df.columns and pd.notna(row.get("values")):
            raw = row["values"]
            values_dict = json.loads(raw) if isinstance(raw, str) else raw
            rows[code] = {str(k): int(v) for k, v in values_dict.items()}
        else:
            rows[code] = {}
            for col in value_columns(df):
                val = row.get(col)
                if pd.notna(val):
                    key = date_key(col)
                    try:
                        rows[code][key] = int(val)
                    except (ValueError, TypeError):
                        rows[code][key] = 0
    return rows
