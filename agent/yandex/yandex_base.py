from yandex_ai_studio_sdk import AIStudio


class YandexBase:
    def __init__(self, folder_id: str, api_key: str, ):
        self.sdk = AIStudio(
            folder_id=folder_id,
            auth=api_key,
        )
