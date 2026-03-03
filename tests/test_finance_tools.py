import pytest

from agent.tools.utils import safe_div
from agent.tools.finance.profitability.ros import calculate_ros
from agent.tools.finance.profitability.roa import calculate_roa
from agent.tools.finance.profitability.roe import calculate_roe
from agent.tools.finance.profitability.gross_margin import calculate_gross_margin
from agent.tools.finance.profitability.operating_margin import calculate_operating_margin
from agent.tools.finance.profitability.turnover.total_asset import calculate_total_asset_turnover
from agent.tools.finance.profitability.turnover.inventory import calculate_inventory_turnover
from agent.tools.finance.profitability.turnover.receivables import calculate_receivables_turnover
from agent.tools.finance.profitability.turnover.payables import calculate_payables_turnover
from agent.tools.finance.stability import calculate_financial_stability_ratio
from agent.tools.finance.liquidity import (
    calculate_current_liquidity_ratio,
    calculate_quick_liquidity_ratio,
    calculate_cash_liquidity_ratio,
)


class TestSafeDiv:
    def test_normal_division(self):
        assert safe_div(10, 2) == 5.0

    def test_division_by_zero(self):
        assert safe_div(10, 0) == 0.0

    def test_rounds_to_six_decimals(self):
        result = safe_div(1, 3)
        assert result == round(1 / 3, 6)


# ========================= Profitability =========================

class TestROS:
    def test_normal(self):
        result = calculate_ros.invoke({"revenue": 500_000_000, "net_income": 30_000_000})
        assert result == safe_div(30_000_000, 500_000_000)

    def test_zero_revenue(self):
        result = calculate_ros.invoke({"revenue": 0, "net_income": 30_000_000})
        assert result == 0.0


class TestROA:
    def test_normal(self):
        result = calculate_roa.invoke({"net_income": 30_000_000, "avg_assets": 400_000_000})
        assert result == safe_div(30_000_000, 400_000_000)

    def test_zero_assets(self):
        result = calculate_roa.invoke({"net_income": 30_000_000, "avg_assets": 0})
        assert result == 0.0


class TestROE:
    def test_normal(self):
        result = calculate_roe.invoke({"net_income": 30_000_000, "avg_equity": 100_000_000})
        assert result == safe_div(30_000_000, 100_000_000)

    def test_zero_equity(self):
        result = calculate_roe.invoke({"net_income": 30_000_000, "avg_equity": 0})
        assert result == 0.0


class TestGrossMargin:
    def test_normal(self):
        result = calculate_gross_margin.invoke({"revenue": 500_000_000, "gross_profit": 100_000_000})
        assert result == safe_div(100_000_000, 500_000_000)

    def test_zero_revenue(self):
        result = calculate_gross_margin.invoke({"revenue": 0, "gross_profit": 100_000_000})
        assert result == 0.0


class TestOperatingMargin:
    def test_normal(self):
        result = calculate_operating_margin.invoke({"operating_income": 50_000_000, "revenue": 500_000_000})
        assert result == safe_div(50_000_000, 500_000_000)

    def test_zero_revenue(self):
        result = calculate_operating_margin.invoke({"operating_income": 50_000_000, "revenue": 0})
        assert result == 0.0


# ========================= Turnover =========================

class TestTotalAssetTurnover:
    def test_normal(self):
        result = calculate_total_asset_turnover.invoke({"revenue": 500_000_000, "avg_assets": 400_000_000})
        assert result == safe_div(500_000_000, 400_000_000)

    def test_zero_assets(self):
        result = calculate_total_asset_turnover.invoke({"revenue": 500_000_000, "avg_assets": 0})
        assert result == 0.0


class TestInventoryTurnover:
    def test_normal(self):
        result = calculate_inventory_turnover.invoke({"cogs": 300_000_000, "avg_inventory": 80_000_000})
        assert result == safe_div(300_000_000, 80_000_000)

    def test_zero_inventory(self):
        result = calculate_inventory_turnover.invoke({"cogs": 300_000_000, "avg_inventory": 0})
        assert result == 0.0


class TestReceivablesTurnover:
    def test_normal(self):
        result = calculate_receivables_turnover.invoke({"revenue": 500_000_000, "avg_receivables": 70_000_000})
        assert result == safe_div(500_000_000, 70_000_000)

    def test_zero_receivables(self):
        result = calculate_receivables_turnover.invoke({"revenue": 500_000_000, "avg_receivables": 0})
        assert result == 0.0


class TestPayablesTurnover:
    def test_normal(self):
        result = calculate_payables_turnover.invoke({"cogs": 300_000_000, "avg_payables": 120_000_000})
        assert result == safe_div(300_000_000, 120_000_000)

    def test_zero_payables(self):
        result = calculate_payables_turnover.invoke({"cogs": 300_000_000, "avg_payables": 0})
        assert result == 0.0


# ========================= Financial Stability =========================

class TestFinancialStabilityRatio:
    def test_normal(self):
        result = calculate_financial_stability_ratio.invoke({
            "equity": 62_993_367,
            "long_term_liabilities": 174_444_942,
            "total_assets": 482_772_230,
        })
        assert result == safe_div(62_993_367 + 174_444_942, 482_772_230)

    def test_zero_assets(self):
        result = calculate_financial_stability_ratio.invoke({
            "equity": 100, "long_term_liabilities": 200, "total_assets": 0,
        })
        assert result == 0.0


# ========================= Liquidity =========================

class TestCurrentLiquidityRatio:
    def test_normal(self):
        result = calculate_current_liquidity_ratio.invoke({
            "current_assets": 277_964_575,
            "current_liabilities": 245_333_921,
        })
        assert result == safe_div(277_964_575, 245_333_921)

    def test_zero_liabilities(self):
        result = calculate_current_liquidity_ratio.invoke({
            "current_assets": 100, "current_liabilities": 0,
        })
        assert result == 0.0


class TestQuickLiquidityRatio:
    def test_normal(self):
        result = calculate_quick_liquidity_ratio.invoke({
            "current_assets": 277_964_575,
            "inventory": 59_370_714,
            "current_liabilities": 245_333_921,
        })
        assert result == safe_div(277_964_575 - 59_370_714, 245_333_921)

    def test_zero_liabilities(self):
        result = calculate_quick_liquidity_ratio.invoke({
            "current_assets": 100, "inventory": 50, "current_liabilities": 0,
        })
        assert result == 0.0


class TestCashLiquidityRatio:
    def test_normal(self):
        result = calculate_cash_liquidity_ratio.invoke({
            "cash": 52_122_098,
            "short_term_investments": 21_802_782,
            "current_liabilities": 245_333_921,
        })
        assert result == safe_div(52_122_098 + 21_802_782, 245_333_921)

    def test_zero_liabilities(self):
        result = calculate_cash_liquidity_ratio.invoke({
            "cash": 100, "short_term_investments": 200, "current_liabilities": 0,
        })
        assert result == 0.0
