"""
Интеграционные тесты для Telegram-бота.

Agent и Telegram API замоканы — проверяется корректность
обработки сообщений, скачивания файлов и маршрутизации запросов.
"""
import asyncio

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from tg_bot.bot import TelegramAgentBot
from tg_bot.storage import ConversationStorage


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_agent():
    agent = MagicMock()
    agent.process_query = MagicMock(return_value="Анализ: ROS = 10.5%")
    return agent


@pytest.fixture
def bot(mock_agent):
    config = MagicMock()
    config.token = "0000000000:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    storage = ConversationStorage()

    with patch("tg_bot.bot.ApplicationBuilder"):
        return TelegramAgentBot(config, storage, mock_agent)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_update(
    chat_id: int = 123,
    text: str = None,
    caption: str = None,
    has_photo: bool = False,
    file_id: str = "test_file_id",
    media_group_id: str = None,
):
    """Собирает мок-объект Update, имитирующий сообщение Telegram."""
    update = MagicMock()
    update.effective_chat.id = chat_id

    message = MagicMock()
    message.text = text
    message.caption = caption
    message.media_group_id = media_group_id
    message.reply_text = AsyncMock()

    if has_photo:
        photo_small = MagicMock()
        photo_large = MagicMock()
        photo_large.file_id = file_id

        file_mock = MagicMock()
        file_mock.download_to_drive = AsyncMock()
        photo_large.get_file = AsyncMock(return_value=file_mock)

        message.photo = [photo_small, photo_large]
    else:
        message.photo = []

    update.message = message
    return update


# ---------------------------------------------------------------------------
# /start
# ---------------------------------------------------------------------------

class TestStartCommand:
    @pytest.mark.asyncio
    async def test_sends_welcome(self, bot):
        update = _make_update()
        await bot.start(update, MagicMock())

        update.message.reply_text.assert_awaited_once()
        text = update.message.reply_text.call_args[0][0]
        assert "финансовый" in text.lower()


# ---------------------------------------------------------------------------
# Текстовые сообщения
# ---------------------------------------------------------------------------

class TestHandleTextMessage:
    @pytest.mark.asyncio
    async def test_calls_agent_with_correct_args(self, bot, mock_agent):
        update = _make_update(chat_id=42, text="Посчитай ROS")
        await bot.handle_message(update, MagicMock())

        mock_agent.process_query.assert_called_once_with(42, "Посчитай ROS")

    @pytest.mark.asyncio
    async def test_sends_formatted_reply(self, bot, mock_agent):
        mock_agent.process_query.return_value = "**ROS** = $10.5\\%"
        update = _make_update(text="Посчитай ROS")
        await bot.handle_message(update, MagicMock())

        update.message.reply_text.assert_awaited_once()
        reply = update.message.reply_text.call_args[0][0]
        assert "ROS" in reply
        assert "**" not in reply
        assert "$" not in reply


# ---------------------------------------------------------------------------
# Одиночное фото
# ---------------------------------------------------------------------------

class TestHandleSinglePhoto:
    @pytest.mark.asyncio
    async def test_downloads_file(self, bot):
        update = _make_update(has_photo=True, caption="Проанализируй")

        with patch("os.makedirs"):
            await bot.handle_photo_with_caption(update, MagicMock())

        photo = update.message.photo[-1]
        photo.get_file.assert_awaited_once()

        file_obj = photo.get_file.return_value
        file_obj.download_to_drive.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_calls_agent_with_file_path(self, bot, mock_agent):
        update = _make_update(
            chat_id=42, has_photo=True, file_id="abc123", caption="Проанализируй"
        )

        with patch("os.makedirs"):
            await bot.handle_photo_with_caption(update, MagicMock())

        args = mock_agent.process_query.call_args[0]
        assert args[0] == 42
        assert args[1] == "Проанализируй"
        assert isinstance(args[2], list)
        assert len(args[2]) == 1
        assert "abc123" in args[2][0]
        assert args[2][0].endswith(".jpg")

    @pytest.mark.asyncio
    async def test_no_caption_passes_empty_string(self, bot, mock_agent):
        update = _make_update(has_photo=True, caption=None)

        with patch("os.makedirs"):
            await bot.handle_photo_with_caption(update, MagicMock())

        caption_arg = mock_agent.process_query.call_args[0][1]
        assert caption_arg == ""

    @pytest.mark.asyncio
    async def test_sends_reply(self, bot, mock_agent):
        mock_agent.process_query.return_value = "Отчёт распознан: выручка 85 962"
        update = _make_update(has_photo=True, caption="Что это?")

        with patch("os.makedirs"):
            await bot.handle_photo_with_caption(update, MagicMock())

        update.message.reply_text.assert_awaited_once()
        reply = update.message.reply_text.call_args[0][0]
        assert "Отчёт распознан" in reply


