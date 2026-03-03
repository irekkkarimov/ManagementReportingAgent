import base64
import json
import re
from pathlib import Path
from typing import List, Optional

import pandas as pd

from agent.yandex.yandex_service import YandexOcrService


def ocr_file_to_positioned_lines(file_path: str) -> List[dict]:
    """
    Вызывает Yandex OCR и возвращает список строк с координатами центра.

    Каждый элемент: {"text": str, "x": float, "y": float}
    Используется для coordinate-based парсинга (напр. отчёт об изменениях капитала),
    где изображение повёрнуто и y-координата определяет колонку таблицы.
    """
    ocr = YandexOcrService()
    ocr.load_env()

    file = Path(file_path)
    if not file.exists():
        raise ValueError(f"File '{file_path}' not found")

    with open(file, "rb") as f:
        base64_content = base64.b64encode(f.read()).decode("utf-8")
        result = ocr.call_ocr(base64_content)

    if result is None:
        raise ValueError("OCR call returned None")

    blocks = result["result"]["textAnnotation"]["blocks"]
    items = []

    for block in blocks:
        for line in block.get("lines", []):
            words = [w["text"] for w in line.get("words", [])]
            text = " ".join(words).strip()
            if not text:
                continue
            verts = line["boundingBox"]["vertices"]
            xs = [int(v.get("x", 0)) for v in verts]
            ys = [int(v.get("y", 0)) for v in verts]
            items.append({
                "text": text,
                "x": sum(xs) / len(xs),
                "y": sum(ys) / len(ys),
            })

    return items


def ocr_file_to_lines(file_path: str) -> List[str]:
    """Вызывает Yandex OCR для одного файла и возвращает список текстовых строк."""
    ocr = YandexOcrService()
    ocr.load_env()

    file = Path(file_path)
    if not file.exists():
        raise ValueError(f"File '{file_path}' not found")

    with open(file, "rb") as f:
        base64_content = base64.b64encode(f.read()).decode("utf-8")
        result = ocr.call_ocr(base64_content)

    if result is None:
        raise ValueError("OCR call returned None")

    blocks = result["result"]["textAnnotation"]["blocks"]

    lines = []
    for block in blocks:
        for line in block.get("lines", []):
            words = [w["text"] for w in line.get("words", [])]
            text = " ".join(words).strip()
            if text:
                lines.append(text)

    return merge_broken_numbers(lines)


def ocr_files_to_lines(file_paths: List[str]) -> List[str]:
    """Вызывает OCR для нескольких страниц/файлов и объединяет строки."""
    all_lines = []
    for path in file_paths:
        all_lines.extend(ocr_file_to_lines(path))
    return all_lines


def merge_broken_numbers(lines: List[str]) -> List[str]:
    """
    Склеивает числа в скобках, разорванные OCR на несколько строк:
    '(37 033 242' + ')' -> '(37 033 242)'
    """
    merged = []
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        if line.startswith("(") and not line.endswith(")"):
            combined = line
            j = i + 1
            while j < len(lines):
                combined += lines[j].strip()
                if ")" in lines[j]:
                    break
                j += 1
            merged.append(combined)
            i = j + 1
        else:
            merged.append(line)
            i += 1

    return merged


def format_number(text: str) -> int:
    """Парсит число из OCR-строки: убирает пробелы, обрабатывает скобки как минус."""
    cleaned = text.replace(" ", "").replace("\u00a0", "")

    if not cleaned or cleaned == "-":
        return 0

    negative = cleaned.startswith("(") or cleaned.endswith(")")
    cleaned = cleaned.replace("(", "").replace(")", "")

    if not cleaned or cleaned == "-":
        return 0

    digits = "".join(c for c in cleaned if c.isdigit())
    if not digits:
        return 0

    value = int(digits)
    return -value if negative else value


