from pandas.core.interchange.dataframe_protocol import DataFrame

from input_models.utils import get_value_by_code
import consts.finance as consts


class FinancialResultsReport:
    # ===== Отчет о прибылях и убытках =====
    year: int
    revenue: float  # Выручка
    other_incoming: float
    cost_of_sales: float  # Себестоимость продаж (COGS)
    gross_profit: float  # Операционная прибыль
    commercial_expenses: float
    management_expenses: float
    profit_from_sales: float
    income_from_participation: float
    percentage_receivable: float
    percentage_to_pay: float
    other_profit: float
    other_expenses: float
    profit_from_continuing_operations: float
    organization_income_tax: float
    deferred_organization_income_tax: float
    other: float
    net_profit: float  # Чистая прибыль

    def __init__(self, df: DataFrame, year: int):
        self.year = year

        self.revenue = get_value_by_code(df, consts.REVENUE)
        self.other_incoming = get_value_by_code(df, consts.OTHER_INCOMING)
        self.cost_of_sales = get_value_by_code(df, consts.COST_OF_SALES)
        self.gross_profit = get_value_by_code(df, consts.GROSS_PROFIT)
        self.commercial_expenses = get_value_by_code(df, consts.COMMERCIAL_EXPENSES)
        self.management_expenses = get_value_by_code(df, consts.MANAGEMENT_EXPENSES)
        self.profit_from_sales = get_value_by_code(df, consts.PROFIT_FROM_SALES)
        self.income_from_participation = get_value_by_code(df, consts.INCOME_FROM_PARTICIPATION)
        self.percentage_receivable = get_value_by_code(df, consts.PERCENTAGE_RECEIVABLE)
        self.percentage_to_pay = get_value_by_code(df, consts.PERCENTAGE_TO_PAY)
        self.other_profit = get_value_by_code(df, consts.OTHER_PROFIT)
        self.other_expenses = get_value_by_code(df, consts.OTHER_EXPENSES)
        self.profit_from_continuing_operations = get_value_by_code(df, consts.PROFIT_FROM_CONTINUING_OPERATIONS)
        self.organization_income_tax = get_value_by_code(df, consts.ORGANIZATION_INCOME_TAX)
        self.deferred_organization_income_tax = get_value_by_code(df, consts.DEFERRED_ORGANIZATION_INCOME_TAX)
        self.other = get_value_by_code(df, consts.OTHER)
        self.net_profit = get_value_by_code(df, consts.NET_PROFIT)
