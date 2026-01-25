import pandas as pd


class DataLoader:
    """Загрузка данных для управленческой отчетности"""

    def load_from_csv(self, path: str) -> pd.DataFrame:
        df = pd.read_csv(path)
        return df

    def load_from_excel(self, path: str, sheet_name=0) -> pd.DataFrame:
        df = pd.read_excel(path, sheet_name=sheet_name)
        return df