import pandas as pd


class TextExplanationGenerator:
    """Генерация текстовых пояснений"""

    def generate_summary(self, df: pd.DataFrame) -> str:
        total_profit = df["profit"].sum()
        avg_profit = df["profit"].mean()

        text = (
            f"За анализируемый период суммарная прибыль составила {total_profit:.2f}. "
            f"Средняя прибыль за период равна {avg_profit:.2f}. "
            "Данные позволяют оценить общую финансовую эффективность деятельности."
        )
        return text