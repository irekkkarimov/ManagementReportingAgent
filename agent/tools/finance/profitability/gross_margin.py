from langchain.tools import tool

from agent.tools.utils import safe_div
from agent.tools.finance.calculation_cache import set_indicator


@tool("calculate_gross_margin", description="Считает Gross Margin (Валовая рентабельность)")
def calculate_gross_margin(revenue: float, gross_profit: float) -> float:
    """
    Calculate Gross Margin - Валовая рентабельность
    """
    result = safe_div(gross_profit, revenue)
    set_indicator("Gross Margin", result)
    return result
