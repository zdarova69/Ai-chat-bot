import asyncio
import logging
import sys
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, FSInputFile, ContentType
from aiogram.types.web_app_info import WebAppInfo   
from aiogram.filters import Command

# from gen_message import generate_messange
from client import Client
from api import TOKEN

# All handlers should be attached to the Router (or Dispatcher)

dp = Dispatcher()
cl = Client()




@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    greeting = '''
Ваш личный мультифункциональный помощник с доступом к лучшим языковым моделям и инструментам искусственного интеллекта!

📌 Что умеет бот:

Общение и помощь: Используйте мощь ChatGPT, DeepSeek, Gemini и GigaChat для решения задач, генерации идей, написания текстов, обучения и многого другого.

Создание изображений: Генерируйте уникальные изображения с помощью DALL-E по вашему запросу.

Мультимодельность: Выбирайте, какая модель лучше подходит для вашей задачи, или сравнивайте ответы от разных ИИ.

Удобство: Все возможности AI в одном месте, доступные прямо в Telegram.

✨ Почему этот бот?

Мощь нескольких AI: Больше не нужно переключаться между сервисами — всё в одном боте.

Простота использования: Интуитивный интерфейс и мгновенные ответы.

Универсальность: Подходит для работы, творчества, обучения и развлечений.

🚀 Начните прямо сейчас!
Отправьте боту запрос, выберите модель и получите результат. Создавайте тексты, изображения, решайте задачи и открывайте новые возможности с AI!

👉 Добавьте бота в Telegram и станьте частью будущего уже сегодня!

/start - Начать общение с ботом
/help - Получить помощь и список доступных команд
/subscription - оформить подписку и поддержать работу бота
/gen_image *ваш промпт* - сгенерировать картинку
/gen_sound *ваш промпт* - сгенерировать голосовое сообщение
/choose_model - выбор модели
/clear_context - очистить контекст

Удачи и успеха в твоих начинаниях! 💻🎉
'''
    await message.answer(greeting)
    
    
    cl.model.new_user(tgID=message.from_user.id, name=message.from_user.full_name, date_start=datetime.now(), model=5, imageModel=8)
# Обработчики команд
@dp.message(Command("subscription"))
async def cmd_buy(message: Message):
    
    buttons = [[InlineKeyboardButton(text="Пробный период (7 дней)", callback_data="limited")],
                [InlineKeyboardButton(text="Бессрочная подписка", callback_data="unlimited")]
        ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons, row_width=2)
    
    await message.answer(f'Выберите подписку', reply_markup=keyboard)
    
# Обработчик callback запросов
@dp.callback_query(lambda c: c.data in ["limited", "unlimited"])
async def process_callback_answer(callback_query: CallbackQuery):
    if callback_query.data == 'unlimited':
        # создаем платеж
        payment_url = cl.create_check(tgID=callback_query.from_user.id, value='1', description='1')
        if payment_url == 'у вас есть подписка':
            await callback_query.answer(f'✅ У вас уже оформлена подписка')
            await callback_query.message.edit_text(f'✅ У вас уже оформлена подписка')
        else:
            print('payment_url')
            buttons = [[InlineKeyboardButton(text="Оплатить подписку",web_app=WebAppInfo(url=payment_url))],
                    [InlineKeyboardButton(text="Подтвердить оплату", callback_data="confirm_subscription")]
            ]
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons, row_width=2)
            # Отправляем сообщение с кнопкой
            await callback_query.answer(f'Совершите оплату подписки 1 руб.', reply_markup=keyboard)
            await callback_query.message.edit_text(f'Совершите оплату подписки 1 руб.', reply_markup=keyboard)
    else:
        has_lim_sub = cl.model.select_lim(callback_query.from_user.id, 'hasLimitedSubscription')
        if has_lim_sub == 1:
            # Текущая дата и время
            now = datetime.now()

            # Добавляем 7 дней
            end_date = now + timedelta(days=7)
            
            cl.model.add_subscriptions(2, callback_query.from_user.id, end_Date=end_date)
            await callback_query.answer(f'Активирована пробная подписка')
            await callback_query.message.edit_text(f'Активирована пробная подписка')
            cl.model.update_lim(callback_query.from_user.id, 'hasLimitedSubscription')
        else:
            await callback_query.message.edit_text(f'Вы уже активировали тестовую подписку')

