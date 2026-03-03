import base64
import json
import pandas as pd
import re

from dotenv import load_dotenv

from agent.yandex.yandex_service import YandexOcrService
from consts.finance import financial_results_consts


# ==========================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ==========================

# def is_code(text):
#     return re.fullmatch(r"\d{4}", text) is not None


# def is_explanation(text):
#     return re.fullmatch(r"[\d\.,\s]+\.?", text) is not None


def is_number(text):
    t = text.replace(" ", "")
    return re.fullmatch(r"\(?-?\d+\)?", t) is not None


def clean_number(text):
    t = text.replace(" ", "")
    if t.startswith("(") and t.endswith(")"):
        return -int(t[1:-1])
    return int(t)




# ==========================
# СОХРАНЕНИЕ
# ==========================

def save_to_excel(df, filename):
    df.to_excel(filename, index=False)
    print("✅ Готово:", filename)


# ==========================
# ЗАПУСК
# ==========================

if __name__ == "__main__":
    with open("./kamaz_png.png", "rb") as f:
        load_dotenv()
        ocr = YandexOcrService()
        ocr.load_env()

        file_content = f.read()
        base64_content = base64.b64encode(file_content).decode("utf-8")
        result = ocr.call_ocr(base64_content)
        print(result)

        df = extract_clean_table(result)

        save_to_excel(df, "report_clean.xlsx")