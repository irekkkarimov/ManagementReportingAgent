import pandas as pd

class DataPostprocessor:
    def prepare(self, df: pd.DataFrame):
        df = df.copy()
        df["month"] = df["date"].dt.to_period("M").astype(str)

        expense_categories = (
            df[df["amount"] < 0]["category"]
            .dropna()
            .unique()
            .tolist()
        )

        revenue_categories = (
            df[df["amount"] > 0]["category"]
            .dropna()
            .unique()
            .tolist()
        )

        # расходы (берём модуль, чтобы не было минусов в таблице)
        expenses_table = (
            df[df["amount"] < 0]
            .pivot_table(
                index="category",
                columns="month",
                values="amount",
                aggfunc="sum",
                fill_value=0,
            )
            .abs()
            .reindex(expense_categories)
        )

        # доходы
        revenue_table = (
            df[df["amount"] > 0]
            .pivot_table(
                index="category",
                columns="month",
                values="amount",
                aggfunc="sum",
                fill_value=0,
            )
            .reindex(revenue_categories)
        )

        # итоговые строки
        total_expenses = expenses_table.sum(axis=0)
        total_revenue = revenue_table.sum(axis=0)
        net_profit = total_revenue - total_expenses

        total_block = pd.DataFrame(
            [total_expenses, total_revenue, net_profit],
            index=[
                "TOTAL EXPENSES",
                "TOTAL REVENUE",
                "NET PROFIT",
            ],
        )

        columns = expenses_table.columns

        # финальная таблица
        return pd.concat(
    [
        self._empty_row("Outcomes", columns),
        expenses_table,

        self._empty_row("Incomes", columns),
        revenue_table,

        self._empty_row("Totals", columns),
        total_block,
    ]
)

    def _empty_row(self, title: str, columns):
        return pd.DataFrame(
            [[None] * len(columns)],
            index=[title],
            columns=columns,
        )
