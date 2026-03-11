from langchain_core.tools import tool

from agent.indicators.compute import compute_receivables_turnover
from agent.tools.finance.calculation_cache import set_indicator
from agent.tools.utils import format_ratio

_NAME = "Receivables Turnover"


@tool("calculate_receivables_turnover", description="Считает Receivables Turnover (Оборачиваемость дебиторской задолженности). Данные берутся из кэша по году.")
def calculate_receivables_turnover(year: str) -> str:
    """Receivables Turnover = Выручка / Средняя дебиторская задолженность"""
    raw = compute_receivables_turnover(year)
    set_indicator(_NAME, round(raw, 4))
    return format_ratio(raw, _NAME)
