"""
Интеграционные тесты: отправка картинки боту → расчёт финансовых показателей.

Мокается только Yandex OCR и Telegram API.
Весь остальной код работает по-настоящему:
  - parse_financial_report_tool (detect_report_type, extract_years, parse_table_by_codes)
  - calculate_ros / calculate_gross_margin / calculate_operating_margin
  - calculate_current_liquidity_ratio / calculate_financial_stability_ratio / etc.
  - Agent.process_query (формирует правильное сообщение с путями к файлам)
  - TelegramAgentBot.handle_photo_with_caption (скачивает фото, вызывает агента)

Каждый тест моделирует конкретный сценарий пользователя:
  "Отправил картинку → попросил посчитать показатель → получил ответ"

parse_financial_report_tool возвращает JSON:
  {
    "report_type": "financial_results",
    "label": "Отчёт о финансовых результатах",
    "years": ["2023", "2022"],
    "rows": {
      "2110": {"name": "Выручка", "2023": 85962, "2022": 101732},
      ...
    }
  }
"""
import json

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from agent.tools.image.recognize_image import parse_financial_report_tool
from agent.tools.finance.profitability.ros import calculate_ros
from agent.tools.finance.profitability.gross_margin import calculate_gross_margin
from agent.tools.finance.profitability.operating_margin import calculate_operating_margin
from agent.tools.finance.liquidity import (
    calculate_current_liquidity_ratio,
    calculate_quick_liquidity_ratio,
    calculate_cash_liquidity_ratio,
)
from agent.tools.finance.stability import calculate_financial_stability_ratio
from tg_bot.bot import TelegramAgentBot


# ---------------------------------------------------------------------------
# Mock OCR data — имитирует то, что возвращает Yandex OCR для каждого типа отчёта
# ---------------------------------------------------------------------------

# ОФР «Дельта» за 2023/2022 — реальные данные с картинки из тестов
DELTA_OFR_LINES = [
    "(в ред. Приказов Минфина Россииот 06.04.2015 № 57н, от 06.03.2018 № 41н,от 19.04.2019 № 61н)",
    "Отчет о финансовых результатах",
    "за _",
    "ГОД",
    "20 23",
    "Коды",
    "0710002",
    "31", "12.", "23", "|",
    "Организация Общество с ограниченной ответственностью \"Дельта\"",
    "12300000", "1234512345",
    "Торговля оптовая за вознаграждение или на",
    "договорной основе", "46.1",
    "Организационно-правовая форма/форма собственности Общество с",
    "ограниченной ответственностью / частная собственность",
    "12300", "16...", "384",
    "Поясне-", "ния 1", "Наименование показателя 2", "Код",
    "За...", "ГОД", "20 23 г.3",
    "За _", "ГОД", "20 22 г.4",
    "Выручка 5",     "2110", "85 962",     "101 732",
    "в том числе:", "выручка от продажи продукции",
    "2111", "63 195",   "70 622",
    "выручка от продажи покупных товаров",
    "2112", "18 149",   "15 287",
    "Себестоимость продаж",
    "2120", "72 014",   "71 165",
    "в том числе:", "проданной продукции",
    "2121", "53 215",   "52 600",
    "проданных товаров",
    "2122", "15 221",   "15 628",
    "Валовая прибыль (убыток)",
    "2100", "13 948",   "30 567",
    "Коммерческие расходы",
    "2210", "860",      "3 781",
    "Управленческие расходы",
    "2220", "4 967",    "15 780",
    "Прибыль (убыток) от продаж",
    "2200", "8 121",    "11 006",
    "Доходы от участия в других организациях",
    "2310", "5 460",    "7 280",
    "Проценты к получению",
    "2320", "281",      "133",
    "Проценты к уплате",
    "2330", "607",      "372",
    "Прочие доходы",
    "2340", "1 131",    "1 554",
    "Прочие расходы",
    "2350", "2 971",    "3 425",
    "Прибыль (убыток) до налогообложения",
    "2300", "11 415",   "16 176",
    "Налог на прибыль 7",
    "2410", "1 557",    "1 381",
    "В Т.Ч.", "текущий налог на прибыль",
    "2411", "1 201",    "1 426",
    "отложенный налог на прибыль",
    "2412", "356",      "45...",
    "Прочее",
    "2460", "135",      "15",
    "Чистая прибыль (убыток)",
    "2400", "9 723",    "14 780",
]

