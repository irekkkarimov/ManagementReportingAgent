"""
Скачивание по ссылке (или парсинг готового DataFrame) в модель баланса или ОФР.
Один метод: ссылка/DataFrame → определение вида по кодам → парсинг. Возвращает кортеж (вид отчёта, модель).
Хранение в глобальное хранилище не используется.
"""

from typing import Tuple, Union

import pandas as pd

from agent.excel.base import normalize_code
from agent.excel.parse_balance_sheet_xlsx import parse_balance_sheet_xlsx
from agent.excel.parse_financial_results_xlsx import parse_financial_results_xlsx
from consts.accountant_balance import (
    BS_TOTAL_ASSETS,
    BS_TOTAL_EQUITY,
    BS_TOTAL_LIABILITIES,
    BS_TOTAL_CURRENT_ASSETS,
    BS_TOTAL_NONCURRENT_ASSETS,
)
from consts.finance import REVENUE, COST_OF_SALES, GROSS_PROFIT, NET_PROFIT, PROFIT_FROM_SALES
from input_models.accountant_balance_report import AccountantBalanceReport
from input_models.financial_results_report import FinancialResultsReport

# Ключевые коды, по наличию которых определяем вид отчёта (содержание, не количество)
KEY_CODES_OFR = {REVENUE, COST_OF_SALES, GROSS_PROFIT, NET_PROFIT, PROFIT_FROM_SALES}
KEY_CODES_BALANCE = {
    BS_TOTAL_ASSETS,
    BS_TOTAL_EQUITY,
    BS_TOTAL_LIABILITIES,
    BS_TOTAL_CURRENT_ASSETS,
    BS_TOTAL_NONCURRENT_ASSETS,
}


def _detect_report_type(df: pd.DataFrame) -> str:
    """
    Определяет вид отчёта по содержанию: наличие характерных кодов ОФР (выручка, прибыль и т.д.)
    или баланса (активы, капитал, обязательства).
    :return: "balance_sheet" или "financial_results"
    """
    if "code" not in df.columns:
        raise ValueError("В DataFrame ожидается колонка 'code'")
    codes_in_df = set()
    for raw in df["code"].dropna():
        c = normalize_code(raw)
        if c:
            codes_in_df.add(c)
    if codes_in_df & KEY_CODES_OFR:
        return "financial_results"
    if codes_in_df & KEY_CODES_BALANCE:
        return "balance_sheet"
    raise ValueError(
        "Не удалось определить вид отчёта: в таблице нет ключевых кодов ОФР (2110, 2120, 2400, ...) "
        "или баланса (1600, 1300, 1700, 1200, 1100)."
    )

def download_and_parse_finance_table(
    source: pd.DataFrame,
) -> Tuple[str, Union[AccountantBalanceReport, FinancialResultsReport]]:
    """
    Скачивает таблицу по ссылке (или берёт готовый DataFrame), определяет вид отчёта по кодам,
    парсит в модель. В хранилище не сохраняет.

    :param source: ссылка на Google Sheets/Drive или DataFrame листа "parsed" (колонки name, code и значения)
    :return: кортеж ("balance_sheet" | "financial_results", модель)
    :raises ValueError: при неверной ссылке, отсутствии колонки code или нераспознаваемых кодах
    """
    df = source
    table_type = _detect_report_type(df)
    if table_type == "balance_sheet":
        report = parse_balance_sheet_xlsx(df)
        return "balance_sheet", report
    report = parse_financial_results_xlsx(df)
    return "financial_results", report


# @tool(
#     "load_finance_table_from_link",
#     description=(
#         "Скачивает таблицу по ссылке (Google Sheets или Google Drive), определяет вид отчёта по кодам строк и парсит. "
#         "Сначала вызови validate_finance_link для этой ссылки."
#     ),
# )
# def load_finance_table_from_link(link: str) -> str:
#     """
#     :param link: ссылка на Google Sheets или Google Drive (баланс или ОФР — определяется автоматически)
#     :return: сообщение об успехе или об ошибке
#     """
#     link = (link or "").strip().strip("'\"")
#
#     try:
#         report_kind, _ = download_and_parse_finance_table(link)
#         return f"Загружено: {report_kind}."
#     except ValueError as e:
#         return f"Ошибка загрузки или парсинга: {e!s}"
#     except Exception as e:
#         return f"Ошибка: {e!s}"
#
