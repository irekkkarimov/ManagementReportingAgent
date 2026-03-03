"""
Интеграционные тесты с реальным Yandex OCR.

Требования:
  - .env файл с YC_FOLDER_ID и YC_OCR_API_KEY
  - Картинки отчётов КамАЗа в tests/fixtures/

Запуск:
  pytest tests/test_integration_ocr.py -v -s
"""
import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

load_dotenv()

FIXTURES = Path(__file__).parent / "fixtures"

HAS_CREDENTIALS = bool(os.getenv("YC_FOLDER_ID") and os.getenv("YC_OCR_API_KEY"))

skip_no_creds = pytest.mark.skipif(
    not HAS_CREDENTIALS,
    reason="YC_FOLDER_ID / YC_OCR_API_KEY not set — skipping real OCR tests",
)

from agent.table_parser.base import (
    ocr_file_to_lines,
    detect_report_type,
    parse_table_by_codes,
)
from consts.finance import (
    financial_results_consts,
    balance_sheet_consts,
    cash_flow_consts,
    equity_changes_consts,
)
from agent.tools.image.recognize_image import (
    parse_financial_report_tool,
    REPORT_CONFIGS,
)


# ======================================================================
# Бухгалтерский баланс (форма 0710001) — 2 страницы
# Ожидаемые значения взяты из реального отчёта КамАЗ за 2025 г.
# ======================================================================

@skip_no_creds
class TestBalanceSheetOCR:
    @pytest.fixture(autouse=True, scope="class")
    def ocr_lines(self, request):
        p1 = str(FIXTURES / "balance_sheet_p1.png")
        p2 = str(FIXTURES / "balance_sheet_p2.png")
        lines_p1 = ocr_file_to_lines(p1)
        lines_p2 = ocr_file_to_lines(p2)
        request.cls.lines_p1 = lines_p1
        request.cls.lines_p2 = lines_p2
        request.cls.lines_all = lines_p1 + lines_p2

    def test_detect_type_page1(self):
        assert detect_report_type(self.lines_p1) == "balance_sheet"

    def test_parse_aktiv(self):
        cfg = REPORT_CONFIGS["balance_sheet"]
        df = parse_table_by_codes(
            self.lines_p1,
            known_codes=set(cfg["codes"]),
            value_columns=cfg["columns"],
            start_keyword=cfg["start_keyword"],
        )
        assert not df.empty, f"DataFrame пустой. Строки OCR:\n{self.lines_p1[:30]}"

        row_1110 = df[df["code"] == "1110"]
        assert not row_1110.empty, f"Код 1110 не найден. Коды: {df['code'].tolist()}"
        assert row_1110.iloc[0]["current_year"] == 30818632

        row_1600 = df[df["code"] == "1600"]
        assert not row_1600.empty, f"Код 1600 не найден. Коды: {df['code'].tolist()}"
        assert row_1600.iloc[0]["current_year"] == 482772230

    def test_parse_passiv(self):
        cfg = REPORT_CONFIGS["balance_sheet"]
        df = parse_table_by_codes(
            self.lines_p2,
            known_codes=set(cfg["codes"]),
            value_columns=cfg["columns"],
            start_keyword=None,
        )

        row_1310 = df[df["code"] == "1310"]
        assert not row_1310.empty, f"Код 1310 не найден. Коды: {df['code'].tolist()}"
        assert row_1310.iloc[0]["current_year"] == 35361478

        row_1700 = df[df["code"] == "1700"]
        assert not row_1700.empty, f"Код 1700 не найден. Коды: {df['code'].tolist()}"
        assert row_1700.iloc[0]["current_year"] == 482772230

    def test_full_tool_two_pages(self):
        p1 = str(FIXTURES / "balance_sheet_p1.png")
        p2 = str(FIXTURES / "balance_sheet_p2.png")
        result = parse_financial_report_tool.invoke(
            {"file_paths": f"{p1}, {p2}"}
        )
        assert "Бухгалтерский баланс" in result
        assert "1600" in result
        assert "1700" in result


# ======================================================================
# Отчёт о движении денежных средств (форма 0710005) — 2 страницы
# ======================================================================

@skip_no_creds
class TestCashFlowOCR:
    @pytest.fixture(autouse=True, scope="class")
    def ocr_lines(self, request):
        p1 = str(FIXTURES / "cash_flow_p1.png")
        lines = ocr_file_to_lines(p1)
        request.cls.lines_p1 = lines

    def test_detect_type(self):
        assert detect_report_type(self.lines_p1) == "cash_flow"

    def test_parse_page1(self):
        cfg = REPORT_CONFIGS["cash_flow"]
        df = parse_table_by_codes(
            self.lines_p1,
            known_codes=set(cfg["codes"]),
            value_columns=cfg["columns"],
            start_keyword=cfg["start_keyword"],
        )
        assert not df.empty, f"DataFrame пустой. Строки OCR:\n{self.lines_p1[:30]}"

        row_4110 = df[df["code"] == "4110"]
        assert not row_4110.empty, f"Код 4110 не найден. Коды: {df['code'].tolist()}"
        assert row_4110.iloc[0]["current_year"] == 366722839

    def test_full_tool_two_pages(self):
        p1 = str(FIXTURES / "cash_flow_p1.png")
        p2 = str(FIXTURES / "cash_flow_p2.png")
        result = parse_financial_report_tool.invoke(
            {"file_paths": f"{p1}, {p2}"}
        )
        assert "движении денежных средств" in result or "cash_flow" in result.lower() or "4110" in result


# ======================================================================
# Отчёт об изменениях капитала (форма 0710004) — 1 страница (повёрнутая)
# ======================================================================

@skip_no_creds
class TestEquityChangesOCR:
    @pytest.fixture(autouse=True, scope="class")
    def ocr_lines(self, request):
        path = str(FIXTURES / "equity_changes.png")
        lines = ocr_file_to_lines(path)
        request.cls.lines = lines

    def test_detect_type(self):
        report_type = detect_report_type(self.lines)
        assert report_type == "equity_changes", (
            f"Ожидался equity_changes, получен {report_type}. "
            f"Первые 20 строк: {self.lines[:20]}"
        )

    def test_parse_has_code_3100(self):
        cfg = REPORT_CONFIGS["equity_changes"]
        df = parse_table_by_codes(
            self.lines,
            known_codes=set(cfg["codes"]),
            value_columns=cfg["columns"],
            start_keyword=cfg["start_keyword"],
        )
        row = df[df["code"] == "3100"]
        assert not row.empty, (
            f"Код 3100 не найден. Коды: {df['code'].tolist()}. "
            f"Первые 20 строк OCR: {self.lines[:20]}"
        )


# ======================================================================
# Проверка OCR-строк — просто дамп для отладки
# ======================================================================

@skip_no_creds
class TestOCRRawOutput:
    """Проверяет, что OCR возвращает непустые строки для каждого файла."""

    def test_balance_p1_has_lines(self):
        lines = ocr_file_to_lines(str(FIXTURES / "balance_sheet_p1.png"))
        assert len(lines) > 50, f"Слишком мало строк: {len(lines)}"

    def test_cash_flow_p1_has_lines(self):
        lines = ocr_file_to_lines(str(FIXTURES / "cash_flow_p1.png"))
        assert len(lines) > 30, f"Слишком мало строк: {len(lines)}"

    def test_equity_changes_has_lines(self):
        lines = ocr_file_to_lines(str(FIXTURES / "equity_changes.png"))
        assert len(lines) > 10, f"Слишком мало строк: {len(lines)}"
