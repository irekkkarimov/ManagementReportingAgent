from langchain_core.tools import tool

from agent.tools.finance.calculation_cache import set_indicator
from agent.tools.finance.inputs_cache import get_input
from agent.tools.utils import format_ratio, safe_div

_NAME = "Payables Turnover"


@tool("calculate_payables_turnover", description="Считает Payables Turnover (Оборачиваемость кредиторской задолженности). Данные берутся из кэша по году.")
def calculate_payables_turnover(year: str) -> str:
    """Payables Turnover = Себестоимость / Средняя кредиторская задолженность"""
    prev_year = str(int(year) - 1)
    avg_payables = (get_input(year, "accounts_payable") + get_input(prev_year, "accounts_payable")) / 2
    raw = safe_div(get_input(year, "cost_of_sales"), avg_payables)
    set_indicator(_NAME, round(raw, 4))
    return format_ratio(raw, _NAME)
