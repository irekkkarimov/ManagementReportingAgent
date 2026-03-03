from langchain.tools import tool

from agent.tools.utils import safe_div
from input_models.financial_results_report import FinancialResultsReport


@tool("calculate_operating_margin", description="Считает Operating Margin (Операционная рентабельность)")
def calculate_operating_margin(operating_income: float, revenue: float) -> float:
    """
    Calculate Operating Margin - Операционная рентабельность
    """
    return safe_div(operating_income, revenue)

@tool("calculate_operating_margin", description="Считает Operating Margin (Операционная рентабельность)")
def calculate_operating_margin2(data: FinancialResultsReport) -> float:
    """
    Calculate Operating Margin - Операционная рентабельность
    """
    return safe_div(data.operating_profit, data.revenue)