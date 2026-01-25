from langchain_openai import ChatOpenAI


class ChatGPTAdapter:

    def __init__(self):
        self.model = ChatOpenAI(
    model="gpt-4o",
    temperature=0.3
    )

    def generate(self):
        return self.model.invoke("Hello!")