# Обработчик callback запросов
@dp.callback_query(lambda c: c.data == 'confirm_subscription')
async def process_callback_answer(callback_query: CallbackQuery):
     tgID = callback_query.from_user.id
     payment_id = cl.model.get_payment_id(tgID, 1)
     payment_status = cl.payments.check_payment_status(payment_id=payment_id)
     if payment_status == 'succeeded':
        cl.model.update_payment_status(payment_status, payment_id)
        cl.model.add_subscriptions(1, tgID, payment_id)
        await callback_query.answer(f"оплата подтверждена")
        await callback_query.message.edit_text(f"оплата подтверждена", reply_markup=None)

@dp.message(Command("choose_model"))
async def choose_model(message: Message):
    has_subscription = cl.model.check_user_subscription(message.from_user.id)
    if 1 in has_subscription:
        buttons = [[InlineKeyboardButton(text="Sber GigaChat", callback_data="Sber GigaChat")],
            [InlineKeyboardButton(text="OpenAI GPT-4.0", callback_data="OpenAI GPT-4.0")],
            [InlineKeyboardButton(text="OpenAI o1", callback_data="OpenAI o1")],
            [InlineKeyboardButton(text="Google Gemini", callback_data="Google Gemini")],
            [InlineKeyboardButton(text="Deepseek", callback_data="Deepseek")],
            [InlineKeyboardButton(text="DALL-E 3.0", callback_data="DALL-E 3.0")],
            [InlineKeyboardButton(text="Sber GigaChat для генерации изображений", callback_data="Sber GigaChat для генерации изображений")],
            [InlineKeyboardButton(text="dall-e-2", callback_data="dall-e-2")],
            [InlineKeyboardButton(text="tts-1", callback_data="tts-1")],
            [InlineKeyboardButton(text="tts-1-hd", callback_data="tts-1-hd")]
        ]
    else:
        buttons = [[InlineKeyboardButton(text="Sber GigaChat", callback_data="Sber GigaChat")],
            [InlineKeyboardButton(text="Sber GigaChat для генерации изображений", callback_data="Sber GigaChat для генерации изображений")],
            [InlineKeyboardButton(text="DALL-E 3.0", callback_data="DALL-E 3.0")],
            [InlineKeyboardButton(text="dall-e-2", callback_data="dall-e-2")]
        ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons, row_width=2)
    await message.answer('Выберите модель', reply_markup=keyboard)

@dp.callback_query(lambda c: c.data in ["Sber GigaChat", "OpenAI GPT-4.0", "OpenAI o1", "Google Gemini", "Deepseek",  "DALL-E 3.0", "Sber GigaChat для генерации изображений", "dall-e-2", "tts-1", "tts-1-hd"])
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
    "Sber GigaChat для генерации изображений": {
        "id": 7,
        "column": "imageModel"
    },
    "dall-e-2": {
        "id": 8,
        "column": "imageModel"
    },
    "tts-1": {
        "id": 9,
        "column": "audioModel"
    },
    "tts-1-hd": {
        "id": 10,
        "column": "audioModel"
    }
}
        
    cl.model.change_model(tgID=tgID, model=models[model]['id'], column=models[model]['column'])


