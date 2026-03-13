"""
Детекция финансовых аномалий и рисков.

Содержит:
- RiskFlag: структура одной проверки
- Набор правил: выручка, капитал, ликвидность, устойчивость
- Модель Альтмана (Z-score) для непубличных компаний
- detect_all_risks(year): запуск всех проверок и возврат списка флагов
"""

from typing import List, NamedTuple, Optional

from agent.indicators.compute import (
    compute_current_liquidity_ratio,
    compute_financial_stability_ratio,
)
from agent.tools.finance.inputs_cache import get_input

LEVEL_CRITICAL = "КРИТИЧНО"
LEVEL_WARNING   = "ВНИМАНИЕ"
LEVEL_OK        = "OK"


class RiskFlag(NamedTuple):
    """Результат одной проверки риска."""
    level: str              # КРИТИЧНО | ВНИМАНИЕ | OK
    indicator: str          # Название показателя
    message: str            # Текст для пользователя
    value: Optional[float]  # Фактическое значение (None если не удалось посчитать)


# ---------------------------------------------------------------------------
# Вспомогательная функция
# ---------------------------------------------------------------------------

def _fmt_thr(v: Optional[float], is_percent: bool = False) -> str:
    """Форматирует значение для вывода в сообщении."""
    if v is None:
        return "нет данных"
    if is_percent:
        return f"{v * 100:.2f}%"
    return f"{v:.4f}"


# ---------------------------------------------------------------------------
# Отдельные проверки
# ---------------------------------------------------------------------------

def _check_revenue_drop(year: str) -> RiskFlag:
    """Падение выручки > 20% год к году."""
    prev = str(int(year) - 1)
    current = get_input(year, "revenue")
    previous = get_input(prev, "revenue")

    if current is None or previous is None or previous == 0:
        return RiskFlag(LEVEL_OK, "Выручка (динамика)", "Нет данных за оба периода для сравнения.", None)

    change = (current - previous) / abs(previous)
    if change <= -0.20:
        return RiskFlag(
            LEVEL_CRITICAL,
            "Выручка (динамика)",
            f"Выручка упала на {abs(change) * 100:.1f}% по сравнению с {prev} годом "
            f"({previous:,.0f} \u2192 {current:,.0f} тыс. руб.). Резкое падение — тревожный сигнал.",
            change,
        )
    if change <= -0.05:
        return RiskFlag(
            LEVEL_WARNING,
            "Выручка (динамика)",
            f"Выручка снизилась на {abs(change) * 100:.1f}% по сравнению с {prev} годом.",
            change,
        )
    return RiskFlag(LEVEL_OK, "Выручка (динамика)", f"Динамика выручки в норме ({change * 100:+.1f}%).", change)


def _check_net_profit(year: str) -> RiskFlag:
    """Отрицательная чистая прибыль."""
    value = get_input(year, "net_profit")
    if value is None:
        return RiskFlag(LEVEL_OK, "Чистая прибыль", "Нет данных.", None)
    if value < 0:
        return RiskFlag(
            LEVEL_CRITICAL,
            "Чистая прибыль",
            f"Чистая прибыль отрицательная: {value:,.0f} тыс. руб. — компания несёт убытки.",
            value,
        )
    return RiskFlag(LEVEL_OK, "Чистая прибыль", f"Чистая прибыль положительная: {value:,.0f} тыс. руб.", value)


def _check_equity(year: str) -> RiskFlag:
    """Отрицательный собственный капитал — угроза банкротства."""
    value = get_input(year, "total_equity")
    if value is None:
        return RiskFlag(LEVEL_OK, "Собственный капитал", "Нет данных.", None)
    if value < 0:
        return RiskFlag(
            LEVEL_CRITICAL,
            "Собственный капитал",
            f"Собственный капитал отрицательный: {value:,.0f} тыс. руб. — "
            "обязательства превышают активы, высокая угроза банкротства.",
            value,
        )
    return RiskFlag(LEVEL_OK, "Собственный капитал", f"Собственный капитал положительный: {value:,.0f} тыс. руб.", value)


def _check_current_liquidity(year: str) -> RiskFlag:
    """Коэффициент текущей ликвидности (норма ≥ 2.0)."""
    value = compute_current_liquidity_ratio(year)
    if value is None:
        return RiskFlag(LEVEL_OK, "Текущая ликвидность", "Нет данных.", None)
    if value < 1.0:
        return RiskFlag(
            LEVEL_CRITICAL,
            "Текущая ликвидность",
            f"Коэффициент текущей ликвидности = {value:.2f} (критично < 1.0). "
            "Краткосрочных активов недостаточно для покрытия краткосрочных обязательств.",
            value,
        )
    if value < 2.0:
        return RiskFlag(
            LEVEL_WARNING,
            "Текущая ликвидность",
            f"Коэффициент текущей ликвидности = {value:.2f} (ниже нормы 2.0). "
            "Платёжеспособность под угрозой.",
            value,
        )
    return RiskFlag(LEVEL_OK, "Текущая ликвидность", f"Коэффициент текущей ликвидности = {value:.2f} (норма ≥ 2.0). ", value)


