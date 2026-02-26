EXCEL_OUTPUT_PATH_BASE = "./xlsx_output/"


def safe_div(a: float, b: float) -> float:
    if b == 0:
        return 0.0
    return round(a / b, 6)

