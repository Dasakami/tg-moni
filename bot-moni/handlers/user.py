from aiogram import Router, types, F
from aiogram.filters import Command
from database import get_keywords, save_message

user_router = Router()

@user_router.message(F.text)
async def catch_keywords(message: types.Message):
    text = message.text.lower()
    keywords = get_keywords()

    if any(word in text for word in keywords):
        username = f"@{message.from_user.username}" if message.from_user.username else "Нет username"
        chat_title = message.chat.title if message.chat.title else "ЛС"
        save_message(message.from_user.id, username, chat_title, message.text)


@user_router.message(Command("start"))
async def user_start(message: types.Message):
    await message.answer("👋 Привет! Я бот, который отслеживает ключевые слова.\nНапиши /iamadmin если ты админ.")