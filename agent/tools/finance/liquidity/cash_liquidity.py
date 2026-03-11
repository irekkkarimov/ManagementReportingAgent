from langchain_core.tools import tool

from agent.indicators.compute import compute_cash_liquidity_ratio
from agent.tools.finance.calculation_cache import set_indicator
from agent.tools.utils import format_ratio

_NAME = "Cash Liquidity Ratio"


@tool("calculate_cash_liquidity_ratio", description="Считает коэффициент абсолютной ликвидности. Данные берутся из кэша по году.")
def calculate_cash_liquidity_ratio(year: str) -> str:
    """Cash Liquidity Ratio = (Денежные средства + Краткосрочные вложения) / Краткосрочные обязательства"""
    raw = compute_cash_liquidity_ratio(year)
    set_indicator(_NAME, round(raw, 4))
    return format_ratio(raw, _NAME)
