import asyncio
import logging
import os
from collections import defaultdict

from anyio import sleep
from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from agent.base import Agent
from tg_bot.config import BotConfig
from tg_bot.models.image_proccessing import ImageBatch
from tg_bot.storage import ConversationStorage

import time

logger = logging.getLogger(__name__)


class TelegramAgentBot:
    def __init__(self, config: BotConfig, storage: ConversationStorage, agent: Agent) -> None:
        self.config = config
        self._agent = agent
        self._media_groups: dict[str, ImageBatch] = defaultdict(type[ImageBatch])  # media_group_id -> list[file_path]

        self.application: Application = (
            ApplicationBuilder().token(self.config.token).build()
        )

        # Регистрация хэндлеров
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.application.add_handler(MessageHandler(filters.PHOTO, self.handle_photo_with_caption))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        welcome_text = (
            "Привет! Я финансовый ИИ-агент. Задавай вопросы про управленческие и финансовые отчеты"
        )

        await update.message.reply_text(welcome_text)

    async def handle_message(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        chat_id = update.effective_chat.id
        user_text = update.message.text.strip()
        reply_text = TelegramAgentBot.format_reply(self._agent.process_text(chat_id, [user_text]))

        await TelegramAgentBot._reply(update, reply_text)

    async def handle_photo_with_caption(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat_id = update.effective_chat.id
        message = update.message
        caption_text = message.caption or ""
        media_group_id = message.media_group_id

        print("received message: ", update)

        os.makedirs("./temp_photos", exist_ok=True)

        # Скачиваем самое большое фото из сообщения
        photo = message.photo[-1]
        file = await photo.get_file()
        file_path = f"./temp_photos/{photo.file_id}.jpg"
        await file.download_to_drive(file_path)

        if media_group_id:
            try_get_image_batch = self._media_groups.get(media_group_id)
            if try_get_image_batch is None:
                try_get_image_batch = ImageBatch(chat_id, caption_text, file_path, update, 10)
                self._media_groups[media_group_id] = try_get_image_batch
                asyncio.create_task(self._init_image_batch_processing(media_group_id))
            else:
                try_get_image_batch.image_paths.append(file_path)
                try_get_image_batch.set_update(update)

        if not media_group_id:
            # Обычное одиночное фото
            reply_text = TelegramAgentBot.format_reply(
                self._agent.process_images(chat_id, caption_text, [file_path])
            )

            await TelegramAgentBot._reply(update, reply_text)

    async def _init_image_batch_processing(self, media_group_id: str):
        image_batch = self._media_groups[media_group_id]

        timeout_start = time.time()
        while time.time() < timeout_start + image_batch.timeout:
            print(image_batch.image_paths)
            await sleep(1)

        image_paths = image_batch.image_paths

        reply_text = TelegramAgentBot.format_reply(
            self._agent.process_images(image_batch.chat_id, image_batch.message, image_paths)
        )

        await TelegramAgentBot._reply(image_batch.update, reply_text)


    def run(self) -> None:
        # logging.basicConfig(
        #     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        #     level=logging.INFO,
        # )
        logger.info("Starting Telegram bot...")

        self.application.run_polling(allowed_updates=Update.ALL_TYPES, timeout=10)

    @staticmethod
    def format_reply(reply_message: str) -> str:
        return (reply_message
                .replace("###", "")
                .replace("##", "")
                .replace("**", "")
                .replace("/", "")
                .replace("\\", "")
                .replace("$", ""))

    @staticmethod
    async def _reply(update, reply_text:str):
        await update.message.reply_text(reply_text)


def create_bot() -> TelegramAgentBot:
    config = BotConfig()
    storage = ConversationStorage()

    creds = os.getenv("GIGACHAT_CREDS")

    agent = Agent(
        gigachat_creds=creds,
        gigachat_prompt_path="../agent/input/agent_llm_prompt.txt",
        gigachat_temperature=0.3,
        yc_folder_id=os.getenv("YC_FOLDER_ID"),
        yandex_gpt_api_key=os.getenv("YANDEX_GPT_API_KEY"),
        yandex_gpt_temperature=0.3,
        yandex_gpt_prompt_path="../agent/input/yandex_gpt_prompt.txt")

    return TelegramAgentBot(config, storage, agent)




