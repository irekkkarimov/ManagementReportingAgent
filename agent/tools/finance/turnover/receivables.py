from langchain_core.tools import tool

from agent.tools.utils import safe_div
from agent.tools.finance.calculation_cache import set_indicator
from input_models.financial_results_report import FinancialResultsReport


@tool("calculate_receivables_turnover", description="Считает Receivables Turnover (Оборачиваемость дебиторской задолженности)")
def calculate_receivables_turnover(revenue: float, avg_receivables: float) -> float:
    """
    Receivables Turnover = Revenue / Average Receivables
    """
    result = safe_div(revenue, avg_receivables)
    set_indicator("Receivables Turnover", result)
    return result
