import asyncio
import logging
import sys
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, FSInputFile, ContentType
from aiogram.types.web_app_info import WebAppInfo

from client import Client
from api import TOKEN

# Инициализация диспетчера и клиента
dp = Dispatcher()
cl = Client()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    Обработчик команды /start
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
/choose_model - выбор модели
/clear_context - очистить контекст

Удачи и успеха в твоих начинаниях! 💻🎉
'''
    await message.answer(greeting)
    await cl.model.new_user(tgID=message.from_user.id, name=message.from_user.full_name, date_start=datetime.now(), model=5, imageModel=8)


@dp.message(Command("subscription"))
async def cmd_buy(message: Message):
    """
    Обработчик команды /subscription
    """
    buttons = [
        [InlineKeyboardButton(text="Пробный период (7 дней)", callback_data="limited")],
        [InlineKeyboardButton(text="Бессрочная подписка", callback_data="unlimited")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons, row_width=2)
    await message.answer('Выберите подписку', reply_markup=keyboard)


@dp.callback_query(lambda c: c.data in ["limited", "unlimited"])
async def process_callback_answer(callback_query: CallbackQuery):
    """
    Обработчик callback-запросов для выбора подписки
    """
    if callback_query.data == 'unlimited':
        payment_url = await cl.create_check(tgID=callback_query.from_user.id, value='1', description='1')
        if payment_url == 'у вас есть подписка':
            await callback_query.answer('✅ У вас уже оформлена подписка')
            await callback_query.message.edit_text('✅ У вас уже оформлена подписка')
        else:
            buttons = [
                [InlineKeyboardButton(text="Оплатить подписку", web_app=WebAppInfo(url=payment_url))],
                [InlineKeyboardButton(text="Подтвердить оплату", callback_data="confirm_subscription")]
            ]
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons, row_width=2)
            await callback_query.answer('Совершите оплату подписки 1 руб.', reply_markup=keyboard)
            await callback_query.message.edit_text('Совершите оплату подписки 1 руб.', reply_markup=keyboard)
    else:
        has_lim_sub = await cl.model.select_lim(callback_query.from_user.id, 'hasLimitedSubscription')
        if has_lim_sub == 1:
            end_date = datetime.now() + timedelta(days=7)
            await cl.model.add_subscriptions(2, callback_query.from_user.id, end_Date=end_date)
            await callback_query.answer('Активирована пробная подписка')
            await callback_query.message.edit_text('Активирована пробная подписка')
            await cl.model.update_lim(callback_query.from_user.id, 'hasLimitedSubscription')
        else:
            await callback_query.message.edit_text('Вы уже активировали тестовую подписку')


@dp.callback_query(lambda c: c.data == 'confirm_subscription')
async def process_callback_answer(callback_query: CallbackQuery):
    """
    Обработчик callback-запросов для подтверждения оплаты
    """
    tgID = callback_query.from_user.id
    payment_id = await cl.model.get_payment_id(tgID, 1)
    payment_status = await cl.payments.check_payment_status(payment_id=payment_id)
    if payment_status == 'succeeded':
        await cl.model.update_payment_status(payment_status, payment_id)
        await cl.model.add_subscriptions(1, tgID, payment_id)
        await callback_query.answer("Оплата подтверждена")
        await callback_query.message.edit_text("Оплата подтверждена", reply_markup=None)


@dp.message(Command("choose_model"))
async def choose_model(message: Message):
    """
    Обработчик команды /choose_model
    """
    has_subscription = await cl.model.check_user_subscription(message.from_user.id)
    if (1,) in has_subscription:
        buttons = [
            [InlineKeyboardButton(text="Sber GigaChat", callback_data="Sber GigaChat")],
            [InlineKeyboardButton(text="OpenAI GPT-4.0", callback_data="OpenAI GPT-4.0")],
            [InlineKeyboardButton(text="OpenAI o1", callback_data="OpenAI o1")],
            [InlineKeyboardButton(text="Google Gemini", callback_data="Google Gemini")],
            [InlineKeyboardButton(text="Deepseek", callback_data="Deepseek")],
            [InlineKeyboardButton(text="Deepseek R1", callback_data="Deepseek R1")],
            [InlineKeyboardButton(text="Claude", callback_data="Claude")],
            [InlineKeyboardButton(text="Perplexity", callback_data="Perplexity")],
            [InlineKeyboardButton(text="DALL-E 3.0", callback_data="DALL-E 3.0")],
            [InlineKeyboardButton(text="Sber GigaChat для генерации изображений", callback_data="Sber GigaChat для генерации изображений")],
            [InlineKeyboardButton(text="dall-e-2", callback_data="dall-e-2")],
            [InlineKeyboardButton(text="tts-1", callback_data="tts-1")],
            [InlineKeyboardButton(text="tts-1-hd", callback_data="tts-1-hd")]
        ]
    else:
        buttons = [
            [InlineKeyboardButton(text="Sber GigaChat", callback_data="Sber GigaChat")],
            [InlineKeyboardButton(text="Deepseek", callback_data="Deepseek")],
            [InlineKeyboardButton(text="DALL-E 3.0", callback_data="DALL-E 3.0")],
            [InlineKeyboardButton(text="dall-e-2", callback_data="dall-e-2")]
        ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons, row_width=2)
    await message.answer('Выберите модель', reply_markup=keyboard)


@dp.callback_query(lambda c: c.data in ["Sber GigaChat", "OpenAI GPT-4.0", "OpenAI o1", "Google Gemini", "Deepseek", "Deepseek R1", 'Perplexity',  "Claude", "DALL-E 3.0", "Sber GigaChat для генерации изображений", "dall-e-2", "tts-1", "tts-1-hd"])
async def process_callback(callback_query: CallbackQuery):
    """
    Обработчик callback-запросов для выбора модели
    """
    tgID = callback_query.from_user.id
    model = callback_query.data

    await callback_query.answer(f'Выбрана модель: {model}')
    await callback_query.message.edit_text(f'Выбрана модель: {model}', reply_markup=None)

    models = {
        "OpenAI GPT-4.0": {"id": 1, "column": "model"},
        "OpenAI o1": {"id": 2, "column": "model"},
        "Google Gemini": {"id": 3, "column": "model"},
        "Deepseek": {"id": 4, "column": "model"},
        "Sber GigaChat": {"id": 5, "column": "model"},
        "Claude": {"id": 11, "column": "model"},
        "Deepseek R1": {"id": 12, "column": "model"},
        "Perplexity": {"id": 13, "column": "model"},
        "DALL-E 3.0": {"id": 6, "column": "imageModel"},
        "Sber GigaChat для генерации изображений": {"id": 7, "column": "imageModel"},
        "dall-e-2": {"id": 8, "column": "imageModel"},
        "tts-1": {"id": 9, "column": "audioModel"},
        "tts-1-hd": {"id": 10, "column": "audioModel"}
    }

    await cl.model.change_model(tgID=tgID, model=models[model]['id'], column=models[model]['column'])


@dp.message(Command("gen_image"))
async def img(message: Message):
    """
    Обработчик команды /gen_image
    """
    tgID = message.from_user.id
    amount = str(await cl.model.select_model_price(tgID))
    model_number = await cl.model.get_model(tgID, column='imageModel')
    prompt = message.text

    if prompt == '/gen_image':
        await message.answer('🎨 Чтобы сгенерировать изображение, после команды /gen_image добавьте описание')
    elif amount == '0':
        buttons = [
            [InlineKeyboardButton(text="🎨 Генерировать", callback_data=f"free_gen:")]
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons, row_width=2)
        await message.answer(f'🎨 Ваш промпт: {prompt}', reply_markup=keyboard)
    else:
        has_free_pic = await cl.model.select_lim(tgID, 'hasFreePicture')
        paymentID, payment_url = await cl.create_check(tgID=tgID, value=amount, description='2')

        buttons = [
            [InlineKeyboardButton(text="💳 Оплатить", web_app=WebAppInfo(url=payment_url))],
            [InlineKeyboardButton(text="✅ Подтвердить оплату", callback_data=f"confirm_image:{paymentID}")]
        ]

        await message.answer(f'🎨 Ваш промпт: {prompt}')

        if has_free_pic >= 1:
            buttons.append([InlineKeyboardButton(text="🆓 Использовать бесплатную генерацию", callback_data=f"use_free_image:{paymentID}")])

        await cl.model.add_image(tgID, paymentID, prompt, model_number)

        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons, row_width=2)
        await message.answer(f"""🎁 У вас есть {has_free_pic} бесплатных генераций.
💸 Проведите оплату в размере {amount} рублей""", reply_markup=keyboard)


@dp.callback_query(lambda c: c.data.startswith(('confirm_image:', 'use_free_image:', "free_gen:")))
async def process_callback_answer(callback_query: CallbackQuery):
    """
    Обработчик callback-запросов для подтверждения оплаты или использования бесплатной генерации
    """
    tgID = callback_query.from_user.id
    action, paymentID= callback_query.data.split(':')

    # Отвечаем на callback-запрос сразу
    await callback_query.answer()

    if action == "confirm_image":
        payment_status = await cl.payments.check_payment_status(payment_id=paymentID)
        if payment_status == 'succeeded':
            await callback_query.bot.send_chat_action(callback_query.message.chat.id, 'upload_photo')
            await callback_query.message.answer("🔄 Начинаем генерацию изображения...")
            await cl.model.update_payment_status(payment_status, paymentID)
            prompt, model = await cl.model.get_prompt_model_by_payment_id(paymentID)
            image_url = await cl.take_image(tgID, prompt, model)
            content = FSInputFile('content.jpg')
            await callback_query.message.answer_photo(photo=content)
            await callback_query.message.edit_text("✅ Оплата подтверждена", reply_markup=None)
            await cl.model.update_image_url(paymentID, image_url)
        else:
            await callback_query.message.answer("❌ Оплата не выполнена")

    else:
        if action == "use_free_image":
            has_free_pic = await cl.model.select_lim(tgID, 'hasFreePicture')
            if has_free_pic == 0:
                await callback_query.message.answer("🎉 Бесплатная генерация использована")
                await cl.model.update_lim(tgID, 'hasFreePicture', has_free_pic - 1)
                return
        await callback_query.bot.send_chat_action(callback_query.message.chat.id, 'upload_photo')
        await callback_query.message.answer("🔄 Начинаем генерацию изображения...")
        prompt, model = await cl.model.get_prompt_model_by_payment_id(paymentID)
        image_url = await cl.take_image(tgID, prompt, model)
        content = FSInputFile('files/images/output/content.jpg')
        await callback_query.message.answer_photo(photo=content)
        await callback_query.message.edit_text("🎉 Бесплатная генерация использована", reply_markup=None)
        await cl.model.update_image_url(paymentID, image_url)


@dp.message(Command("help"))
async def cmd_help(message: Message):
    """
    Обработчик команды /help
    """
    help_message = '''
