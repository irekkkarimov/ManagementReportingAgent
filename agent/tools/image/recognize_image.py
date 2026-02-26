import base64
from pathlib import Path

from langchain_core.tools import tool

from agent.yandex.yandex_service import YandexOcrService


@tool("recognize_image_tool", description="Распознает текстовую информацию (таблицы) из картинки")
def recognize_image_tool(file_path: str) -> dict:
    """
    Распознает текстовую информацию (таблицы) из картинки
    :param file_path:
    :return:
    """
    prompt_file = Path(file_path)
    if not prompt_file.exists():
        raise ValueError(f"File '{file_path}' not found")

    with open(prompt_file, "rb") as f:
        file_content = f.read()
        base64_content = base64.b64encode(file_content).decode("utf-8")

        yandex_service = YandexOcrService()
        yandex_service.load_env()

        response = yandex_service.call_ocr(base64_content)
        return response