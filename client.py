from payments import Payments
from aimodels import OpenAIModel
from datetime import datetime, timedelta
import re
from db import UserModel


class Client:
    def __init__(self):
        self.model = UserModel()
        self.payments = Payments()
        self.aimodel = OpenAIModel()

    async def create_check(self, tgID, value, description):
        try:
            if description == '1':
                PaymentID = await self.model.check_payment_exist(tgID=tgID, description=description)
                if PaymentID:
                    status = await self.model.check_status(tgID=tgID, description=description)
                    if status == 'succeeded':
                        print('подписка уже есть')
                        return 'у вас есть подписка'
                    elif status == 'pending':
                        print('ожидание оплаты')
                        payment_url = await self.model.get_payment_url(tgID, description)
                        return payment_url
                    else:
                        # Создаем новый платеж вместо старого
                        payment_check = await self.payments.payment(value, description)  # Используем позиционные аргументы

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
                            await self.model.update_payment(PaymentID, status, value, created_at, expires_at, payment_url, tgID, description)
                            return payment_url
                else:
                    # Создаем новый платеж вместо старого
                    payment_check = await self.payments.payment(value, description)  # Используем позиционные аргументы

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

                    await self.model.add_payment(PaymentID, status, description, tgID, value, created_at, expires_at, payment_url)

                return payment_url
            if description == '2':
                payment_check = await self.payments.payment(value, description)  # Используем позиционные аргументы
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

                await self.model.add_payment(PaymentID, status, description, tgID, value, created_at, expires_at, payment_url)

                return PaymentID, payment_url
        except Exception as e:
            print(f"An error occurred: {e}")

    async def generate_answer(self, tgID, prompt: str):
        if prompt is None:
            return 'я не люблю работать со стикерами'
        # Получаем сообщения и номер модели
        messages = await self.model.select_messages(tgID)
        model_number = await self.model.get_model(tgID, column='model')
        # Генерируем ответ
        answer, content = await self.aimodel.generate_text(
            model_name=self.aimodel.model_list[model_number]['name'],
            base_url=self.aimodel.model_list[model_number]['base_url'],
            prompt=prompt,
            api=self.aimodel.model_list[model_number]['api'],
            messages=messages
        )

        # Обновляем сообщения в базе данных
        await self.model.update_messages(tgID, answer)

        return content

    async def take_image(self, tgID, prompt: str):
        model_number = await self.model.get_model(tgID, column='imageModel')

        url = await self.aimodel.generate_image(
            model_name=self.aimodel.model_list[model_number]['name'],
            base_url=self.aimodel.model_list[model_number]['base_url'],
            prompt=prompt,
            api=self.aimodel.model_list[model_number]['api']
        )
        return url

    async def answer_photo(self, tgID, photo: str, prompt: str):
        # Получаем сообщения и номер модели
        messages = await self.model.select_messages(tgID)

        answer, content = await self.aimodel.vizard_photo(photo=photo, messages=messages, prompt=prompt)

        # Обновляем сообщения в базе данных
        await self.model.update_messages(tgID, answer)

        return content