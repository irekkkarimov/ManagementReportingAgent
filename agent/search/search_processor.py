import json
from pathlib import Path

from bs4 import BeautifulSoup

from agent.models.yandex_search_result import YandexSearchResult


class SearchProcessor:
    def __init__(self):
        return

    @staticmethod
    def clean_html(html) -> BeautifulSoup:
        soup = BeautifulSoup(html, "html.parser")

        # Удаляем скрипты и стили
        for tag in soup(["script", "style", "svg", "path", "noscript"]):
            tag.decompose()

        return soup

    @staticmethod
    def extract_result(search_query: str, soup: BeautifulSoup) -> YandexSearchResult:
        results = []

        items = soup.select("li.serp-item")

        for item in items:
            title_tag = item.select_one("h2")
            link_tag = item.select_one("a")
            path_tag = item.select_one(".Path-Item")  # домен
            snippet_tag = item.select_one(".Organic")

            title = title_tag.get_text(" ", strip=True) if title_tag else None
            page_url = link_tag["href"] if link_tag and link_tag.has_attr("href") else None
            site_url = path_tag.get_text(" ", strip=True) if path_tag else None
            text = snippet_tag.get_text(" ", strip=True) if snippet_tag else None

            if title or text:
                results.append({
                    "site_url": site_url,
                    "page_url": page_url,
                    "page_title": title,
                    "text": text
                })

        return YandexSearchResult(search_query, results)

    @staticmethod
    def save_html_to_file(search_result: str, file_path: str) -> None:
        path = Path(file_path)
        
        # создаём папку если её нет
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, "w", encoding="utf-8") as f:
            f.write(search_result)
        print(f"HTML saved to file {path}")

    @staticmethod
    def save_formatted_json(data: YandexSearchResult, file_path: str) -> None:
        path = Path(file_path)

        # создаём папку если её нет
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                data.to_dict(),
                f,
                ensure_ascii=False,  # важно для русского текста
                indent=4  # красивый формат
            )
