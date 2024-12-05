import asyncio
import logging
import sys
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command


from datetime import datetime
# from gen_message import generate_messange
from client import Client
from payments import Payments
# Открываем файл в режиме чтения
with open('tg_api.txt', 'r') as file:
    # Читаем содержимое файла
    TOKEN = file.read()

# All handlers should be attached to the Router (or Dispatcher)

dp = Dispatcher()
cl = Client()




@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    greeting = '''
🚀 Приветствую тебя дорогой друг. 🌟

🤖 Я - чат бот, работающий с большими языковыми моделями, а именно:

✅ **OpenAI ChatGPT и DALL-E**
   - **ChatGPT**: Это мощная языковая модель, способная генерировать человекоподобный текст на основе входных данных. Она может отвечать на вопросы, вести диалог, создавать истории и многое другое.
   - **DALL-E**: Это модель, способная создавать изображения на основе текстовых описаний. Она может генерировать уникальные и креативные изображения, соответствующие заданным описаниям.
   - **OpenAI O1**: Это оптимизированная модель для обработки естественного языка, разработанная OpenAI. Она предназначена для высокопроизводительных задач, таких как анализ текста, классификация и извлечение информации. OpenAI O1 обеспечивает быструю и эффективную обработку данных, что делает её идеальной для приложений, требующих высокой скорости и точности.

✅ **Sber Gigachat и Kandinsky 3.1**
   - **Gigachat**: Это российская языковая модель, разработанная Сбербанком. Она обладает высокой способностью к пониманию и генерации текста на русском языке.
   - **Kandinsky 3.1**: Это модель для генерации изображений, названная в честь русского художника Казимира Малевича. Она способна создавать абстрактные и художественные изображения на основе текстовых описаний.

✅ **Google Gemini**
   - **Gemini**: Это многофункциональная модель искусственного интеллекта от Google, которая объединяет в себе возможности обработки естественного языка, генерации изображений и других задач. Она способна выполнять широкий спектр задач, от диалога до анализа данных.

✅ **Deepseek**
   - **Deepseek**: Это модель, специализирующаяся на глубоком поиске и анализе информации. Она способна извлекать ценные данные из больших объемов текста, помогая в исследованиях и анализе данных.

🔍 Чем могу помочь? Вот несколько вещей, которые ты можешь узнать или сделать прямо сейчас:

/start - Начать общение с ботом
/help - Получить помощь и список доступных команд
/buy - оформить подписку и поддержать работу бота
/gen_image *ваш промпт* - сгенерировать картинку
/choose_model - выбор модели

Удачи и успеха в твоих начинаниях! 💻🎉
'''
    await message.answer(greeting)
    
    
    cl.model.new_user(tgID=message.from_user.id, name=message.from_user.full_name, date_start=datetime.now(), model=5, imageModel=8)
# Обработчики команд
@dp.message(Command("buy"))
async def cmd_buy(message: Message):
    payment_url = cl.create_check(tgID=message.from_user.id, value='1', description='1')
    if payment_url == 'у вас есть подписка':
        await message.answer(f'✅ У вас уже оформлена подписка')
    else:
        buttons = [[InlineKeyboardButton(text="Оплатить подписку", url=payment_url)],
                [InlineKeyboardButton(text="Подтвердить оплату", callback_data="confirm_subscription")]
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons, row_width=2)
        # Отправляем сообщение с кнопкой
        await message.answer(f'Совершите оплату подписки 1 руб.', reply_markup=keyboard)

# Обработчик callback запросов
@dp.callback_query(lambda c: c.data == 'confirm_subscription')
async def process_callback_answer(callback_query: CallbackQuery):
     tgID = callback_query.from_user.id
     payment_id = cl.model.get_payment_id(tgID, 1)
     payment_status = cl.payments.check_payment(payment_id=payment_id)
     if payment_status == 'succeeded':
        cl.model.update_payment_status(payment_status, payment_id)
        cl.model.add_subscriptions(1, tgID, payment_id)
        await callback_query.answer(f"оплата подтверждена")
        await callback_query.message.edit_text(f"оплата подтверждена", reply_markup=None)

