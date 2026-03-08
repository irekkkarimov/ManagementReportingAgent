import os
from dataclasses import fields, is_dataclass
from datetime import datetime

from langchain_core.tools import tool
from openpyxl import Workbook
from openpyxl.styles import Font

from agent.models.finance_report import FinanceReportModel
from agent.tools.utils import EXCEL_OUTPUT_PATH_BASE


@tool("generate_excel_report", description="Создает Excel (xlsx) документ с посчитанными финансовыми показателями")
def generate_excel_report(report: FinanceReportModel) -> None:
    """
    Создает Excel (xlsx) документ с посчитанными финансовыми показателями
    :param report: Данные типа FinanceReportModel
    """

    if not is_dataclass(report):
        raise ValueError("report_model должен быть экземпляром dataclass")

    data = report.to_dict()

    # --- Генерация имени файла ---
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"financial_report_{timestamp}.xlsx"
    file_path = os.path.join(EXCEL_OUTPUT_PATH_BASE, filename)

    wb = Workbook()
    wb.remove(wb.active)  # удаляем стандартный лист

    for section, metrics in data.items():
        ws = wb.create_sheet(title=section)
        ws.append([section])  # заголовок раздела
        ws["A1"].font = Font(bold=True, size=14)

        ws.append(["Metric", "Value"])
        ws["A2"].font = Font(bold=True)
        ws["B2"].font = Font(bold=True)

        row_index = 3
        for metric, value in metrics.items():
            if value is not None:
                ws.append([metric, float(value).__round__(4)])
                row_index += 1

        # Автоширина колонок
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            ws.column_dimensions[column_letter].width = max_length + 2

    wb.save(file_path)