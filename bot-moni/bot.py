import asyncio
from aiogram import Bot, Dispatcher
from config import TOKEN
import database
from handlers.admin import admin_router

async def main():
    database.pool = await database.get_pool()  # создаём глобальный pool
    await database.init_db()                    # создаём таблицы

    bot = Bot(TOKEN)
    dp = Dispatcher()
    dp.include_router(admin_router)


    print("🚀 Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
