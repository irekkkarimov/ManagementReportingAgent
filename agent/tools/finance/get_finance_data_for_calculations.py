"""
Возвращает числовые входные данные за указанный год из загруженных таблиц (баланс + ОФР).
"""

import json
from typing import Dict

from langchain_core.tools import tool

from agent.indicators.calculator import get_calculation_inputs
from agent.tools.finance.parsed_tables_store import get_available_years, get_both


def extract_finance_inputs(year: str) -> Dict[str, float]:
    """
    Извлекает числовые данные за год из хранилища текущей сессии.

    :param year: год, например "2024"
    :return: словарь с именованными значениями для calculate_*
    :raises ValueError: если таблицы не загружены или год недоступен
    """
    year = (year or "").strip()
    if not year or not year.isdigit():
        raise ValueError("Укажи год, например 2024.")

    balance, ofr = get_both()
    if not balance:
        raise ValueError("Баланс не загружен. Сначала вызови download_google_sheets со ссылкой на баланс.")
    if not ofr:
        raise ValueError("ОФР не загружен. Сначала вызови download_google_sheets со ссылкой на ОФР.")

    available = get_available_years()
    if year not in available:
        raise ValueError(f"За год {year} нет данных. Доступные годы: {available}.")

    return get_calculation_inputs(balance, ofr, year)


@tool(
    "get_finance_data_for_calculations",
    description=(
        "Возвращает числовые данные за указанный год из таблиц, загруженных через download_google_sheets. "
        "Сначала загрузи баланс и ОФР, затем вызови этот инструмент с нужным годом. "
        "Используй полученные числа для вызова инструментов calculate_*."
    ),
)
def get_finance_data_for_calculations(year: str) -> str:
    """
    :param year: год, например "2024"
    :return: JSON со всеми числами для calculate_* или сообщение об ошибке
    """
    try:
        inputs = extract_finance_inputs(year)
        return json.dumps(inputs, ensure_ascii=False)
    except ValueError as exc:
        return f"Ошибка: {exc}"
