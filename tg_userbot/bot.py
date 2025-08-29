import asyncio
from telethon import TelegramClient
from config import API_ID, API_HASH
import database
from handlers import admin, group
import os
session_name = os.environ.get("SESSION")
# Сессия Telethon сохранится в session.session
client = TelegramClient(session_name, API_ID, API_HASH)
pool = None

async def main():
    global pool
    # Подключение к базе
    pool = await database.get_pool()
    await database.init_db(pool)

    # Подключаем обработчики
    admin.setup(client, pool)
    group.setup(client, pool)

    # Запускаем клиент (если уже авторизован, просто подключится)
    await client.start()
    print("🚀 Юзербот запущен и слушает группы...")

    # Теперь слушаем новые сообщения без повторного вступления в группы
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
