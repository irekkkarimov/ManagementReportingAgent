from langchain.tools import tool

from agent.tools.utils import safe_div

@tool("calculate_operating_margin", description="Считает Operating Margin (Операционная рентабельность)")
def calculate_operating_margin(operating_income: float, revenue: float) -> float:
    """
    Calculate Operating Margin - Операционная рентабельность
    """
    return safe_div(operating_income, revenue)