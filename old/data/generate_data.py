import pandas as pd
import numpy as np

class DataGenerator:
    def generate(self, categories_to_random_delete):
        np.random.seed(42)

        dates = pd.date_range(start="2024-01-01", end="2024-12-31", freq="D")
        departments = ["Продажи", "Маркетинг", "IT", "Операции"]

        revenue_categories = ["Продажа продуктов", "Услуги"]
        expense_categories = ["Аренда", "Зарплата", "Реклама"]

        data = []

        for date in dates:
            for dept in departments:
                # выбираем тип операции: доход или расход
                is_revenue = np.random.rand() > 0.5

                if is_revenue:
                    category = np.random.choice(revenue_categories)
                    amount = np.random.randint(50, 200)  # доходы
                else:
                    category = np.random.choice(expense_categories)
                    amount = -np.random.randint(30, 150)  # расходы

                # с вероятностью 20% делаем доход/расход пустым
                if np.random.rand() < 0.2:
                    amount = 0

                data.append(
                    {
                        "date": date,
                        "department": dept,
                        "category": category,
                        "amount": amount,
                    }
                )

        df = pd.DataFrame(data)

        for i in categories_to_random_delete:
            df = self.delete_random_month(df, i, 2)

        df.to_csv("./management_reporting_data.csv", index=False)
        print("Dataset generated: ./management_reporting_data.csv")

    def delete_random_month(self, df: pd.DataFrame, category: str, n_months: int = 1) -> pd.DataFrame:
        """
        Удаляет данные за случайный(ые) месяц(ы) для указанной категории.

        Args:
            df: исходный DataFrame с колонками ['date', 'department', 'category', 'amount']
            category: категория дохода или расхода, для которой нужно удалить данные
            n_months: количество случайных месяцев для удаления (по умолчанию 1)

        Returns:
            DataFrame с удалёнными данными
        """
        df = df.copy()

        # создаём колонку "месяц" в формате YYYY-MM
        df["month"] = df["date"].dt.to_period("M").astype(str)

        # выбираем все месяцы, где есть эта категория
        available_months = df[df["category"] == category]["month"].unique()

        # случайно выбираем n_months месяцев для удаления
        months_to_delete = np.random.choice(available_months, size=min(n_months, len(available_months)), replace=False)

        # удаляем строки для выбранных месяцев и категории
        df = df[~((df["category"] == category) & (df["month"].isin(months_to_delete)))]

        # можно удалить колонку month, если она больше не нужна
        df = df.drop(columns=["month"])

        return df
