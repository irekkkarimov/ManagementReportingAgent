import json
import os
from typing import Any

import requests


class YandexOcrService:
    def __init__(self, folder_id: str = None, api_key: str = None):
        self._folder_id = folder_id
        self._ocr_api_key = api_key

    def load_env(self):
        self._folder_id = os.getenv("YC_FOLDER_ID")
        self._ocr_api_key = os.getenv("YC_OCR_API_KEY")

    def call_ocr(self, content: str) ->  Any:
        if self._folder_id is None or self._ocr_api_key is None:
            raise ValueError("Creds not initialized")

        data = {"mimeType": "JPEG",
        "languageCodes": ["ru", "en"],
        "content": content}

        url = "https://ocr.api.cloud.yandex.net/ocr/v1/recognizeText"

        headers = {"Content-Type": "application/json",
                   "Authorization": "Api-Key {:s}".format(self._ocr_api_key),
        "x-folder-id": self._folder_id,
        "x-data-logging-enabled": "true"}

        response = requests.post(url=url, headers=headers, data=json.dumps(data))

        return response.json()