from langchain_core.tools import tool


@tool
def calculate_turnover(revenue: float,
                       total_assets: float,
                       cogs: float,
                       inventory: float) -> dict:
    """Посчитать показатели оборачиваемости"""

    return {
        "Asset_Turnover": revenue / total_assets,
        "Inventory_Turnover": cogs / inventory
    }