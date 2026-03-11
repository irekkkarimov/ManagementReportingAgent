from langchain_core.tools import tool

from agent.tools.finance.calculation_cache import set_indicator
from agent.tools.finance.inputs_cache import get_input
from agent.tools.utils import format_ratio, safe_div

_NAME = "Cash Liquidity Ratio"


@tool("calculate_cash_liquidity_ratio", description="Считает коэффициент абсолютной ликвидности. Данные берутся из кэша по году.")
def calculate_cash_liquidity_ratio(year: str) -> str:
    """Cash Liquidity Ratio = (Денежные средства + Краткосрочные вложения) / Краткосрочные обязательства"""
    raw = safe_div(
        get_input(year, "cash") + get_input(year, "financial_investments_current"),
        get_input(year, "total_current_liabilities"),
    )
    set_indicator(_NAME, round(raw, 4))
    return format_ratio(raw, _NAME)
