from langchain_core.tools import tool

from agent.tools.utils import safe_div


@tool(
    "calculate_current_liquidity_ratio",
    description="Считает коэффициент текущей ликвидности",
)
def calculate_current_liquidity_ratio(
    current_assets: float, current_liabilities: float
) -> float:
    """
    Current Liquidity Ratio = Current Assets / Current Liabilities

    :param current_assets: Оборотные активы
    :param current_liabilities: Краткосрочные обязательства
    """
    return safe_div(current_assets, current_liabilities)