"""
Скачивание xlsx из Google Sheets или Google Drive по ссылке.
Чтение в DataFrame из памяти (BytesIO), без сохранения в файл; при необходимости можно сохранить по output_path.
"""

import io
import re
from pathlib import Path
from typing import Optional

import pandas as pd
import requests

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


def download_sheets_as_xlsx(
    url: str,
    gid: Optional[str] = None,
    sheet_name: str = "parsed",
    timeout: int = 30,
) -> pd.DataFrame:
    """
    Скачивает Google Sheets и возвращает DataFrame листа (без сохранения в файл).

    :param url: ссылка на таблицу (docs.google.com/spreadsheets/d/...)
    :param gid: ID листа (опционально); иначе экспортируется первый лист
    :param sheet_name: имя листа для чтения (по умолчанию "parsed"); при отсутствии читается первый лист
    :param timeout: таймаут запроса в секундах
    :return: pandas DataFrame
    :raises ValueError: если не удалось извлечь ID или скачать
    """
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


def download_as_xlsx(
    url: str,
    sheet_name: str = "parsed",
    timeout: int = 30,
) -> pd.DataFrame:
    """
    Скачивает xlsx по ссылке (Google Sheets или Google Drive) и возвращает DataFrame листа.

    :param url: ссылка на Google Sheets (docs.google.com/spreadsheets/d/...) или Google Drive (drive.google.com/file/d/...)
    :param sheet_name: имя листа (по умолчанию "parsed")
    :param timeout: таймаут запроса в секундах
    :return: pandas DataFrame
    """
    if extract_sheets_id(url):
        return download_sheets_as_xlsx(url, sheet_name=sheet_name, timeout=timeout)
    if extract_drive_file_id(url):
        return download_drive_file(url, sheet_name=sheet_name, timeout=timeout)
    raise ValueError(
        "Ссылка не распознана: ожидается Google Sheets (docs.google.com/spreadsheets/d/...) "
        "или Google Drive (drive.google.com/file/d/...)."
    )


def download_drive_file(
    url: str,
    sheet_name: str = "parsed",
    timeout: int = 30,
) -> pd.DataFrame:
    """
    Скачивает xlsx из Google Drive и возвращает DataFrame листа (без сохранения в файл).

    :param url: ссылка вида drive.google.com/file/d/FILE_ID/view или прямая ссылка
    :param sheet_name: имя листа для чтения (по умолчанию "parsed")
    :param timeout: таймаут запроса
    :return: pandas DataFrame
    """
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


SHEET_PARSED = "parsed"
