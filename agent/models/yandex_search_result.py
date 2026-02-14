

class YandexSearchResult:
    def __init__(self, search_query: str, results: list):
        self.search_query = search_query
        self.results = [
            YandexSearchResultItem(
                site_url=item.get("site_url", ""),
                page_url=item.get("page_url", ""),
                page_title=item.get("page_title", ""),
                text=item.get("text", "")
            )
            for item in results
        ]

    def to_dict(self):
        return {
            "search_query": self.search_query,
            "results": [item.to_dict() for item in self.results]
        }

    def get_texts(self) -> list[str]:
        return [item.text for item in self.results]


class YandexSearchResultItem:
    def __init__(self, site_url: str, page_url: str, page_title: str, text: str):
        self.site_url = site_url
        self.page_url = page_url
        self.page_title = page_title
        self.text = text

    def to_dict(self):
        return {
            "site_url": self.site_url,
            "page_url": self.page_url,
            "page_title": self.page_title,
            "text": self.text
        }