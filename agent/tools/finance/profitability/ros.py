from langchain.tools import tool

from agent.tools.utils import safe_div
from agent.tools.finance.calculation_cache import set_indicator


@tool("calculate_ros", description="Считает ROS (Рентабельность продаж)")
def calculate_ros(revenue: float, net_income: float) -> float:
    """
    Calculate ROS - Рентабельность продаж
    """
    result = safe_div(net_income, revenue)
    set_indicator("ROS", result)
    return result