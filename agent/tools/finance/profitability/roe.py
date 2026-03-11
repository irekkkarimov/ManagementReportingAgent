from langchain_core.tools import tool

from agent.indicators.compute import compute_roe
from agent.tools.finance.calculation_cache import set_indicator
from agent.tools.utils import format_percent

_NAME = "ROE"


@tool("calculate_roe", description="Считает ROE (Рентабельность собственного капитала). Данные берутся из кэша по году.")
def calculate_roe(year: str) -> str:
    """ROE = Чистая прибыль / Средний собственный капитал"""
    raw = compute_roe(year)
    set_indicator(_NAME, round(raw, 4))
    return format_percent(raw, _NAME)
