from langchain_core.tools import tool

from agent.tools.utils import safe_div
from agent.tools.finance.calculation_cache import set_indicator
from input_models.financial_results_report import FinancialResultsReport


@tool("calculate_inventory_turnover", description="Считает Inventory Turnover (Оборачиваемость запасов)")
def calculate_inventory_turnover(cogs: float, avg_inventory: float) -> float:
    """
    Inventory Turnover = Cost of Goods Sold / Average Inventory
    """
    result = safe_div(cogs, avg_inventory)
    set_indicator("Inventory Turnover", result)
    return result