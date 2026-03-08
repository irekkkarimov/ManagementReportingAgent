from langchain_core.tools import tool

from agent.tools.utils import safe_div
from input_models.financial_results_report import FinancialResultsReport


@tool("calculate_total_asset_turnover", description="Считает Total Asset Turnover (Оборачиваемость активов)")
def calculate_total_asset_turnover(revenue: float, avg_assets: float) -> float:
    """
    Total Asset Turnover = Revenue / Average Total Assets
    """
    return safe_div(revenue, avg_assets)
