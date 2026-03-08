"""
Модель отчёта о финансовых результатах (форма 0710002), загруженного из Excel.
Каждое поле — строка ОФР по коду; значение — dict {год: значение}.
"""

from dataclasses import dataclass, field
from typing import Dict

from consts.finance import OFR_CODE_TO_FIELD


@dataclass
class FinancialResultsReport:
    """
    Отчёт о финансовых результатах: отдельное поле на каждую строку по коду.
    В каждом поле — словарь {дата/год: значение} (год как строка "2023", значение в тыс. руб.).
    """

    revenue: Dict[str, int] = field(default_factory=dict)  # 2110 Выручка
    other_incoming: Dict[str, int] = field(default_factory=dict)  # 2115
    cost_of_sales: Dict[str, int] = field(default_factory=dict)  # 2120 Себестоимость продаж
    gross_profit: Dict[str, int] = field(default_factory=dict)  # 2100
    commercial_expenses: Dict[str, int] = field(default_factory=dict)  # 2210
    management_expenses: Dict[str, int] = field(default_factory=dict)  # 2220
    profit_from_sales: Dict[str, int] = field(default_factory=dict)  # 2200
    income_from_participation: Dict[str, int] = field(default_factory=dict)  # 2310
    percentage_receivable: Dict[str, int] = field(default_factory=dict)  # 2320
    percentage_to_pay: Dict[str, int] = field(default_factory=dict)  # 2330
    other_profit: Dict[str, int] = field(default_factory=dict)  # 2340
    other_expenses: Dict[str, int] = field(default_factory=dict)  # 2350
    profit_from_continuing_operations: Dict[str, int] = field(default_factory=dict)  # 2300
    organization_income_tax: Dict[str, int] = field(default_factory=dict)  # 2410
    deferred_organization_income_tax: Dict[str, int] = field(default_factory=dict)  # 2412
    other: Dict[str, int] = field(default_factory=dict)  # 2460
    net_profit: Dict[str, int] = field(default_factory=dict)  # 2400 Чистая прибыль
    total_financial_result: Dict[str, int] = field(default_factory=dict)  # 2500

    def get_value(self, code: str, date: str) -> int:
        """Возвращает значение по коду строки ОФР и году. Если нет — 0."""
        field_name = OFR_CODE_TO_FIELD.get(code)
        if not field_name:
            return 0
        return getattr(self, field_name, {}).get(date, 0)
