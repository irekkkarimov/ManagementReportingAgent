from langchain_core.tools import tool

from agent.tools.utils import safe_div
from input_models.financial_results_report import FinancialResultsReport


@tool("calculate_payables_turnover", description="Считает Payables Turnover (Оборачиваемость кредиторской задолженности)")
def calculate_payables_turnover(cogs: float, avg_payables: float) -> float:
    """
    Payables Turnover = Cost of Goods Sold / Average Payables
    """
    return safe_div(cogs, avg_payables)
