import pytest

from agent.table_parser.base import format_number, merge_broken_numbers


class TestFormatNumber:
    def test_number_with_spaces(self):
        assert format_number("30 818 632") == 30818632

    def test_large_number_with_spaces(self):
        assert format_number("366 722 839") == 366722839

    def test_negative_in_parentheses(self):
        assert format_number("(37 033 242)") == -37033242

    def test_negative_already_merged(self):
        assert format_number("(15089737)") == -15089737

    def test_dash_returns_zero(self):
        assert format_number("-") == 0

    def test_empty_string_returns_zero(self):
        assert format_number("") == 0

    def test_zero(self):
        assert format_number("0") == 0

    def test_ocr_artifact_digits_extracted(self):
        assert format_number("12a34") == 1234

    def test_non_breaking_space(self):
        assert format_number("100\u00a0200") == 100200

    def test_single_digit(self):
        assert format_number("5") == 5

    def test_opening_paren_only(self):
        assert format_number("(12345") == -12345

    def test_closing_paren_only(self):
        assert format_number("12345)") == -12345


class TestMergeBrokenNumbers:
    def test_simple_merge(self):
        lines = ["(37 033 242", ")"]
        result = merge_broken_numbers(lines)
        assert result == ["(37 033 242)"]

    def test_no_merge_needed(self):
        lines = ["обычная строка", "другая строка"]
        result = merge_broken_numbers(lines)
        assert result == ["обычная строка", "другая строка"]

    def test_multiline_merge(self):
        lines = ["(100", "200", ")"]
        result = merge_broken_numbers(lines)
        assert result == ["(100200)"]

    def test_already_closed_parentheses(self):
        lines = ["(37 033 242)", "следующая"]
        result = merge_broken_numbers(lines)
        assert result == ["(37 033 242)", "следующая"]

    def test_mixed_lines(self):
        lines = ["Выручка", "2110", "500 000", "(100 000", ")", "Прибыль"]
        result = merge_broken_numbers(lines)
        assert result == ["Выручка", "2110", "500 000", "(100 000)", "Прибыль"]

    def test_empty_list(self):
        assert merge_broken_numbers([]) == []
