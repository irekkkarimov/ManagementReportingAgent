"""
Парсер XML-файла КНД 0710099 (бухгалтерская отчётность из 1С/ФНС).

Файл содержит одновременно:
  <Баланс ОКУД="0710001"> — бухгалтерский баланс
  <ФинРез ОКУД="0710002"> — отчёт о финансовых результатах

Атрибуты значений:
  СумОтч   — текущий отчётный год (берётся из Документ/@ОтчетГод)
  СумПрдщ  — предыдущий год (отчётный − 1)  — только в Баланс
  СумПрдшв — год до предыдущего (отчётный − 2) — только в Баланс
  СумПред  — предыдущий год — только в ФинРез

Расходные строки ОФР (OFR_NEGATIVE_CODES) хранятся в модели со знаком минус
для совместимости с формулами calculate_*.
"""

import xml.etree.ElementTree as ET
from typing import Optional, Tuple

from consts.finance import OFR_NEGATIVE_CODES
from input_models.accountant_balance_report import AccountantBalanceReport
from input_models.financial_results_report import FinancialResultsReport

# Соответствие кодов ОФР к тегам XML-файла
_OFR_TAG_TO_FIELD = {
    "Выруч":           ("revenue",                           "2110"),
    "СебестПрод":      ("cost_of_sales",                     "2120"),
    "ВаловаяПрибыль":  ("gross_profit",                      "2100"),
    "КоммРасх":        ("commercial_expenses",               "2210"),
    "УпрРасх":         ("management_expenses",               "2220"),
    "ПрибПрод":        ("profit_from_sales",                 "2200"),
    "ПроцПолуч":       ("percentage_receivable",             "2320"),
    "ПроцУпл":         ("percentage_to_pay",                 "2330"),
    "ПрочДоход":       ("other_profit",                      "2340"),
    "ПрочРасход":      ("other_expenses",                    "2350"),
    "ПрибУбДоНал":     ("profit_from_continuing_operations", "2300"),
    "НалПриб":         ("organization_income_tax",           "2410"),
    "ОтложНалПриб":    ("deferred_organization_income_tax",  "2412"),
    "ЧистПриб":        ("net_profit",                        "2400"),
    "ЧистПрибУб":      ("net_profit",                        "2400"),  # 1С 3.x
    "СовФинРез":       ("total_financial_result",            "2500"),
}


def _safe_int(el: Optional[ET.Element], attr: str) -> Optional[int]:
    """Читает целочисленный атрибут из элемента. None если атрибут отсутствует."""
    if el is None:
        return None
    raw = el.get(attr)
    if raw is None:
        return None
    try:
        return int(raw)
    except (ValueError, TypeError):
        return None


def _set3(el: Optional[ET.Element], d: dict,
          yr: str, yr_p: str, yr_p2: str) -> None:
    """
    Записывает в словарь d значения трёх годов из атрибутов СумОтч/СумПрдщ/СумПрдшв.
    Пропускает год если атрибут отсутствует в XML.
    """
    if el is None:
        return
    v = _safe_int(el, "СумОтч");  d[yr]   = v if v is not None else d.get(yr, 0)
    v = _safe_int(el, "СумПрдщ"); d[yr_p] = v if v is not None else d.get(yr_p, 0)
    v = _safe_int(el, "СумПрдшв")
    if v is not None:
        d[yr_p2] = v


def _set2_ofr(el: Optional[ET.Element], d: dict,
              yr: str, yr_p: str, code: str) -> None:
    """
    Записывает два года из атрибутов СумОтч/СумПред (формат ФинРез).
    Инвертирует знак для кодов из OFR_NEGATIVE_CODES.
    """
    if el is None:
        return
    negative = code in OFR_NEGATIVE_CODES

    v = _safe_int(el, "СумОтч")
    if v is not None:
        d[yr] = -abs(v) if negative and v != 0 else v

    v = _safe_int(el, "СумПред")
    if v is not None:
        d[yr_p] = -abs(v) if negative and v != 0 else v


