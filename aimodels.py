from abc import ABC, abstractmethod

from openai import OpenAI

import requests
import json
from pathlib import Path
from PIL import Image
from io import BytesIO
import base64

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
        'name': 'Sber GigaChat для генерации изображений',
        'base_url': ''
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

    }
} 
    def generate_text(self,model_name: str, base_url: str, prompt: str, api: str, messages: list ) -> str:
        # Добавляем новый запрос пользователя
        messages.append({"role": "user", "content": prompt})
        
        if model_name == 'Sber GigaChat':
            payload = Chat(
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
            )
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
        
        else:
        # Здесь можно разместить логику для отправки запроса на API
            client = OpenAI(
                api_key=api,
                base_url=base_url,
            )
            
            # Выполняем запрос к модели
            completion = client.chat.completions.create(
                model=model_name,
                messages=messages
            )
            
            content = completion.choices[0].message.content
            # Добавляем ответ ассистента в messages
        messages.append({"role": "assistant", "content": content})

        # Возвращаем обновлённый список messages
        return messages, content

    def generate_image(self,model_name: str, base_url: str, prompt: str) -> str:
        content = 'content.jpg'
        if model_name == "Sber GigaChat для генерации изображений":
            giga = GigaChat(credentials=GIGACHAT_API_KEY, verify_ssl_certs=False)

            payload = Chat(
                messages=[Messages(role=MessagesRole.USER, content=f"Нарисуй картину: {prompt}")],
                temperature=0.7,
                max_tokens=100,
                function_call="auto",
            )

            # Получение изображения
            response = giga.chat(payload)
            url = response.choices[0].message.content.split('src="')[1].split('"')[0]
            img = giga.get_image(url)

            # Декодирование base64 и создание изображения
            img_data = base64.b64decode(img.content)
            image = Image.open(BytesIO(img_data))

            image.save(content)
            # Отображение изображения
        else:
            client = OpenAI(
                api_key=PROXY_API_KEY,
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
    def generate_audio(self,model_name: str, base_url: str, prompt: str) -> str:
        client = OpenAI(api_key=PROXY_API_KEY, base_url="base_url")

        speech_file_path = Path(__file__).parent / "speech.mp3"
        response = client.audio.speech.create(
        model=model_name,
        voice="alloy",
        input=prompt
        )

        response.stream_to_file(speech_file_path)

        return speech_file_path
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
