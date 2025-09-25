import asyncio
from telethon import TelegramClient
from config import API_ID, API_HASH
import database
from handlers import admin, group
import os
session_name = os.environ.get("SESSION")
client = TelegramClient(session_name, API_ID, API_HASH)
pool = None

async def main():
    global pool

    pool = await database.get_pool()
    await database.init_db(pool)

    admin.setup(client, pool)
    group.setup(client, pool)

    await client.start()
    print("🚀 Юзербот запущен и слушает группы...")

    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
