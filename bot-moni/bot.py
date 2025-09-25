import asyncio
from aiogram import Bot, Dispatcher
from config import TOKEN
import database
from handlers.admin import admin_router

async def main():
    database.pool = await database.get_pool()  
    await database.init_db()                   

    bot = Bot(TOKEN)
    dp = Dispatcher()
    dp.include_router(admin_router)


    print("🚀 Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
