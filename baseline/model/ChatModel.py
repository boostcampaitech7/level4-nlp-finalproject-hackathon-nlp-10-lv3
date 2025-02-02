import os
from langchain_community.chat_models import ChatClovaX

class ClovaXChatModel():
    def __init__(self):
        os.environ["NCP_CLOVASTUDIO_API_KEY"] = "private key"
        
        self.chat = ChatClovaX(
            model="HCX-003",
            max_tokens=4096,
        )

    def get_answer(self, system_prompt, inputs):
        messages = [
            ("system", system_prompt),
            ("human", inputs)
        ]
        outputs = self.chat.invoke(messages)

        return outputs.content