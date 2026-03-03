from langchain.tools import tool

from agent.tools.utils import safe_div
from input_models.financial_results_report import FinancialResultsReport


@tool("calculate_roe", description="Считает ROE (Рентабельность собственного капитала)")
def calculate_roe(net_income: float, avg_equity: float) -> float:
    """Calculates ROE - Рентабельность собственного капитала"""
    return safe_div(net_income, avg_equity)


@tool("calculate_roe", description="Считает ROE (Рентабельность собственного капитала)")
def calculate_roe2(data: FinancialResultsReport) -> float:
    """Calculates ROE - Рентабельность собственного капитала"""
    return safe_div(data.net_profit, data.average_equity())