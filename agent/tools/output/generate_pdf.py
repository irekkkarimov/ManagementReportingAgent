"""
Генерация PDF-отчёта с аналитическими графиками.

Структура PDF (4 страницы):
1. Рентабельность  — line chart (значения в %)
2. Оборачиваемость — grouped bar chart
3. Ликвидность     — grouped bar chart + нормативные линии
4. Финансовая устойчивость — bar chart

Данные берутся из inputs_cache текущей сессии.
Параметры не нужны.
"""

from typing import Dict, List, Optional

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.backends.backend_pdf import PdfPages

from langchain_core.tools import tool

from agent.indicators.compute import ALL_INDICATORS, IndicatorDef
from agent.tools.output._shared import compute_all_indicators, get_years_or_error, make_output_path

matplotlib.use("Agg")

_PDF_OUTPUT_DIR = "./pdf_output"

_COLORS = ["#2E86AB", "#E84855", "#F9A620", "#3BB273", "#7B2D8B", "#FF6B35"]

_LIQUIDITY_NORMS = {
    "Коэффициент текущей ликвидности": (2.0, "норма ≥ 2.0"),
    "Коэффициент быстрой ликвидности": (1.0, "норма ≥ 1.0"),
    "Коэффициент абсолютной ликвидности": (0.2, "норма ≥ 0.2"),
}


def _get_section_indicators(section: str) -> List[IndicatorDef]:
    return [ind for ind in ALL_INDICATORS if ind.section == section]


def _filter_valid(
    indicators: List[IndicatorDef],
    years: List[str],
    results: Dict[str, Dict[str, Optional[float]]],
) -> Dict[str, List[Optional[float]]]:
    """
    Возвращает только те показатели, у которых есть хотя бы одно ненулевое значение.
    Структура: {indicator_name: [val_year1, val_year2, ...]}
    """
    data = {}
    for ind in indicators:
        vals = [results.get(ind.name, {}).get(y) for y in years]
        if any(v is not None for v in vals):
            data[ind.name] = vals
    return data


def _short_name(name: str) -> str:
    """Сокращает длинное название для отображения на оси."""
    replacements = {
        "Рентабельность продаж (ROS)": "ROS",
        "Рентабельность активов (ROA)": "ROA",
        "Рентабельность капитала (ROE)": "ROE",
        "Оборачиваемость дебиторской задолженности": "Об. дебит.",
        "Оборачиваемость кредиторской задолженности": "Об. кредит.",
        "Коэффициент финансовой устойчивости": "Фин. устойч.",
        "Коэффициент текущей ликвидности": "Текущая",
        "Коэффициент быстрой ликвидности": "Быстрая",
        "Коэффициент абсолютной ликвидности": "Абсолютная",
    }
    return replacements.get(name, name)


def _page_profitability(pdf: PdfPages, years: List[str], results: Dict) -> None:
    """Страница 1: Рентабельность — line chart."""
    indicators = _get_section_indicators("Рентабельность")
    data = _filter_valid(indicators, years, results)
    if not data:
        return

    fig, ax = plt.subplots(figsize=(11, 6))
    fig.suptitle("Рентабельность", fontsize=16, fontweight="bold", y=0.98)

    for idx, (name, vals) in enumerate(data.items()):
        color = _COLORS[idx % len(_COLORS)]
        plot_years = [y for y, v in zip(years, vals) if v is not None]
        plot_vals = [v * 100 for v in vals if v is not None]
        ax.plot(plot_years, plot_vals, marker="o", label=_short_name(name), color=color, linewidth=2)

    ax.axhline(0, color="black", linewidth=0.8, linestyle="--", alpha=0.5)
    ax.set_ylabel("Значение, %")
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f%%"))
    ax.legend(loc="best", fontsize=9)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.set_title("Динамика показателей рентабельности по годам", fontsize=11, pad=8)
    fig.tight_layout()
    pdf.savefig(fig)
    plt.close(fig)


def _page_turnover(pdf: PdfPages, years: List[str], results: Dict) -> None:
    """Страница 2: Оборачиваемость — grouped bar chart."""
    indicators = _get_section_indicators("Оборачиваемость")
    data = _filter_valid(indicators, years, results)
    if not data:
        return

    fig, ax = plt.subplots(figsize=(11, 6))
    fig.suptitle("Оборачиваемость", fontsize=16, fontweight="bold", y=0.98)

    n_groups = len(years)
    n_bars = len(data)
    bar_width = 0.7 / n_bars
    x = range(n_groups)

    for idx, (name, vals) in enumerate(data.items()):
        offsets = [xi + (idx - n_bars / 2 + 0.5) * bar_width for xi in x]
        plot_vals = [v if v is not None else 0 for v in vals]
        bars = ax.bar(offsets, plot_vals, bar_width * 0.9,
                      label=_short_name(name), color=_COLORS[idx % len(_COLORS)], alpha=0.85)
        for bar, val in zip(bars, vals):
            if val is not None:
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                        f"{val:.2f}", ha="center", va="bottom", fontsize=7)

    ax.set_xticks(list(x))
    ax.set_xticklabels(years)
    ax.set_ylabel("Коэффициент")
    ax.legend(loc="best", fontsize=9)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.set_title("Коэффициенты оборачиваемости по годам", fontsize=11, pad=8)
    fig.tight_layout()
    pdf.savefig(fig)
    plt.close(fig)


