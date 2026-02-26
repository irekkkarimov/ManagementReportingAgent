import numpy as np
import pandas as pd
from pandas.core.interchange.dataframe_protocol import DataFrame

from agent.common.data_loader import DataLoader


class FinanceProcessor:
    def __init__(self, income_file, balance_file):
        # Загружаем данные
        self.income_df = pd.read_csv(income_file)
        self.income_df["Date"] = pd.to_datetime(self.income_df["Month"])
        self.income_df["Year"] = self.income_df["Date"].dt.year
        self.income_df = self.income_df.drop('Date', axis=1)

        self.balance_df = pd.read_csv(balance_file)
        # Проверка индексов по году и месяцу
        self.income_df['Month_Year'] = self.income_df['Year'].astype(str) + '-' + self.income_df['Month'].astype(str)
        self.balance_df['Month_Year'] = self.balance_df['Year'].astype(str) + '-' + self.balance_df['Month'].astype(str)

    def calc_profitability(self):
        # Рентабельность
        self.income_df['ROS'] = self.income_df['Net_Profit'] / self.income_df['Revenue']
        self.income_df['Gross_Margin'] = self.income_df['Gross_Profit'] / self.income_df['Revenue']
        self.income_df['Operating_Margin'] = self.income_df['Operating_Profit'] / self.income_df['Revenue']
        return self.income_df[['Month_Year', 'ROS', 'Gross_Margin', 'Operating_Margin']]

    def calc_liquidity(self):
        # Ликвидность
        self.balance_df['Current_Ratio'] = self.balance_df['Current_Assets'] / self.balance_df['Current_Liabilities']
        self.balance_df['Quick_Ratio'] = (self.balance_df['Current_Assets'] - self.balance_df['Inventory']) / \
                                         self.balance_df['Current_Liabilities']
        return self.balance_df[['Month_Year', 'Current_Ratio', 'Quick_Ratio']]

    def calc_financial_stability(self):
        # Финансовая устойчивость
        self.balance_df['Debt_to_Equity'] = self.balance_df['Debt'] / self.balance_df['Equity']
        self.balance_df['Debt_Ratio'] = self.balance_df['Debt'] / self.balance_df['Total_Assets']
        return self.balance_df[['Month_Year', 'Debt_to_Equity', 'Debt_Ratio']]

    def calc_asset_turnover(self):
        # Оборачиваемость активов
        merged = pd.merge(self.income_df, self.balance_df[['Month_Year', 'Total_Assets']], on='Month_Year', how='left')
        merged['Asset_Turnover'] = merged['Revenue'] / merged['Total_Assets']
        return merged[['Month_Year', 'Asset_Turnover']]

    def summary(self):
        # Сводный DataFrame со всеми показателями
        df = pd.merge(self.calc_profitability(), self.calc_liquidity(), on='Month_Year')
        df = pd.merge(df, self.calc_financial_stability(), on='Month_Year')
        df = pd.merge(df, self.calc_asset_turnover(), on='Month_Year')
        return df

































    # # 1️⃣ Скользящая средняя
    # def moving_average(self, column: str, window: int = 3) -> pd.Series:
    #     return self.data[column].rolling(window=window, min_periods=1).mean()
    #
    # # 2️⃣ Анализ сезонности
    # def seasonal_analysis(self, column: str) -> pd.DataFrame:
    #     self.data["Month_Num"] = self.data["Month"].dt.month
    #     return self.data.groupby("Month_Num")[column].mean().reset_index().rename(
    #         columns={column: f"{column}_avg_by_month"})
    #
    # # 3️⃣ Детекция аномалий
    # def detect_anomalies(self, column: str, threshold: float = 2.0) -> pd.DataFrame:
    #     mean = self.data[column].mean()
    #     std = self.data[column].std()
    #     self.data[f"{column}_anomaly"] = np.abs(self.data[column] - mean) > threshold * std
    #     return self.data[["Month", column, f"{column}_anomaly"]][self.data[f"{column}_anomaly"]]
    #
    # # 4️⃣ Авто-выявление ухудшения маржи
    # def check_margin_decline(self) -> pd.DataFrame:
    #     self.data["Gross_Margin"] = self.data["Gross_Profit"] / self.data["Revenue"]
    #     self.data["Operating_Margin"] = self.data["Operating_Profit"] / self.data["Revenue"]
    #     self.data["Net_Margin"] = self.data["Net_Profit"] / self.data["Revenue"]
    #
    #     for col in ["Gross_Margin", "Operating_Margin", "Net_Margin"]:
    #         self.data[f"{col}_decline"] = self.data[col].diff() < 0
    #
    #     return self.data[["Month", "Gross_Margin", "Gross_Margin_decline",
    #                     "Operating_Margin", "Operating_Margin_decline",
    #                     "Net_Margin", "Net_Margin_decline"]]