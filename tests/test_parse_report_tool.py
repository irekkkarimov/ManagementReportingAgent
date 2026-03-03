import json

import pytest
from unittest.mock import patch

from agent.tools.image.recognize_image import parse_financial_report_tool

MOCK_OFR_LINES = [
    "Отчет о финансовых результатах",
    "за 2025 год",
    "Пояснения", "Наименование показателя", "Код", "За 2025 г.", "За 2024 г.",
    "Выручка",
    "2110",
    "366 722 839",
    "356 882 685",
    "Себестоимость продаж",
    "2120",
    "(300 000 000)",
    "(280 000 000)",
    "Валовая прибыль (убыток)",
    "2100",
    "66 722 839",
    "76 882 685",
    "Чистая прибыль (убыток)",
    "2400",
    "41 022 839",
    "50 482 685",
    "Совокупный финансовый результат периода",
    "2500",
    "41 022 839",
    "50 482 685",
]

MOCK_BALANCE_LINES = [
    "Бухгалтерский баланс",
    "на 31 декабря 2025 г.",
    "Форма по ОКУД", "0710001",
    "Пояснения", "Наименование показателя", "Код показателя",
    "На 31 декабря 2025 г.", "На 31 декабря 2024 г.", "На 31 декабря 2023 г.",
    "АКТИВ",
    "I. Внеоборотные активы",
    "Нематериальные активы",
    "1110",
    "30 818 632",
    "27 819 290",
    "23 666 277",
    "БАЛАНС",
    "1600",
    "482 772 230",
    "497 950 514",
    "424 629 854",
]

MOCK_UNKNOWN_LINES = [
    "Какой-то документ",
    "без финансовых данных",
    "просто текст",
]

MOCK_BALANCE_PAGE2_LINES = [
    "Форма 0710001 с. 2",
    "ПАССИВ",
    "III. Капитал",
    "Уставный капитал",
    "1310",
    "35 361 478",
    "35 361 478",
    "35 361 478",
    "БАЛАНС",
    "1700",
    "482 772 230",
    "497 950 514",
    "424 629 854",
]


def _parse(mock_lines, file_paths="./test.jpg"):
    """Хелпер: вызывает инструмент с замокаными OCR-данными и возвращает dict."""
    with patch("agent.tools.image.recognize_image.ocr_file_to_lines", return_value=mock_lines):
        raw = parse_financial_report_tool.invoke({"file_paths": file_paths})
    return json.loads(raw)


