from langchain_core.tools import tool

from agent.tools.utils import safe_div
from agent.tools.finance.calculation_cache import set_indicator
from input_models.financial_results_report import FinancialResultsReport


@tool("calculate_total_asset_turnover", description="Считает Total Asset Turnover (Оборачиваемость активов)")
def calculate_total_asset_turnover(revenue: float, avg_assets: float) -> float:
    """
    Total Asset Turnover = Revenue / Average Total Assets
    """
    result = safe_div(revenue, avg_assets)
    set_indicator("Total Asset Turnover", result)
    return result
