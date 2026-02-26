from langchain.tools import tool

from agent.tools.utils import safe_div

@tool("calculate_ros", description="Считает ROS (Рентабельность продаж)")
def calculate_ros(revenue: float, net_income: float) -> float:
    """
    Calculate ROS - Рентабельность продаж
    """
    return safe_div(net_income, revenue)