@dp.message(Command("gen_image"))
async def img(message: Message):
    amount = '5'
    tgID = message.from_user.id
    prompt = message.text
    
    if prompt == '/gen_image':
        await message.answer(f'🎨 Чтобы сгенерировать изображение, после команды /gen_image добавьте описание')
    else:
        # Проверяем, есть ли у пользователя бесплатные генерации
        has_free_pic = cl.model.select_lim(tgID, 'hasFreePicture')
        paymentID, payment_url = cl.create_check(tgID=tgID, value=amount, description='2')
        
        # Создаем кнопки
        buttons = [
            [InlineKeyboardButton(text="💳 Оплатить", web_app=WebAppInfo(url=payment_url))],
            [InlineKeyboardButton(text="✅ Подтвердить оплату", callback_data=f"confirm_image:{paymentID}")]
        ]
        
        # Отправляем сообщение с промптом и информацией о бесплатных генерациях
        await message.answer(f'🎨 Ваш промпт: {prompt}')
    
        
        # Если есть бесплатные генерации, добавляем кнопку для их использования
        if has_free_pic > 1:
            buttons.append([InlineKeyboardButton(text="🆓 Использовать бесплатную генерацию", callback_data=f"use_free_image:{paymentID}")])
        
        # Добавляем запись о генерации в базу данных
        cl.model.add_image(tgID, paymentID, prompt)
        
        # Отправляем сообщение с кнопками
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons, row_width=2)
        await message.answer(f"""🎁 У вас есть {has_free_pic} бесплатных генераций.
    💸 Проведите оплату в размере {amount} рублей""", reply_markup=keyboard)


# Обработчик callback запросов
@dp.callback_query(lambda c: c.data.startswith(('confirm_image:', 'use_free_image:')))
async def process_callback_answer(callback_query: CallbackQuery):
    tgID = callback_query.from_user.id
    action, paymentID = callback_query.data.split(':')
    
    if action == "confirm_image":
        # Обработка подтверждения оплаты
        payment_status = cl.payments.check_payment_status(payment_id=paymentID)
        if payment_status == 'succeeded':
            # Уведомляем пользователя о начале генерации
            await callback_query.message.answer("🔄 Начинаем генерацию изображения...")
            
            cl.model.update_payment_status(payment_status, paymentID)
            prompt = cl.model.get_prompt_by_payment_id(paymentID)
            image_url = cl.take_image(tgID, prompt)
            # Открываем файл в бинарном режиме
            content = FSInputFile('content.jpg')
            await callback_query.message.answer_photo(photo=content)
            await callback_query.answer(f"✅ Оплата подтверждена")
            await callback_query.message.edit_text(f"✅ Оплата подтверждена", reply_markup=None)
            cl.model.update_image_url(paymentID, image_url)
        else:
            await callback_query.answer(f"❌ Оплата не выполнена")
    
    elif action == "use_free_image":
        has_free_pic = cl.model.select_lim(tgID, 'hasFreePicture')
        if has_free_pic == 0:
            await callback_query.answer(f"🎉 Бесплатная генерация использована")
        else: 
            # Уведомляем пользователя о начале генерации
            await callback_query.message.answer("🔄 Начинаем генерацию изображения...")
            
            # Обработка использования бесплатной генерации
            prompt = cl.model.get_prompt_by_payment_id(paymentID)
            image_url= cl.take_image(tgID, prompt)
            
            # Обновляем статус бесплатной генерации
            cl.model.update_lim(tgID, 'hasFreePicture', has_free_pic - 1)  # Уменьшаем количество бесплатных генераций
            content = FSInputFile('files/images/output/content.jpg')
            await callback_query.message.answer_photo(photo=content)
            await callback_query.answer(f"🎉 Бесплатная генерация использована")
            await callback_query.message.edit_text(f"🎉 Бесплатная генерация использована", reply_markup=None)
            cl.model.update_image_url(paymentID, image_url)

@dp.message(Command("help"))
async def cmd_help(message: Message):
    help_message = '''
/buy - оформить подписку и поддержать работу бота
/gen_image - сгенерировать картинку ПОКА НЕ РАБОТАЕТ
/choose_model - выбор модели
/clear_context - очистить контекст
техподдержка - @zdarova_69
        '''
    await message.reply(help_message)

@dp.message(Command("clear_context"))
async def cmd_clear_context(message: Message):
    cl.model.update_context_clear(message.from_user.id)
    await message.reply('контекст очищен! ✅')


@dp.message(F.content_type == ContentType.PHOTO)
async def photo_handler(message: Message):
    image_path = "files/images/input/input.jpg"
    prompt=message.caption
    # Скачивание фотографии
    await message.bot.download(file=message.photo[-1].file_id, destination=image_path)

    answer = cl.answer_photo(tgID=message.from_user.id, photo=image_path, prompt=prompt)
    await message.reply(answer)


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