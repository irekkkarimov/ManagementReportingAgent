from typing import List

import pandas as pd

from agent.table_parser.base import (
    ocr_file_to_lines,
    ocr_files_to_lines,
    extract_years,
    parse_table_by_codes,
)
from consts.finance import balance_sheet_consts

VALUE_COLUMNS = ["current_year", "previous_year", "year_before"]


def parse_balance_sheet(file_paths: List[str]) -> pd.DataFrame:
    """
    Парсит бухгалтерский баланс (форма 0710001).

    Принимает список путей к файлам (страницам):
      - страница 1: АКТИВ
      - страница 2: ПАССИВ

    Возвращает DataFrame с колонками:
      name, code, current_year, previous_year, year_before, values (JSON)
    """
    if isinstance(file_paths, str):
        file_paths = [file_paths]

    if len(file_paths) == 1:
        lines = ocr_file_to_lines(file_paths[0])
    else:
        lines = ocr_files_to_lines(file_paths)

    known_codes = set(balance_sheet_consts)
    years = extract_years(lines, num_expected=len(VALUE_COLUMNS))

    return parse_table_by_codes(
        lines=lines,
        known_codes=known_codes,
        value_columns=VALUE_COLUMNS,
        start_keyword="Нематериальные",
        year_labels=years if len(years) == len(VALUE_COLUMNS) else None,
    )
