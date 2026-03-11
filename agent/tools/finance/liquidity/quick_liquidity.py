from langchain_core.tools import tool

from agent.indicators.compute import compute_quick_liquidity_ratio
from agent.tools.finance.calculation_cache import set_indicator
from agent.tools.utils import format_ratio

_NAME = "Quick Liquidity Ratio"


@tool("calculate_quick_liquidity_ratio", description="Считает коэффициент быстрой ликвидности. Данные берутся из кэша по году.")
def calculate_quick_liquidity_ratio(year: str) -> str:
    """Quick Liquidity Ratio = (Оборотные активы - Запасы) / Краткосрочные обязательства"""
    raw = compute_quick_liquidity_ratio(year)
    set_indicator(_NAME, round(raw, 4))
    return format_ratio(raw, _NAME)
