from langchain_core.tools import tool

from agent.tools.finance.calculation_cache import set_indicator
from agent.tools.finance.inputs_cache import get_input
from agent.tools.utils import format_percent, safe_div

_NAME = "ROE"


@tool("calculate_roe", description="Считает ROE (Рентабельность собственного капитала). Данные берутся из кэша по году.")
def calculate_roe(year: str) -> str:
    """ROE = Чистая прибыль / Средний собственный капитал"""
    prev_year = str(int(year) - 1)
    avg_equity = (get_input(year, "total_equity") + get_input(prev_year, "total_equity")) / 2
    raw = safe_div(get_input(year, "net_profit"), avg_equity)
    set_indicator(_NAME, round(raw, 4))
    return format_percent(raw, _NAME)
