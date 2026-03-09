from langchain_core.tools import tool

from agent.tools.utils import safe_div
from agent.tools.finance.calculation_cache import set_indicator


@tool(
    "calculate_financial_stability_ratio",
    description="Считает коэффициент финансовой устойчивости",
)
def calculate_financial_stability_ratio(
    equity: float, long_term_liabilities: float, total_assets: float
) -> float:
    """
    Financial Stability Ratio = (Equity + Long-Term Liabilities) / Total Assets

    :param equity: Собственный капитал
    :param long_term_liabilities: Долгосрочные обязательства
    :param total_assets: Общие активы
    """
    result = safe_div(equity + long_term_liabilities, total_assets)
    set_indicator("Financial Stability Ratio", result)
    return result