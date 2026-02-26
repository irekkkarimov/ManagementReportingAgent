import pandas as pd


class DataLoader:
    """Загрузка данных для управленческой отчетности"""

    @staticmethod
    def load_from_csv(path: str) -> pd.DataFrame:
        df = pd.read_csv(path)
        return df

    @staticmethod
    def load_from_excel(path: str, sheet_name=0) -> pd.DataFrame:
        df = pd.read_excel(path, sheet_name=sheet_name)
        return df