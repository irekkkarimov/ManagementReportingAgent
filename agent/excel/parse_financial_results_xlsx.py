"""
Парсинг отчёта о финансовых результатах (ОФР) из DataFrame.
"""

import pandas as pd

from agent.excel.base import parse_rows_from_df
from consts.finance import OFR_CODE_TO_FIELD
from input_models.financial_results_report import FinancialResultsReport


def parse_financial_results_xlsx(df: pd.DataFrame) -> FinancialResultsReport:
    """
    Собирает модель FinancialResultsReport из DataFrame листа "parsed" (ОФР).
    Строки маппятся на поля по кодам из consts.finance.OFR_CODE_TO_FIELD.

    Ожидаемые колонки: name, code и колонки со значениями по годам или "values" с JSON.

    :param df: DataFrame (например результат download_as_xlsx или pd.read_excel(..., sheet_name="parsed"))
    :return: FinancialResultsReport с полями по кодам, каждое поле — dict {дата: значение}
    """
    if "code" not in df.columns:
        raise ValueError("В DataFrame ожидается колонка 'code'")

    rows = parse_rows_from_df(df)
    report = FinancialResultsReport()

    for code, field_name in OFR_CODE_TO_FIELD.items():
        setattr(report, field_name, rows.get(code, {}))

    return report
