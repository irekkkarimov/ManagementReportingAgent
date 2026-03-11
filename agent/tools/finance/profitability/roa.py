from langchain_core.tools import tool

from agent.tools.finance.calculation_cache import set_indicator
from agent.tools.finance.inputs_cache import get_input
from agent.tools.utils import format_percent, safe_div

_NAME = "ROA"


@tool("calculate_roa", description="Считает ROA (Рентабельность активов). Данные берутся из кэша по году.")
def calculate_roa(year: str) -> str:
    """ROA = Чистая прибыль / Средние активы"""
    prev_year = str(int(year) - 1)
    avg_assets = (get_input(year, "total_assets") + get_input(prev_year, "total_assets")) / 2
    raw = safe_div(get_input(year, "net_profit"), avg_assets)
    set_indicator(_NAME, round(raw, 4))
    return format_percent(raw, _NAME)
