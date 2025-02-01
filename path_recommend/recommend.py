import os
from langchain_community.chat_models import ChatClovaX
from dotenv import load_dotenv


load_dotenv()
CLOVA_STUDIO_API_KEY = os.getenv("CLOVA_STUDIO_API_KEY")


class ClovaX_Model():
    def __init__(self, model_name="HCX-003", top_p=0.8, temp=0.5, max_tokens=1024, repeat_penalty=5):
        self.model_name = model_name
        self.top_p = top_p
        self.temp = temp
        self.max_tokens = max_tokens
        self.repeat_penalty = repeat_penalty

        self.chat_model = self.get_chat_model()

    def get_chat_model(self):
        chat = ChatClovaX(
            model="HCX-003",
            top_p=self.top_p,
            temperature=self.temp,
            max_tokens=self.max_tokens,
            repeat_penalty=self.repeat_penalty,
            api_key=CLOVA_STUDIO_API_KEY
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


if __name__ == "__main__":
    chat_model = ClovaX_Model()
    
    with open("./prompt/next_place_system.txt","r") as prompt:
        system_prompt = prompt.read()
    
    # 실제 User Prompt의 경우에는 review와 후보장소를 받아와야함
    with open("./prompt/next_place_user.txt","r") as prompt:
        user_prompt = prompt.read()
    

    message = chat_model.template_message(system_prompt=system_prompt, user_prompt=user_prompt)
    response = chat_model.invoke_message(message)

    for res in response.content.split("\n"):
        print(res)
