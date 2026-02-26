from agent.common.data_loader import DataLoader
from agent.other.data_preprocessor import DataPreprocessor
from agent.other.analytics import AnalyticsEngine
from agent.other.visualization import VisualizationEngine
from agent.other.text_generator import TextExplanationGenerator


class ReportAIAgent:
    """ИИ-агент для управленческой отчетности"""

    def __init__(self):
        self.loader = DataLoader()
        self.preprocessor = DataPreprocessor()
        self.analytics = AnalyticsEngine()
        self.visualizer = VisualizationEngine()
        self.text_generator = TextExplanationGenerator()

    def run(self, data_path: str):
        df = self.loader.load_from_csv(data_path)
        df = self.preprocessor.preprocess(df)
        df = self.analytics.calculate_profit(df)
        df = self.analytics.aggregate_by_period(df)

        self.visualizer.plot_profit(df)

        explanation = self.text_generator.generate_summary(df)
        print(explanation)