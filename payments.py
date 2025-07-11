import json
from yookassa import Configuration, Payment
from api import ACCOUNT_ID, SECRET_KEY

class Payments():
    def __init__(self):
        Configuration.account_id = ACCOUNT_ID
        Configuration.secret_key = SECRET_KEY
    async def payment(self, value, description):
        payment = Payment.create({
            "amount": {
                "value": value,
                "currency": "RUB"
            },
            "payment_method_data": {
                "type": "bank_card"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": "https://t.me/NeuralLLM_Bot"
            },
            "capture": True,
            "description": description,  # Добавлена запятая
            "receipt": {
                "customer": {
                    "email": "stapkt@gmail.com"
                },
                "items": [
                    {
                        "description": description,
                        "quantity": 1,
                        "amount": {
                            "value": value,
                            "currency": "RUB"
                        },
                        "vat_code": 1
                    }
                ]
            }
        })  # Добавлена закрывающая скобка
        return json.loads(payment.json())
    async def check_payment_status(self, payment_id):
        payment = Payment.find_one(payment_id=payment_id)
        return payment['status']