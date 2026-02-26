from collections import defaultdict
from typing import Dict, List

from tg_bot.models.message import Message


class ConversationStorage:
    """
    Простое локальное in-memory хранилище истории сообщений.
    Ключ: chat_id, значение: список сообщений в формате dict.
    """

    def __init__(self) -> None:
        self._history: Dict[int, List[Message]] = defaultdict(list)

    def add_message(self, chat_id: int, role: str, text: str, file_path: str = None) -> None:
        self._history[chat_id].append(Message(role, text, file_path))

    def get_history(self, chat_id: int) -> List[Message]:
        return list(self._history.get(chat_id))

    def clear_history(self, chat_id: int) -> None:
        if chat_id in self._history:
            del self._history[chat_id]




