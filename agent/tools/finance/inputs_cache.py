"""
Кэш входных данных для расчёта финансовых показателей, изолированный по session_id и году.

Структура: Dict[session_id, Dict[year, Dict[field, value]]]

Заполняется автоматически при загрузке таблиц через merge_model_fields.
Читается инструментами calculate_*(year).
"""

from contextvars import ContextVar
from dataclasses import fields, is_dataclass
from typing import Any, Dict, Optional

_current_session_id: ContextVar[Optional[int]] = ContextVar("inputs_session_id", default=None)

_cache: Dict[int, Dict[str, Dict[str, float]]] = {}


def set_session(session_id: int) -> None:
    """
    Выставляет текущий session_id. Вызывается из agent/base.py перед запуском агента.
    :param session_id: идентификатор пользователя/сессии
    """
    _current_session_id.set(session_id)


def _session_bucket() -> Dict[str, Dict[str, float]]:
    sid = _current_session_id.get()
    if sid is None:
        raise RuntimeError(
            "session_id не задан — вызовите set_session(user_id) перед работой с inputs_cache."
        )
    if sid not in _cache:
        _cache[sid] = {}
    return _cache[sid]


def merge_model_fields(model: Any) -> None:
    """
    Читает все поля dataclass-модели (AccountantBalanceReport или FinancialResultsReport),
    у каждого поля ожидает Dict[year, value], и мержит данные в кэш по годам.

    Вызывается сразу после загрузки таблицы — без необходимости вызывать
    get_finance_data_for_calculations отдельно.

    :param model: экземпляр AccountantBalanceReport или FinancialResultsReport
    """
    if not is_dataclass(model):
        return
    bucket = _session_bucket()
    for f in fields(model):
        year_dict = getattr(model, f.name, None)
        if not isinstance(year_dict, dict):
            continue
        for year, value in year_dict.items():
            if value is None:
                continue
            if year not in bucket:
                bucket[year] = {}
            try:
                bucket[year][f.name] = float(value)
            except (TypeError, ValueError):
                pass


def set_inputs(year: str, inputs: Dict[str, float]) -> None:
    """
    Сохраняет (или дополняет) входные данные за указанный год.
    :param year: год, например "2024"
    :param inputs: словарь полей
    """
    bucket = _session_bucket()
    if year not in bucket:
        bucket[year] = {}
    bucket[year].update(inputs)


def get_input(year: str, name: str, default: float = 0.0) -> float:
    """
    Возвращает конкретное поле из кэша за указанный год.
    :param year: год, например "2024"
    :param name: имя поля, например "revenue", "total_assets"
    :param default: значение по умолчанию если поля или года нет
    """
    return _session_bucket().get(year, {}).get(name, default)


def get_all_inputs(year: str) -> Dict[str, float]:
    """Возвращает копию всех входных данных за указанный год."""
    return dict(_session_bucket().get(year, {}))


def get_available_years() -> list:
    """Возвращает список годов, за которые загружены данные."""
    return sorted(_session_bucket().keys(), reverse=True)


def clear_year(year: str) -> None:
    """Очищает данные за конкретный год в текущей сессии."""
    _session_bucket().pop(year, None)


def clear_session(session_id: int) -> None:
    """Полностью удаляет данные сессии из памяти."""
    _cache.pop(session_id, None)
