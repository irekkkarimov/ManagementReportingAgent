"""
Кэш результатов финансовых расчётов, изолированный по session_id.

Схема: Dict[session_id, Dict[indicator_name, raw_value]]

session_id устанавливается через ContextVar перед вызовом агента (agent/base.py),
поэтому инструменты calculate_* не получают его явно — они просто вызывают
set_indicator/get_indicators, а кэш сам разберётся, к какой сессии обращаться.
"""

from contextvars import ContextVar
from typing import Dict, Optional

_current_session_id: ContextVar[Optional[int]] = ContextVar("current_session_id", default=None)

_cache: Dict[int, Dict[str, float]] = {}


def set_session(session_id: int) -> None:
    """
    Выставляет текущий session_id для всех последующих вызовов в этом контексте.
    Вызывается один раз в agent/base.py перед передачей запроса агенту.
    :param session_id: идентификатор пользователя/сессии
    """
    _current_session_id.set(session_id)


def _session_bucket() -> Dict[str, float]:
    """Возвращает (или создаёт) словарь показателей для текущей сессии."""
    sid = _current_session_id.get()
    if sid is None:
        raise RuntimeError(
            "session_id не задан — вызовите set_session(user_id) перед работой с кэшем."
        )
    if sid not in _cache:
        _cache[sid] = {}
    return _cache[sid]


def set_indicator(name: str, value: float) -> None:
    """
    Сохраняет сырое значение показателя в кэш текущей сессии.
    :param name: название показателя (например, "ROS", "ROA", "Gross Margin")
    :param value: сырое числовое значение (0.123 для 12.3%)
    """
    if value is None:
        return
    try:
        _session_bucket()[name] = float(value)
    except (TypeError, ValueError):
        pass


def get_indicators() -> Dict[str, float]:
    """
    Возвращает копию кэша всех показателей текущей сессии.
    """
    return dict(_session_bucket())


def clear_indicators() -> None:
    """
    Очищает кэш показателей текущей сессии.
    """
    _session_bucket().clear()


def clear_session(session_id: int) -> None:
    """
    Полностью удаляет данные сессии из глобального словаря (освобождает память).
    :param session_id: идентификатор сессии
    """
    _cache.pop(session_id, None)
