"""
Общие утилиты для инструментов генерации отчётов (Excel и PDF).
"""

import os
from datetime import datetime
from typing import Dict, List, Optional

from agent.indicators.compute import ALL_INDICATORS
from agent.tools.finance.inputs_cache import get_available_years


def compute_all_indicators(years: List[str]) -> Dict[str, Dict[str, Optional[float]]]:
    """
    Рассчитывает все показатели из ALL_INDICATORS по каждому году.

    :param years: список лет, например ["2025", "2024", "2023"]
    :return: {indicator_name: {year: value_or_None}}
    """
    results: Dict[str, Dict[str, Optional[float]]] = {}
    for ind in ALL_INDICATORS:
        results[ind.name] = {}
        for year in years:
            try:
                results[ind.name][year] = ind.fn(year)
            except Exception:
                results[ind.name][year] = None
    return results


def get_years_or_error() -> List[str] | str:
    """
    Возвращает список доступных лет или строку с сообщением об ошибке.
    Используется перед любой генерацией отчёта.
    """
    years = get_available_years()
    if not years:
        return (
            "Нет загруженных данных. "
            "Сначала загрузи таблицу через download_google_sheets или загрузи файл."
        )
    return years


def make_output_path(directory: str, prefix: str, extension: str) -> str:
    """
    Создаёт директорию и возвращает путь к файлу с временной меткой.

    :param directory: путь к папке, например "./pdf_output"
    :param prefix: префикс имени файла, например "financial_report"
    :param extension: расширение без точки, например "pdf"
    """
    os.makedirs(directory, exist_ok=True)
    filename = f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{extension}"
    return os.path.join(directory, filename)
