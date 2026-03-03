from langchain.tools import tool

from agent.tools.utils import safe_div
from input_models.financial_results_report import FinancialResultsReport


@tool("calculate_ros", description="Считает ROS (Рентабельность продаж)")
def calculate_ros(revenue: float, net_income: float) -> float:
    """
    Calculate ROS - Рентабельность продаж
    """
    return safe_div(net_income, revenue)

@tool("calculate_ros", description="Считает ROS (Рентабельность продаж)")
def calculate_ros2(data: FinancialResultsReport) -> float:
    """
    Calculate ROS - Рентабельность продаж
    """
    return safe_div(data.net_profit, data.revenue)