import pytest

from agent.table_parser.base import detect_report_type, extract_years


class TestDetectByHeader:
    def test_balance_sheet_header(self):
        lines = [
            "Бухгалтерский баланс",
            "на 31 декабря 2025 г.",
            "Форма по ОКУД", "0710001",
        ]
        assert detect_report_type(lines) == "balance_sheet"

    def test_financial_results_header(self):
        lines = [
            "Отчет о финансовых результатах",
            "за 2025 год",
            "Форма по ОКУД", "0710002",
        ]
        assert detect_report_type(lines) == "financial_results"

    def test_financial_results_alt_header(self):
        lines = [
            "Отчет о финансовые результаты",
            "за январь - декабрь 2025 г.",
        ]
        assert detect_report_type(lines) == "financial_results"

    def test_cash_flow_header(self):
        lines = [
            "Отчет о движении денежных средств",
            "за 2025 год",
            "Форма по ОКУД", "0710005",
        ]
        assert detect_report_type(lines) == "cash_flow"

    def test_equity_changes_header(self):
        lines = [
            "Отчет об изменениях капитала",
            "за 2025 год",
            "Форма по ОКУД", "0710004",
        ]
        assert detect_report_type(lines) == "equity_changes"


class TestDetectByCodesFallback:
    def test_balance_sheet_by_codes(self):
        lines = ["Нематериальные активы", "1110", "30 818 632", "1600", "482 772 230"]
        assert detect_report_type(lines) == "balance_sheet"

    def test_financial_results_by_codes(self):
        lines = ["Выручка", "2110", "366 722 839", "Чистая прибыль", "2400", "10 000"]
        assert detect_report_type(lines) == "financial_results"

    def test_cash_flow_by_codes(self):
        lines = ["Поступления", "4110", "366 722 839", "Сальдо", "4100", "100"]
        assert detect_report_type(lines) == "cash_flow"

    def test_equity_changes_by_codes(self):
        lines = ["На 31 декабря 2023 г.", "3100", "35 361 478", "3200", "62 993 367"]
        assert detect_report_type(lines) == "equity_changes"


class TestDetectUnknown:
    def test_random_text(self):
        lines = ["Какой-то текст", "без кодов", "и без заголовков"]
        assert detect_report_type(lines) == "unknown"

    def test_empty_lines(self):
        assert detect_report_type([]) == "unknown"


class TestExtractYears:
    def test_balance_sheet_three_years(self):
        lines = [
            "Бухгалтерский баланс",
            "на 31 декабря 2025 г.",
            "Форма по ОКУД", "0710001",
            "Пояснения", "Наименование показателя", "Код показателя",
            "На 31 декабря 2025 г.", "На 31 декабря 2024 г.", "На 31 декабря 2023 г.",
        ]
        years = extract_years(lines, num_expected=3)
        assert years == ["2025", "2024", "2023"]

    def test_ofr_two_years(self):
        lines = [
            "Отчет о финансовых результатах",
            "за 2025 год",
            "Коды",
            "Форма по ОКУД", "0710002",
            "Пояснения", "Наименование показателя", "Код", "За 2025 г.", "За 2024 г.",
        ]
        years = extract_years(lines, num_expected=2)
        assert years == ["2025", "2024"]

    def test_cash_flow_two_years(self):
        lines = [
            "Отчет о движении денежных средств",
            "за 2025 год",
            "Коды",
            "Форма по ОКУД", "0710005",
            "Наименование показателя", "Код показателя", "За 2025 г.", "За 2024 г.",
        ]
        years = extract_years(lines, num_expected=2)
        assert years == ["2025", "2024"]

    def test_empty_lines_returns_empty(self):
        assert extract_years([], num_expected=2) == []

    def test_no_years_in_text(self):
        lines = ["Какой-то текст", "без дат"]
        assert extract_years(lines, num_expected=2) == []

    def test_limits_to_num_expected(self):
        lines = [
            "На 31 декабря 2025 г.", "На 31 декабря 2024 г.", "На 31 декабря 2023 г.",
        ]
        years = extract_years(lines, num_expected=2)
        assert years == ["2025", "2024"]

    def test_fallback_to_bare_years(self):
        lines = ["Данные за 2025 2024 2023 годы"]
        years = extract_years(lines, num_expected=3)
        assert len(years) == 3
        assert "2025" in years
