from openai import OpenAI

import requests
import json
from pathlib import Path
import base64
from bs4 import BeautifulSoup

from gigachat import GigaChat
from gigachat.models import Chat

from api import PROXY_API_KEY, GIGACHAT_API_KEY, DEEPSEEK_API_KEY, PERPLEXITY_API_KEY


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
        'name': 'Sber GigaChat для генерации изображений',
        'base_url': '',
        'api': GIGACHAT_API_KEY
    },
    8:{
        'name': 'dall-e-2',
        'base_url': 'https://api.proxyapi.ru/openai/v1',
        'api': PROXY_API_KEY
    },
    9:{
        'name': 'tts-1',
        'base_url': 'https://api.proxyapi.ru/openai/v1',
        'api': PROXY_API_KEY

    },
    10:{
        'name': 'tts-1-hd',
        'base_url': 'https://api.proxyapi.ru/openai/v1',
        'api': PROXY_API_KEY

    },
    11:{
        'name': 'claude-3-7-sonnet-20250219',
        'base_url': 'https://api.proxyapi.ru/anthropic/v1/messages',
        'api': PROXY_API_KEY
    },
    12: {
        'name': 'deepseek-reasoner', 
        'base_url': "https://api.deepseek.com",
        'api': DEEPSEEK_API_KEY
    },
     13: {
        'name': 'sonar', 
        'base_url': "https://api.perplexity.ai",
        'api': PERPLEXITY_API_KEY
    }
}   
    async def create_gigachat_payload(self, messages, temperature: float, max_tokens: int, function_call: str = 'none'):
        payload = Chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            function_call=function_call
        )
        return payload

    async def generate_text(self, model_name: str, base_url: str, prompt: str, api: str, messages: list) -> str:
        # Добавляем новый запрос пользователя
        messages.append({"role": "user", "content": prompt})
        
        if model_name == 'Sber GigaChat':
            payload = await self.create_gigachat_payload(messages=messages, temperature=0.7, max_tokens=2000)
            giga = GigaChat(credentials=api, 
                            model="GigaChat-Pro", 
                            verify_ssl_certs=False)
            response = giga.chat(payload)
            content = response.choices[0].message.content

            
        elif model_name == 'gemini-1.5-flash':
            
            # Заголовки запроса
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api}"
            }

            # Данные для запроса
            # data = {
            #     "contents": messages
            # }
            data = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}]
}
            # Отправка POST-запроса
            response = requests.post(base_url, headers=headers, data=json.dumps(data))

            result = response.json()
            
            content = result['candidates'][0]['content']['parts'][0]['text']
        elif model_name == 'claude-3-7-sonnet-20250219':
            
            # Заголовки запроса
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api}"
            }

            # Данные для запроса
            # data = {
            #     "contents": messages
            # }
            # Данные для запроса
            data = {
                "model": model_name,
                "system": messages[0]['content'],
                "messages": messages[1:],
                "max_tokens": 2024
            }
            # Отправка POST-запроса
            response = requests.post(base_url, headers=headers, data=json.dumps(data))

            result = response.json()
            
            content = result['content'][0]['text']
        else:
        # Здесь можно разместить логику для отправки запроса на API
            client = OpenAI(
                api_key=api,
                base_url=base_url,
            )
            if model_name == 'deepseek-reasoner':
                print(prompt)
                 # Выполняем запрос к модели
                completion = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt}]
                )
            else:
                # Выполняем запрос к модели
                completion = client.chat.completions.create(
                    model=model_name,
                    messages=messages
                )
            # Получаем ответ от модели
            content = completion.choices[0].message.content
            # Добавляем ответ ассистента в messages
        messages.append({"role": "assistant", "content": content})
        
        # Возвращаем обновлённый список messages
        return messages, content

    async def generate_image(self,model_name: str, base_url: str, prompt: str, api:str) -> str:
        content = 'files/images/output/content.jpg'
        if model_name == "Sber GigaChat для генерации изображений":
            giga = GigaChat(credentials=api, verify_ssl_certs=False)

            # Исправлено: передаем список сообщений, как в оригинальном коде
            payload = await self.create_gigachat_payload(
                messages=[{"role": "system", "content": f"Ты - Василий Кандинский"},
                    {"role": "user", "content": f"Нарисуй картину: {prompt}"}],  # Список сообщений
                function_call='auto', 
                temperature=0.7, 
                max_tokens=2000
            )
            response = giga.chat(payload).choices[0].message.content
            url = response
            # Получение идентификатора изоборажения из ответа модели
            # с помощью библиотеки BeautifulSoup
            file_id = BeautifulSoup(response, "html.parser").find('img').get("src")

            image = giga.get_image(file_id)

            # Сохранение изображения в файл
            with open(content, mode="wb") as fd:
                fd.write(base64.b64decode(image.content))
        else:
            client = OpenAI(
                api_key=api,
                base_url=base_url,
            )

            size = "1024x1024"
            response = client.images.generate(
                model=model_name,
                prompt=prompt,
                n=1,
                size=size

        )
            url = response.data[0].url
            # Заголовки для запроса (если нужны)
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
            }

            # Отправляем GET-запрос для получения изображения
            response = requests.get(url, headers=headers)

            # Проверяем, успешен ли запрос
            if response.status_code == 200:
                # Сохраняем изображение в файл
                with open(content, "wb") as file:
                    file.write(response.content)
                print("Изображение успешно скачано и сохранено как image.png")
            else:
                print(f"Ошибка при скачивании изображения: {response.status_code}")
        
        return url
    
    async def generate_audio(self,model_name: str, base_url: str, prompt: str) -> str:
        client = OpenAI(api_key=PROXY_API_KEY, base_url=base_url)

        speech_file_path = Path(__file__).parent / "speech.mp3"
        response = client.audio.speech.create(
        model=model_name,
        voice="alloy",
        input=prompt
        )

        response.stream_to_file(speech_file_path)

        return speech_file_path
    
    async def vizard_photo(self, photo: str, messages: list, prompt: str):
        client = OpenAI(api_key=PROXY_API_KEY, base_url="https://api.proxyapi.ru/openai/v1")
        # Function to encode the image
        with open(photo, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"что на этой картинке?{prompt}",
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                        },
                    ],
                }
            ],
        )

        content = response.choices[0].message.content
        messages.append({"role": "assistant", "content": content})

        return messages, content
# # Класс для хранения всех моделей и доступа к ним
# class ModelRegistry:
#     async def __init__(self) -> None:
#         self.models = {
#             'OpenAI GPT-4.0': OpenAIModel('gpt-4o-mini', "https://api.proxyapi.ru/openai/v1"),
#             'OpenAI o1': OpenAIModel('o1-mini', "https://api.proxyapi.ru/openai/v1"),
#             'Google Gemini': OpenAIModel('gemini-1.5-flash', "https://api.proxyapi.ru/google/v1")
#         }

#     async def get_model(self, name: str) -> Model:
#         return self.models.get(name)

# # Пример использования
# model_registry = ModelRegistry()
# model = model_registry.get_model('OpenAI GPT-4.0')

# if model:
#     output = model.generate("Hello, world!")
#     print(output)
