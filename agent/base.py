import base64
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from langchain.agents import create_agent
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.tools import BaseTool
from langchain_gigachat import GigaChat
from openai import max_retries

from agent.tools.finance.profitability.gross_margin import calculate_gross_margin
from agent.tools.finance.profitability.operating_margin import calculate_operating_margin
from agent.tools.finance.profitability.roa import calculate_roa
from agent.tools.finance.profitability.roe import calculate_roe
from agent.tools.finance.profitability.ros import calculate_ros
from agent.tools.image.recognize_image import recognize_image_tool
from agent.tools.output.generate_xlsx import generate_xlsx_tool
from agent.yandex.yandex_gpt import YandexGPT
from agent.yandex.yandex_service import YandexOcrService


class Agent:
    def __init__(self,
                 gigachat_creds: str,
                 gigachat_prompt_path: str,
                 gigachat_temperature: float,
                 yc_folder_id: str,
                 yandex_gpt_api_key: str,
                 yandex_gpt_prompt_path: str,
                 yandex_gpt_temperature: float):
        model = GigaChat(
            model="GigaChat-2-Pro",
            verify_ssl_certs=False,
            credentials=gigachat_creds,
            timeout=220,
            temperature=gigachat_temperature
        )

        self._yandex_gpt = YandexGPT(yc_folder_id, yandex_gpt_api_key, yandex_gpt_prompt_path, yandex_gpt_temperature)

        self._model = model
        self._agent = create_agent(model, tools=Agent.get_tools(), system_prompt=Agent.read_prompt(gigachat_prompt_path))
        self._history: Dict[int, List[BaseMessage]] = defaultdict(list)

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

        print(message_history)

        result = self._agent.invoke(
            {
                "messages": message_history
            },
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

    # noinspection PyTypeChecker
    def process_images(self, user_id: int, query: str, file_paths: list[str] = None):
        message_history = list()

        try_get_history = self._history.get(user_id)
        if try_get_history is not None:
            message_history = list(try_get_history)

        images_processed = Agent._process_images(file_paths)
        images_processed_str: list[str] = []
        for img in images_processed:
            images_processed_str.append(img.__str__())

        messages: list[dict] = [
            {
                "role": "user",
                "content": "Обработай только числа, заключение не пиши. Числа, указанные в скобках, интерпретируй как отрицательные числа! Выпиши все указанные в файле данные в формате: Название - значение (x год), значение за (y год) и т.д."
            },
            {
                "role": "user",
                "content": ' | '.join(images_processed_str)
            }
        ]

        messages = message_history + messages

        result = self._agent.invoke(
            {
                "messages": messages
            },
        )

        messages = result["messages"]

        final_ai_message = next(
            msg for msg in reversed(messages)
            if isinstance(msg, AIMessage)
        )

        print("process_images: ", query,  final_ai_message.content)

        return self.process_text(user_id, [query, final_ai_message.content])



    @staticmethod
    def get_tools() -> list[BaseTool]:
        # init tools

        tools = [
            generate_xlsx_tool,
            recognize_image_tool,

            # finance tools
            calculate_ros,
            calculate_roa,
            calculate_roe,
            calculate_gross_margin,
            calculate_operating_margin]

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

        print(f"Результат сохранён в {file_path}")

    def _upload_files(self, file_paths: list[str]) -> list[str]:
        file_uploaded_ids: list[str] = []

        for file_path in file_paths:
            file = open(file_path, "rb")
            file_uploaded_ids.append(self._model.upload_file(file).id_)

        return file_uploaded_ids

    @staticmethod
    def _process_images(file_paths: list[str]) -> list[dict]:
        result: list[dict] = list()

        yandex_service = YandexOcrService()
        yandex_service.load_env()

        for file_path in file_paths:
            prompt_file = Path(file_path)
            if not prompt_file.exists():
                raise ValueError(f"File '{file_path}' not found")

            with open(prompt_file, "rb") as f:
                file_content = f.read()
                base64_content = base64.b64encode(file_content).decode("utf-8")

                result.append(yandex_service.call_ocr(base64_content))

        return result
