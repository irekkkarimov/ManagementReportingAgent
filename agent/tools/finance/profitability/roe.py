from langchain.tools import tool

from agent.tools.utils import safe_div
from agent.tools.finance.calculation_cache import set_indicator


@tool("calculate_roe", description="Считает ROE (Рентабельность собственного капитала)")
def calculate_roe(net_income: float, equity_end: float, equity_start: float) -> float:
    """Calculates ROE - Рентабельность собственного капитала"""
    avg_equity = (equity_end + equity_start) / 2

    result = safe_div(net_income, avg_equity)
    set_indicator("ROE", result)
    return result
