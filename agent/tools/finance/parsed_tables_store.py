"""
Хранилище распарсенных таблиц (баланс и ОФР), изолированное по session_id.

session_id устанавливается через ContextVar из agent/base.py (тот же set_session что и в calculation_cache).
Все инструменты обращаются к хранилищу без явной передачи session_id.
"""

from contextvars import ContextVar
from typing import Any, Dict, Optional, Tuple

_current_session_id: ContextVar[Optional[int]] = ContextVar("parsed_tables_session_id", default=None)

_store: Dict[int, Dict[str, Optional[Any]]] = {}


def set_session(session_id: int) -> None:
    """
    Выставляет текущий session_id. Вызывается из agent/base.py перед запуском агента.
    :param session_id: идентификатор пользователя/сессии
    """
    _current_session_id.set(session_id)


def _bucket() -> Dict[str, Optional[Any]]:
    """Возвращает (или создаёт) слот хранилища для текущей сессии."""
    sid = _current_session_id.get()
    if sid is None:
        raise RuntimeError(
            "session_id не задан — вызовите set_session(user_id) перед работой с хранилищем."
        )
    if sid not in _store:
        _store[sid] = {"balance": None, "ofr": None}
    return _store[sid]


def put_balance(report: Any) -> None:
    """Сохраняет баланс для текущей сессии."""
    _bucket()["balance"] = report


def put_ofr(report: Any) -> None:
    """Сохраняет ОФР для текущей сессии."""
    _bucket()["ofr"] = report


def get_balance() -> Optional[Any]:
    """Возвращает баланс текущей сессии."""
    return _bucket()["balance"]


def get_ofr() -> Optional[Any]:
    """Возвращает ОФР текущей сессии."""
    return _bucket()["ofr"]


def get_both() -> Tuple[Optional[Any], Optional[Any]]:
    """Возвращает (баланс, ОФР) текущей сессии."""
    b = _bucket()
    return b["balance"], b["ofr"]


def get_available_years() -> list:
    """Собирает список годов, для которых есть данные в текущей сессии."""
    balance, ofr = get_both()
    years = set()
    if balance and getattr(balance, "total_assets", None):
        years.update(balance.total_assets.keys())
    if ofr and getattr(ofr, "revenue", None):
        years.update(ofr.revenue.keys())
    return sorted(years, reverse=True)


def clear_session(session_id: int) -> None:
    """Полностью удаляет данные сессии из памяти."""
    _store.pop(session_id, None)