def detect_report_type(lines: List[str]) -> str:
    """
    Определяет тип финансового отчёта по ключевым словам и кодам строк в OCR-результате.

    Возвращает одно из: 'balance_sheet', 'financial_results', 'cash_flow',
    'equity_changes', 'unknown'.
    """
    header = " ".join(lines[:40]).lower()
    all_text = " ".join(lines)

    if "бухгалтерский баланс" in header:
        return "balance_sheet"
    if "финансовых результатах" in header or "финансовые результаты" in header:
        return "financial_results"
    if "движении денежных средств" in header or "движение денежных средств" in header:
        return "cash_flow"
    if "изменениях капитала" in header or "изменения капитала" in header:
        return "equity_changes"

    if any(c in all_text for c in ["1110", "1150", "1600", "1700"]):
        return "balance_sheet"
    if any(c in all_text for c in ["2110", "2120", "2200", "2400"]):
        return "financial_results"
    if any(c in all_text for c in ["4110", "4120", "4100", "4200"]):
        return "cash_flow"
    if any(c in all_text for c in ["3100", "3200", "3211"]):
        return "equity_changes"

    return "unknown"


def extract_years(lines: List[str], num_expected: int = 0) -> List[str]:
    """
    Извлекает годы из заголовков OCR-результата.

    Обрабатывает в том числе ситуации, когда OCR разбивает год пробелом:
    «20 23 г.» → 2023, «20 22 г.4» → 2022.

    Возвращает список уникальных годов в порядке появления (от нового к старому).
    """
    header_text = " ".join(lines[:50])

    split_year = re.compile(r"20\s+(\d{2})\s*г", re.IGNORECASE)
    years: List[str] = []
    for m in split_year.finditer(header_text):
        y = "20" + m.group(1)
        if y not in years:
            years.append(y)

    solid_year = re.compile(r"(20[0-9]{2})\s*(?:г\.?|год)", re.IGNORECASE)
    for m in solid_year.finditer(header_text):
        y = m.group(1)
        if y not in years:
            years.append(y)

    if len(years) < max(num_expected, 2):
        fallback = re.findall(r"\b(20[0-9]{2})\b", header_text)
        for y in fallback:
            if y not in years:
                years.append(y)

    if num_expected > 0:
        years = years[:num_expected]

    return years


def parse_table_by_codes(
    lines: List[str],
    known_codes: set,
    value_columns: List[str],
    start_keyword: str = None,
    year_labels: Optional[List[str]] = None,
    negative_codes: Optional[set] = None,
) -> pd.DataFrame:
    """
    Универсальный парсер табличных отчётов.

    Ищет строки с известными кодами, берёт название из предыдущей строки
    и N значений из последующих строк.

    Args:
        lines: текстовые строки из OCR
        known_codes: множество известных кодов строк отчёта
        value_columns: названия колонок со значениями (определяет кол-во колонок)
        start_keyword: ключевое слово для поиска начала таблицы
        year_labels: список годов (строки), извлечённых из заголовков OCR;
                     используется как ключи в JSON-колонке ``values``
        negative_codes: коды строк, значения которых по стандарту бухучёта
                        всегда отрицательные (расходы). Если OCR не распознал
                        скобки, положительное число будет инвертировано.
    """
    if start_keyword:
        start_index = 0
        for i, line in enumerate(lines):
            if start_keyword in line:
                start_index = max(0, i - 1)
                break
        lines = lines[start_index:]

    json_keys = year_labels if year_labels and len(year_labels) == len(value_columns) else value_columns
    neg = negative_codes or set()

    num_values = len(value_columns)
    data = []
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        if line in known_codes:
            name = lines[i - 1] if i > 0 else ""

            values = []
            consumed = 0

            for j in range(1, num_values + 1):
                next_idx = i + j
                if next_idx >= len(lines):
                    values.append(0)
                elif lines[next_idx].strip() in known_codes:
                    # Следующая строка — уже код, пустые ячейки пропущены OCR
                    while len(values) < num_values:
                        values.append(0)
                    break
                else:
                    values.append(format_number(lines[next_idx]))
                    consumed = j

            while len(values) < num_values:
                values.append(0)

            if line in neg:
                values = [-abs(v) if v != 0 else 0 for v in values]

            row = {"name": name, "code": line}
            for col_name, val in zip(value_columns, values):
                row[col_name] = val

            values_dict = {k: v for k, v in zip(json_keys, values)}
            row["values"] = json.dumps(values_dict, ensure_ascii=False)

            data.append(row)
            i += consumed + 1
        else:
            i += 1

    return pd.DataFrame(data)
