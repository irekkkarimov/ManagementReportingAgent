from langchain_core.tools import tool

from agent.tools.finance.calculation_cache import set_indicator
from agent.tools.finance.inputs_cache import get_input
from agent.tools.utils import format_percent, safe_div

_NAME = "Gross Margin"


@tool("calculate_gross_margin", description="Считает Gross Margin (Валовая рентабельность). Данные берутся из кэша по году.")
def calculate_gross_margin(year: str) -> str:
    """Gross Margin = Валовая прибыль / Выручка"""
    raw = safe_div(get_input(year, "gross_profit"), get_input(year, "revenue"))
    set_indicator(_NAME, round(raw, 4))
    return format_percent(raw, _NAME)
