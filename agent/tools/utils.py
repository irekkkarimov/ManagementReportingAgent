EXCEL_OUTPUT_PATH_BASE = "./xlsx_output/"


def safe_div(a: float, b: float) -> float:
    if b == 0:
        return 0.0
    return round(a / b, 6)


def format_percent(raw: float, name: str) -> str:
    """
    Форматирует сырое значение (0.1234) как процент для вывода пользователю.
    Округляет до 4 знаков после запятой перед форматированием.
    :param raw: сырое значение, например 0.1234
    :param name: название показателя, например "ROS"
    :return: строка вида "ROS: 12.34%"
    """
    rounded = round(raw, 4)
    return f"{name}: {rounded * 100:.2f}%"


def format_ratio(raw: float, name: str) -> str:
    """
    Форматирует сырое значение как коэффициент для вывода пользователю.
    Округляет до 4 знаков после запятой перед форматированием.
    :param raw: сырое значение, например 3.4567
    :param name: название показателя, например "Current Liquidity Ratio"
    :return: строка вида "Current Liquidity Ratio: 3.4567"
    """
    rounded = round(raw, 4)
    return f"{name}: {rounded}"

