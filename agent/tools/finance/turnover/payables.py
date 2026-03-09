from langchain_core.tools import tool

from agent.tools.utils import safe_div
from agent.tools.finance.calculation_cache import set_indicator
from input_models.financial_results_report import FinancialResultsReport


@tool("calculate_payables_turnover", description="Считает Payables Turnover (Оборачиваемость кредиторской задолженности)")
def calculate_payables_turnover(cogs: float, avg_payables: float) -> float:
    """
    Payables Turnover = Cost of Goods Sold / Average Payables
    """
    result = safe_div(cogs, avg_payables)
    set_indicator("Payables Turnover", result)
    return result
