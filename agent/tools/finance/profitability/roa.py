from langchain_core.tools import tool

from agent.tools.utils import safe_div


@tool("calculate_roa", description="Считает ROA (Рентабельность активов)")
def calculate_roa(net_income: float, assets_end: float, assets_start: float) -> float:
    """Calculate ROA - Рентабельность активов"""
    avg_assets = (assets_end - assets_start) / 2

    return safe_div(net_income, avg_assets)
