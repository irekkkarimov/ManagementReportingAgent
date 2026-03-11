from langchain_core.tools import tool

from agent.indicators.compute import compute_financial_stability_ratio
from agent.tools.finance.calculation_cache import set_indicator
from agent.tools.utils import format_ratio

_NAME = "Financial Stability Ratio"


@tool("calculate_financial_stability_ratio", description="Считает коэффициент финансовой устойчивости. Данные берутся из кэша по году.")
def calculate_financial_stability_ratio(year: str) -> str:
    """Financial Stability Ratio = (Собственный капитал + Долгосрочные обязательства) / Активы"""
    raw = compute_financial_stability_ratio(year)
    set_indicator(_NAME, round(raw, 4))
    return format_ratio(raw, _NAME)
