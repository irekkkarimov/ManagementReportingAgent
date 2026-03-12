"""
Генерация Excel-отчёта.

При вызове generate_excel_report самостоятельно считает все 13 финансовых показателей
по всем годам, доступным в inputs_cache, и сохраняет результат в .xlsx.
"""

from typing import Dict, List, Optional

from langchain_core.tools import tool
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.worksheet import Worksheet

from agent.indicators.compute import ALL_INDICATORS, IndicatorDef
from agent.tools.output._shared import compute_all_indicators, get_years_or_error, make_output_path
from agent.tools.utils import EXCEL_OUTPUT_PATH_BASE

_SECTION_FILL = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
_HEADER_FILL = PatternFill(start_color="BDD7EE", end_color="BDD7EE", fill_type="solid")
_BOLD = Font(bold=True)
_DASH = "—"


def _fmt(value: Optional[float]):
    """None → прочерк; число → само число (0 остаётся 0)."""
    return _DASH if value is None else value




def _write_sheet(
    ws: Worksheet,
    years: List[str],
    results: Dict[str, Dict[str, Optional[float]]],
) -> None:
    """Заполняет лист: строки — показатели, сгруппированные по разделам; столбцы — годы."""

    year_col_start = 2

    ws.column_dimensions["A"].width = 45
    for i, year in enumerate(years):
        col_letter = chr(ord("A") + year_col_start - 1 + i)
        ws.column_dimensions[col_letter].width = 16

    header = ["Показатель"] + years
    ws.append(header)
    for col_idx in range(1, len(header) + 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.font = _BOLD
        cell.fill = _HEADER_FILL
        cell.alignment = Alignment(horizontal="center")

    seen_sections: set = set()
    used_names: set = set()

    def _append_indicator(ind: IndicatorDef, section: str) -> None:
        if section not in seen_sections:
            seen_sections.add(section)
            row = [section] + [""] * len(years)
            ws.append(row)
            for col_idx in range(1, len(years) + 2):
                cell = ws.cell(row=ws.max_row, column=col_idx)
                cell.font = _BOLD
                cell.fill = _SECTION_FILL

        year_values = results.get(ind.name, {})
        row = [ind.name] + [_fmt(year_values.get(y)) for y in years]
        ws.append(row)
        used_names.add(ind.name)

    for ind in ALL_INDICATORS:
        _append_indicator(ind, ind.section)

    leftover = [(name, vals) for name, vals in results.items() if name not in used_names]
    if leftover:
        section = "Прочее"
        seen_sections.discard(section)
        for name, vals in leftover:
            ind_stub = IndicatorDef(name, section, lambda _y: None, False)
            _append_indicator(ind_stub, section)
            row_num = ws.max_row
            for i, year in enumerate(years):
                ws.cell(row=row_num, column=year_col_start + i).value = _fmt(vals.get(year))


@tool(
    "generate_excel_report",
    description=(
        "Создаёт Excel (.xlsx) со всеми финансовыми показателями. "
        "Считает все показатели самостоятельно по всем доступным годам. "
        "Параметры не нужны."
    ),
)
def generate_excel_report() -> str:
    """
    Рассчитывает все 13 финансовых показателей по всем годам из inputs_cache
    и сохраняет в Excel.

    :return: путь к файлу или сообщение об ошибке
    """
    years = get_years_or_error()
    if isinstance(years, str):
        return years

    results = compute_all_indicators(years)
    file_path = make_output_path(EXCEL_OUTPUT_PATH_BASE, "financial_report", "xlsx")

    wb = Workbook()
    ws = wb.active
    ws.title = "Финансовые показатели"
    _write_sheet(ws, years, results)
    wb.save(file_path)

    return f"Файл сохранён: {file_path}"
