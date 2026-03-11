from langchain_core.tools import tool

from agent.indicators.compute import compute_operating_margin
from agent.tools.finance.calculation_cache import set_indicator
from agent.tools.utils import format_percent

_NAME = "Operating Margin"


@tool("calculate_operating_margin", description="Считает Operating Margin (Операционную маржу). Данные берутся из кэша по году.")
def calculate_operating_margin(year: str) -> str:
    """Operating Margin = Операционная прибыль / Выручка"""
    raw = compute_operating_margin(year)
    set_indicator(_NAME, round(raw, 4))
    return format_percent(raw, _NAME)
