from langchain_core.tools import tool

from agent.tools.finance.calculation_cache import set_indicator
from agent.tools.finance.inputs_cache import get_input
from agent.tools.utils import format_ratio, safe_div

_NAME = "Inventory Turnover"


@tool("calculate_inventory_turnover", description="Считает Inventory Turnover (Оборачиваемость запасов). Данные берутся из кэша по году.")
def calculate_inventory_turnover(year: str) -> str:
    """Inventory Turnover = Себестоимость / Средние запасы"""
    prev_year = str(int(year) - 1)
    avg_inventory = (get_input(year, "inventories") + get_input(prev_year, "inventories")) / 2
    raw = safe_div(get_input(year, "cost_of_sales"), avg_inventory)
    set_indicator(_NAME, round(raw, 4))
    return format_ratio(raw, _NAME)
