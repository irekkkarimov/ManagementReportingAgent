import json

from langchain_core.tools import tool

from agent.table_parser.base import (
    ocr_file_to_lines,
    ocr_files_to_lines,
    detect_report_type,
    extract_years,
    parse_table_by_codes,
)
from agent.table_parser.equity_changes import parse_equity_changes, VALUE_COLUMNS as EC_COLUMNS
from consts.finance import (
    financial_results_consts,
    balance_sheet_consts,
    cash_flow_consts,
    equity_changes_consts,
    OFR_NEGATIVE_CODES,
)

REPORT_CONFIGS = {
    "financial_results": {
        "codes": financial_results_consts,
        "columns": ["current_year", "previous_year"],
        "start_keyword": "Выручка",
        "label": "Отчёт о финансовых результатах",
        "negative_codes": OFR_NEGATIVE_CODES,
    },
    "balance_sheet": {
        "codes": balance_sheet_consts,
        "columns": ["current_year", "previous_year", "year_before"],
        "start_keyword": "Нематериальные",
        "label": "Бухгалтерский баланс",
        "negative_codes": None,
    },
    "cash_flow": {
        "codes": cash_flow_consts,
        "columns": ["current_year", "previous_year"],
        "start_keyword": "Денежные потоки",
        "label": "Отчёт о движении денежных средств",
        "negative_codes": None,
    },
    "equity_changes": {
        "codes": equity_changes_consts,
        "columns": [
            "charter_capital",
            "additional_capital",
            "reserve_capital",
            "retained_earnings",
            "total",
        ],
        "start_keyword": "3100",
        "label": "Отчёт об изменениях капитала",
        "negative_codes": None,
    },
}


@tool(
    "parse_financial_report_tool",
    description=(
        "Распознаёт финансовый отчёт из изображений с помощью OCR. "
        "Автоматически определяет тип отчёта (баланс, ОФР, ОДДС, изменения капитала). "
        "Принимает пути к файлам через запятую. "
        "Возвращает JSON: {report_type, label, years, rows}, "
        "где rows — словарь {код_строки: {name, <год>: значение, ...}}. "
        "Пример: rows['2110']['2023'] = выручка за 2023 год."
    ),
)
def parse_financial_report_tool(file_paths: str) -> str:
    """
    Распознаёт финансовый отчёт из изображений с помощью OCR и возвращает JSON.

    :param file_paths: Пути к файлам изображений, разделённые запятой.
                       Для многостраничных отчётов передай все страницы.
    :return: JSON-строка со структурированными данными отчёта
    """
    paths = [p.strip() for p in file_paths.split(",")]

    if len(paths) == 1:
        lines = ocr_file_to_lines(paths[0])
    else:
        lines = ocr_files_to_lines(paths)

    report_type = detect_report_type(lines)

    if report_type == "unknown":
        return json.dumps({
            "error": "Не удалось определить тип отчёта.",
            "hint": "Поддерживаемые формы: бухгалтерский баланс, ОФР, ОДДС, изменения капитала.",
        }, ensure_ascii=False)

    config = REPORT_CONFIGS[report_type]
    columns = config["columns"]

    # Отчёт об изменениях капитала: использует coordinate-based парсер,
    # потому что OCR пропускает пустые ячейки и линейный парсер даёт неверные колонки.
    if report_type == "equity_changes":
        df = parse_equity_changes(paths)
        value_keys = EC_COLUMNS
    else:
        years = extract_years(lines, num_expected=len(columns))
        year_labels = years if len(years) == len(columns) else None

        df = parse_table_by_codes(
            lines=lines,
            known_codes=set(config["codes"]),
            value_columns=columns,
            start_keyword=config["start_keyword"],
            year_labels=year_labels,
            negative_codes=config.get("negative_codes"),
        )
        value_keys = year_labels if year_labels else columns

    if df.empty:
        return json.dumps({
            "error": f"Тип отчёта определён как '{config['label']}', но данные не удалось распарсить.",
        }, ensure_ascii=False)

    rows = {}
    for _, row in df.iterrows():
        code = str(row["code"])
        entry = {"name": str(row["name"])}
        for col, key in zip(columns, value_keys):
            entry[key] = int(row[col])
        rows[code] = entry

    result = {
        "report_type": report_type,
        "label": config["label"],
        "years": value_keys,
        "rows": rows,
    }
    return json.dumps(result, ensure_ascii=False)
