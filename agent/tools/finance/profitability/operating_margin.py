from langchain.tools import tool

from agent.tools.utils import safe_div
from agent.tools.finance.calculation_cache import set_indicator


@tool("calculate_operating_margin", description="Считает Operating Margin (Операционная рентабельность)")
def calculate_operating_margin(
        revenue: float,
        cost_of_sales: float,
        commercial_expenses: float,
        management_expenses: float) -> float:
    """
    Calculate Operating Margin - Операционная рентабельность
    """
    operating_income = revenue + cost_of_sales + commercial_expenses + management_expenses

    result = safe_div(operating_income, revenue)
    set_indicator("Operating Margin", result)
    return result
