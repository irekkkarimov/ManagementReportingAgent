import matplotlib.pyplot as plt
import pandas as pd


class VisualizationEngine:
    """Визуализация управленческой отчетности"""

    def plot_monthly_pl(self, df: pd.DataFrame):
        plt.figure()
        plt.plot(df["month"], df["revenue"], label="Revenue")
        plt.plot(df["month"], df["expenses"], label="Expenses")
        plt.plot(df["month"], df["profit"], label="Profit")

        plt.title("Monthly P&L Dynamics")
        plt.xlabel("Month")
        plt.ylabel("Amount")
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def plot_profit_by_department(self, df: pd.DataFrame):
        plt.figure()
        plt.bar(df["department"], df["profit"])

        plt.title("Profit by Department")
        plt.xlabel("Department")
        plt.ylabel("Profit")
        plt.tight_layout()
        plt.show()

    def _prepare_monthly_pl(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        monthly = (
            df.groupby("month")
            .agg(
                revenue=("amount", lambda x: x[x > 0].sum()),
                expenses=("amount", lambda x: -x[x < 0].sum()),
                profit=("amount", "sum"),
            )
            .reset_index()
        )

        return monthly