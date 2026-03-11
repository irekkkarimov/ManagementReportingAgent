from langchain_core.tools import tool

from agent.tools.finance.calculation_cache import set_indicator
from agent.tools.finance.inputs_cache import get_input
from agent.tools.utils import format_ratio, safe_div

_NAME = "Current Liquidity Ratio"


@tool("calculate_current_liquidity_ratio", description="Считает коэффициент текущей ликвидности. Данные берутся из кэша по году.")
def calculate_current_liquidity_ratio(year: str) -> str:
    """Current Liquidity Ratio = Оборотные активы / Краткосрочные обязательства"""
    raw = safe_div(get_input(year, "total_current_assets"), get_input(year, "total_current_liabilities"))
    set_indicator(_NAME, round(raw, 4))
    return format_ratio(raw, _NAME)
