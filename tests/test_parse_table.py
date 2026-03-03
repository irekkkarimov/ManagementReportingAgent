import json

import pytest
import pandas as pd

from agent.table_parser.base import parse_table_by_codes
from consts.finance import (
    financial_results_consts,
    balance_sheet_consts,
    cash_flow_consts,
    equity_changes_consts,
)

# ---------------------------------------------------------------------------
# Реалистичные OCR-строки, эмулирующие вывод Yandex OCR по отчётам КамАЗа
# ---------------------------------------------------------------------------

SAMPLE_OFR_LINES = [
    "Отчет о финансовых результатах",
    "за 2025 год",
    "Коды",
    "Форма по ОКУД", "0710002",
    "Пояснения", "Наименование показателя", "Код", "За 2025 г.", "За 2024 г.",
    "Выручка",
    "2110",
    "366 722 839",
    "356 882 685",
    "в том числе: выручка от продажи продукции",
    "2115",
    "287 298 165",
    "298 010 090",
    "Себестоимость продаж",
    "2120",
    "(300 000 000)",
    "(280 000 000)",
    "Валовая прибыль (убыток)",
    "2100",
    "66 722 839",
    "76 882 685",
    "Коммерческие расходы",
    "2210",
    "(5 000 000)",
    "(4 500 000)",
    "Управленческие расходы",
    "2220",
    "(10 000 000)",
    "(9 000 000)",
    "Прибыль (убыток) от продаж",
    "2200",
    "51 722 839",
    "63 382 685",
    "Доходы от участия в других организациях",
    "2310",
    "1 000 000",
    "800 000",
    "Проценты к получению",
    "2320",
    "2 000 000",
    "1 500 000",
    "Проценты к уплате",
    "2330",
    "(3 000 000)",
    "(2 500 000)",
    "Прочие доходы",
    "2340",
    "5 000 000",
    "4 000 000",
    "Прочие расходы",
    "2350",
    "(6 000 000)",
    "(5 000 000)",
    "Прибыль (убыток) до налогообложения",
    "2300",
    "50 722 839",
    "62 182 685",
    "Налог на прибыль организации",
    "2410",
    "(10 000 000)",
    "(12 000 000)",
    "в т. ч. отложенный налог на прибыль",
    "2412",
    "500 000",
    "400 000",
    "Прочее",
    "2460",
    "(200 000)",
    "(100 000)",
    "Чистая прибыль (убыток)",
    "2400",
    "41 022 839",
    "50 482 685",
    "Совокупный финансовый результат периода",
    "2500",
    "41 022 839",
    "50 482 685",
]

SAMPLE_BALANCE_LINES = [
    "Бухгалтерский баланс",
    "на 31 декабря 2025 г.",
    "Коды",
    "Форма по ОКУД", "0710001",
    "Пояснения", "Наименование показателя", "Код показателя",
    "На 31 декабря 2025 г.", "На 31 декабря 2024 г.", "На 31 декабря 2023 г.",
    "АКТИВ",
    "I. Внеоборотные активы",
    "3.1, 3.2, 3.3, 3.4, 3.5, 6.1",
    "Нематериальные активы",
    "1110",
    "30 818 632",
    "27 819 290",
    "23 666 277",
    "4.1, 4.2, 4.3, 4.4, 4.5, 4.6",
    "Основные средства",
    "1150",
    "79 802 713",
    "73 105 357",
    "64 377 722",
    "Итого по Разделу I",
    "1100",
    "204 807 655",
    "205 594 799",
    "182 233 408",
    "II. Оборотные активы",
    "6.1, 6.2, 6.3",
    "Запасы",
    "1210",
    "59 370 714",
    "101 915 123",
    "57 829 068",
    "Итого по Разделу II",
    "1200",
    "277 964 575",
    "292 355 715",
    "242 396 446",
    "БАЛАНС",
    "1600",
    "482 772 230",
    "497 950 514",
    "424 629 854",
]

