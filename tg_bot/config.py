import os

from dotenv import load_dotenv


load_dotenv()


class BotConfig:
    def __init__(self) -> None:
        token = os.getenv("TELEGRAM_BOT_TOKEN")

        if not token:
            raise ValueError("TELEGRAM_BOT_TOKEN is not set in environment variables")

        self.token = token




