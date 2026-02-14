import requests


class PageFetcher:
    def __init__(self):
        return

    @staticmethod
    def fetch_page(url: str) -> str | None:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                return response.text

            print("Ошибка запроса:", response.status_code)
            return None

        except Exception as e:
            print("Ошибка при запросе:", e)
            return None