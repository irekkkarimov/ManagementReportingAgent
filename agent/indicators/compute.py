"""
Чистые функции расчёта финансовых показателей.
Не зависят от LangChain — читают только из inputs_cache.

Используются как инструментами calculate_*, так и generate_excel_report напрямую.
Все функции возвращают Optional[float]: None означает отсутствие данных (не то же самое, что 0).
"""

from typing import Callable, List, NamedTuple, Optional

from agent.tools.finance.inputs_cache import get_input
from agent.tools.utils import safe_div


def _avg(a: Optional[float], b: Optional[float]) -> Optional[float]:
    """
    Среднее двух значений с учётом None.
    Если оба None — None. Если одно None — берём только имеющееся.
    """
    if a is None and b is None:
        return None
    if a is None:
        return b
    if b is None:
        return a
    return (a + b) / 2


def _add(*args: Optional[float]) -> Optional[float]:
    """
    Сумма нескольких слагаемых. None-значения пропускаются.
    Если все None — возвращает None.
    """
    vals = [v for v in args if v is not None]
    return sum(vals) if vals else None


def _sub(a: Optional[float], b: Optional[float]) -> Optional[float]:
    """Вычитание: None в любом операнде → None."""
    if a is None or b is None:
        return None
    return a - b


# ---------------------------------------------------------------------------
# Рентабельность
# ---------------------------------------------------------------------------

def compute_ros(year: str) -> Optional[float]:
    return safe_div(get_input(year, "net_profit"), get_input(year, "revenue"))


def compute_roa(year: str) -> Optional[float]:
    prev = str(int(year) - 1)
    return safe_div(
        get_input(year, "net_profit"),
        _avg(get_input(year, "total_assets"), get_input(prev, "total_assets")),
    )


def compute_roe(year: str) -> Optional[float]:
    prev = str(int(year) - 1)
    return safe_div(
        get_input(year, "net_profit"),
        _avg(get_input(year, "total_equity"), get_input(prev, "total_equity")),
    )


def compute_gross_margin(year: str) -> Optional[float]:
    return safe_div(get_input(year, "gross_profit"), get_input(year, "revenue"))


def compute_operating_margin(year: str) -> Optional[float]:
    revenue = get_input(year, "revenue")
    operating_income = _add(
        revenue,
        get_input(year, "cost_of_sales"),
        get_input(year, "commercial_expenses"),
        get_input(year, "management_expenses"),
    )
    return safe_div(operating_income, revenue)


# ---------------------------------------------------------------------------
# Оборачиваемость
# ---------------------------------------------------------------------------

def compute_total_asset_turnover(year: str) -> Optional[float]:
    prev = str(int(year) - 1)
    return safe_div(
        get_input(year, "revenue"),
        _avg(get_input(year, "total_assets"), get_input(prev, "total_assets")),
    )


def compute_inventory_turnover(year: str) -> Optional[float]:
    prev = str(int(year) - 1)
    return safe_div(
        get_input(year, "cost_of_sales"),
        _avg(get_input(year, "inventories"), get_input(prev, "inventories")),
    )


def compute_receivables_turnover(year: str) -> Optional[float]:
    prev = str(int(year) - 1)
    return safe_div(
        get_input(year, "revenue"),
        _avg(get_input(year, "receivables"), get_input(prev, "receivables")),
    )


def compute_payables_turnover(year: str) -> Optional[float]:
    prev = str(int(year) - 1)
    return safe_div(
        get_input(year, "cost_of_sales"),
        _avg(get_input(year, "accounts_payable"), get_input(prev, "accounts_payable")),
    )


# ---------------------------------------------------------------------------
# Финансовая устойчивость
# ---------------------------------------------------------------------------

def compute_financial_stability_ratio(year: str) -> Optional[float]:
    return safe_div(
        _add(get_input(year, "total_equity"), get_input(year, "total_noncurrent_liabilities")),
        get_input(year, "total_assets"),
    )


# ---------------------------------------------------------------------------
# Ликвидность
# ---------------------------------------------------------------------------

def compute_current_liquidity_ratio(year: str) -> Optional[float]:
    return safe_div(
        get_input(year, "total_current_assets"),
        get_input(year, "total_current_liabilities"),
    )


def compute_quick_liquidity_ratio(year: str) -> Optional[float]:
    return safe_div(
        _sub(get_input(year, "total_current_assets"), get_input(year, "inventories")),
        get_input(year, "total_current_liabilities"),
    )


def compute_cash_liquidity_ratio(year: str) -> Optional[float]:
    return safe_div(
        _add(get_input(year, "cash"), get_input(year, "financial_investments_current")),
        get_input(year, "total_current_liabilities"),
    )


# ---------------------------------------------------------------------------
# Реестр всех показателей
# ---------------------------------------------------------------------------

class IndicatorDef(NamedTuple):
    name: str
    section: str
    fn: Callable[[str], float]
    is_percent: bool


ALL_INDICATORS: List[IndicatorDef] = [
    IndicatorDef("Рентабельность продаж (ROS)",                 "Рентабельность",         compute_ros,                      True),
    IndicatorDef("Рентабельность активов (ROA)",                "Рентабельность",         compute_roa,                      True),
    IndicatorDef("Рентабельность капитала (ROE)",               "Рентабельность",         compute_roe,                      True),
    IndicatorDef("Валовая маржа",                               "Рентабельность",         compute_gross_margin,             True),
    IndicatorDef("Операционная маржа",                          "Рентабельность",         compute_operating_margin,         True),
    IndicatorDef("Оборачиваемость активов",                     "Оборачиваемость",        compute_total_asset_turnover,     False),
    IndicatorDef("Оборачиваемость запасов",                     "Оборачиваемость",        compute_inventory_turnover,       False),
    IndicatorDef("Оборачиваемость дебиторской задолженности",   "Оборачиваемость",        compute_receivables_turnover,     False),
    IndicatorDef("Оборачиваемость кредиторской задолженности",  "Оборачиваемость",        compute_payables_turnover,        False),
    IndicatorDef("Коэффициент финансовой устойчивости",         "Финансовая устойчивость", compute_financial_stability_ratio,False),
    IndicatorDef("Коэффициент текущей ликвидности",             "Ликвидность",            compute_current_liquidity_ratio,  False),
    IndicatorDef("Коэффициент быстрой ликвидности",             "Ликвидность",            compute_quick_liquidity_ratio,    False),
    IndicatorDef("Коэффициент абсолютной ликвидности",          "Ликвидность",            compute_cash_liquidity_ratio,     False),
]