SAMPLE_CASHFLOW_LINES = [
    "Отчет о движении денежных средств",
    "за 2025 год",
    "Коды",
    "Форма по ОКУД", "0710005",
    "Пояснения", "Наименование показателя", "Код показателя", "За 2025 г.", "За 2024 г.",
    "Денежные потоки от текущих операций",
    "Поступления - всего",
    "4110",
    "366 722 839",
    "356 882 685",
    "Платежи - всего",
    "4120",
    "(413 350 861)",
    "(426 919 303)",
    "Сальдо денежных потоков от текущих операций",
    "4100",
    "(46 628 022)",
    "(70 036 618)",
]


class TestParseFinancialResults:
    def test_parses_revenue(self):
        df = parse_table_by_codes(
            lines=SAMPLE_OFR_LINES,
            known_codes=set(financial_results_consts),
            value_columns=["current_year", "previous_year"],
            start_keyword="Выручка",
        )
        row = df[df["code"] == "2110"]
        assert not row.empty
        assert row.iloc[0]["current_year"] == 366722839
        assert row.iloc[0]["previous_year"] == 356882685
        assert row.iloc[0]["name"] == "Выручка"

    def test_parses_negative_cost_of_sales(self):
        df = parse_table_by_codes(
            lines=SAMPLE_OFR_LINES,
            known_codes=set(financial_results_consts),
            value_columns=["current_year", "previous_year"],
            start_keyword="Выручка",
        )
        row = df[df["code"] == "2120"]
        assert row.iloc[0]["current_year"] == -300000000
        assert row.iloc[0]["previous_year"] == -280000000

    def test_parses_net_profit(self):
        df = parse_table_by_codes(
            lines=SAMPLE_OFR_LINES,
            known_codes=set(financial_results_consts),
            value_columns=["current_year", "previous_year"],
            start_keyword="Выручка",
        )
        row = df[df["code"] == "2400"]
        assert not row.empty
        assert row.iloc[0]["current_year"] == 41022839

    def test_all_ofr_codes_present(self):
        df = parse_table_by_codes(
            lines=SAMPLE_OFR_LINES,
            known_codes=set(financial_results_consts),
            value_columns=["current_year", "previous_year"],
            start_keyword="Выручка",
        )
        expected_codes = {
            "2110", "2115", "2120", "2100", "2210", "2220", "2200",
            "2310", "2320", "2330", "2340", "2350", "2300",
            "2410", "2412", "2460", "2400", "2500",
        }
        assert set(df["code"].tolist()) == expected_codes


class TestParseBalanceSheet:
    def test_parses_three_columns(self):
        df = parse_table_by_codes(
            lines=SAMPLE_BALANCE_LINES,
            known_codes=set(balance_sheet_consts),
            value_columns=["current_year", "previous_year", "year_before"],
            start_keyword="Нематериальные",
        )
        row = df[df["code"] == "1110"]
        assert not row.empty
        assert row.iloc[0]["current_year"] == 30818632
        assert row.iloc[0]["previous_year"] == 27819290
        assert row.iloc[0]["year_before"] == 23666277

    def test_parses_total_assets(self):
        df = parse_table_by_codes(
            lines=SAMPLE_BALANCE_LINES,
            known_codes=set(balance_sheet_consts),
            value_columns=["current_year", "previous_year", "year_before"],
            start_keyword="Нематериальные",
        )
        row = df[df["code"] == "1600"]
        assert not row.empty
        assert row.iloc[0]["current_year"] == 482772230

    def test_inventories_parsed(self):
        df = parse_table_by_codes(
            lines=SAMPLE_BALANCE_LINES,
            known_codes=set(balance_sheet_consts),
            value_columns=["current_year", "previous_year", "year_before"],
            start_keyword="Нематериальные",
        )
        row = df[df["code"] == "1210"]
        assert not row.empty
        assert row.iloc[0]["current_year"] == 59370714


