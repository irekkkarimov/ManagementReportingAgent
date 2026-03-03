import json
from typing import List, Optional

import pandas as pd

from agent.table_parser.base import (
    ocr_file_to_positioned_lines,
    format_number,
    merge_broken_numbers,
)
from consts.finance import equity_changes_consts, EC_NEGATIVE_CODES

VALUE_COLUMNS = [
    "charter_capital",
    "additional_capital",
    "reserve_capital",
    "retained_earnings",
    "total",
]

# Ключевые слова заголовков колонок для автоопределения y-позиций
_COLUMN_HEADER_KEYWORDS = [
    ("Уставный", 0),
    ("Добавочный", 1),
    ("Резервный", 2),
    ("Нераспределен", 3),
    ("Итого", 4),
]

# Максимальный зазор по x между СОСЕДНИМИ (consecutive) элементами одной строки.
# Используем consecutive gap (не от первого элемента), иначе заголовки разделов
# (e.g. "За 2024 г." x=312) склеиваются с данными строки (x=322, gap=10).
# Зазор между разными строками в KamAZ-данных ≥ 10 px, внутри строки ≤ 3 px.
_X_ROW_TOLERANCE = 9

# Значение y в "колонке кода" (Код) + этот отступ = граница между
# текстовыми именами строк (слева) и числовыми значениями (справа).
_NAME_Y_OFFSET = 50


def _detect_column_y_positions(positioned: List[dict]) -> Optional[List[float]]:
    """
    Определяет y-координаты для каждой из 5 колонок значений
    по ключевым словам заголовков.

    Возвращает список из 5 y-значений или None, если определить не удалось.
    """
    col_y: List[Optional[float]] = [None] * 5
    for item in positioned:
        text = item["text"]
        for keyword, idx in _COLUMN_HEADER_KEYWORDS:
            if keyword in text and col_y[idx] is None:
                col_y[idx] = item["y"]
    if any(v is None for v in col_y):
        return None
    return col_y  # type: ignore[return-value]


def _nearest_column(y: float, col_y: List[float]) -> int:
    """Возвращает индекс ближайшей колонки по y-координате."""
    return min(range(len(col_y)), key=lambda i: abs(y - col_y[i]))


def _fix_signs_by_total(values: List[int], value_columns: List[str]) -> List[int]:
    """
    Проверяет, что сумма колонок капитала равна итоговой колонке (total).

    В форме 0710004: charter + additional + reserve + retained = total.
    Если равенство нарушено — OCR убрал скобки у одного значения.
    Находим его перебором и инвертируем знак.

    Если исправить не получается (нарушено ≥2 значений) — возвращаем как есть.
    """
    if "total" not in value_columns:
        return values

    total_idx = value_columns.index("total")
    other_idxs = [i for i in range(len(value_columns)) if i != total_idx]

    total = values[total_idx]
    current_sum = sum(values[i] for i in other_idxs)

    if current_sum == total:
        return values  # Уже корректно

    # Пробуем инвертировать одно значение
    for flip_idx in other_idxs:
        if values[flip_idx] == 0:
            continue
        test_sum = current_sum - values[flip_idx] + (-values[flip_idx])
        if test_sum == total:
            result = list(values)
            result[flip_idx] = -values[flip_idx]
            return result

    # Пробуем инвертировать total (если все остальные правильные, но total перевёрнут)
    if total != 0 and current_sum == -total:
        result = list(values)
        result[total_idx] = -total
        return result

    return values  # Не удалось исправить однозначно — оставляем как есть