class TestParseFinancialReportTool:
    # --- возвращает валидный JSON ---

    @patch("agent.tools.image.recognize_image.ocr_file_to_lines")
    def test_returns_valid_json(self, mock_ocr):
        mock_ocr.return_value = MOCK_OFR_LINES
        raw = parse_financial_report_tool.invoke({"file_paths": "./test.jpg"})
        data = json.loads(raw)
        assert isinstance(data, dict)

    # --- структура JSON ---

    def test_ofr_has_required_keys(self):
        data = _parse(MOCK_OFR_LINES)
        assert "report_type" in data
        assert "label" in data
        assert "years" in data
        assert "rows" in data

    def test_ofr_report_type(self):
        data = _parse(MOCK_OFR_LINES)
        assert data["report_type"] == "financial_results"

    def test_ofr_label(self):
        data = _parse(MOCK_OFR_LINES)
        assert "финансовых результатах" in data["label"]

    def test_ofr_years_extracted(self):
        data = _parse(MOCK_OFR_LINES)
        assert "2025" in data["years"]
        assert "2024" in data["years"]

    # --- содержимое rows ---

    def test_ofr_rows_keyed_by_code(self):
        data = _parse(MOCK_OFR_LINES)
        assert "2110" in data["rows"]
        assert "2400" in data["rows"]

    def test_ofr_row_has_name(self):
        data = _parse(MOCK_OFR_LINES)
        assert data["rows"]["2110"]["name"] == "Выручка"

    def test_ofr_revenue_value(self):
        data = _parse(MOCK_OFR_LINES)
        year = data["years"][0]
        assert data["rows"]["2110"][year] == 366722839

    def test_ofr_previous_year_revenue(self):
        data = _parse(MOCK_OFR_LINES)
        prev_year = data["years"][1]
        assert data["rows"]["2110"][prev_year] == 356882685

    def test_ofr_cost_is_negative(self):
        """Себестоимость (2120) должна быть отрицательной через OFR_NEGATIVE_CODES."""
        data = _parse(MOCK_OFR_LINES)
        year = data["years"][0]
        assert data["rows"]["2120"][year] == -300000000

    def test_ofr_net_profit(self):
        data = _parse(MOCK_OFR_LINES)
        year = data["years"][0]
        assert data["rows"]["2400"][year] == 41022839

    # --- баланс ---

    def test_balance_sheet_report_type(self):
        data = _parse(MOCK_BALANCE_LINES, "./balance.jpg")
        assert data["report_type"] == "balance_sheet"

    def test_balance_sheet_label(self):
        data = _parse(MOCK_BALANCE_LINES, "./balance.jpg")
        assert "Бухгалтерский баланс" in data["label"]

    def test_balance_sheet_three_years(self):
        data = _parse(MOCK_BALANCE_LINES, "./balance.jpg")
        assert len(data["years"]) == 3

    def test_balance_sheet_total_assets(self):
        data = _parse(MOCK_BALANCE_LINES, "./balance.jpg")
        year = data["years"][0]
        assert data["rows"]["1600"][year] == 482772230

    def test_balance_sheet_intangible_assets_all_years(self):
        data = _parse(MOCK_BALANCE_LINES, "./balance.jpg")
        y0, y1, y2 = data["years"]
        assert data["rows"]["1110"][y0] == 30818632
        assert data["rows"]["1110"][y1] == 27819290
        assert data["rows"]["1110"][y2] == 23666277

    # --- неизвестный документ ---

    @patch("agent.tools.image.recognize_image.ocr_file_to_lines")
    def test_unknown_report_type_returns_error(self, mock_ocr):
        mock_ocr.return_value = MOCK_UNKNOWN_LINES
        raw = parse_financial_report_tool.invoke({"file_paths": "./unknown.jpg"})
        data = json.loads(raw)
        assert "error" in data
        assert "Не удалось определить" in data["error"]

    # --- пустой результат парсинга ---

    @patch("agent.tools.image.recognize_image.ocr_file_to_lines")
    def test_empty_parse_result_returns_error(self, mock_ocr):
        mock_ocr.return_value = [
            "Отчет о финансовых результатах",
            "за 2025 год",
            "пустая таблица без кодов",
        ]
        raw = parse_financial_report_tool.invoke({"file_paths": "./empty.jpg"})
        data = json.loads(raw)
        assert "error" in data
        assert "не удалось распарсить" in data["error"]

    # --- несколько файлов ---

    @patch("agent.tools.image.recognize_image.ocr_files_to_lines")
    def test_multiple_files_calls_ocr_for_each(self, mock_ocr_multi):
        combined = MOCK_BALANCE_LINES + MOCK_BALANCE_PAGE2_LINES
        mock_ocr_multi.return_value = combined

        raw = parse_financial_report_tool.invoke({
            "file_paths": "./page1.jpg, ./page2.jpg"
        })
        data = json.loads(raw)

        assert data["report_type"] == "balance_sheet"
        assert "1700" in data["rows"]
        mock_ocr_multi.assert_called_once_with(["./page1.jpg", "./page2.jpg"])

    # --- OCR вызывается корректно ---

    @patch("agent.tools.image.recognize_image.ocr_file_to_lines")
    def test_ocr_called_with_correct_path(self, mock_ocr):
        mock_ocr.return_value = MOCK_OFR_LINES
        parse_financial_report_tool.invoke({"file_paths": "./test.jpg"})
        mock_ocr.assert_called_once_with("./test.jpg")
