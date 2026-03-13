"""
LangChain-инструмент для детекции финансовых рисков и аномалий.
"""

from langchain_core.tools import tool

from agent.indicators.risk_detector import LEVEL_CRITICAL, LEVEL_OK, LEVEL_WARNING, detect_all_risks

_ICONS = {
    LEVEL_CRITICAL: "\U0001f534",  # 🔴
    LEVEL_WARNING:  "\U0001f7e1",  # 🟡
    LEVEL_OK:       "\U0001f7e2",  # 🟢
}


@tool(
    "analyze_risks",
    description=(
        "Анализирует финансовые риски и аномалии за указанный год: "
        "динамика выручки, убыточность, отрицательный капитал, ликвидность, "
        "финансовая устойчивость и Z-score Альтмана (риск банкротства). "
        "Принимает один параметр year (например '2025')."
    ),
)
def analyze_risks(year: str) -> str:
    """
    Запускает все проверки рисков за указанный год и возвращает
    форматированный текстовый отчёт для пользователя.

    :param year: год в виде строки, например "2025"
    :return: текст с результатами анализа
    """
    flags = detect_all_risks(year)

    critical = [f for f in flags if f.level == LEVEL_CRITICAL]
    warnings  = [f for f in flags if f.level == LEVEL_WARNING]
    ok_flags  = [f for f in flags if f.level == LEVEL_OK]

    lines = [f"Анализ финансовых рисков за {year} год:\n"]

    if critical:
        lines.append(f"{_ICONS[LEVEL_CRITICAL]} КРИТИЧЕСКИЕ РИСКИ:")
        for f in critical:
            lines.append(f"  • {f.indicator}: {f.message}")
        lines.append("")

    if warnings:
        lines.append(f"{_ICONS[LEVEL_WARNING]} ПРЕДУПРЕЖДЕНИЯ:")
        for f in warnings:
            lines.append(f"  • {f.indicator}: {f.message}")
        lines.append("")

    if ok_flags:
        lines.append(f"{_ICONS[LEVEL_OK]} В НОРМЕ:")
        for f in ok_flags:
            lines.append(f"  • {f.indicator}: {f.message}")

    if not critical and not warnings:
        lines.append("Критических рисков и предупреждений не обнаружено.")

    return "\n".join(lines)
