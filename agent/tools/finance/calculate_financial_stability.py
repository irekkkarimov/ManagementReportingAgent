from langchain_core.messages import tool


@tool
def calculate_financial_stability(debt: float,
                                  equity: float,
                                  total_assets: float) -> dict:
    """Посчитать показатели финансовой стабильность"""

    return {
        "Debt_to_Equity": debt / equity,
        "Debt_Ratio": debt / total_assets,
        "Equity_Ratio": equity / total_assets
    }