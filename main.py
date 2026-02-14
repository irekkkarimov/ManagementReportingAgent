import os

from agent.analytics import AnalyticsEngine
from agent.data_loader import DataLoader
from agent.data_preprocessor import DataPreprocessor
from agent.file_outputs.data_postprocessor import DataPostprocessor
from agent.file_outputs.excel_generator import ExcelReportGenerator
from agent.file_outputs.pdf_generator import PDFReportGenerator
from agent.search.yandex_gpt import YandexGPT
from agent.visualization import VisualizationEngine
from agent.search.search_processor import SearchProcessor
from agent.search.yandex_search import YandexSearch
from dotenv import load_dotenv

load_dotenv()

FOLDER_ID = os.getenv("FOLDER_ID")
API_KEY = os.getenv("API_KEY_ALL")


def main():
    yc_search = YandexSearch(folder_id=FOLDER_ID, api_key=API_KEY)
    yc_gpt = YandexGPT(folder_id=FOLDER_ID, api_key=API_KEY, prompt_path="./agent/input/prompt.txt")
    search_processor = SearchProcessor()

    domain = "Логистика"
    search_query = "Средняя выручка предприятий в сфере логистики в РФ в 2025"

    search_result = yc_search.search(search_query)

    clean_html = search_processor.clean_html(search_result)
    extracted_html = search_processor.extract_result(search_query, clean_html)

    search_processor.save_html_to_file(str(clean_html), "./output/search.html")
    search_processor.save_formatted_json(extracted_html, "./output/result.json")

    gpt_result = yc_gpt.process_search(domain, extracted_html)
    yc_gpt.save_result_to_json(gpt_result, "./output/gpt_result.json")
    print(YandexGPT.extract_gpt_answer(gpt_result))

    return

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


if __name__ == "__main__":
    main()