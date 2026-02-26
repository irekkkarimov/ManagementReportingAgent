from gigachat import GigaChat


class GigachatService:
    def __init__(self, gigachat_creds: str, gigachat_prompt_path: str, gigachat_temperature: float):
        model = GigaChat(
            model="GigaChat-2-Pro",
            verify_ssl_certs=False,
            credentials=gigachat_creds,
            timeout=60,
            temperature=gigachat_temperature,
        )
        return
