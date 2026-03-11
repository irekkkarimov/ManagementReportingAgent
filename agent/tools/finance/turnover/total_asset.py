from langchain_core.tools import tool

from agent.tools.finance.calculation_cache import set_indicator
from agent.tools.finance.inputs_cache import get_input
from agent.tools.utils import format_ratio, safe_div

_NAME = "Total Asset Turnover"


@tool("calculate_total_asset_turnover", description="Считает Total Asset Turnover (Оборачиваемость активов). Данные берутся из кэша по году.")
def calculate_total_asset_turnover(year: str) -> str:
    """Total Asset Turnover = Выручка / Средние активы"""
    prev_year = str(int(year) - 1)
    avg_assets = (get_input(year, "total_assets") + get_input(prev_year, "total_assets")) / 2
    raw = safe_div(get_input(year, "revenue"), avg_assets)
    set_indicator(_NAME, round(raw, 4))
    return format_ratio(raw, _NAME)
