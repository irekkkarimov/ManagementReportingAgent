

class GPTResult:
    def __init__(self, summary: str = "", key_facts: list[str] = None, 
                 main_trends: list[str] = None, risks_and_problems: list[str] = None,
                 conclusion: str = ""):
        self.summary = summary
        self.key_facts = key_facts if key_facts is not None else []
        self.main_trends = main_trends if main_trends is not None else []
        self.risks_and_problems = risks_and_problems if risks_and_problems is not None else []
        self.conclusion = conclusion

    def to_dict(self):
        return {
            "краткий_обзор": self.summary,
            "ключевые_факты": self.key_facts,
            "основные_тенденции": self.main_trends,
            "риски_и_проблемы": self.risks_and_problems,
            "итоговое_заключение": self.conclusion
        }

