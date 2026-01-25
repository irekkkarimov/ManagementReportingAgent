from langchain_deepseek import ChatDeepSeek


class DeepSeekAdapter:

    def __init__(self):
        self.model = ChatDeepSeek(
            model="deepseek-chat",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2
        )

    def generate(self):
        print(self.model)
        messages = [
            (
                "system",
                "You are a helpful assistant that translates English to French. Translate the user sentence.",
            ),
            ("human", "I love programming."),
        ]
        ai_msg = self.model.invoke(messages)
        return ai_msg.content