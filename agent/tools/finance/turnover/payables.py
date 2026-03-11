from langchain_core.tools import tool

from agent.indicators.compute import compute_payables_turnover
from agent.tools.finance.calculation_cache import set_indicator
from agent.tools.utils import format_ratio

_NAME = "Payables Turnover"


@tool("calculate_payables_turnover", description="Считает Payables Turnover (Оборачиваемость кредиторской задолженности). Данные берутся из кэша по году.")
def calculate_payables_turnover(year: str) -> str:
    """Payables Turnover = Себестоимость / Средняя кредиторская задолженность"""
    raw = compute_payables_turnover(year)
    set_indicator(_NAME, round(raw, 4))
    return format_ratio(raw, _NAME)
