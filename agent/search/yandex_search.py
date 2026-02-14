import pathlib

from yandex_ai_studio_sdk import AIStudio

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"

xml_format = "xml"
html_format = "html"

class YandexSearch:
    def __init__(self, folder_id, api_key):
        sdk = AIStudio(
            folder_id=folder_id,
            auth=api_key,
        )
        sdk.setup_default_logging("error")

        self.engine = sdk.search_api.web(
            search_type="ru",
            user_agent=USER_AGENT,
        )

    def search(self, search_query, page=0):
        operation = self.engine.run_deferred(query=search_query, format=html_format, page=page)
        search_result = operation.wait(poll_interval=1)

        return search_result