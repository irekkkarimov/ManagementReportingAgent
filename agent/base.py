import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from langchain.agents import create_agent
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.tools import BaseTool
from langchain_gigachat import GigaChat

from agent.tools.finance.liquidity.cash_liquidity import calculate_cash_liquidity_ratio
from agent.tools.finance.liquidity.current_liquidity import calculate_current_liquidity_ratio
from agent.tools.finance.liquidity.quick_liquidity import calculate_quick_liquidity_ratio
from agent.tools.finance.profitability.gross_margin import calculate_gross_margin
from agent.tools.finance.profitability.operating_margin import calculate_operating_margin
from agent.tools.finance.profitability.roa import calculate_roa
from agent.tools.finance.profitability.roe import calculate_roe
from agent.tools.finance.profitability.ros import calculate_ros
from agent.tools.finance.stability.financial_stability import calculate_financial_stability_ratio
from agent.tools.finance.turnover.total_asset import calculate_total_asset_turnover
from agent.tools.finance.turnover.inventory import calculate_inventory_turnover
from agent.tools.finance.turnover.receivables import calculate_receivables_turnover
from agent.tools.finance.turnover.payables import calculate_payables_turnover
from agent.tools.finance.calculation_cache import set_session as _set_calc_session
from agent.tools.finance.get_finance_data_for_calculations import get_finance_data_for_calculations
from agent.tools.finance.inputs_cache import set_session as _set_inputs_session
from agent.tools.finance.parsed_tables_store import set_session as _set_store_session
from agent.tools.input.download_google_sheets import download_google_sheets
from agent.tools.input.load_excel_file import load_excel_file_tool
from agent.tools.input.validate_finance_link import validate_finance_link_tool
from agent.tools.output.generate import generate_excel_report
from agent.tools.output.generate_pdf import generate_pdf_report
from agent.yandex.yandex_gpt import YandexGPT


