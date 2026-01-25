import pandas as pd


class DataPreprocessor:
    """Очистка и подготовка управленческих данных"""

    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Удаление пустых строк
        df.dropna(how="all", inplace=True)

        # Заполнение пропусков
        df.fillna(0, inplace=True)

        # Приведение дат
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])

        return df