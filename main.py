import os

import pandas as pd

from agent.base import Agent
from agent.other.analytics import AnalyticsEngine
from agent.common.data_loader import DataLoader
from agent.other.data_preprocessor import DataPreprocessor
from agent.file_outputs.data_postprocessor import DataPostprocessor
from agent.file_outputs.excel_generator import ExcelReportGenerator
from agent.file_outputs.pdf_generator import PDFReportGenerator
from agent.finance.FinanceProcessor import FinanceProcessor
from agent.other.visualization import VisualizationEngine
from dotenv import load_dotenv

load_dotenv()

FOLDER_ID = os.getenv("FOLDER_ID")
API_KEY = os.getenv("API_KEY_ALL")


def main():
    return test_agent()
    # return financial_reports_main()
    # yc_search = YandexSearch(folder_id=FOLDER_ID, api_key=API_KEY)
    # yc_gpt = YandexGPT(folder_id=FOLDER_ID, api_key=API_KEY, prompt_path="./agent/input/yandex_gpt_prompt.txt")
    # search_processor = SearchProcessor()
    #
    # domain = "Логистика"
    # search_query = "Средняя выручка предприятий в сфере логистики в РФ в 2025"
    #
    # search_result = yc_search.search(search_query)
    #
    # clean_html = search_processor.clean_html(search_result)
    # extracted_html = search_processor.extract_result(search_query, clean_html)
    #
    # search_processor.save_html_to_file(str(clean_html), "./output/search.html")
    # search_processor.save_formatted_json(extracted_html, "./output/result.json")
    #
    # gpt_result = yc_gpt.process_search(domain, extracted_html)
    # yc_gpt.save_result_to_json(gpt_result, "./output/gpt_result.json")
    # print(YandexGPT.extract_gpt_answer(gpt_result))
    #
    # return

    loader = DataLoader()
    preprocessor = DataPreprocessor()
    postprocessor = DataPostprocessor()
    analytics = AnalyticsEngine()
    visualizer = VisualizationEngine()
    excel_generator = ExcelReportGenerator()
    pdf_generator = PDFReportGenerator()

    # 1. Подгрузка данных
    df = loader.load_from_csv("data/management_reporting_data.csv")

    # 2. Предобработка
    df = preprocessor.preprocess(df)

    # 3. Расчет прибыли
    df = analytics.calculate_profit(df)

    # 4. Итоговые показатели
    totals = analytics.calculate_totals(df)

    # 5. Агрегации
    monthly_report = analytics.aggregate_by_month(df)
    department_report = analytics.aggregate_by_department(df)

    print(monthly_report)

    # 6. Вывод результатов
    print("\n=== TOTAL METRICS ===")
    for k, v in totals.items():
        print(f"{k}: {v:,.2f}")

    print("\n=== MONTHLY P&L ===")
    print(monthly_report.head())

    print("\n=== DEPARTMENT P&L ===")
    print(department_report)

    # 4. Вывод в файл
    final_table = postprocessor.prepare(df)
    pdf_generator.generate(final_table, "C:/Users/Irek Karimov/PycharmProjects/ManagementReportingAgent/data/output.pdf")

    # 5. Визуализация
    visualizer.plot_monthly_pl(monthly_report)
    visualizer.plot_profit_by_department(department_report)

def financial_reports_main():
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)
    pd.set_option('display.float_format', lambda x: f'{x:,.2f}' if pd.notna(x) else '')
    pd.set_option('display.precision', 2)
    
    finance = FinanceProcessor("old/data/income.csv", "old/data/balance.csv")

    profitability = finance.calc_profitability()


    print(profitability)

    return

def test_agent():
    agent = Agent(gigachat_creds=API_KEY, gigachat_prompt_path="agent/input/yandex_gpt_prompt.txt")
    print(agent.process_text("What is the weather in Kazan?"))

if __name__ == "__main__":
    main()