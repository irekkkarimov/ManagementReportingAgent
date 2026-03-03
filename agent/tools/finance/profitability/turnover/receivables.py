from langchain_core.tools import tool

from agent.tools.utils import safe_div
from input_models.financial_results_report import FinancialResultsReport


@tool("calculate_receivables_turnover", description="Считает Receivables Turnover (Оборачиваемость дебиторской задолженности)")
def calculate_receivables_turnover(revenue: float, avg_receivables: float) -> float:
    """
    Receivables Turnover = Revenue / Average Receivables
    """
    return safe_div(revenue, avg_receivables)


@tool("calculate_receivables_turnover", description="Считает Receivables Turnover из объекта данных")
def calculate_receivables_turnover2(data: FinancialResultsReport) -> float:
    """
    Receivables Turnover = Revenue / Average Receivables
    """
    return safe_div(data.revenue, data.average_receivables())