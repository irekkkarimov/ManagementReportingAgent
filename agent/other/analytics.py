import pandas as pd


class AnalyticsEngine:
    def calculate_profit(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["profit"] = df["amount"]
        return df

    def calculate_totals(self, df: pd.DataFrame) -> dict:
        total_profit = df["amount"].sum()

        return {
            "revenue": df[df["amount"] > 0]["amount"].sum(),
            "expenses": abs(df[df["amount"] < 0]["amount"].sum()),
            "profit": total_profit,
            "avg_profit": total_profit / df["date"].nunique(),
        }

    def aggregate_by_month(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["month"] = df["date"].dt.to_period("M").astype(str)

        result = (
            df.groupby("month")
            .agg(
                revenue=("amount", lambda x: x[x > 0].sum()),
                expenses=("amount", lambda x: -x[x < 0].sum()),
                profit=("amount", "sum"),
            )
            .reset_index()
        )

        return result

    def aggregate_by_department(self, df: pd.DataFrame) -> pd.DataFrame:
        result = (
            df.groupby("department")["amount"]
            .sum()
            .reset_index(name="profit")
        )

        return result