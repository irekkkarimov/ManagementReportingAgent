from langchain_core.tools import tool

from agent.tools.utils import safe_div
from agent.tools.finance.calculation_cache import set_indicator


@tool(
    "calculate_quick_liquidity_ratio",
    description="Считает коэффициент быстрой ликвидности",
)
def calculate_quick_liquidity_ratio(
    current_assets: float, inventory: float, current_liabilities: float
) -> float:
    """
    Quick Liquidity Ratio = (Current Assets - Inventory) / Current Liabilities

    :param current_assets: Оборотные активы
    :param inventory: Запасы
    :param current_liabilities: Краткосрочные обязательства
    """
    result = safe_div(current_assets - inventory, current_liabilities)
    set_indicator("Quick Liquidity Ratio", result)
    return result