"""
Проверка ссылки: можно ли по ней скачать таблицу (Google Sheets или Google Drive).
"""

from langchain_core.tools import tool

from agent.sheets.google_fetch import extract_drive_file_id, extract_sheets_id


@tool(
    "validate_finance_link_tool",
    description=(
        "Проверяет, является ли ссылка рабочей для загрузки финансовой таблицы: "
        "Google Sheets или Google Drive (xlsx). Вызывай для каждой ссылки до скачивания. "
        "Если ссылка не подходит — вернётся сообщение об ошибке; если подходит — можно вызывать load_finance_table_from_link."
    ),
)
def validate_finance_link_tool(url: str) -> bool:
    """
    :param url: ссылка от пользователя (может быть в кавычках)
    :return: bool: True - ссылка правильная, False - ссылка не подходит
    """
    raw = (url or "").strip().strip("'\"")
    if not raw:
        return False
    if not raw.startswith("http://") and not raw.startswith("https://"):
        return False
    if extract_sheets_id(raw):
        return True
    if extract_drive_file_id(raw):
        return True
    return False
