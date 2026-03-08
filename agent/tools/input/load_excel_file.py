"""
Загрузка и парсинг Excel-файла с диска. Возвращает модель (вид отчёта, отчёт), без сохранения в хранилище.
"""

from pathlib import Path
from typing import Tuple, Union

import pandas as pd
from langchain_core.tools import tool

from agent.excel.base import SHEET_PARSED
from input_models.accountant_balance_report import AccountantBalanceReport
from input_models.financial_results_report import FinancialResultsReport

@tool(
    "load_excel_file_tool",
    description=(
        "Читает Excel-файл по пути (например, загруженный пользователем), определяет вид отчёта (баланс или ОФР) "
        "по кодам строк и парсит. Возвращает информацию об загруженных данных. "
        "Используй, когда пользователь приложил файл Excel к сообщению."
    ),
)
def load_excel_file_tool(
    file_path: str,
) -> Tuple[str, Union[AccountantBalanceReport, FinancialResultsReport]]:
    """
    Читает Excel по пути, определяет вид отчёта, парсит и возвращает модель. В хранилище не сохраняет.

    :param file_path: путь к файлу .xlsx или .xls
    :return: кортеж (вид отчёта "balance_sheet" | "financial_results", модель)
    :raises FileNotFoundError: файл не найден
    :raises ValueError: неверное расширение или ошибка парсинга
    """
    path = Path((file_path or "").strip().strip("'\""))
    if not path.exists():
        raise FileNotFoundError(f"Файл не найден: {path}")
    if path.suffix.lower() not in (".xlsx", ".xls"):
        raise ValueError(f"Ожидается файл Excel (.xlsx или .xls), получено: {path.suffix}")

    try:
        df = pd.read_excel(path, sheet_name=SHEET_PARSED)
    except ValueError:
        df = pd.read_excel(path, sheet_name=0)

    return download_and_parse_finance_table(df)

