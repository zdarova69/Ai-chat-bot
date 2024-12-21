from abc import ABC, abstractmethod

from openai import OpenAI

import requests
import json

from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole

from api import PROXY_API_KEY, GIGACHAT_API_KEY, DEEPSEEK_API_KEY


# Класс для конкретной модели
class OpenAIModel():
    def __init__(self ) -> None:
       self.model_list = {
    1: {
        'name': 'gpt-4o-mini', 
        'base_url': "https://api.proxyapi.ru/openai/v1",
        'api': PROXY_API_KEY
    },
    2: {
        'name': 'o1-mini', 
        'base_url': "https://api.proxyapi.ru/openai/v1",
        'api': PROXY_API_KEY
    },
    3: {
        'name': 'gemini-1.5-flash', 
        'base_url': "https://api.proxyapi.ru/google/v1/models/gemini-1.5-flash:generateContent",
        'api': PROXY_API_KEY
    },
    4: {
        'name': 'deepseek-chat', 
        'base_url': "https://api.deepseek.com",
        'api': DEEPSEEK_API_KEY
    },
    5:{
        'name': 'Sber GigaChat',
        'base_url': '',
        'api': GIGACHAT_API_KEY
    },
    6:{
        'name': 'dall-e-3',
        'base_url': 'https://api.proxyapi.ru/openai/v1',
        'api': PROXY_API_KEY
    },
    7:{
        'name': 'Kandynsky',
        'base_url': ''
    },
    8:{
        'name': 'dall-e-2',
        'base_url': 'https://api.proxyapi.ru/openai/v1',
        'api': PROXY_API_KEY
    },
} 
    def generate_text(self,model_name: str, base_url: str, prompt: str, api: str) -> str:
        if model_name == 'Sber GigaChat':
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
            giga = GigaChat(credentials=api, 
                            # model="GigaChat-Pro", 
                            verify_ssl_certs=False)
            payload.messages.append(Messages(role=MessagesRole.USER, content=prompt))
            response = giga.chat(payload)
            return response.choices[0].message.content
        elif model_name == 'gemini-1.5-flash':
            
            # Заголовки запроса
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {PROXY_API_KEY}"
            }

            # Данные для запроса
            data = {
                "contents": [{"role": "user", "parts": [{"text": prompt}]}]
            }

            # Отправка POST-запроса
            response = requests.post(base_url, headers=headers, data=json.dumps(data))

            result = response.json()

            return result['candidates'][0]['content']['parts'][0]['text']
        
        else:
        # Здесь можно разместить логику для отправки запроса на API
            client = OpenAI(
                api_key=api,
                base_url=base_url,
            )

            completion = client.chat.completions.create(
                model = model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ]
                )


            return completion.choices[0].message.content

    def generate_image(self,model_name: str, base_url: str, prompt: str) -> str:
        client = OpenAI(
                api_key=PROXY_API_KEY,
                base_url=base_url,
            )
        print(f'промпт - {prompt}')
        if model_name == 'dall-e-3':
            size = "1024x1024"
        else:
            size = "512x512"
        response = client.images.generate(
            model=model_name,
            prompt=prompt,
            n=1,
            size=size

    )
        return response.data[0].url
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
