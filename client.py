from payments import Payments
from aimodels import OpenAIModel
from datetime import datetime, timedelta
import re
import json

from db import UserModel


class Client():
    def __init__(self):
        self.model = UserModel()
        self.payments = Payments()
        self.aimodel = OpenAIModel()
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
        

    def create_check(self, tgID, value, description):
        try:
            if description == '1':         
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
                        
                        # Удаляем временную зону и заменяем 'T' на пробел
                        created_at = re.sub(r'\.\d{3}Z$', '', created_at).replace('T', ' ')
                        # Преобразуем строку в объект datetime
                        created_at_dt = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')

                        # Добавляем 1 час к created_at
                        expires_at_dt = created_at_dt + timedelta(hours=1)

                        # Преобразуем expires_at обратно в строку
                        expires_at = expires_at_dt.strftime('%Y-%m-%d %H:%M:%S')
                                                
                        if status == 'canceled':  
                            status = payment_check['status']
                            print('обновляем')
                            # Если запись существует, обновляем остальные атрибуты
                            self.model.update_payment(PaymentID, status, value, created_at,expires_at, payment_url, tgID, description)
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
                    # Если записи не существует, добавляем новую запись
                    status = payment_check['status']

                    # Удаляем временную зону и заменяем 'T' на пробел
                    created_at = re.sub(r'\.\d{3}Z$', '', created_at).replace('T', ' ')

                    # Преобразуем строку в объект datetime
                    created_at_dt = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')

                    # Прибавляем 3 часа, чтобы учесть разницу во времени
                    adjusted_created_at_dt = created_at_dt + timedelta(hours=3)

                    # Прибавляем еще 1 час, чтобы получить время закрытия платежа
                    expires_at_dt = adjusted_created_at_dt + timedelta(hours=1)

                    # Преобразуем expires_at обратно в строку
                    created_at = adjusted_created_at_dt.strftime('%Y-%m-%d %H:%M:%S')
                    expires_at = expires_at_dt.strftime('%Y-%m-%d %H:%M:%S')

                    self.model.add_payment(PaymentID, status, description, tgID, value, created_at, expires_at, payment_url)
                        
                return payment_url
            if description == '2':
                payment_check = self.payments.payment(value, description)  # Используем позиционные аргументы
                payment_url = payment_check['confirmation']['confirmation_url']
                # Получаем значения
                PaymentID = payment_check['id']
                description = payment_check['description']
                value = payment_check['amount']['value']
                created_at = payment_check['created_at']
                status = payment_check['status']

                # Удаляем временную зону и заменяем 'T' на пробел
                # Получаем created_at и status
                created_at = payment_check['created_at']
                status = payment_check['status']

                # Удаляем временную зону и заменяем 'T' на пробел
                created_at = re.sub(r'\.\d{3}Z$', '', created_at).replace('T', ' ')

                # Преобразуем строку в объект datetime
                created_at_dt = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')

                # Прибавляем 3 часа, чтобы учесть разницу во времени
                adjusted_created_at_dt = created_at_dt + timedelta(hours=3)

                # Прибавляем еще 1 час, чтобы получить время закрытия платежа
                expires_at_dt = adjusted_created_at_dt + timedelta(hours=1)

                # Преобразуем  обратно в строку
                created_at = adjusted_created_at_dt.strftime('%Y-%m-%d %H:%M:%S')
                expires_at = expires_at_dt.strftime('%Y-%m-%d %H:%M:%S')

                self.model.add_payment(PaymentID, status, description, tgID, value, created_at, expires_at, payment_url)

                return PaymentID, payment_url
        except Exception as e:
            print(f"An error occurred: {e}")
            
    def generate_answer(self, tgID, prompt:str): 
       # Получаем сообщения и номер модели
        messages = self.model.select_messages(tgID)
        model_number = self.model.get_model(tgID, column='model')
        # Генерируем ответ
        answer, content = self.aimodel.generate_text(
            model_name=self.aimodel.model_list[model_number]['name'],
            base_url=self.aimodel.model_list[model_number]['base_url'],
            prompt=prompt,
            api=self.aimodel.model_list[model_number]['api'],
            messages=messages
        )

        
        # Обновляем сообщения в базе данных
        self.model.update_messages(tgID, answer)

        return content

    def take_image(self, tgID, prompt:str): 
       
        model_number = self.model.get_model(tgID, column='imageModel')
        
        url =self.aimodel.generate_image(model_name=self.aimodel.model_list[model_number]['name'], base_url=self.aimodel.model_list[model_number]['base_url'], prompt=prompt)
        return url
        


        
    
       
