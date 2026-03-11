from langchain_core.tools import tool

from agent.tools.finance.calculation_cache import set_indicator
from agent.tools.finance.inputs_cache import get_input
from agent.tools.utils import format_percent, safe_div

_NAME = "ROS"


@tool("calculate_ros", description="Считает ROS (Рентабельность продаж). Данные берутся из кэша по году.")
def calculate_ros(year: str) -> str:
    """ROS = Чистая прибыль / Выручка"""
    raw = safe_div(get_input(year, "net_profit"), get_input(year, "revenue"))
    set_indicator(_NAME, round(raw, 4))
    return format_percent(raw, _NAME)
