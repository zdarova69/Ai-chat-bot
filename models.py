from abc import ABC, abstractmethod

from openai import OpenAI

from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole

from api import proxy_api, gigachat_api


# Класс для конкретной модели
class OpenAIModel():
    def __init__(self, model_name: str, base_url: str) -> None:
        self.model_name = model_name
        self.base_url = base_url
        
    def generate(self, prompt: str) -> str:
        # Здесь можно разместить логику для отправки запроса на API
        client = OpenAI(
            api_key=proxy_api,
            base_url=self.base_url,
        )

        completion = client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "user", "content": prompt}
            ]
            )


        return completion.choices[0].message.content
    def generate_gigachat(self, prompt: str):
        payload = Chat(
            messages=[
                Messages(
                    role=MessagesRole.SYSTEM,
                    content="Ты - чат-бот ассистент"
                )
            ],
            temperature=0.7,
            max_tokens=1000,
        )
        giga = GigaChat(credentials=gigachat_api, 
                        # model="GigaChat-Pro", 
                        verify_ssl_certs=False)
        payload.messages.append(Messages(role=MessagesRole.USER, content=prompt))
        response = giga.chat(payload)
        return response.choices[0].message.content

# # Класс для хранения всех моделей и доступа к ним
# class ModelRegistry:
#     def __init__(self) -> None:
#         self.models = {
#             'OpenAI GPT-4.0': OpenAIModel('gpt-4o-mini', "https://api.proxyapi.ru/openai/v1"),
#             'OpenAI o1': OpenAIModel('o1-mini', "https://api.proxyapi.ru/openai/v1"),
#             'Google Gemini': OpenAIModel('gemini-1.5-flash', "https://api.proxyapi.ru/google/v1")
#         }

#     def get_model(self, name: str) -> Model:
#         return self.models.get(name)

# # Пример использования
# model_registry = ModelRegistry()
# model = model_registry.get_model('OpenAI GPT-4.0')

# if model:
#     output = model.generate("Hello, world!")
#     print(output)
