from langchain_core.tools import tool

from agent.tools.finance.calculation_cache import set_indicator
from agent.tools.finance.inputs_cache import get_input
from agent.tools.utils import format_ratio, safe_div

_NAME = "Financial Stability Ratio"


@tool("calculate_financial_stability_ratio", description="Считает коэффициент финансовой устойчивости. Данные берутся из кэша по году.")
def calculate_financial_stability_ratio(year: str) -> str:
    """Financial Stability Ratio = (Собственный капитал + Долгосрочные обязательства) / Активы"""
    raw = safe_div(
        get_input(year, "total_equity") + get_input(year, "total_noncurrent_liabilities"),
        get_input(year, "total_assets"),
    )
    set_indicator(_NAME, round(raw, 4))
    return format_ratio(raw, _NAME)
