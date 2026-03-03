import json

from pandas import DataFrame


def get_value_by_code(
    df: DataFrame, code: str, value_column: str = "current_year"
) -> float:
    """
    Ищет строку по коду и возвращает значение из указанной колонки.

    Если ``value_column`` — обычная колонка DataFrame, берёт из неё напрямую.
    Если колонки нет, но есть ``values`` (JSON), пробует найти ключ
    ``value_column`` внутри JSON (удобно для поиска по году, например "2025").

    Если код не найден — возвращает 0.0
    """
    row = df[df["code"] == code]

    if row.empty:
        return 0.0

    if value_column in df.columns:
        return float(row[value_column].values[0])

    if "values" in df.columns:
        raw = row["values"].values[0]
        values_dict = json.loads(raw) if isinstance(raw, str) else raw
        return float(values_dict.get(value_column, 0.0))

    return 0.0
