from typing import Optional

EXCEL_OUTPUT_PATH_BASE = "./xlsx_output/"


def safe_div(a: Optional[float], b: Optional[float]) -> Optional[float]:
    """
    Деление с защитой от None и деления на ноль.
    Возвращает None если любой из аргументов None или знаменатель равен 0.
    """
    if a is None or b is None or b == 0:
        return None
    return round(a / b, 6)


def format_percent(raw: Optional[float], name: str) -> str:
    """
    Форматирует сырое значение (0.1234) как процент для вывода пользователю.
    :param raw: сырое значение, например 0.1234, или None если данных нет
    :param name: название показателя, например "ROS"
    :return: строка вида "ROS: 12.34%" или "ROS: нет данных"
    """
    if raw is None:
        return f"{name}: нет данных"
    return f"{name}: {round(raw, 4) * 100:.2f}%"


def format_ratio(raw: Optional[float], name: str) -> str:
    """
    Форматирует сырое значение как коэффициент для вывода пользователю.
    :param raw: сырое значение, например 3.4567, или None если данных нет
    :param name: название показателя, например "Current Liquidity Ratio"
    :return: строка вида "Current Liquidity Ratio: 3.4567" или "... нет данных"
    """
    if raw is None:
        return f"{name}: нет данных"
    return f"{name}: {round(raw, 4)}"

