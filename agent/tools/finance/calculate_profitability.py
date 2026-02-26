from langchain_core.tools import tool


@tool
def calculate_profitability(revenue: float,
                            net_profit: float,
                            gross_profit: float,
                            operating_profit: float) -> dict:
    """Посчитать показатели рентабельности"""

    return {
        "ROS": net_profit / revenue,
        "Gross_Margin": gross_profit / revenue,
        "Operating_Margin": operating_profit / revenue
    }
