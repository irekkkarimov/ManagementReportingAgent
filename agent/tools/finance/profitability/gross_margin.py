from langchain_core.tools import tool

from agent.indicators.compute import compute_gross_margin
from agent.tools.finance.calculation_cache import set_indicator
from agent.tools.utils import format_percent

_NAME = "Gross Margin"


@tool("calculate_gross_margin", description="Считает Gross Margin (Валовую маржу). Данные берутся из кэша по году.")
def calculate_gross_margin(year: str) -> str:
    """Gross Margin = Валовая прибыль / Выручка"""
    raw = compute_gross_margin(year)
    set_indicator(_NAME, round(raw, 4))
    return format_percent(raw, _NAME)
