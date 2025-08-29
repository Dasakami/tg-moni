from aiogram import Router, types
import database

group_router = Router()

@group_router.message()
async def track_keywords(message: types.Message):
    if message.from_user.is_bot or not message.text:
        return

    keywords = await database.get_keywords()
    text = message.text.lower()
    found = [word for word in keywords if word in text]

    if found:
        await database.save_message(
            user_id=message.from_user.id,
            username=message.from_user.username or "Нет username",
            chat_title=message.chat.title or "Личный чат",
            chat_username=message.chat.username,  # <- тег группы
            message=message.text
        )



        
