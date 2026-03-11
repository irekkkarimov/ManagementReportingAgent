from langchain_core.tools import tool

from agent.indicators.compute import compute_ros
from agent.tools.finance.calculation_cache import set_indicator
from agent.tools.utils import format_percent

_NAME = "ROS"


@tool("calculate_ros", description="Считает ROS (Рентабельность продаж). Данные берутся из кэша по году.")
def calculate_ros(year: str) -> str:
    """ROS = Чистая прибыль / Выручка"""
    raw = compute_ros(year)
    set_indicator(_NAME, round(raw, 4))
    return format_percent(raw, _NAME)