def _check_financial_stability(year: str) -> RiskFlag:
    """Коэффициент финансовой устойчивости (норма ≥ 0.6)."""
    value = compute_financial_stability_ratio(year)
    if value is None:
        return RiskFlag(LEVEL_OK, "Финансовая устойчивость", "Нет данных.", None)
    if value < 0.4:
        return RiskFlag(
            LEVEL_CRITICAL,
            "Финансовая устойчивость",
            f"Коэффициент финансовой устойчивости = {value:.2f} (критично < 0.4). "
            "Компания крайне зависима от заёмного капитала.",
            value,
        )
    if value < 0.6:
        return RiskFlag(
            LEVEL_WARNING,
            "Финансовая устойчивость",
            f"Коэффициент финансовой устойчивости = {value:.2f} (ниже нормы 0.6). "
            "Доля собственных и долгосрочных источников финансирования недостаточна.",
            value,
        )
    return RiskFlag(LEVEL_OK, "Финансовая устойчивость", f"Коэффициент финансовой устойчивости = {value:.2f} (норма ≥ 0.6).", value)


# ---------------------------------------------------------------------------
# Модель Альтмана (Z-score) для непубличных компаний
# ---------------------------------------------------------------------------
# Формула (модифицированная, 1983):
#   Z = 0.717*X1 + 0.847*X2 + 3.107*X3 + 0.420*X4 + 0.998*X5
#
# X1 = Оборотный капитал / Активы       = (ОА - КО) / А
# X2 = Нераспределённая прибыль / Активы = НП / А
# X3 = EBIT / Активы                    ≈ Чистая прибыль / Активы
# X4 = Балансовая ст-сть капитала / Обяз = СК / (ДО + КО)
# X5 = Выручка / Активы

def compute_altman_z(year: str) -> Optional[float]:
    """
    Вычисляет Z-score Альтмана для непубличных компаний.
    Возвращает None если недостаточно данных.
    """
    current_assets  = get_input(year, "total_current_assets")
    current_liab    = get_input(year, "total_current_liabilities")
    total_assets    = get_input(year, "total_assets")
    retained        = get_input(year, "retained_earnings")
    net_profit      = get_input(year, "net_profit")
    equity          = get_input(year, "total_equity")
    noncurrent_liab = get_input(year, "total_noncurrent_liabilities")
    revenue         = get_input(year, "revenue")

    # Минимально необходимые поля
    if any(v is None for v in (current_assets, current_liab, total_assets, net_profit, equity, revenue)):
        return None
    if total_assets == 0:
        return None

    working_capital = current_assets - current_liab  # type: ignore[operator]
    total_liab = (noncurrent_liab or 0.0) + (current_liab or 0.0)  # type: ignore[operator]

    x1 = working_capital / total_assets
    x2 = (retained or 0.0) / total_assets  # type: ignore[operator]
    x3 = net_profit / total_assets          # type: ignore[operator]
    x4 = equity / total_liab if total_liab != 0 else 0.0  # type: ignore[operator]
    x5 = revenue / total_assets             # type: ignore[operator]

    return 0.717 * x1 + 0.847 * x2 + 3.107 * x3 + 0.420 * x4 + 0.998 * x5


def _check_altman_z(year: str) -> RiskFlag:
    """Проверка по модели Альтмана."""
    z = compute_altman_z(year)
    if z is None:
        return RiskFlag(LEVEL_OK, "Z-score Альтмана", "Недостаточно данных для расчёта.", None)

    if z < 1.23:
        return RiskFlag(
            LEVEL_CRITICAL,
            "Z-score Альтмана",
            f"Z-score = {z:.3f} — ВЫСОКИЙ риск банкротства (порог: < 1.23). "
            "Модель Альтмана сигнализирует об угрозе финансовой несостоятельности.",
            z,
        )
    if z < 2.90:
        return RiskFlag(
            LEVEL_WARNING,
            "Z-score Альтмана",
            f"Z-score = {z:.3f} — зона неопределённости (1.23 – 2.90). "
            "Финансовое состояние нестабильно, требует мониторинга.",
            z,
        )
    return RiskFlag(
        LEVEL_OK,
        "Z-score Альтмана",
        f"Z-score = {z:.3f} — низкий риск банкротства (порог: > 2.90).",
        z,
    )


# ---------------------------------------------------------------------------
# Главная функция
# ---------------------------------------------------------------------------

def detect_all_risks(year: str) -> List[RiskFlag]:
    """
    Запускает все проверки рисков для указанного года.
    Возвращает список RiskFlag, отсортированный: сначала КРИТИЧНО, затем ВНИМАНИЕ, затем OK.

    :param year: год в виде строки, например "2025"
    :return: список флагов рисков
    """
    flags: List[RiskFlag] = [
        _check_revenue_drop(year),
        _check_net_profit(year),
        _check_equity(year),
        _check_current_liquidity(year),
        _check_financial_stability(year),
        _check_altman_z(year),
    ]

    order = {LEVEL_CRITICAL: 0, LEVEL_WARNING: 1, LEVEL_OK: 2}
    return sorted(flags, key=lambda f: order.get(f.level, 9))
