from typing import List

import pandas as pd

from agent.table_parser.base import (
    ocr_file_to_lines,
    ocr_files_to_lines,
    extract_years,
    parse_table_by_codes,
)
from consts.finance import financial_results_consts, OFR_NEGATIVE_CODES

VALUE_COLUMNS = ["current_year", "previous_year"]


def parse_financial_results_report(file_paths) -> pd.DataFrame:
    """
    Парсит отчёт о финансовых результатах (форма 0710002).

    Принимает путь к файлу (str) или список путей (list[str]).

    Возвращает DataFrame с колонками:
      name, code, current_year, previous_year, values (JSON)
    """
    if isinstance(file_paths, str):
        file_paths = [file_paths]

    if len(file_paths) == 1:
        lines = ocr_file_to_lines(file_paths[0])
    else:
        lines = ocr_files_to_lines(file_paths)

    known_codes = set(financial_results_consts)
    years = extract_years(lines, num_expected=len(VALUE_COLUMNS))

    return parse_table_by_codes(
        lines=lines,
        known_codes=known_codes,
        value_columns=VALUE_COLUMNS,
        start_keyword="Выручка",
        year_labels=years if len(years) == len(VALUE_COLUMNS) else None,
        negative_codes=OFR_NEGATIVE_CODES,
    )
