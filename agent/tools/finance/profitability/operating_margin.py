from langchain_core.tools import tool

from agent.tools.finance.calculation_cache import set_indicator
from agent.tools.finance.inputs_cache import get_input
from agent.tools.utils import format_percent, safe_div

_NAME = "Operating Margin"


@tool("calculate_operating_margin", description="Считает Operating Margin (Операционная рентабельность). Данные берутся из кэша по году.")
def calculate_operating_margin(year: str) -> str:
    """Operating Margin = (Выручка + Себестоимость + Коммерческие + Управленческие расходы) / Выручка"""
    revenue = get_input(year, "revenue")
    operating_income = (
        revenue
        + get_input(year, "cost_of_sales")
        + get_input(year, "commercial_expenses")
        + get_input(year, "management_expenses")
    )
    raw = safe_div(operating_income, revenue)
    set_indicator(_NAME, round(raw, 4))
    return format_percent(raw, _NAME)
