from dataclasses import dataclass


@dataclass
class FinanceReportModel:
    # Рентабельность
    ros: float = None
    roa: float = None
    roe: float = None
    gross_margin: float = None
    operating_margin: float = None

    def to_dict(self) -> dict:
        """Возвращает все показатели в виде словаря"""
        return {
            "Profitability": {
                "ROS": self.ros,
                "ROA": self.roa,
                "ROE": self.roe,
                "Gross Margin": self.gross_margin,
                "Operating Margin": self.operating_margin,
            }
        }



 # # Оборачиваемость
    # total_asset_turnover: float = None  # Оборачиваемость активов
    # inventory_turnover: float = None  # Оборачиваемость запасов
    # receivables_turnover: float = None  # Оборачиваемость дебиторской задолженности
    # payables_turnover: float = None  # Оборачиваемость кредиторской задолженности
    #
    # # Финансовая устойчивость
    # financial_stability_ratio: float = None  # Коэффициент финансовой устойчивости
    #
    # # Ликвидность
    # current_ratio: float = None  # Коэффициент текущей ликвидности
    # quick_ratio: float = None  # Коэффициент быстрой ликвидности
    # cash_ratio: float = None  # Коэффициент абсолютной ликвидности



# "Turnover": {
            #     "Total Asset Turnover": self.total_asset_turnover,
            #     "Inventory Turnover": self.inventory_turnover,
            #     "Receivables Turnover": self.receivables_turnover,
            #     "Payables Turnover": self.payables_turnover,
            # },
            # "Financial Stability": {
            #     "Financial Stability Ratio": self.financial_stability_ratio,
            # },
            # "Liquidity": {
            #     "Current Ratio": self.current_ratio,
            #     "Quick Ratio": self.quick_ratio,
            #     "Cash Ratio": self.cash_ratio,
            # }