class Agent:
    def __init__(self,
                 gigachat_creds: str,
                 gigachat_prompt_path: str,
                 gigachat_temperature: float,
                 yc_folder_id: str,
                 yandex_gpt_api_key: str,
                 yandex_gpt_prompt_path: str,
                 yandex_gpt_temperature: float):
        self._model = GigaChat(
            model="GigaChat-2-Pro",
            verify_ssl_certs=False,
            credentials=gigachat_creds,
            timeout=30,
            temperature=gigachat_temperature,
        )

        self._yandex_gpt = YandexGPT(yc_folder_id, yandex_gpt_api_key, yandex_gpt_prompt_path, yandex_gpt_temperature)

        self._agent = create_agent(self._model, tools=Agent.get_tools(), system_prompt=Agent.read_prompt(gigachat_prompt_path))
        self._history: Dict[int, List[BaseMessage]] = defaultdict(list)

    def process_query(self, user_id: int, query: str, file_paths: list[str] = None):
        message_history: list[BaseMessage] = list()

        try_get_history = self._history.get(user_id)
        if try_get_history is not None:
            message_history = list(try_get_history)

        content = query
        if file_paths:
            content = f"{query}\n\nПриложенные файлы: {', '.join(file_paths)}"
        message_history.append({"role": "user", "content": content})

        print("MESSAGE HISTORY BEFORE AGENT CALL:", message_history)

        _set_calc_session(user_id)
        _set_inputs_session(user_id)
        _set_store_session(user_id)
        result = self._agent.invoke({"messages": message_history})

        result_content = Agent._get_ai_result_content(result)
        Agent._save_results(query=query, result=result)

        self._history[user_id] = result["messages"]

        return result_content

    # noinspection PyTypeChecker
    def process_text(self, user_id: int, queries: list[str]) -> str:
        message_history = list()

        try_get_history = self._history.get(user_id)
        if try_get_history is not None:
            message_history = list(try_get_history)

        for query in queries:
            message_history.append({
            "role": "user",
            "content": query
        })

        result = self._agent.invoke(
            {
                "messages": message_history
            },
            config={"recursion_limit": 10}
        )

        messages = result["messages"]

        final_ai_message = next(
            msg for msg in reversed(messages)
            if isinstance(msg, AIMessage)
        )

        Agent._save_results(query=queries[0], result=result)
        self._history[user_id] = messages

        print(final_ai_message.content)
        return final_ai_message.content

    @staticmethod
    def get_tools() -> list[BaseTool]:
        tools = [
            # input
            validate_finance_link_tool,
            download_google_sheets,
            load_excel_file_tool,

            # profitability
            calculate_ros,
            calculate_roa,
            calculate_roe,
            calculate_gross_margin,
            calculate_operating_margin,

            # turnover
            calculate_total_asset_turnover,
            calculate_inventory_turnover,
            calculate_receivables_turnover,
            calculate_payables_turnover,

            # financial stability
            calculate_financial_stability_ratio,

            # liquidity
            calculate_current_liquidity_ratio,
            calculate_quick_liquidity_ratio,
            calculate_cash_liquidity_ratio,

            # output
            generate_excel_report,
            generate_pdf_report,
        ]

        return tools

    @staticmethod
    def read_prompt(prompt_path: str) -> str:
        prompt_file = Path(prompt_path)
        if prompt_file.exists():
            with open(prompt_file, "r", encoding="utf-8") as f:
                return f.read()
        else:
            print(f"Warning: File {prompt_file} not found. Using empty prompt.")
            return ""

    @staticmethod
    def _save_results(query: str, result: Dict[str, Any], file_path: str = None):
        if file_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            file_path = f"./agent_output/agent_result_{timestamp}.json"

            # Если агент вернул строку — оборачиваем в dict

        data = {
            "query": query,
            "result": str(result)
        }

        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        print(f"AGENT RESULT SAVED TO {file_path}")

    def _upload_files(self, file_paths: list[str]) -> list[str]:
        file_uploaded_ids: list[str] = []

        for file_path in file_paths:
            file = open(file_path, "rb")
            file_uploaded_ids.append(self._model.upload_file(file).id_)

        print("UPLOADED FILES TO GIGACHAT: ", ', '.join(file_uploaded_ids))
        return file_uploaded_ids

    @staticmethod
    def _get_ai_result_content(result: dict[str, Any] | Any) -> str:
        return next(
            msg for msg in reversed(result["messages"])
            if isinstance(msg, AIMessage)
        ).content

    def extract_image_data(self, file_ids: list[str]) -> str:
        messages = [
            {
                "role": "user",
                "content": (
                    "Ты OCR + data extraction модель. "
                    "Извлеки ВСЕ возможные данные с изображения. "
                    "Верни результат строго в формате JSON. "
                    "Не выполняй анализ. Только извлечение данных."
                )
            },
            {
                "role": "user",
                "content": "Извлеки все данные с изображения",
                "attachments": file_ids
            }
        ]

        response = self._agent.invoke({"messages": messages})

        content = self._get_ai_result_content(response)
        print("DATA EXTRACTED FROM IMAGE: \n", "IMAGE IDS: ", ', '.join(file_ids), "\n", content)

        return content

    def process_with_extracted_data(
            self,
            extracted_data: str,
            user_query: str,
            message_history: list[Any]
    ):
        message_history.append({
            "role": "user",
            "content": "Используй данные из JSON для выполнения запроса."
        })

        message_history.append({
            "role": "user",
            "content": f"""
            Вот данные, извлечённые с изображения:

            {extracted_data}

            Запрос пользователя:
            {user_query}
            """
        })

        result = self._agent.invoke({
            "messages": message_history
        })

        print("PROCESS WITH EXTRACTED DATA: \n", Agent._get_ai_result_content(result))

        return result

















































    # # noinspection PyTypeChecker
    # def process_images(self, user_id: int, query: str, file_paths: list[str] = None):
    #     # message_history = list()
    #     #
    #     # try_get_history = self._history.get(user_id)
    #     # if try_get_history is not None:
    #     #     message_history = list(try_get_history)
    #
    #     images_processed = Agent._process_images(file_paths)
    #     images_processed_from_llm: list[str] = []
    #     for img in images_processed:
    #         messages: list[dict] = [
    #             {
    #                 "role": "user",
    #                 "content": "Обработай только числа, заключение не пиши. Числа, указанные в скобках, интерпретируй как отрицательные числа! Выпиши все указанные в файле данные в формате: Название - значение (x год), значение за (y год) и т.д. Заключение не пиши, пиши сухие данные"
    #             },
    #             {
    #                 "role": "user",
    #                 "content": img.__str__()
    #             }
    #         ]
    #
    #         result = self._agent.invoke(
    #             {
    #                 "messages": messages
    #             },
    #         )
    #
    #         messages = result["messages"]
    #
    #         images_processed_from_llm.append(next(
    #             msg for msg in reversed(messages)
    #             if isinstance(msg, AIMessage)
    #         ).content)
    #
    #     print("process_images: ", query,  ' | '.join(images_processed_from_llm))
    #
    #     return self.process_text(user_id, [query, ' | '.join(images_processed_from_llm)])
    #
    # @staticmethod
    # def _process_images(file_paths: list[str]) -> list[dict]:
    #     result: list[dict] = list()
    #
    #     yandex_service = YandexOcrService()
    #     yandex_service.load_env()
    #
    #     for file_path in file_paths:
    #         prompt_file = Path(file_path)
    #         if not prompt_file.exists():
    #             raise ValueError(f"File '{file_path}' not found")
    #
    #         with open(prompt_file, "rb") as f:
    #             file_content = f.read()
    #             base64_content = base64.b64encode(file_content).decode("utf-8")
    #
    #             ocr_result = yandex_service.call_ocr(base64_content)
    #
    #             print("result of processing image: ", file_path, ". ", ocr_result)
    #             result.append(ocr_result)
    #
    #
    #     return result
