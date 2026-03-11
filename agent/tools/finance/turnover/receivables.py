from langchain_core.tools import tool

from agent.tools.finance.calculation_cache import set_indicator
from agent.tools.finance.inputs_cache import get_input
from agent.tools.utils import format_ratio, safe_div

_NAME = "Receivables Turnover"


@tool("calculate_receivables_turnover", description="Считает Receivables Turnover (Оборачиваемость дебиторской задолженности). Данные берутся из кэша по году.")
def calculate_receivables_turnover(year: str) -> str:
    """Receivables Turnover = Выручка / Средняя дебиторская задолженность"""
    prev_year = str(int(year) - 1)
    avg_receivables = (get_input(year, "receivables") + get_input(prev_year, "receivables")) / 2
    raw = safe_div(get_input(year, "revenue"), avg_receivables)
    set_indicator(_NAME, round(raw, 4))
    return format_ratio(raw, _NAME)
