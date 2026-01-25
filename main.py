from agent.analytics import AnalyticsEngine
from agent.data_loader import DataLoader
from agent.data_preprocessor import DataPreprocessor
from agent.file_outputs.data_postprocessor import DataPostprocessor
from agent.file_outputs.excel_generator import ExcelReportGenerator
from agent.file_outputs.pdf_generator import PDFReportGenerator
from agent.visualization import VisualizationEngine
from data.generate_data import DataGenerator


def main():
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