"""
Парсинг бухгалтерского баланса из DataFrame (лист "parsed").
"""

import pandas as pd
from langchain_core.tools import tool

from agent.excel.base import parse_rows_from_df
from consts.accountant_balance import CODE_TO_FIELD
from input_models.accountant_balance_report import AccountantBalanceReport


def parse_balance_sheet_xlsx(df: pd.DataFrame) -> AccountantBalanceReport:
    """
    Собирает модель AccountantBalanceReport из DataFrame листа "parsed".
    Строки маппятся на поля модели по кодам из consts.accountant_balance.CODE_TO_FIELD.

    Ожидаемые колонки: name, code и колонки со значениями по годам (2023, 2024, …)
    или current_year, previous_year, year_before, либо колонка "values" с JSON.

    :param df: DataFrame (например результат download_as_xlsx или pd.read_excel(..., sheet_name="parsed"))
    :return: AccountantBalanceReport с полями по кодам, каждое поле — dict {дата: значение}
    """
    if "code" not in df.columns:
        raise ValueError("В DataFrame ожидается колонка 'code'")

    rows = parse_rows_from_df(df)
    report = AccountantBalanceReport()

    for code, field_name in CODE_TO_FIELD.items():
        print('code:', code, "; field_name:", field_name, "; data:", rows.get(code, {}))
        setattr(report, field_name, rows.get(code, {}))

    return report
