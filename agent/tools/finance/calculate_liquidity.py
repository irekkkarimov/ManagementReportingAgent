from langchain_core.tools import tool


@tool
def calculate_liquidity(current_assets: float,
                        current_liabilities: float,
                        inventory: float,
                        cash: float) -> dict:
    """Посчитать показатели ликвидности"""

    return {
        "Current_Ratio": current_assets / current_liabilities,
        "Quick_Ratio": (current_assets - inventory) / current_liabilities,
        "Cash_Ratio": cash / current_liabilities
    }