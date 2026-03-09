import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from langchain.agents import create_agent
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.runnables import RunnableConfig
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
from agent.tools.input.download_google_sheets import download_google_sheets
from agent.tools.input.load_excel_file import load_excel_file_tool
from agent.tools.input.validate_finance_link import validate_finance_link_tool
from agent.tools.finance.calculation_cache import set_session as _set_calc_session
from agent.tools.finance.get_finance_data_for_calculations import get_finance_data_for_calculations
from agent.tools.finance.parsed_tables_store import set_session as _set_store_session
from agent.tools.output.generate_excel import generate_excel_report
from agent.yandex.yandex_gpt import YandexGPT


class Agent:
    def __init__(self,
                 gigachat_creds: str,
                 gigachat_prompt_path: str,
                 gigachat_temperature: float):
        self._model = GigaChat(
            model="GigaChat-2-Pro",
            verify_ssl_certs=False,
            credentials=gigachat_creds,
            timeout=30,
            temperature=gigachat_temperature,
        )

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
        _set_store_session(user_id)
        result = self._agent.invoke({"messages": message_history})

        result_content = Agent._get_ai_result_content(result)
        Agent._save_results(query=query, result=result)

        self._history[user_id] = result["messages"]

        return result_content

    @staticmethod
    def get_tools() -> list[BaseTool]:
        tools = [
            # input
            validate_finance_link_tool,
            download_google_sheets,
            load_excel_file_tool,

            # data extraction
            get_finance_data_for_calculations,

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
