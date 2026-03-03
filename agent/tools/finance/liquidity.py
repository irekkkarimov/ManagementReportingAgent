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
    return safe_div(current_assets - inventory, current_liabilities)


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
    return safe_div(cash + short_term_investments, current_liabilities)
