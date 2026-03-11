from langchain_core.tools import tool

from agent.indicators.compute import compute_total_asset_turnover
from agent.tools.finance.calculation_cache import set_indicator
from agent.tools.utils import format_ratio

_NAME = "Total Asset Turnover"


@tool("calculate_total_asset_turnover", description="Считает Total Asset Turnover (Оборачиваемость активов). Данные берутся из кэша по году.")
def calculate_total_asset_turnover(year: str) -> str:
    """Total Asset Turnover = Выручка / Средние активы"""
    raw = compute_total_asset_turnover(year)
    set_indicator(_NAME, round(raw, 4))
    return format_ratio(raw, _NAME)