/subscription - оформить подписку и поддержать работу бота
/gen_image - сгенерировать картинку ПОКА НЕ РАБОТАЕТ
/choose_model - выбор модели
/clear_context - очистить контекст
техподдержка - @zdarova_69
    '''
    await message.reply(help_message)


@dp.message(Command("clear_context"))
async def cmd_clear_context(message: Message):
    """
    Обработчик команды /clear_context
    """
    await cl.model.update_context_clear(message.from_user.id)
    await message.reply('Контекст очищен! ✅')


@dp.message(F.content_type == ContentType.PHOTO)
async def photo_handler(message: Message):
    """
    Обработчик фотографий
    """
    image_path = "files/images/input/input.jpg"
    await message.bot.send_chat_action(message.chat.id, 'typing')
    prompt = message.caption
    await message.bot.download(file=message.photo[-1].file_id, destination=image_path)
    answer = await cl.answer_photo(tgID=message.from_user.id, photo=image_path, prompt=prompt)
    await message.reply(answer)


@dp.message()
async def message_handler(message: Message) -> None:
    """
    Обработчик текстовых сообщений
    """
    # Показываем индикатор "печатает..."
    await message.bot.send_chat_action(message.chat.id, 'typing')
    answer = await cl.generate_answer(tgID=message.from_user.id, prompt=message.text)
    await message.reply(answer)


async def main() -> None:
    """
    Основная функция для запуска бота
    """
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())