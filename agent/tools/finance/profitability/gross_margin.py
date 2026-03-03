from langchain.tools import tool

from agent.tools.utils import safe_div
from input_models.financial_results_report import FinancialResultsReport


@tool("calculate_gross_margin", description="Считает Gross Margin (Валовая рентабельность)")
def calculate_gross_margin(revenue: float, gross_profit: float) -> float:
    """
    Calculate Gross Margin - Валовая рентабельность
    """
    return safe_div(gross_profit, revenue)

@tool("calculate_gross_margin", description="Считает Gross Margin (Валовая рентабельность)")
def calculate_gross_margin2(data: FinancialResultsReport) -> float:
    """
    Calculate Gross Margin - Валовая рентабельность
    """
    return safe_div(data.gross_profit, data.revenue)