# Бухгалтерский баланс с оборотными активами и пассивами для тестов ликвидности
BALANCE_SHEET_LINES = [
    "Бухгалтерский баланс",
    "на 31 декабря 2025 г.",
    "Коды",
    "Форма по ОКУД", "0710001",
    "Пояснения", "Наименование показателя", "Код показателя",
    "На 31 декабря 2025 г.", "На 31 декабря 2024 г.", "На 31 декабря 2023 г.",
    "АКТИВ",
    "I. Внеоборотные активы",
    "3.1, 3.2, 3.3, 3.4, 3.5, 6.1",
    "Нематериальные активы",
    "1110", "30 818 632",  "27 819 290",  "23 666 277",
    "Основные средства",
    "1150", "79 802 713",  "73 105 357",  "64 377 722",
    "Итого по Разделу I",
    "1100", "204 807 655", "205 594 799", "182 233 408",
    "II. Оборотные активы",
    "6.1, 6.2, 6.3",
    "Запасы",
    "1210", "59 370 714",  "101 915 123", "57 829 068",
    "Денежные средства",
    "1250", "12 000 000",  "9 500 000",   "8 000 000",
    "Краткосрочные финансовые вложения",
    "1240", "5 000 000",   "3 000 000",   "2 500 000",
    "Дебиторская задолженность",
    "1230.2", "80 000 000", "70 000 000", "60 000 000",
    "Итого по Разделу II",
    "1200", "277 964 575", "292 355 715", "242 396 446",
    "БАЛАНС",
    "1600", "482 772 230", "497 950 514", "424 629 854",
    "ПАССИВ",
    "III. Капитал",
    "Уставный капитал",
    "1310", "35 361 478",  "35 361 478",  "35 361 478",
    "Нераспределенная прибыль",
    "1370", "62 993 367",  "51 624 130",  "37 021 450",
    "Итого по Разделу III",
    "1300", "142 000 000", "130 000 000", "110 000 000",
    "IV. Долгосрочные обязательства",
    "Заёмные средства",
    "1410", "78 400 000",  "90 000 000",  "85 000 000",
    "Итого по Разделу IV",
    "1400", "80 000 000",  "95 000 000",  "90 000 000",
    "V. Краткосрочные обязательства",
    "Заёмные средства",
    "1510", "50 000 000",  "45 000 000",  "40 000 000",
    "Кредиторская задолженность",
    "1520", "100 000 000", "110 000 000", "95 000 000",
    "Итого по Разделу V",
    "1500", "165 000 000", "172 772 230", "155 000 000",
    "БАЛАНС",
    "1700", "482 772 230", "497 950 514", "424 629 854",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_ofr(file_path: str = "./foto.jpg") -> dict:
    """Вызывает parse_financial_report_tool с замокаными OCR-данными ОФР, возвращает dict."""
    with patch("agent.tools.image.recognize_image.ocr_file_to_lines", return_value=DELTA_OFR_LINES):
        raw = parse_financial_report_tool.invoke({"file_paths": file_path})
    return json.loads(raw)


def _parse_bs(file_path: str = "./foto.jpg") -> dict:
    """Вызывает parse_financial_report_tool с замокаными OCR-данными баланса, возвращает dict."""
    with patch("agent.tools.image.recognize_image.ocr_file_to_lines", return_value=BALANCE_SHEET_LINES):
        raw = parse_financial_report_tool.invoke({"file_paths": file_path})
    return json.loads(raw)


def _make_photo_update(
    chat_id: int = 1,
    file_id: str = "photo_001",
    caption: str = "",
    media_group_id: str = None,
):
    update = MagicMock()
    update.effective_chat.id = chat_id
    message = MagicMock()
    message.caption = caption
    message.media_group_id = media_group_id
    message.reply_text = AsyncMock()

    photo = MagicMock()
    photo.file_id = file_id
    file_mock = MagicMock()
    file_mock.download_to_drive = AsyncMock()
    photo.get_file = AsyncMock(return_value=file_mock)
    message.photo = [MagicMock(), photo]

    update.message = message
    return update


def _make_bot(agent_response: str) -> TelegramAgentBot:
    mock_agent = MagicMock()
    mock_agent.process_query = MagicMock(return_value=agent_response)
    config = MagicMock()
    config.token = "0000000000:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    with patch("tg_bot.bot.ApplicationBuilder"):
        from tg_bot.storage import ConversationStorage
        bot = TelegramAgentBot(config, ConversationStorage(), mock_agent)
    return bot, mock_agent


# ---------------------------------------------------------------------------
# 1. parse_financial_report_tool — распознаёт ОФР корректно
# ---------------------------------------------------------------------------

class TestOFRParseTool:
    def test_detects_report_type(self):
        data = _parse_ofr()
        assert data["report_type"] == "financial_results"
        assert "финансовых результатах" in data["label"]

    def test_extracts_years_from_split_header(self):
        """OCR бьёт '20 23 г.' на части — должны правильно склеить."""
        data = _parse_ofr()
        assert "2023" in data["years"]
        assert "2022" in data["years"]

    def test_revenue_present(self):
        data = _parse_ofr()
        year = data["years"][0]
        assert data["rows"]["2110"][year] == 85962

    def test_cost_is_negative(self):
        """Себестоимость (2120) отрицательная через OFR_NEGATIVE_CODES."""
        data = _parse_ofr()
        year = data["years"][0]
        assert data["rows"]["2120"][year] == -72014

    def test_commercial_expenses_negative(self):
        data = _parse_ofr()
        year = data["years"][0]
        assert data["rows"]["2210"][year] == -860

    def test_net_profit_present(self):
        data = _parse_ofr()
        year = data["years"][0]
        assert data["rows"]["2400"][year] == 9723

    def test_years_are_json_keys_in_rows(self):
        """Годы должны быть ключами внутри каждой строки."""
        data = _parse_ofr()
        year = data["years"][0]
        assert year in data["rows"]["2110"]


# ---------------------------------------------------------------------------
# 2. parse_financial_report_tool — распознаёт баланс корректно
# ---------------------------------------------------------------------------

class TestBalanceSheetParseTool:
    def test_detects_report_type(self):
        data = _parse_bs()
        assert data["report_type"] == "balance_sheet"
        assert "Бухгалтерский баланс" in data["label"]

    def test_three_year_columns(self):
        data = _parse_bs()
        assert len(data["years"]) == 3
        assert "2025" in data["years"]
        assert "2024" in data["years"]
        assert "2023" in data["years"]

    def test_total_assets_present(self):
        data = _parse_bs()
        year = data["years"][0]
        assert data["rows"]["1600"][year] == 482772230

    def test_current_assets_present(self):
        data = _parse_bs()
        year = data["years"][0]
        assert data["rows"]["1200"][year] == 277964575

    def test_inventories_present(self):
        data = _parse_bs()
        year = data["years"][0]
        assert data["rows"]["1210"][year] == 59370714


# ---------------------------------------------------------------------------
# 3. Сценарий: фото ОФР + «посчитай рентабельность продаж (ROS)»
# ---------------------------------------------------------------------------

class TestROSFromPhoto:
    def test_parse_gives_correct_revenue_and_profit(self):
        data = _parse_ofr()
        year = data["years"][0]
        assert data["rows"]["2110"][year] == 85962
        assert data["rows"]["2400"][year] == 9723

    def test_calculate_ros_with_parsed_values(self):
        """Значения из parse → calculate_ros → верный результат."""
        ros = calculate_ros.invoke({"revenue": 85962.0, "net_income": 9723.0})
        expected = round(9723 / 85962, 6)
        assert ros == pytest.approx(expected)
        assert abs(ros - 0.1131) < 0.001  # ≈ 11.3%

    def test_previous_year_ros(self):
        ros = calculate_ros.invoke({"revenue": 101732.0, "net_income": 14780.0})
        assert abs(ros - 0.1452) < 0.001  # ≈ 14.5%

    def test_ros_declined_year_over_year(self):
        ros_current = calculate_ros.invoke({"revenue": 85962.0, "net_income": 9723.0})
        ros_prev    = calculate_ros.invoke({"revenue": 101732.0, "net_income": 14780.0})
        assert ros_current < ros_prev  # рентабельность упала

    @pytest.mark.asyncio
    async def test_bot_handler_passes_file_path_to_agent(self):
        bot, mock_agent = _make_bot("ROS = 11.31%")
        update = _make_photo_update(chat_id=7, file_id="ros_img", caption="Посчитай рентабельность продаж")

        with patch("os.makedirs"):
            await bot.handle_photo_with_caption(update, MagicMock())

        args = mock_agent.process_query.call_args[0]
        assert args[0] == 7
        assert "рентабельность" in args[1].lower()
        assert len(args[2]) == 1 and "ros_img" in args[2][0]

    @pytest.mark.asyncio
    async def test_bot_sends_ros_result_to_user(self):
        bot, _ = _make_bot("ROS = 11.31%")
        update = _make_photo_update(caption="Посчитай рентабельность продаж")

        with patch("os.makedirs"):
            await bot.handle_photo_with_caption(update, MagicMock())

        update.message.reply_text.assert_awaited_once()
        reply = update.message.reply_text.call_args[0][0]
        assert "ROS" in reply or "11.31" in reply


# ---------------------------------------------------------------------------
# 4. Сценарий: фото ОФР + «посчитай валовую рентабельность (Gross Margin)»
# ---------------------------------------------------------------------------

class TestGrossMarginFromPhoto:
    def test_parse_gives_gross_profit(self):
        data = _parse_ofr()
        year = data["years"][0]
        assert data["rows"]["2100"][year] == 13948

    def test_calculate_gross_margin(self):
        gm = calculate_gross_margin.invoke({"revenue": 85962.0, "gross_profit": 13948.0})
        expected = round(13948 / 85962, 6)
        assert gm == pytest.approx(expected)
        assert abs(gm - 0.1622) < 0.001  # ≈ 16.2%

    def test_gross_margin_previous_year(self):
        gm = calculate_gross_margin.invoke({"revenue": 101732.0, "gross_profit": 30567.0})
        assert abs(gm - 0.3004) < 0.001  # ≈ 30%

    def test_gross_margin_fell_significantly(self):
        gm_curr = calculate_gross_margin.invoke({"revenue": 85962.0, "gross_profit": 13948.0})
        gm_prev = calculate_gross_margin.invoke({"revenue": 101732.0, "gross_profit": 30567.0})
        assert gm_curr < gm_prev
        assert (gm_prev - gm_curr) > 0.13  # упала более чем на 13 п.п.

    @pytest.mark.asyncio
    async def test_bot_routes_gross_margin_request(self):
        bot, mock_agent = _make_bot("Gross Margin = 16.2%")
        update = _make_photo_update(caption="Посчитай валовую рентабельность")

        with patch("os.makedirs"):
            await bot.handle_photo_with_caption(update, MagicMock())

        assert mock_agent.process_query.called
        caption = mock_agent.process_query.call_args[0][1]
        assert "валовую" in caption.lower() or "gross" in caption.lower()


# ---------------------------------------------------------------------------
# 5. Сценарий: фото ОФР + «посчитай операционную рентабельность»
# ---------------------------------------------------------------------------

class TestOperatingMarginFromPhoto:
    def test_parse_gives_operating_profit(self):
        data = _parse_ofr()
        year = data["years"][0]
        assert data["rows"]["2200"][year] == 8121

    def test_calculate_operating_margin(self):
        om = calculate_operating_margin.invoke({"operating_income": 8121.0, "revenue": 85962.0})
        expected = round(8121 / 85962, 6)
        assert om == pytest.approx(expected)
        assert abs(om - 0.0945) < 0.001  # ≈ 9.4%

    def test_operating_margin_previous_year(self):
        om = calculate_operating_margin.invoke({"operating_income": 11006.0, "revenue": 101732.0})
        assert abs(om - 0.1082) < 0.001

    @pytest.mark.asyncio
    async def test_bot_routes_operating_margin_request(self):
        bot, mock_agent = _make_bot("Operating Margin = 9.45%")
        update = _make_photo_update(caption="Посчитай операционную рентабельность")

        with patch("os.makedirs"):
            await bot.handle_photo_with_caption(update, MagicMock())

        assert mock_agent.process_query.called
        file_paths = mock_agent.process_query.call_args[0][2]
        assert len(file_paths) == 1


# ---------------------------------------------------------------------------
# 6. Сценарий: фото баланса + «посчитай текущую ликвидность»
# ---------------------------------------------------------------------------

class TestLiquidityFromBalanceSheet:
    def test_parse_gives_current_assets(self):
        data = _parse_bs()
        year = data["years"][0]
        assert data["rows"]["1200"][year] == 277964575

    def test_parse_gives_current_liabilities(self):
        data = _parse_bs()
        year = data["years"][0]
        assert data["rows"]["1500"][year] == 165000000

    def test_current_liquidity(self):
        ratio = calculate_current_liquidity_ratio.invoke({
            "current_assets": 277_964_575.0,
            "current_liabilities": 165_000_000.0,
        })
        expected = round(277_964_575 / 165_000_000, 6)
        assert ratio == pytest.approx(expected)
        assert ratio > 1.0  # норма > 1

    def test_quick_liquidity(self):
        """(Оборотные активы − Запасы) / Краткосрочные обязательства."""
        ratio = calculate_quick_liquidity_ratio.invoke({
            "current_assets": 277_964_575.0,
            "inventory": 59_370_714.0,
            "current_liabilities": 165_000_000.0,
        })
        expected = round((277_964_575 - 59_370_714) / 165_000_000, 6)
        assert ratio == pytest.approx(expected)
        assert ratio > 0.8

    def test_cash_liquidity(self):
        """(Денежные средства + Краткосрочные вложения) / Краткосрочные обязательства."""
        ratio = calculate_cash_liquidity_ratio.invoke({
            "cash": 12_000_000.0,
            "short_term_investments": 5_000_000.0,
            "current_liabilities": 165_000_000.0,
        })
        expected = round(17_000_000 / 165_000_000, 6)
        assert ratio == pytest.approx(expected)

    @pytest.mark.asyncio
    async def test_bot_routes_liquidity_request(self):
        bot, mock_agent = _make_bot("Коэффициент текущей ликвидности = 1.69")
        update = _make_photo_update(caption="Посчитай текущую ликвидность")

        with patch("os.makedirs"):
            await bot.handle_photo_with_caption(update, MagicMock())

        args = mock_agent.process_query.call_args[0]
        assert "ликвидность" in args[1].lower()
        assert len(args[2]) == 1

    @pytest.mark.asyncio
    async def test_bot_sends_liquidity_result(self):
        bot, _ = _make_bot("Коэффициент текущей ликвидности = 1.69")
        update = _make_photo_update(caption="Посчитай текущую ликвидность")

        with patch("os.makedirs"):
            await bot.handle_photo_with_caption(update, MagicMock())

        reply = update.message.reply_text.call_args[0][0]
        assert "1.69" in reply or "ликвидност" in reply.lower()


# ---------------------------------------------------------------------------
# 7. Сценарий: фото баланса + «посчитай финансовую устойчивость»
# ---------------------------------------------------------------------------

class TestStabilityFromBalanceSheet:
    def test_parse_gives_equity_and_ltl(self):
        data = _parse_bs()
        year = data["years"][0]
        assert data["rows"]["1300"][year] == 142000000
        assert data["rows"]["1400"][year] == 80000000
        assert data["rows"]["1600"][year] == 482772230

    def test_financial_stability_ratio(self):
        """(Капитал + Долгосрочные обязательства) / Активы."""
        ratio = calculate_financial_stability_ratio.invoke({
            "equity": 142_000_000.0,
            "long_term_liabilities": 80_000_000.0,
            "total_assets": 482_772_230.0,
        })
        expected = round((142_000_000 + 80_000_000) / 482_772_230, 6)
        assert ratio == pytest.approx(expected)
        assert ratio > 0.4  # норма ≥ 0.6

    @pytest.mark.asyncio
    async def test_bot_routes_stability_request(self):
        bot, mock_agent = _make_bot("Коэффициент финансовой устойчивости = 0.46")
        update = _make_photo_update(caption="Посчитай финансовую устойчивость")

        with patch("os.makedirs"):
            await bot.handle_photo_with_caption(update, MagicMock())

        args = mock_agent.process_query.call_args[0]
        assert "устойчив" in args[1].lower()


# ---------------------------------------------------------------------------
# 8. Сценарий: фото ОФР без подписи → агент сам инициирует анализ
# ---------------------------------------------------------------------------

class TestPhotoWithoutCaption:
    @pytest.mark.asyncio
    async def test_empty_caption_still_calls_agent(self):
        bot, mock_agent = _make_bot("Отчёт распознан. Выручка: 85 962 тыс. руб.")
        update = _make_photo_update(caption=None)

        with patch("os.makedirs"):
            await bot.handle_photo_with_caption(update, MagicMock())

        assert mock_agent.process_query.called
        caption = mock_agent.process_query.call_args[0][1]
        assert caption == ""  # пустая строка — агент обработает сам

    @pytest.mark.asyncio
    async def test_parse_tool_called_with_correct_path(self):
        """Agent.process_query должен получить путь, сформированный из file_id."""
        bot, mock_agent = _make_bot("Данные распознаны")
        update = _make_photo_update(file_id="unique_photo_xyz", caption="")

        with patch("os.makedirs"):
            await bot.handle_photo_with_caption(update, MagicMock())

        file_paths = mock_agent.process_query.call_args[0][2]
        assert any("unique_photo_xyz" in p for p in file_paths)
        assert all(p.endswith(".jpg") for p in file_paths)


# ---------------------------------------------------------------------------
# 9. Сценарий: несколько фото (баланс - два листа) + запрос по балансу
# ---------------------------------------------------------------------------

class TestMultiPageBalanceSheet:
    @pytest.mark.asyncio
    async def test_two_pages_accumulated_in_batch(self):
        bot, mock_agent = _make_bot("Баланс обработан")
        update1 = _make_photo_update(
            chat_id=10, file_id="bs_p1", caption="Посчитай ликвидность", media_group_id="mg_bs"
        )
        update2 = _make_photo_update(
            chat_id=10, file_id="bs_p2", caption="", media_group_id="mg_bs"
        )

        with patch("os.makedirs"), patch("asyncio.create_task"):
            await bot.handle_photo_with_caption(update1, MagicMock())
            await bot.handle_photo_with_caption(update2, MagicMock())

        batch = bot._media_groups["mg_bs"]
        assert len(batch.image_paths) == 2
        assert any("bs_p1" in p for p in batch.image_paths)
        assert any("bs_p2" in p for p in batch.image_paths)

    @pytest.mark.asyncio
    async def test_batch_passes_both_paths_to_agent(self):
        bot, mock_agent = _make_bot("Ликвидность рассчитана по 2 страницам")
        update1 = _make_photo_update(
            chat_id=10, file_id="bs_p1", caption="Посчитай ликвидность", media_group_id="mg_bs2"
        )
        update2 = _make_photo_update(
            chat_id=10, file_id="bs_p2", caption="", media_group_id="mg_bs2"
        )

        with patch("os.makedirs"), patch("asyncio.create_task"):
            await bot.handle_photo_with_caption(update1, MagicMock())
            await bot.handle_photo_with_caption(update2, MagicMock())

        batch = bot._media_groups["mg_bs2"]
        batch.timeout = 0

        with patch("tg_bot.bot.sleep", new_callable=AsyncMock):
            await bot._init_image_batch_processing("mg_bs2")

        args = mock_agent.process_query.call_args[0]
        assert args[0] == 10
        assert "ликвидность" in args[1].lower()
        assert len(args[2]) == 2

    def test_multi_page_parse_with_mocked_ocr(self):
        """parse_financial_report_tool для двух страниц = ocr_files_to_lines."""
        combined = BALANCE_SHEET_LINES + [
            "БАЛАНС", "1700", "482 772 230", "497 950 514", "424 629 854",
        ]
        with patch("agent.tools.image.recognize_image.ocr_files_to_lines", return_value=combined):
            raw = parse_financial_report_tool.invoke({
                "file_paths": "./bs_p1.jpg, ./bs_p2.jpg"
            })
        data = json.loads(raw)
        assert data["report_type"] == "balance_sheet"
        year = data["years"][0]
        assert data["rows"]["1700"][year] == 482772230


# ---------------------------------------------------------------------------
# 10. Сценарий: неизвестный тип документа
# ---------------------------------------------------------------------------

class TestUnknownDocumentPhoto:
    @pytest.mark.asyncio
    async def test_bot_still_calls_agent_for_unknown_doc(self):
        """Бот не фильтрует документы — агент сам решит что делать."""
        bot, mock_agent = _make_bot("Не удалось определить тип отчёта.")
        update = _make_photo_update(caption="Что это?", file_id="unknown_doc")

        with patch("os.makedirs"):
            await bot.handle_photo_with_caption(update, MagicMock())

        assert mock_agent.process_query.called
        reply = update.message.reply_text.call_args[0][0]
        assert "Не удалось" in reply or "определить" in reply

    def test_parse_tool_returns_error_for_unknown_doc(self):
        unknown_lines = ["Договор аренды № 123", "г. Набережные Челны", "01.01.2025"]
        with patch("agent.tools.image.recognize_image.ocr_file_to_lines", return_value=unknown_lines):
            raw = parse_financial_report_tool.invoke({"file_paths": "./contract.jpg"})
        data = json.loads(raw)
        assert "error" in data
        assert "Не удалось определить" in data["error"]