def _parse_balance(doc: ET.Element, yr: str, yr_p: str, yr_p2: str) -> AccountantBalanceReport:
    b = AccountantBalanceReport()
    bal = doc.find("Баланс")
    if bal is None:
        return b

    aktiv = bal.find("Актив")
    if aktiv is not None:
        _set3(aktiv, b.total_assets, yr, yr_p, yr_p2)

        vneoboa = aktiv.find("ВнеОбА")
        if vneoboa is not None:
            _set3(vneoboa,                    b.total_noncurrent_assets,          yr, yr_p, yr_p2)
            _set3(vneoboa.find("НематАкт"),   b.intangible_assets,                yr, yr_p, yr_p2)
            _set3(vneoboa.find("ОснСр"),      b.fixed_assets,                     yr, yr_p, yr_p2)
            _set3(vneoboa.find("ИнвНедв"),    b.investment_property,              yr, yr_p, yr_p2)
            _set3(vneoboa.find("ФинВлож"),    b.financial_investments_noncurrent, yr, yr_p, yr_p2)
            _set3(vneoboa.find("ОтлНалАкт"),  b.deferred_tax_assets,              yr, yr_p, yr_p2)
            _set3(vneoboa.find("ПрочВнеОбА"), b.other_noncurrent_assets,          yr, yr_p, yr_p2)

        oba = aktiv.find("ОбА")
        if oba is not None:
            _set3(oba,                    b.total_current_assets,          yr, yr_p, yr_p2)
            _set3(oba.find("Запасы"),     b.inventories,                   yr, yr_p, yr_p2)
            _set3(oba.find("НДСПриобрЦен"), b.vat,                         yr, yr_p, yr_p2)
            _set3(oba.find("ДебЗад"),     b.receivables,                   yr, yr_p, yr_p2)
            _set3(oba.find("ФинВлож"),    b.financial_investments_current, yr, yr_p, yr_p2)
            _set3(oba.find("ДенежнСр"),   b.cash,                          yr, yr_p, yr_p2)
            _set3(oba.find("ПрочОбА"),    b.other_current_assets,          yr, yr_p, yr_p2)

    passiv = bal.find("Пассив")
    if passiv is not None:
        _set3(passiv, b.total_liabilities, yr, yr_p, yr_p2)

        kapital = passiv.find("Капитал")
        if kapital is not None:
            _set3(kapital,                    b.total_equity,      yr, yr_p, yr_p2)
            _set3(kapital.find("УставКапитал"), b.charter_capital, yr, yr_p, yr_p2)
            _set3(kapital.find("НакОцВнеОбА"),  b.additional_capital, yr, yr_p, yr_p2)
            _set3(kapital.find("РезКапитал"),    b.reserve_capital, yr, yr_p, yr_p2)
            _set3(kapital.find("НераспПриб"),    b.retained_earnings, yr, yr_p, yr_p2)

        dolg = passiv.find("ДолгосрОбяз")
        if dolg is not None:
            _set3(dolg,                    b.total_noncurrent_liabilities, yr, yr_p, yr_p2)
            _set3(dolg.find("ЗаемСредств"), b.borrowings_noncurrent,       yr, yr_p, yr_p2)
            _set3(dolg.find("ОтложНалОбяз"), b.deferred_tax_liabilities,   yr, yr_p, yr_p2)
            _set3(dolg.find("ПрочОбяз"),    b.other_noncurrent_liabilities, yr, yr_p, yr_p2)

        kratk = passiv.find("КраткосрОбяз")
        if kratk is not None:
            _set3(kratk,                    b.total_current_liabilities, yr, yr_p, yr_p2)
            _set3(kratk.find("ЗаемСредств"), b.borrowings_current,       yr, yr_p, yr_p2)
            _set3(kratk.find("КредитЗадолж"), b.accounts_payable,        yr, yr_p, yr_p2)

    return b


def _parse_ofr(doc: ET.Element, yr: str, yr_p: str) -> FinancialResultsReport:
    ofr = FinancialResultsReport()
    fin = doc.find("ФинРез")
    if fin is None:
        return ofr

    for tag, (field_name, code) in _OFR_TAG_TO_FIELD.items():
        _set2_ofr(fin.find(tag), getattr(ofr, field_name), yr, yr_p, code)

    return ofr


def parse_xml_report(file_path: str) -> Tuple[AccountantBalanceReport, FinancialResultsReport]:
    """
    Парсит XML-файл КНД 0710099 (формат 1С/ФНС, кодировка windows-1251).
    ElementTree автоматически читает encoding из заголовка XML-файла.

    :param file_path: путь к .xml файлу
    :return: кортеж (AccountantBalanceReport, FinancialResultsReport)
    :raises FileNotFoundError: файл не найден
    :raises ET.ParseError: XML повреждён
    """
    tree = ET.parse(file_path)
    root = tree.getroot()

    doc = root.find("Документ")
    if doc is None:
        raise ValueError("Элемент <Документ> не найден в XML-файле.")

    report_year = doc.get("ОтчетГод", "2025")
    yr   = report_year
    yr_p = str(int(report_year) - 1)
    yr_p2 = str(int(report_year) - 2)

    balance = _parse_balance(doc, yr, yr_p, yr_p2)
    ofr     = _parse_ofr(doc, yr, yr_p)

    return balance, ofr
