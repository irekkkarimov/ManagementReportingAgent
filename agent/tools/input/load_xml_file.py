"""
Загрузка и парсинг XML-файла бухгалтерской отчётности (КНД 0710099, формат ФНС/1С).

Файл содержит сразу бухгалтерский баланс и ОФР — оба отчёта парсятся и
кладутся в inputs_cache за один вызов.
"""

from pathlib import Path

from langchain_core.tools import tool

from agent.tools.finance.inputs_cache import get_available_years, merge_model_fields
from agent.tools.finance.parsed_tables_store import put_balance, put_ofr
from agent.xml.balance_xml_parser import parse_xml_report


@tool(
    "load_xml_file_tool",
    description=(
        "Читает XML-файл бухгалтерской отчётности (формат ФНС / выгрузка из 1С, расширение .xml), "
        "парсит баланс и ОФР и загружает данные в память. "
        "Используй, когда пользователь приложил .xml файл к сообщению."
    ),
)
def load_xml_file_tool(file_path: str) -> str:
    """
    Парсит XML-файл КНД 0710099 (бухгалтерский баланс + ОФР),
    сохраняет обе модели в хранилище и inputs_cache.

    :param file_path: путь к .xml файлу
    :return: строка-сообщение об успехе или ошибке
    """
    path = Path((file_path or "").strip().strip("'\""))

    if not path.exists():
        return f"Ошибка: файл не найден — {path}"
    if path.suffix.lower() != ".xml":
        return f"Ошибка: ожидается .xml файл, получено: {path.suffix}"

    try:
        balance, ofr = parse_xml_report(str(path))

        put_balance(balance)
        put_ofr(ofr)
        merge_model_fields(balance)
        merge_model_fields(ofr)

        years = get_available_years()
        return (
            f"XML-файл загружен успешно. "
            f"Содержит: Бухгалтерский баланс + Отчёт о финансовых результатах. "
            f"Доступные годы: {years}."
        )
    except Exception as exc:
        return f"Ошибка парсинга XML: {exc}"