def parse_equity_changes_from_positioned(
    positioned: List[dict],
    known_codes: set,
    value_columns: List[str],
) -> pd.DataFrame:
    """
    Парсит отчёт об изменениях капитала используя координаты OCR-блоков.

    В сканах отчёта изображение повёрнуто на 90°:
      x-координата = позиция строки в таблице
      y-координата = позиция колонки в таблице

    Это позволяет корректно присваивать значения колонкам даже когда
    OCR полностью пропускает пустые ячейки.
    """
    col_y = _detect_column_y_positions(positioned)
    if col_y is None:
        return pd.DataFrame()

    # Определяем y-позицию колонки кода (из заголовка "Код" или из первого кода)
    code_col_y: Optional[float] = None
    for item in positioned:
        if item["text"].strip() == "Код":
            code_col_y = item["y"]
            break
    if code_col_y is None:
        for item in positioned:
            if item["text"].strip() in known_codes:
                code_col_y = item["y"]
                break

    # Всё с y > (y_кода + отступ) считается текстом названия строки
    name_y_threshold = (code_col_y or max(col_y)) + _NAME_Y_OFFSET

    # Группируем элементы по x-координате (одинаковый x = одна строка таблицы).
    # Используем consecutive gap: проверяем зазор между СОСЕДНИМИ элементами,
    # а не от первого элемента группы. Это важно, потому что заголовки разделов
    # ("За 2024 г.") и данные следующей строки могут иметь суммарный разброс > 12 px,
    # но зазор между любыми двумя соседними элементами одной строки ≤ 9 px.
    sorted_items = sorted(positioned, key=lambda i: i["x"])
    groups: List[List[dict]] = []
    current: List[dict] = []
    prev_x: Optional[float] = None

    for item in sorted_items:
        if prev_x is None or abs(item["x"] - prev_x) <= _X_ROW_TOLERANCE:
            current.append(item)
        else:
            if current:
                groups.append(current)
            current = [item]
        prev_x = item["x"]
    if current:
        groups.append(current)

    data = []
    prev_name = ""

    for group in groups:
        code_items = [it for it in group if it["text"].strip() in known_codes]

        if not code_items:
            # Группа без кода — возможно, раздел или заголовок
            name_parts = [it["text"] for it in group if it["y"] > name_y_threshold]
            if name_parts:
                prev_name = " ".join(name_parts)
            continue

        code = code_items[0]["text"].strip()

        # Название строки может быть в той же группе, что и код
        group_name_parts = [it["text"] for it in group if it["y"] > name_y_threshold]
        current_name = " ".join(group_name_parts) if group_name_parts else prev_name

        # Собираем значения по колонкам через y-координату.
        # Группируем по индексу колонки, чтобы корректно объединить
        # разорванные скобки (OCR иногда выдаёт "(" и "число" как отдельные блоки).
        col_buckets: dict[int, List[str]] = {}
        for it in group:
            if it["text"].strip() in known_codes:
                continue
            if it["y"] > name_y_threshold:
                continue
            col_idx = _nearest_column(it["y"], col_y)
            col_buckets.setdefault(col_idx, []).append(it["text"].strip())

        values = [0] * len(value_columns)
        for col_idx, texts in col_buckets.items():
            merged = merge_broken_numbers(texts)
            for text in merged:
                val = format_number(text)
                if val != 0 or any(c.isdigit() for c in text):
                    values[col_idx] = val
                    break

        # Коды, которые по стандарту всегда отрицательные (дивиденды и т.п.):
        # если OCR убрал скобки и значение положительное — инвертируем знак.
        if code in EC_NEGATIVE_CODES:
            values = [-abs(v) if v != 0 else 0 for v in values]

        # Математическая верификация знаков:
        # В отчёте об изменениях капитала всегда выполняется
        # charter + additional + reserve + retained = total.
        # Если это нарушено, OCR убрал скобки у одного значения — находим его
        # перебором и инвертируем знак.
        values = _fix_signs_by_total(values, value_columns)

        row = {"name": current_name, "code": code}
        for col_name, val in zip(value_columns, values):
            row[col_name] = val

        values_dict = dict(zip(value_columns, values))
        row["values"] = json.dumps(values_dict, ensure_ascii=False)

        data.append(row)
        prev_name = ""

    return pd.DataFrame(data)


def parse_equity_changes(file_paths: List[str]) -> pd.DataFrame:
    """
    Парсит отчёт об изменениях капитала (форма 0710004).

    Использует координаты OCR-блоков для корректного сопоставления
    значений с колонками при наличии пустых ячеек.

    Возвращает DataFrame с колонками:
      name, code, charter_capital, additional_capital,
      reserve_capital, retained_earnings, total, values (JSON)
    """
    if isinstance(file_paths, str):
        file_paths = [file_paths]

    positioned: List[dict] = []
    for path in file_paths:
        positioned.extend(ocr_file_to_positioned_lines(path))

    return parse_equity_changes_from_positioned(
        positioned=positioned,
        known_codes=set(equity_changes_consts),
        value_columns=VALUE_COLUMNS,
    )
