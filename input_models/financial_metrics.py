
class FinancialMetrics:
    # ===== Отчет о прибылях и убытках =====
    revenue: float  # Выручка
    cost_of_goods_sold: float  # Себестоимость продаж (COGS)
    operating_profit: float  # Операционная прибыль
    gross_profit: float  # Операционная прибыль
    net_profit: float  # Чистая прибыль

    # ===== Баланс (на начало периода) =====
    total_assets_begin: float  # Активы на начало периода
    equity_begin: float  # Собственный капитал на начало периода
    inventory_begin: float  # Запасы на начало периода
    receivables_begin: float  # Дебиторская задолженность на начало периода
    payables_begin: float  # Кредиторская задолженность на начало периода

    # ===== Баланс (на конец периода) =====
    total_assets_end: float  # Активы на конец периода
    equity_end: float  # Собственный капитал на конец периода
    inventory_end: float  # Запасы на конец периода
    receivables_end: float  # Дебиторская задолженность на конец периода
    payables_end: float  # Кредиторская задолженность на конец периода

    # ===== Вычисляемые средние (опционально можно считать отдельно) =====
    def average_assets(self) -> float:
        return (self.total_assets_begin + self.total_assets_end) / 2

    def average_equity(self) -> float:
        return (self.equity_begin + self.equity_end) / 2

    def average_inventory(self) -> float:
        return (self.inventory_begin + self.inventory_end) / 2

    def average_receivables(self) -> float:
        return (self.receivables_begin + self.receivables_end) / 2

    def average_payables(self) -> float:
        return (self.payables_begin + self.payables_end) / 2