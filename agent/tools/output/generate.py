"""
Генерация Excel-отчёта с финансовыми показателями из кэша расчётов.
Параметры не нужны — данные берутся из calculation_cache текущей сессии.
"""

import os
from datetime import datetime
from typing import Dict, List, Tuple

from langchain_core.tools import tool
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.worksheet import Worksheet

from agent.tools.finance.calculation_cache import get_indicators
from agent.tools.utils import EXCEL_OUTPUT_PATH_BASE

_SECTIONS: List[Tuple[str, List[str]]] = [
    ("Рентабельность", ["ROS", "ROA", "ROE", "Gross Margin", "Operating Margin"]),
    ("Оборачиваемость", ["Total Asset Turnover", "Inventory Turnover", "Receivables Turnover", "Payables Turnover"]),
    ("Финансовая устойчивость", ["Financial Stability Ratio"]),
    ("Ликвидность", ["Current Liquidity Ratio", "Quick Liquidity Ratio", "Cash Liquidity Ratio"]),
]

_SECTION_FILL = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
_HEADER_FILL = PatternFill(start_color="BDD7EE", end_color="BDD7EE", fill_type="solid")


def _build_rows(indicators: Dict[str, float]) -> List[Tuple[str, str, float]]:
    """
    Возвращает список строк: (секция, название_показателя, значение).
    Показатели, не попавшие ни в одну секцию, идут в раздел 'Прочее'.
    """
    rows: List[Tuple[str, str, float]] = []
    used: set = set()

    for section_title, keys in _SECTIONS:
        for key in keys:
            if key in indicators:
                rows.append((section_title, key, indicators[key]))
                used.add(key)

    leftover = [(k, v) for k, v in indicators.items() if k not in used]
    for key, value in leftover:
        rows.append(("Прочее", key, value))

    return rows


def _write_sheet(ws: Worksheet, rows: List[Tuple[str, str, float]]) -> None:
    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 40
    ws.column_dimensions["C"].width = 16

    header_row = ["Раздел", "Показатель", "Значение"]
    ws.append(header_row)
    for col_idx, _ in enumerate(header_row, start=1):
        cell = ws.cell(row=1, column=col_idx)
        cell.font = Font(bold=True)
        cell.fill = _HEADER_FILL
        cell.alignment = Alignment(horizontal="center")

    current_section = None
    for section, name, value in rows:
        if section != current_section:
            current_section = section
            ws.append([section, "", ""])
            for col_idx in range(1, 4):
                cell = ws.cell(row=ws.max_row, column=col_idx)
                cell.font = Font(bold=True)
                cell.fill = _SECTION_FILL

        ws.append(["", name, value])


def _make_file_path() -> str:
    os.makedirs(EXCEL_OUTPUT_PATH_BASE, exist_ok=True)
    filename = f"financial_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return os.path.join(EXCEL_OUTPUT_PATH_BASE, filename)


@tool(
    "generate_excel_report",
    description="Создаёт Excel (xlsx) с финансовыми показателями из кэша. Параметры не нужны.",
)
def generate_excel_report() -> str:
    """
    :return: путь к сохранённому файлу или сообщение об ошибке
    """
    indicators = get_indicators()
    if not indicators:
        return (
            "Нет сохранённых расчётов. "
            "Сначала посчитай показатели с помощью calculate_* (ROS, ROA, ROE и т.д.)."
        )

    rows = _build_rows(indicators)
    file_path = _make_file_path()

    wb = Workbook()
    ws = wb.active
    ws.title = "Финансовые показатели"
    _write_sheet(ws, rows)

    wb.save(file_path)
    return f"Файл сохранён: {file_path}"
