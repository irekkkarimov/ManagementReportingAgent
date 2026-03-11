from langchain_core.tools import tool

from agent.indicators.compute import compute_roa
from agent.tools.finance.calculation_cache import set_indicator
from agent.tools.utils import format_percent

_NAME = "ROA"


@tool("calculate_roa", description="Считает ROA (Рентабельность активов). Данные берутся из кэша по году.")
def calculate_roa(year: str) -> str:
    """ROA = Чистая прибыль / Средние активы"""
    raw = compute_roa(year)
    set_indicator(_NAME, round(raw, 4))
    return format_percent(raw, _NAME)
