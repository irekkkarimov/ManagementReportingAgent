"""
Модель бухгалтерского баланса (форма 0710001), загруженного из Excel.
Каждое поле — строка баланса по коду; значение — dict {год: значение}.
"""

from dataclasses import dataclass, field
from typing import Dict

from consts.accountant_balance import CODE_TO_FIELD


@dataclass
class AccountantBalanceReport:
    """
    Бухгалтерский баланс: отдельное поле на каждую строку баланса по коду.
    В каждом поле — словарь {дата/год: значение} (год как строка "2023", значение в тыс. руб.).
    """

    # АКТИВ — I. Внеоборотные активы
    intangible_assets: Dict[str, int] = field(default_factory=dict)  # 1110
    fixed_assets: Dict[str, int] = field(default_factory=dict)  # 1150
    investment_property: Dict[str, int] = field(default_factory=dict)  # 1160
    financial_investments_noncurrent: Dict[str, int] = field(default_factory=dict)  # 1170
    deferred_tax_assets: Dict[str, int] = field(default_factory=dict)  # 1180
    other_noncurrent_assets: Dict[str, int] = field(default_factory=dict)  # 1190
    total_noncurrent_assets: Dict[str, int] = field(default_factory=dict)  # 1100

    # АКТИВ — II. Оборотные активы
    inventories: Dict[str, int] = field(default_factory=dict)  # 1210
    long_term_assets_for_sale: Dict[str, int] = field(default_factory=dict)  # 1215
    vat: Dict[str, int] = field(default_factory=dict)  # 1220
    receivables: Dict[str, int] = field(default_factory=dict)  # 1230
    financial_investments_current: Dict[str, int] = field(default_factory=dict)  # 1240
    cash: Dict[str, int] = field(default_factory=dict)  # 1250
    other_current_assets: Dict[str, int] = field(default_factory=dict)  # 1260
    total_current_assets: Dict[str, int] = field(default_factory=dict)  # 1200
    total_assets: Dict[str, int] = field(default_factory=dict)  # 1600

    # ПАССИВ — III. Капитал
    charter_capital: Dict[str, int] = field(default_factory=dict)  # 1310
    additional_capital: Dict[str, int] = field(default_factory=dict)  # 1350
    reserve_capital: Dict[str, int] = field(default_factory=dict)  # 1360
    retained_earnings: Dict[str, int] = field(default_factory=dict)  # 1370
    total_equity: Dict[str, int] = field(default_factory=dict)  # 1300

    # ПАССИВ — IV. Долгосрочные обязательства
    borrowings_noncurrent: Dict[str, int] = field(default_factory=dict)  # 1410
    deferred_tax_liabilities: Dict[str, int] = field(default_factory=dict)  # 1420
    estimated_liabilities_noncurrent: Dict[str, int] = field(default_factory=dict)  # 1430
    deferred_income_noncurrent: Dict[str, int] = field(default_factory=dict)  # 1440
    other_noncurrent_liabilities: Dict[str, int] = field(default_factory=dict)  # 1450
    total_noncurrent_liabilities: Dict[str, int] = field(default_factory=dict)  # 1400

    # ПАССИВ — V. Краткосрочные обязательства
    borrowings_current: Dict[str, int] = field(default_factory=dict)  # 1510
    accounts_payable: Dict[str, int] = field(default_factory=dict)  # 1520
    deferred_income_current: Dict[str, int] = field(default_factory=dict)  # 1530
    estimated_liabilities_current: Dict[str, int] = field(default_factory=dict)  # 1540
    other_current_liabilities: Dict[str, int] = field(default_factory=dict)  # 1550
    total_current_liabilities: Dict[str, int] = field(default_factory=dict)  # 1500
    total_liabilities: Dict[str, int] = field(default_factory=dict)  # 1700

    def get_value(self, code: str, date: str) -> int:
        """Возвращает значение по коду строки баланса и году. Если нет — 0."""
        field_name = CODE_TO_FIELD.get(code)
        if not field_name:
            return 0
        return getattr(self, field_name, {}).get(date, 0)
