from langchain_core.tools import tool

from agent.tools.utils import safe_div
from input_models.financial_results_report import FinancialResultsReport


@tool("calculate_inventory_turnover", description="Считает Inventory Turnover (Оборачиваемость запасов)")
def calculate_inventory_turnover(cogs: float, avg_inventory: float) -> float:
    """
    Inventory Turnover = Cost of Goods Sold / Average Inventory
    """
    return safe_div(cogs, avg_inventory)