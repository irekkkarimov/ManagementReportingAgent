import json
import re
from datetime import datetime
from pathlib import Path

from yandex_ai_studio_sdk import AIStudio
from yandex_ai_studio_sdk._models.completions.result import GPTModelResult
from yandex_ai_studio_sdk._tools.tool_call import ToolCall

from agent.models.gpt_result import GPTResult
from agent.models.yandex_search_result import YandexSearchResult


class YandexGPT:
    def __init__(self, folder_id: str, api_key: str, prompt_path: str, temperature: float = 0.5):
        sdk = AIStudio(
            folder_id=folder_id,
            auth=api_key,
        )
        sdk.setup_default_logging("error")

        self.engine = sdk.models.completions("yandexgpt").configure(temperature=temperature)

        # Считывание yandex_gpt_prompt.txt по переданному пути
        prompt_file = Path(prompt_path)
        if prompt_file.exists():
            with open(prompt_file, "r", encoding="utf-8") as f:
                self.prompt_text = f.read()
        else:
            raise ValueError(f"Error when initializing YandexGPT instance. Prompt '{prompt_path}' file not found")

    def process_search(self, domain: str, search_result: YandexSearchResult) -> GPTModelResult[ToolCall]:
        messages = [
            {
                "role": "system",
                "text": self.prompt_text + " Предметная область предприятия: " + domain
            },
            {
                "role": "user",
                "text": ".\n".join(search_result.get_texts()),
            },
        ]

        result = self.engine.run(messages)

        return result

    @staticmethod
    def save_result_to_json(result: GPTModelResult[ToolCall], file_path: str) -> None:
        path = Path(file_path)

        # создаём папку если её нет
        path.parent.mkdir(parents=True, exist_ok=True)

        # Извлекаем текст и парсим в GPTResult
        text = YandexGPT.extract_gpt_answer(result)
        gpt_result = YandexGPT.parse_gpt_result_to_json(text)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                gpt_result.to_dict(),
                f,
                ensure_ascii=False,  # важно для русского текста
                indent=4  # красивый формат
            )
        print(f"GPT result saved to file {path}")

    @staticmethod
    def extract_gpt_answer(result: GPTModelResult[ToolCall]) -> str:
        alternatives = result.alternatives

        if len(alternatives) == 0:
            raise ValueError("No response received from GPT")

        first_alternative = alternatives[0]

        return first_alternative.text

    @staticmethod
    def parse_gpt_result_to_json(text: str) -> GPTResult:
        summary = ""
        key_facts = []
        main_trends = []
        risks_and_problems = []
        conclusion = ""

        delimiter_pattern = r'\$(\w+_?\w*)%'
        parts = re.split(delimiter_pattern, text)

        for i in range(1, len(parts), 2):
            section_name = parts[i]
            section_content = parts[i + 1].strip() if i + 1 < len(parts) else ""

            if section_name == "краткий_обзор":
                summary = section_content
            elif section_name == "ключевые_факты":
                facts = [line.strip()[2:] if line.strip().startswith("-") else line.strip()
                         for line in section_content.split("\n") if line.strip()]
                key_facts = facts
            elif section_name == "основные_тенденции":
                trends = [line.strip()[2:] if line.strip().startswith("-") else line.strip()
                          for line in section_content.split("\n") if line.strip()]
                main_trends = trends
            elif section_name == "риски_и_проблемы":
                risks = [line.strip()[2:] if line.strip().startswith("-") else line.strip()
                         for line in section_content.split("\n") if line.strip()]
                risks_and_problems = risks
            elif section_name == "итоговое_заключение":
                conclusion = section_content

        return GPTResult(
            summary=summary,
            key_facts=key_facts,
            main_trends=main_trends,
            risks_and_problems=risks_and_problems,
            conclusion=conclusion
        )

    # noinspection PyTypeChecker
    def generate(self, query, temperature: float = 0.3) -> GPTModelResult[ToolCall]:
        messages= [{
                "role": "system",
                "text": self.prompt_text
            },
            {
                "role": "user",
                "text": query
            }
        ]

        result = self.engine.run(messages)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = f"yandex_gpt_results/yandex_gpt_{timestamp}.json"

        YandexGPT.save_result_to_json(result, file_path)

        return result