# ---------------------------------------------------------------------------
# Media group (несколько фото)
# ---------------------------------------------------------------------------

class TestMediaGroup:
    @pytest.mark.asyncio
    async def test_first_photo_creates_batch(self, bot):
        update = _make_update(
            chat_id=42, has_photo=True, caption="Баланс", media_group_id="mg_001"
        )

        with patch("os.makedirs"), patch("asyncio.create_task"):
            await bot.handle_photo_with_caption(update, MagicMock())

        assert "mg_001" in bot._media_groups
        batch = bot._media_groups["mg_001"]
        assert batch.chat_id == 42
        assert batch.message == "Баланс"
        assert len(batch.image_paths) == 1

    @pytest.mark.asyncio
    async def test_second_photo_appends_to_batch(self, bot):
        update1 = _make_update(
            chat_id=42, has_photo=True, file_id="file_a",
            caption="Баланс", media_group_id="mg_002",
        )
        update2 = _make_update(
            chat_id=42, has_photo=True, file_id="file_b",
            caption="", media_group_id="mg_002",
        )

        with patch("os.makedirs"), patch("asyncio.create_task"):
            await bot.handle_photo_with_caption(update1, MagicMock())
            await bot.handle_photo_with_caption(update2, MagicMock())

        batch = bot._media_groups["mg_002"]
        assert len(batch.image_paths) == 2
        paths = batch.image_paths
        assert "file_a" in paths[0]
        assert "file_b" in paths[1]

    @pytest.mark.asyncio
    async def test_does_not_reply_immediately(self, bot, mock_agent):
        update = _make_update(
            has_photo=True, caption="", media_group_id="mg_003"
        )

        with patch("os.makedirs"), patch("asyncio.create_task"):
            await bot.handle_photo_with_caption(update, MagicMock())

        mock_agent.process_query.assert_not_called()
        update.message.reply_text.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_batch_processing_calls_agent(self, bot, mock_agent):
        update1 = _make_update(
            chat_id=42, has_photo=True, file_id="p1",
            caption="Баланс", media_group_id="mg_004",
        )
        update2 = _make_update(
            chat_id=42, has_photo=True, file_id="p2",
            caption="", media_group_id="mg_004",
        )

        with patch("os.makedirs"), patch("asyncio.create_task"):
            await bot.handle_photo_with_caption(update1, MagicMock())
            await bot.handle_photo_with_caption(update2, MagicMock())

        batch = bot._media_groups["mg_004"]
        batch.timeout = 0

        with patch("tg_bot.bot.sleep", new_callable=AsyncMock):
            await bot._init_image_batch_processing("mg_004")

        args = mock_agent.process_query.call_args[0]
        assert args[0] == 42
        assert args[1] == "Баланс"
        assert len(args[2]) == 2


# ---------------------------------------------------------------------------
# format_reply
# ---------------------------------------------------------------------------

class TestFormatReply:
    def test_strips_markdown_bold(self):
        assert "ROS" in TelegramAgentBot.format_reply("**ROS**")
        assert "**" not in TelegramAgentBot.format_reply("**ROS**")

    def test_strips_headings(self):
        result = TelegramAgentBot.format_reply("### Заголовок\n## Подзаголовок")
        assert "###" not in result
        assert "##" not in result
        assert "Заголовок" in result

    def test_strips_dollar_sign(self):
        assert "$" not in TelegramAgentBot.format_reply("$100")

    def test_strips_backslash(self):
        assert "\\" not in TelegramAgentBot.format_reply("10\\%")

    def test_strips_slashes(self):
        assert "/" not in TelegramAgentBot.format_reply("10/20")

    def test_plain_text_unchanged(self):
        text = "Простой текст"
        assert TelegramAgentBot.format_reply(text) == text
