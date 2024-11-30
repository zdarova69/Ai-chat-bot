
from api import account_id, secret_key, proxy_api
import sqlite3
from openai import OpenAI
from payments import Payments
from models import OpenAIModel

from db import UserModel


class Client():
    def __init__(self):
        self.model = UserModel()
        self.payments = Payments()
        # self.tgID = tgID
        # self.name = name
        # self.date_start = date_start
        # self.model = model
        # self.models = {
        #     'OpenAI GPT-4.0': OpenAIModel('gpt-4o-mini', "https://api.proxyapi.ru/openai/v1"),
        #     'OpenAI o1': OpenAIModel('o1-mini', "https://api.proxyapi.ru/openai/v1"),
        #     'Google Gemini': OpenAIModel('gemini-1.5-flash', "https://api.proxyapi.ru/google/v1"),
        #     'Deepseek':''
        # }
        self.model_list = {
    1: {
        'name': 'gpt-4o-mini', 
        'base_url': "https://api.proxyapi.ru/openai/v1"
    },
    2: {
        'name': 'o1-mini', 
        'base_url': "https://api.proxyapi.ru/openai/v1"
    },
    3: {
        'name': 'gemini-1.5-flash', 
        'base_url': "https://api.proxyapi.ru/google/v1"
    },
    4: {
        'name': 'Deepseek', 
        'base_url': ""
    }
} 

    def create_check(self, tgID, value, description):
        try:
            PaymentID = self.model.check_payment_exist(tgID=tgID, description=description)
            print(PaymentID)
            if PaymentID:         
                status = self.model.check_status(tgID=tgID, description=description)
                if status == 'succeeded':
                    print('подписка уже есть')
                    return 'у вас есть подписка'
                elif status == 'pending':
                    print('ожидание оплаты')
                    payment_url = self.model.get_payment_url(tgID, description)
                    return payment_url
                else:
                    # Создаем новый платеж вместо старого
                    payment_check = self.payments.payment(value, description)  # Используем позиционные аргументы

                    payment_url = payment_check['confirmation']['confirmation_url']

                    # Получаем значения
                    PaymentID = payment_check['id']
                    
                    description = payment_check['description']
                    value = payment_check['amount']['value']
                    created_at = payment_check['created_at']
                    
                    if status == 'canceled':  
                        print('обновляем')
                        # Если запись существует, обновляем остальные атрибуты
                        self.model.update_payment(PaymentID, value, created_at, payment_url, tgID, description)
            else:
                # Если записи не существует, добавляем новую запись
                payment_check = self.payments.payment(value, description)  # Используем позиционные аргументы

                payment_url = payment_check['confirmation']['confirmation_url']
                # Получаем значения
                PaymentID = payment_check['id']
                
                description = payment_check['description']
                value = payment_check['amount']['value']
                created_at = payment_check['created_at']
                status = payment_check['status']
                self.model.add_payment(PaymentID, status, description, tgID, value, created_at, payment_url)
                
                return payment_url

        except Exception as e:
            print(f"An error occurred: {e}")
            
    def generate_text(self, tgID, prompt:str): 
        # Обновляем информацию о пользователе в базе данных
        # conn = sqlite3.connect(self.db)
        # cursor = conn.cursor()     
        # # Проверяем, существует ли пользователь в базе данных
        # cursor.execute('SELECT model FROM users WHERE tgID = ?', (tgID,))
        # model_number = cursor.fetchone()[0]
        model_number = self.model.get_model(tgID)
        answer = OpenAIModel(model_name=self.model_list[model_number]['name'], base_url=self.model_list[model_number]['base_url'])

        return answer.generate(prompt=prompt)
        


        
    
       
