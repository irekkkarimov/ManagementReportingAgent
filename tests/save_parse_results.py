"""
Скрипт для сохранения результатов парсинга всех отчётов в Excel.
Запуск: .venv/Scripts/python.exe tests/save_parse_results.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv()

import pandas as pd

from agent.table_parser.base import (
    ocr_file_to_lines,
    ocr_files_to_lines,
    detect_report_type,
    extract_years,
    parse_table_by_codes,
)
from agent.table_parser.equity_changes import parse_equity_changes
from agent.tools.image.recognize_image import REPORT_CONFIGS

FIXTURES = Path(__file__).parent / "fixtures"
OUTPUT = Path(__file__).parent / "test_results"


def parse_and_save(name: str, file_paths: list[str], report_type: str):
    """OCR + парсинг + сохранение в Excel."""
    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}")

    cfg = REPORT_CONFIGS[report_type]

    # Отчёт об изменениях капитала использует coordinate-based парсер
    if report_type == "equity_changes":
        df = parse_equity_changes(file_paths)
        lines = ocr_file_to_lines(file_paths[0]) if len(file_paths) == 1 else ocr_files_to_lines(file_paths)
        detected = detect_report_type(lines)
        print(f"  Определён тип: {detected}")
        print(f"  Всего строк OCR: {len(lines)}")
        print(f"  Строк в DataFrame: {len(df)}")
    else:
        if len(file_paths) == 1:
            lines = ocr_file_to_lines(file_paths[0])
        else:
            lines = ocr_files_to_lines(file_paths)

        detected = detect_report_type(lines)
        print(f"  Определён тип: {detected}")
        print(f"  Всего строк OCR: {len(lines)}")

        columns = cfg["columns"]
        years = extract_years(lines, num_expected=len(columns))
        print(f"  Извлечённые годы: {years}")

        df = parse_table_by_codes(
            lines=lines,
            known_codes=set(cfg["codes"]),
            value_columns=columns,
            start_keyword=cfg["start_keyword"],
            year_labels=years if len(years) == len(columns) else None,
            negative_codes=cfg.get("negative_codes"),
        )

        print(f"  Строк в DataFrame: {len(df)}")

    xlsx_path = OUTPUT / f"{name}.xlsx"
    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="parsed", index=False)

        lines_df = pd.DataFrame({"line_index": range(len(lines)), "text": lines})
        lines_df.to_excel(writer, sheet_name="raw_ocr_lines", index=False)

    print(f"  Сохранено: {xlsx_path}")
    return df


if __name__ == "__main__":
    print("Парсинг реальных отчётов КамАЗ -> Excel\n")

    parse_and_save(
        name="balance_sheet_p1_aktiv",
        file_paths=[str(FIXTURES / "balance_sheet_p1.png")],
        report_type="balance_sheet",
    )

    parse_and_save(
        name="balance_sheet_p2_passiv",
        file_paths=[str(FIXTURES / "balance_sheet_p2.png")],
        report_type="balance_sheet",
    )

    parse_and_save(
        name="balance_sheet_full",
        file_paths=[
            str(FIXTURES / "balance_sheet_p1.png"),
            str(FIXTURES / "balance_sheet_p2.png"),
        ],
        report_type="balance_sheet",
    )

    parse_and_save(
        name="cash_flow_p1",
        file_paths=[str(FIXTURES / "cash_flow_p1.png")],
        report_type="cash_flow",
    )

    parse_and_save(
        name="cash_flow_p2",
        file_paths=[str(FIXTURES / "cash_flow_p2.png")],
        report_type="cash_flow",
    )

    parse_and_save(
        name="cash_flow_full",
        file_paths=[
            str(FIXTURES / "cash_flow_p1.png"),
            str(FIXTURES / "cash_flow_p2.png"),
        ],
        report_type="cash_flow",
    )

    parse_and_save(
        name="equity_changes",
        file_paths=[str(FIXTURES / "equity_changes.png")],
        report_type="equity_changes",
    )

    print(f"\n\nГотово! Результаты в папке: {OUTPUT.resolve()}")
