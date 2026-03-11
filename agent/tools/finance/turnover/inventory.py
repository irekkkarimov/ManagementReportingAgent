from langchain_core.tools import tool

from agent.indicators.compute import compute_inventory_turnover
from agent.tools.finance.calculation_cache import set_indicator
from agent.tools.utils import format_ratio

_NAME = "Inventory Turnover"


@tool("calculate_inventory_turnover", description="Считает Inventory Turnover (Оборачиваемость запасов). Данные берутся из кэша по году.")
def calculate_inventory_turnover(year: str) -> str:
    """Inventory Turnover = Себестоимость / Средние запасы"""
    raw = compute_inventory_turnover(year)
    set_indicator(_NAME, round(raw, 4))
    return format_ratio(raw, _NAME)