def _page_liquidity(pdf: PdfPages, years: List[str], results: Dict) -> None:
    """Страница 3: Ликвидность — grouped bar chart + нормативные линии."""
    indicators = _get_section_indicators("Ликвидность")
    data = _filter_valid(indicators, years, results)
    if not data:
        return

    fig, ax = plt.subplots(figsize=(11, 6))
    fig.suptitle("Ликвидность", fontsize=16, fontweight="bold", y=0.98)

    n_groups = len(years)
    n_bars = len(data)
    bar_width = 0.7 / n_bars
    x = range(n_groups)

    for idx, (name, vals) in enumerate(data.items()):
        offsets = [xi + (idx - n_bars / 2 + 0.5) * bar_width for xi in x]
        plot_vals = [v if v is not None else 0 for v in vals]
        bars = ax.bar(offsets, plot_vals, bar_width * 0.9,
                      label=_short_name(name), color=_COLORS[idx % len(_COLORS)], alpha=0.85)
        for bar, val in zip(bars, vals):
            if val is not None:
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                        f"{val:.2f}", ha="center", va="bottom", fontsize=7)

        norm_info = _LIQUIDITY_NORMS.get(name)
        if norm_info:
            norm_val, norm_label = norm_info
            ax.axhline(norm_val, linestyle="--", linewidth=1.2,
                       color=_COLORS[idx % len(_COLORS)], alpha=0.6,
                       label=norm_label)

    ax.set_xticks(list(x))
    ax.set_xticklabels(years)
    ax.set_ylabel("Коэффициент")
    ax.legend(loc="best", fontsize=8)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.set_title("Коэффициенты ликвидности с нормативами", fontsize=11, pad=8)
    fig.tight_layout()
    pdf.savefig(fig)
    plt.close(fig)


def _page_stability(pdf: PdfPages, years: List[str], results: Dict) -> None:
    """Страница 4: Финансовая устойчивость — bar chart."""
    indicators = _get_section_indicators("Финансовая устойчивость")
    data = _filter_valid(indicators, years, results)
    if not data:
        return

    fig, ax = plt.subplots(figsize=(11, 6))
    fig.suptitle("Финансовая устойчивость", fontsize=16, fontweight="bold", y=0.98)

    for idx, (name, vals) in enumerate(data.items()):
        plot_vals = [v if v is not None else 0 for v in vals]
        bars = ax.bar(years, plot_vals, color=_COLORS[idx % len(_COLORS)], alpha=0.85,
                      label=_short_name(name))
        for bar, val in zip(bars, vals):
            if val is not None:
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
                        f"{val:.4f}", ha="center", va="bottom", fontsize=9)

    ax.axhline(0.6, linestyle="--", linewidth=1.2, color="red", alpha=0.7, label="норма ≥ 0.6")
    ax.set_ylabel("Коэффициент")
    ax.set_ylim(bottom=0)
    ax.legend(loc="best", fontsize=9)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.set_title("Коэффициент финансовой устойчивости по годам", fontsize=11, pad=8)
    fig.tight_layout()
    pdf.savefig(fig)
    plt.close(fig)


@tool(
    "generate_pdf_report",
    description=(
        "Создаёт PDF с аналитическими графиками по всем финансовым показателям. "
        "Считает показатели самостоятельно по всем доступным годам. "
        "Параметры не нужны."
    ),
)
def generate_pdf_report() -> str:
    """
    Рассчитывает все 13 показателей и генерирует PDF с 4 страницами графиков:
    рентабельность, оборачиваемость, ликвидность, финансовая устойчивость.

    :return: путь к файлу или сообщение об ошибке
    """
    years = get_years_or_error()
    if isinstance(years, str):
        return years

    results = compute_all_indicators(years)
    file_path = make_output_path(_PDF_OUTPUT_DIR, "financial_report", "pdf")

    with PdfPages(file_path) as pdf:
        _page_profitability(pdf, years, results)
        _page_turnover(pdf, years, results)
        _page_liquidity(pdf, years, results)
        _page_stability(pdf, years, results)

        info = pdf.infodict()
        info["Title"] = "Финансовый отчёт"
        info["Subject"] = "Аналитические графики финансовых показателей"

    return f"PDF сохранён: {file_path}"
