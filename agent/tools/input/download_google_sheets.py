"""
Скачивание xlsx из Google Sheets или Google Drive по ссылке и парсинг в модель (баланс/ОФР).
Один инструмент: ссылка → скачать → определить вид по кодам → распарсить → сохранить в хранилище → ответ.
"""

import io
import re
from typing import Optional, Tuple, Union

import pandas as pd
import requests
from langchain_core.tools import tool

from agent.tools.input.download_and_parse_finance_table import download_and_parse_finance_table
from input_models.accountant_balance_report import AccountantBalanceReport
from input_models.financial_results_report import FinancialResultsReport

# Google Sheets: https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit...
# Google Drive file: https://drive.google.com/file/d/FILE_ID/view...
SHEETS_REGEX = re.compile(
    r"(?:https?://)?(?:www\.)?docs\.google\.com/spreadsheets/d/([a-zA-Z0-9_-]+)",
    re.IGNORECASE,
)
DRIVE_REGEX = re.compile(
    r"(?:https?://)?(?:drive\.google\.com/file/d/|docs\.google\.com/uc\?id=)([a-zA-Z0-9_-]+)",
    re.IGNORECASE,
)

SHEET_PARSED = "parsed"


def extract_sheets_id(url: str) -> Optional[str]:
    """Извлекает ID таблицы из ссылки Google Sheets."""
    url = url.strip().strip("'\"")
    m = SHEETS_REGEX.search(url)
    return m.group(1) if m else None


def extract_drive_file_id(url: str) -> Optional[str]:
    """Извлекает ID файла из ссылки Google Drive."""
    url = url.strip().strip("'\"")
    m = DRIVE_REGEX.search(url)
    return m.group(1) if m else None


def _download_sheets_as_xlsx(
    url: str,
    sheet_name: str = SHEET_PARSED,
    gid: Optional[str] = None,
    timeout: int = 60,
) -> pd.DataFrame:
    """Скачивает Google Sheets и возвращает DataFrame листа."""
    sheet_id = extract_sheets_id(url)
    if not sheet_id:
        raise ValueError(f"Не удалось извлечь ID таблицы из ссылки: {url}")

    export_url = (
        f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
    )
    if gid:
        export_url += f"&gid={gid}"

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101"}
    response = requests.get(export_url, headers=headers, timeout=timeout, allow_redirects=True)

    if response.status_code != 200:
        raise ValueError(
            f"Ошибка скачивания Google Sheets (код {response.status_code}). "
            "Проверьте, что доступ настроен как «все, у кого есть ссылка», могут просматривать."
        )

    content_type = response.headers.get("Content-Type", "")
    if "spreadsheet" not in content_type and "octet-stream" not in content_type:
        if "html" in content_type.lower():
            raise ValueError(
                "В ответе пришла HTML-страница вместо xlsx. "
                "Сделайте таблицу доступной по ссылке (без входа) или используйте файл из Drive."
            )

    try:
        return pd.read_excel(io.BytesIO(response.content), sheet_name=sheet_name)
    except ValueError:
        return pd.read_excel(io.BytesIO(response.content), sheet_name=0)


def _download_drive_file(
    url: str,
    sheet_name: str = SHEET_PARSED,
    timeout: int = 30,
) -> pd.DataFrame:
    """Скачивает xlsx из Google Drive и возвращает DataFrame листа."""
    file_id = extract_drive_file_id(url)
    if not file_id:
        raise ValueError(f"Не удалось извлечь ID файла из ссылки: {url}")

    download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(download_url, headers=headers, timeout=timeout, allow_redirects=True)

    if response.status_code != 200:
        raise ValueError(f"Ошибка скачивания с Drive (код {response.status_code})")

    try:
        return pd.read_excel(io.BytesIO(response.content), sheet_name=sheet_name)
    except ValueError:
        return pd.read_excel(io.BytesIO(response.content), sheet_name=0)


def _download_as_xlsx(url: str, sheet_name: str = SHEET_PARSED) -> pd.DataFrame:
    """Скачивает xlsx по ссылке (Sheets или Drive) и возвращает DataFrame."""
    url = url.strip().strip("'\"")
    if extract_sheets_id(url):
        return _download_sheets_as_xlsx(url, sheet_name=sheet_name)
    if extract_drive_file_id(url):
        return _download_drive_file(url, sheet_name=sheet_name)
    raise ValueError(
        "Ссылка не распознана: ожидается Google Sheets (docs.google.com/spreadsheets/d/...) "
        "или Google Drive (drive.google.com/file/d/...)."
    )


@tool(
    "download_google_sheets",
    description=(
        "Скачивает таблицу по ссылке (Google Sheets или Google Drive), определяет вид отчёта по кодам строк "
        "(баланс или ОФР) и парсит. Сначала при необходимости проверь ссылку через validate_finance_link."
    ),
)
def download_google_sheets(
    url: str,
    sheet_name: str = SHEET_PARSED,
) -> Tuple[str, Union[AccountantBalanceReport, FinancialResultsReport]]:
    """
    Скачивает xlsx по ссылке, парсит в модель (баланс/ОФР) и возвращает сообщение для агента.

    :param url: ссылка на Google Sheets или Google Drive
    :param sheet_name: имя листа (по умолчанию "parsed")
    :return: сообщение об успехе или об ошибке
    """
    df = _download_as_xlsx(url, sheet_name=sheet_name)
    return download_and_parse_finance_table(df)

