from langchain_core.tools import tool

from agent.tools.utils import safe_div
from agent.tools.finance.calculation_cache import set_indicator


@tool(
    "calculate_cash_liquidity_ratio",
    description="Считает коэффициент абсолютной ликвидности",
)
def calculate_cash_liquidity_ratio(
    cash: float, short_term_investments: float, current_liabilities: float
) -> float:
    """
    Cash Liquidity Ratio = (Cash + Short-Term Investments) / Current Liabilities

    :param cash: Денежные средства
    :param short_term_investments: Краткосрочные финансовые вложения
    :param current_liabilities: Краткосрочные обязательства
    """
    result = safe_div(cash + short_term_investments, current_liabilities)
    set_indicator("Cash Liquidity Ratio", result)
    return result