class TestParseCashFlow:
    def test_parses_receipts(self):
        df = parse_table_by_codes(
            lines=SAMPLE_CASHFLOW_LINES,
            known_codes=set(cash_flow_consts),
            value_columns=["current_year", "previous_year"],
            start_keyword="Денежные потоки",
        )
        row = df[df["code"] == "4110"]
        assert not row.empty
        assert row.iloc[0]["current_year"] == 366722839

    def test_parses_negative_payments(self):
        df = parse_table_by_codes(
            lines=SAMPLE_CASHFLOW_LINES,
            known_codes=set(cash_flow_consts),
            value_columns=["current_year", "previous_year"],
            start_keyword="Денежные потоки",
        )
        row = df[df["code"] == "4120"]
        assert not row.empty
        assert row.iloc[0]["current_year"] == -413350861

    def test_parses_net_operating(self):
        df = parse_table_by_codes(
            lines=SAMPLE_CASHFLOW_LINES,
            known_codes=set(cash_flow_consts),
            value_columns=["current_year", "previous_year"],
            start_keyword="Денежные потоки",
        )
        row = df[df["code"] == "4100"]
        assert not row.empty
        assert row.iloc[0]["current_year"] == -46628022


class TestValuesJsonColumn:
    def test_values_column_present(self):
        df = parse_table_by_codes(
            lines=SAMPLE_OFR_LINES,
            known_codes=set(financial_results_consts),
            value_columns=["current_year", "previous_year"],
            start_keyword="Выручка",
        )
        assert "values" in df.columns

    def test_values_json_with_column_names_as_keys(self):
        df = parse_table_by_codes(
            lines=SAMPLE_OFR_LINES,
            known_codes=set(financial_results_consts),
            value_columns=["current_year", "previous_year"],
            start_keyword="Выручка",
        )
        row = df[df["code"] == "2110"].iloc[0]
        vals = json.loads(row["values"])
        assert vals == {"current_year": 366722839, "previous_year": 356882685}

    def test_values_json_with_year_labels(self):
        df = parse_table_by_codes(
            lines=SAMPLE_OFR_LINES,
            known_codes=set(financial_results_consts),
            value_columns=["current_year", "previous_year"],
            start_keyword="Выручка",
            year_labels=["2025", "2024"],
        )
        row = df[df["code"] == "2110"].iloc[0]
        vals = json.loads(row["values"])
        assert vals == {"2025": 366722839, "2024": 356882685}
        assert row["current_year"] == 366722839

    def test_balance_values_json_three_years(self):
        df = parse_table_by_codes(
            lines=SAMPLE_BALANCE_LINES,
            known_codes=set(balance_sheet_consts),
            value_columns=["current_year", "previous_year", "year_before"],
            start_keyword="Нематериальные",
            year_labels=["2025", "2024", "2023"],
        )
        row = df[df["code"] == "1110"].iloc[0]
        vals = json.loads(row["values"])
        assert vals == {"2025": 30818632, "2024": 27819290, "2023": 23666277}

    def test_year_labels_length_mismatch_falls_back_to_column_names(self):
        df = parse_table_by_codes(
            lines=SAMPLE_OFR_LINES,
            known_codes=set(financial_results_consts),
            value_columns=["current_year", "previous_year"],
            start_keyword="Выручка",
            year_labels=["2025"],
        )
        row = df[df["code"] == "2110"].iloc[0]
        vals = json.loads(row["values"])
        assert "current_year" in vals

    def test_negative_values_in_json(self):
        df = parse_table_by_codes(
            lines=SAMPLE_OFR_LINES,
            known_codes=set(financial_results_consts),
            value_columns=["current_year", "previous_year"],
            start_keyword="Выручка",
            year_labels=["2025", "2024"],
        )
        row = df[df["code"] == "2120"].iloc[0]
        vals = json.loads(row["values"])
        assert vals["2025"] == -300000000
        assert vals["2024"] == -280000000


class TestEdgeCases:
    def test_empty_lines_returns_empty_df(self):
        df = parse_table_by_codes(
            lines=[],
            known_codes={"2110"},
            value_columns=["a", "b"],
        )
        assert df.empty

    def test_no_matching_codes_returns_empty_df(self):
        df = parse_table_by_codes(
            lines=["foo", "bar", "baz"],
            known_codes={"2110"},
            value_columns=["a", "b"],
        )
        assert df.empty

    def test_start_keyword_skips_prefix(self):
        lines = ["мусор", "ещё мусор", "Выручка", "2110", "100", "200"]
        df = parse_table_by_codes(
            lines=lines,
            known_codes={"2110"},
            value_columns=["a", "b"],
            start_keyword="Выручка",
        )
        row = df[df["code"] == "2110"]
        assert not row.empty
        assert row.iloc[0]["a"] == 100

    def test_code_at_end_of_lines_gets_zero_values(self):
        lines = ["Выручка", "2110"]
        df = parse_table_by_codes(
            lines=lines,
            known_codes={"2110"},
            value_columns=["a", "b"],
        )
        row = df[df["code"] == "2110"]
        assert not row.empty
        assert row.iloc[0]["a"] == 0
        assert row.iloc[0]["b"] == 0


