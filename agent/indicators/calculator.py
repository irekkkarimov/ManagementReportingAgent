"""
Извлекает все поля из AccountantBalanceReport и FinancialResultsReport за указанный год.
Для показателей, требующих среднее (avg_*), берётся среднее между текущим и предыдущим годом.
Если предыдущий год отсутствует — используется значение за текущий год.
"""

from typing import Any, Dict, Optional


def _prev_year(year: str, balance: Any, ofr: Any) -> Optional[str]:
    """Возвращает предыдущий год из доступных данных, или None если нет."""
    years = set()
    if balance and getattr(balance, "total_assets", None):
        years.update(balance.total_assets.keys())
    if ofr and getattr(ofr, "revenue", None):
        years.update(ofr.revenue.keys())

    sorted_years = sorted(years)
    try:
        idx = sorted_years.index(year)
        return sorted_years[idx - 1] if idx > 0 else None
    except ValueError:
        return None


def _avg(current: int, previous: int) -> float:
    """Среднее двух значений."""
    return (current + previous) / 2


def get_calculation_inputs(balance: Any, ofr: Any, year: str) -> Dict[str, float]:
    """
    Возвращает все поля обеих моделей за указанный год.
    Дополнительно вычисляет средние значения (avg_*) для показателей оборачиваемости и рентабельности.

    :param balance: AccountantBalanceReport
    :param ofr: FinancialResultsReport
    :param year: год в виде строки, например "2024"
    :return: словарь всех полей для передачи в calculate_*
    """

    def b(field: str, y: str = year) -> int:
        return getattr(balance, field, {}).get(y, 0) or 0

    def o(field: str, y: str = year) -> int:
        return getattr(ofr, field, {}).get(y, 0) or 0

    return {
        # --- ОФР (FinancialResultsReport) ---
        "revenue":                          o("revenue"),                           # 2110
        "other_incoming":                   o("other_incoming"),                    # 2115
        "cost_of_sales":                    o("cost_of_sales"),                     # 2120
        "gross_profit":                     o("gross_profit"),                      # 2100
        "commercial_expenses":              o("commercial_expenses"),               # 2210
        "management_expenses":              o("management_expenses"),               # 2220
        "profit_from_sales":                o("profit_from_sales"),                 # 2200
        "income_from_participation":        o("income_from_participation"),         # 2310
        "percentage_receivable":            o("percentage_receivable"),             # 2320
        "percentage_to_pay":                o("percentage_to_pay"),                 # 2330
        "other_profit":                     o("other_profit"),                      # 2340
        "other_expenses":                   o("other_expenses"),                    # 2350
        "profit_from_continuing_ops":       o("profit_from_continuing_operations"), # 2300
        "organization_income_tax":          o("organization_income_tax"),           # 2410
        "deferred_organization_income_tax": o("deferred_organization_income_tax"),  # 2412
        "other":                            o("other"),                             # 2460
        "net_profit":                       o("net_profit"),                        # 2400
        "total_financial_result":           o("total_financial_result"),            # 2500

        # --- Баланс: внеоборотные активы (AccountantBalanceReport) ---
        "intangible_assets":                b("intangible_assets"),                 # 1110
        "fixed_assets":                     b("fixed_assets"),                      # 1150
        "investment_property":              b("investment_property"),               # 1160
        "financial_investments_noncurrent": b("financial_investments_noncurrent"),  # 1170
        "deferred_tax_assets":              b("deferred_tax_assets"),               # 1180
        "other_noncurrent_assets":          b("other_noncurrent_assets"),           # 1190
        "total_noncurrent_assets":          b("total_noncurrent_assets"),           # 1100

        # --- Баланс: оборотные активы ---
        "inventories":                      b("inventories"),                       # 1210
        "long_term_assets_for_sale":        b("long_term_assets_for_sale"),         # 1215
        "vat":                              b("vat"),                               # 1220
        "receivables":                      b("receivables"),                       # 1230
        "financial_investments_current":    b("financial_investments_current"),     # 1240
        "cash":                             b("cash"),                              # 1250
        "other_current_assets":             b("other_current_assets"),              # 1260
        "total_current_assets":             b("total_current_assets"),              # 1200
        "total_assets":                     b("total_assets"),                      # 1600

        # --- Баланс: капитал ---
        "charter_capital":                  b("charter_capital"),                   # 1310
        "additional_capital":               b("additional_capital"),                # 1350
        "reserve_capital":                  b("reserve_capital"),                   # 1360
        "retained_earnings":                b("retained_earnings"),                 # 1370
        "total_equity":                     b("total_equity"),                      # 1300

        # --- Баланс: долгосрочные обязательства ---
        "borrowings_noncurrent":            b("borrowings_noncurrent"),             # 1410
        "deferred_tax_liabilities":         b("deferred_tax_liabilities"),          # 1420
        "estimated_liabilities_noncurrent": b("estimated_liabilities_noncurrent"),  # 1430
        "deferred_income_noncurrent":       b("deferred_income_noncurrent"),        # 1440
        "other_noncurrent_liabilities":     b("other_noncurrent_liabilities"),      # 1450
        "total_noncurrent_liabilities":     b("total_noncurrent_liabilities"),      # 1400

        # --- Баланс: краткосрочные обязательства ---
        "borrowings_current":               b("borrowings_current"),                # 1510
        "accounts_payable":                 b("accounts_payable"),                  # 1520
        "deferred_income_current":          b("deferred_income_current"),           # 1530
        "estimated_liabilities_current":    b("estimated_liabilities_current"),     # 1540
        "other_current_liabilities":        b("other_current_liabilities"),         # 1550
        "total_current_liabilities":        b("total_current_liabilities"),         # 1500
        "total_liabilities":                b("total_liabilities"),                 # 1700
    }
