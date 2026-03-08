from langchain.tools import tool

from agent.tools.utils import safe_div


@tool("calculate_roe", description="Считает ROE (Рентабельность собственного капитала)")
def calculate_roe(net_income: float, equity_end: float, equity_start: float) -> float:
    """Calculates ROE - Рентабельность собственного капитала"""
    avg_equity = (equity_end - equity_start) / 2

    return safe_div(net_income, avg_equity)
