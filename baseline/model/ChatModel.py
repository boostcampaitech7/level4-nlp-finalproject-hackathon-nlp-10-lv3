import os
from langchain_community.chat_models import ChatClovaX

class ClovaXChatModel():
    def __init__(self, model_name="HCX-003", top_p=0.8, temp=0.5, max_tokens=1024, repeat_penalty=5, API_KEY=""):
        self.model_name = model_name
        self.top_p = top_p
        self.temp = temp
        self.max_tokens = max_tokens
        self.repeat_penalty = repeat_penalty
        self.CLOVA_STUDIO_API_KEY = API_KEY

        self.chat_model = self.get_chat_model()

    def get_chat_model(self):
        chat = ChatClovaX(
            model="HCX-003",
            top_p=self.top_p,
            temperature=self.temp,
            max_tokens=self.max_tokens,
            repeat_penalty=self.repeat_penalty,
            api_key=self.CLOVA_STUDIO_API_KEY
        )
        return chat

    def template_message(self, system_prompt, user_prompt):
        messages = [
            (
                "system",
                system_prompt
            ),
            (
                "human",
                user_prompt
            )
        ]
        return messages
    
    def invoke_message(self, message):
        response = self.chat_model.invoke(message)
        return response
    
    def stream_message(self, message):
        for chunk in self.chat_model.stream(message):
            print(chunk.content, end="", flush=True)