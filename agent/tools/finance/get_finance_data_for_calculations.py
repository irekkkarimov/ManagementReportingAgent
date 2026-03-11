"""
Извлекает числовые данные за указанный год из загруженных таблиц и сохраняет в inputs_cache.
После вызова этого инструмента все calculate_* могут работать без параметров.
"""

import json
from typing import Dict

from langchain_core.tools import tool

from agent.indicators.calculator import get_calculation_inputs
from agent.tools.finance.inputs_cache import set_inputs
from agent.tools.finance.parsed_tables_store import get_available_years, get_both


def extract_finance_inputs(year: str) -> Dict[str, float]:
    """
    Извлекает числовые данные за год из хранилища текущей сессии и сохраняет в inputs_cache.

    :param year: год, например "2024"
    :return: словарь со всеми полями баланса и ОФР
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

    inputs = get_calculation_inputs(balance, ofr, year)
    set_inputs(year, inputs)
    return inputs


@tool(
    "get_finance_data_for_calculations",
    description=(
        "Загружает данные за указанный год из таблиц (баланс + ОФР) в кэш. "
        "После вызова все инструменты calculate_* берут данные из кэша автоматически — без параметров. "
        "Сначала загрузи таблицы через download_google_sheets, затем вызови этот инструмент с нужным годом."
    ),
)
def get_finance_data_for_calculations(year: str) -> str:
    """
    :param year: год, например "2024"
    :return: подтверждение загрузки или сообщение об ошибке
    """
    try:
        inputs = extract_finance_inputs(year)
        keys = ", ".join(inputs.keys())
        return f"Данные за {year} год загружены в кэш. Доступные поля: {keys}."
    except ValueError as exc:
        return f"Ошибка: {exc}"