@dp.message(Command("choose_model"))
async def choose_model(message: Message):
    buttons = [[InlineKeyboardButton(text="Sber GigaChat", callback_data="Sber GigaChat")],
        [InlineKeyboardButton(text="OpenAI GPT-4.0", callback_data="OpenAI GPT-4.0")],
        [InlineKeyboardButton(text="OpenAI o1", callback_data="OpenAI o1")],
        [InlineKeyboardButton(text="Google Gemini", callback_data="Google Gemini")],
        [InlineKeyboardButton(text="DALL-E 3.0", callback_data="DALL-E 3.0")],
        [InlineKeyboardButton(text="Kandinsky", callback_data="Kandinsky")],
        [InlineKeyboardButton(text="dall-e-2", callback_data="dall-e-2")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons, row_width=2)
    await message.answer('Выберите модель', reply_markup=keyboard)

@dp.callback_query(lambda c: c.data in ["Sber GigaChat", "OpenAI GPT-4.0", "OpenAI o1", "Google Gemini", "Deepseek",  "DALL-E 3.0", "Kandinsky", "dall-e-2"])
async def process_callback(callback_query: CallbackQuery):
    tgID = callback_query.from_user.id
    model = callback_query.data

    await callback_query.answer(f'Выбрана модель: {model}')
    await callback_query.message.edit_text(f'Выбрана модель: {model}', reply_markup=None)

    models = {
    "OpenAI GPT-4.0": {
        "id": 1,
        "column": "model"
    },
    "OpenAI o1": {
        "id": 2,
        "column": "model"
    },
    "Google Gemini": {
        "id": 3,
        "column": "model"
    },
    "Deepseek": {
        "id": 4,
        "column": "model"
    },
    "Sber GigaChat": {
        "id": 5,
        "column": "model"
    },
    "DALL-E 3.0": {
        "id": 6,
        "column": "imageModel"
    },
    "Kandinsky": {
        "id": 7,
        "column": "imageModel"
    },
    "dall-e-2": {
        "id": 8,
        "column": "imageModel"
    }
}
        
    cl.model.change_model(tgID=tgID, model=models[model]['id'], column=models[model]['column'])


@dp.message(Command("gen_image"))
async def img(message: Message):
    amount = '5'
    tgID = message.from_user.id
    prompt = message.text
    paymentID, payment_url = cl.create_check(tgID=tgID, value=amount, description='2')
    cl.model.add_image(tgID, paymentID, prompt)
    buttons = [
        [InlineKeyboardButton(text="Оплатить подписку", url=payment_url)],
        [InlineKeyboardButton(text="Подтвердить оплату", callback_data=f"confirm_image:{paymentID}")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons, row_width=2)
    await message.answer(f'Проведите оплату в размере {amount} рублей', reply_markup=keyboard)
    
    # # Обработчик callback запросов
@dp.callback_query(lambda c: c.data.startswith('confirm_image:'))
async def process_callback_answer(callback_query: CallbackQuery):
    tgID = callback_query.from_user.id
    _, paymentID = callback_query.data.split(':')
    payment_status = cl.payments.check_payment(payment_id=paymentID)
    if payment_status == 'succeeded':
        cl.model.update_payment_status(payment_status, paymentID)
        prompt = cl.model.get_prompt_by_payment_id(paymentID)
        image_url = cl.take_image(tgID, prompt)
 
        await callback_query.message.reply(image_url)
        await callback_query.answer(f"Оплата подтверждена")
        await callback_query.message.edit_text(f"Оплата подтверждена", reply_markup=None)
        cl.model.update_image_url(paymentID, image_url)
    else:
        await callback_query.answer(f"Оплата не выполнена")

@dp.message(Command("help"))
async def cmd_help(message: Message):
    help_message = '''
/buy - оформить подписку и поддержать работу бота
/gen_image - сгенерировать картинку ПОКА НЕ РАБОТАЕТ
/choose_model - выбор модели
техподдержка - @zdarova_69
        '''
    await message.reply(help_message)


@dp.message()
async def message_handler(message: Message) -> None:
    """
    Handler will forward receive a message back to the sender

    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """
    # try:
        # Send a copy of the received message
    print(message.text)
    answer = cl.generate_answer(tgID=message.from_user.id ,prompt=message.text)
    await message.reply(answer)
    # except TypeError:
    #     # But not all the types is supported to be copied so need to handle it
    #     await message.answer("Nice try!")


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())