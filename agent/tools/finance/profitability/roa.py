from langchain_core.tools import tool

from agent.tools.utils import safe_div
from input_models.financial_results_report import FinancialResultsReport


@tool("calculate_roa", description="Считает ROA (Рентабельность активов)")
def calculate_roa(net_income: float, avg_assets: float) -> float:
    """Calculate ROA - Рентабельность активов"""
    return safe_div(net_income, avg_assets)

@tool("calculate_roa", description="Считает ROA (Рентабельность активов)")
def calculate_roa2(data: FinancialResultsReport) -> float:
    """Calculate ROA - Рентабельность активов"""
    return safe_div(data.net_profit, data.average_assets())