class TestEquityChangesEmptyCells:
    """
    Тесты для корректной обработки пустых ячеек в отчёте об изменениях капитала.
    OCR иногда пропускает пустые ячейки — следующий код строки не должен
    считываться как значение предыдущей строки.
    """

    CODES = {"3100", "3211", "3200"}
    COLS = ["charter", "additional", "reserve", "retained", "total"]

    def test_next_code_stops_value_reading(self):
        """Если сразу после кода идёт другой код, все значения = 0."""
        lines = ["Остаток начало", "3100", "3211", "Чистая прибыль"]
        df = parse_table_by_codes(
            lines=lines,
            known_codes=self.CODES,
            value_columns=self.COLS,
        )
        row = df[df["code"] == "3100"]
        assert not row.empty
        for col in self.COLS:
            assert row.iloc[0][col] == 0

    def test_partial_values_then_next_code(self):
        """Только часть ячеек заполнена, остальные пропущены OCR."""
        lines = [
            "Остаток начало",
            "3100",
            "10000",   # charter_capital
            "50000",   # retained_earnings (но OCR пропустил 3 пустые ячейки)
            "3211",    # следующий код — должен быть обнаружен
            "Чистая прибыль",
        ]
        df = parse_table_by_codes(
            lines=lines,
            known_codes=self.CODES,
            value_columns=self.COLS,
        )
        row_3100 = df[df["code"] == "3100"]
        assert not row_3100.empty
        assert row_3100.iloc[0]["charter"] == 10000
        assert row_3100.iloc[0]["additional"] == 50000
        assert row_3100.iloc[0]["reserve"] == 0
        assert row_3100.iloc[0]["retained"] == 0
        assert row_3100.iloc[0]["total"] == 0

        # Следующий код 3211 тоже должен быть распознан
        row_3211 = df[df["code"] == "3211"]
        assert not row_3211.empty

    def test_next_code_name_is_correct(self):
        """Название строки после пропущенных ячеек читается правильно."""
        lines = [
            "Остаток начало",
            "3100",
            "10000",
            "Чистая прибыль",  # название следующей строки
            "3211",
        ]
        df = parse_table_by_codes(
            lines=lines,
            known_codes=self.CODES,
            value_columns=self.COLS,
        )
        row_3211 = df[df["code"] == "3211"]
        assert not row_3211.empty
        assert row_3211.iloc[0]["name"] == "Чистая прибыль"

    def test_all_five_values_present_works_as_before(self):
        """Если все 5 значений заполнены, парсинг не ломается."""
        lines = [
            "Остаток конец",
            "3200",
            "1000",
            "2000",
            "3000",
            "4000",
            "10000",
        ]
        df = parse_table_by_codes(
            lines=lines,
            known_codes=self.CODES,
            value_columns=self.COLS,
        )
        row = df[df["code"] == "3200"]
        assert not row.empty
        assert row.iloc[0]["charter"] == 1000
        assert row.iloc[0]["additional"] == 2000
        assert row.iloc[0]["reserve"] == 3000
        assert row.iloc[0]["retained"] == 4000
        assert row.iloc[0]["total"] == 10000

    def test_multiple_rows_all_parsed(self):
        """Все коды распознаются корректно при наличии пустых ячеек."""
        lines = [
            "Остаток начало",
            "3100",
            "5000",   # только 1 значение, остальные пустые
            "Чистая прибыль",
            "3211",
            "300",
            "300",
            "Остаток конец",
            "3200",
            "5300",
        ]
        df = parse_table_by_codes(
            lines=lines,
            known_codes=self.CODES,
            value_columns=self.COLS,
        )
        assert len(df) == 3
        assert set(df["code"].tolist()) == {"3100", "3211", "3200"}
