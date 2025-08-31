import asyncpg
from config import DB_USER, DB_PASS, DB_NAME, DB_HOST

pool = None  # глобальный пул

async def get_pool():
    return await asyncpg.create_pool(
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        host=DB_HOST
    )

async def init_db():
    async with pool.acquire() as conn:
        # таблица админов
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            user_id BIGINT PRIMARY KEY,
            username TEXT
        )
        """)
        # таблица ключевых слов
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS keywords (
            id SERIAL PRIMARY KEY,
            word TEXT UNIQUE
        )
        """)
        # таблица сообщений
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            username TEXT,
            chat_title TEXT,
            chat_username TEXT,
            message TEXT,
            status TEXT DEFAULT 'Неотвеченные'
        )
        """)

# --- Админы ---
async def add_admin(user_id, username):
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO admins(user_id, username) VALUES($1,$2) ON CONFLICT DO NOTHING",
            user_id, username
        )

async def delete_message(msg_id: int):
    async with pool.acquire() as conn:
        result = await conn.execute("DELETE FROM messages WHERE id = $1", msg_id)
        return result.endswith("DELETE 1")


async def delete_messages_range(start_id: int, end_id: int):
    async with pool.acquire() as conn:
        result = await conn.execute(
            "DELETE FROM messages WHERE id BETWEEN $1 AND $2",
            start_id, end_id
        )
        # result типа 'DELETE X' → достанем число
        return int(result.split()[-1])


async def is_admin(user_id):
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT 1 FROM admins WHERE user_id=$1", user_id)
        return row is not None

async def get_admins():
    async with pool.acquire() as conn:
        return await conn.fetch("SELECT user_id, username FROM admins")

async def remove_admin(user_id):
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM admins WHERE user_id=$1", user_id)

# --- Ключевые слова ---
async def add_keyword(word):
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO keywords(word) VALUES($1) ON CONFLICT DO NOTHING", word.lower()
        )

async def get_keywords():
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT word FROM keywords")
        return [r["word"] for r in rows]


async def save_message(user_id, username, chat_title, message, chat_username=None):
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO messages(user_id, username, chat_title, chat_username, message, status)
            VALUES($1,$2,$3,$4,$5,'Неотвеченные')
            """,
            user_id, username, chat_title, chat_username, message
        )


async def update_message_status(msg_id, status):
    async with pool.acquire() as conn:
        await conn.execute("UPDATE messages SET status=$1 WHERE id=$2", status, msg_id)


async def get_messages(limit=10):
    async with pool.acquire() as conn:
        return await conn.fetch(
            "SELECT id, user_id, username, chat_title, chat_username, message, status "
            "FROM messages ORDER BY id DESC LIMIT $1",
            limit
        )
