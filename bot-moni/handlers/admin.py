from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import database

admin_router = Router()
# создаём пустую клавиатуру
filter_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Все", callback_data="filter_all"),
            InlineKeyboardButton(text="Неотвеченные", callback_data="filter_unanswered"),
            InlineKeyboardButton(text="Отвеченные", callback_data="filter_done")
        ]
    ]
)

@admin_router.message(Command("start"))
async def admin_start(message: types.Message):
    if not await database.is_admin(message.from_user.id):
        return await message.answer("❌ У вас нет доступа!")
    await message.answer(
        "✅ Админ-панель.\n"
        "Команды:\n"
        "/add слово — добавить ключ\n"
        "/show — показать совпадения\n"
        "/list — список ключей\n"
        "/iamadmin — стать админом\n"
        "/add_admin <id или @username> — добавить админа\n"
        "/del_admin <id> — удалить админа\n"
        "/admins — список админов"
    )

@admin_router.message(Command("iamadmin"))
async def iam_admin(message: types.Message):
    if await database.is_admin(message.from_user.id):
        return await message.answer("✅ Вы уже админ.")
    if await database.get_admins == 0:
        await database.add_admin(message.from_user.id, message.from_user.username or "Нет username")
    await message.answer("🎉 Вы назначены админом!")


@admin_router.message(Command("show"))
async def show_messages(message: types.Message):
    if not await database.is_admin(message.from_user.id):
        return
    await message.answer("Выберите фильтр:", reply_markup=filter_keyboard)

MAX_LEN = 4000  # лимит Telegram

@admin_router.callback_query(lambda c: c.data.startswith("filter_"))
async def filter_messages(callback: types.CallbackQuery):
    filter_type = callback.data.split("_")[1]  # all / unanswered / done

    rows = await database.get_messages(100)

    if filter_type == "unanswered":
        rows = [r for r in rows if r["status"] == "Неотвеченные"]
    elif filter_type == "done":
        rows = [r for r in rows if r["status"] == "Отвеченные"]

    if not rows:
        await callback.message.edit_text("⚠️ Сообщений нет для выбранного фильтра")
        return

    await callback.message.delete()  # удаляем сообщение с кнопками

    for r in rows:
        chat_link = f"@{r['chat_username']}" if r['chat_username'] else r['chat_title']
        username_text = f"@{r['username']}" if r['username'] != "Нет username" else "Нет username"

        if r['username'] != "Нет username":
        # Кнопка с кликабельной ссылкой на username
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Открыть чат с пользователем", url=f"https://t.me/{r['username']}")]
            ]
        )
        else:
            keyboard = None  # для пользователей без username кнопки нет

        text = (
        f"{r['message']}\n\n"
        f"Канал: {chat_link}\n"
        f"Username: {username_text}\n"
        f"ID сообщения: {r['id']}\n"
        f"Статус: {r['status']}"
    )

        await callback.message.answer(text, reply_markup=keyboard)



    await callback.answer()  # убрать часики

@admin_router.message(Command("done"))
async def mark_done(message: types.Message):
    if not await database.is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 2:
        return await message.answer("⚠️ Используй: /done <id сообщения>")
    msg_id = int(parts[1])
    await database.update_message_status(msg_id, "Отвеченные")
    await message.answer(f"✅ Сообщение {msg_id} помечено как Отвеченное")


@admin_router.message(Command("add_admin"))
async def add_new_admin(message: types.Message):
    if not await database.is_admin(message.from_user.id):
        return await message.answer("❌ Нет доступа!")
    parts = message.text.split()
    if len(parts) < 2:
        return await message.answer("⚠️ Используй: /add_admin <user_id или @username>")
    target = parts[1]
    if target.startswith("@"):
        await database.add_admin(0, target)
        await message.answer(f"✅ Пользователь {target} добавлен как админ (надо написать боту).")
    else:
        await database.add_admin(int(target), "ID-only")
        await message.answer(f"✅ ID {target} добавлен как админ.")

@admin_router.message(Command("del_admin"))
async def del_admin(message: types.Message):
    if not await database.is_admin(message.from_user.id):
        return await message.answer("❌ Нет доступа!")
    parts = message.text.split()
    if len(parts) < 2:
        return await message.answer("⚠️ Используй: /del_admin <user_id>")
    target_id = int(parts[1])
    await database.remove_admin(target_id)
    await message.answer(f"🗑 Админ {target_id} удалён.")

@admin_router.message(Command("admins"))
async def list_admins(message: types.Message):
    if not await database.is_admin(message.from_user.id):
        return await message.answer("❌ Нет доступа!")
    admins = await database.get_admins()
    if not admins:
        return await message.answer("⚠️ Админов пока нет.")
    text = "👑 Список админов:\n\n"
    for a in admins:
        text += f"ID: {a['user_id']} | {a['username']}\n"
    await message.answer(text)


@admin_router.message(Command("del_message"))
async def delete_message(message: types.Message):
    if not await database.is_admin(message.from_user.id):
        return await message.answer("❌ Нет доступа!")

    parts = message.text.split()
    if len(parts) < 2:
        return await message.answer("⚠️ Используй: /del_message <id>")

    try:
        msg_id = int(parts[1])
    except ValueError:
        return await message.answer("❌ ID должно быть числом!")

    deleted = await database.delete_message(msg_id)
    if deleted:
        await message.answer(f"🗑 Сообщение {msg_id} удалено.")
    else:
        await message.answer(f"❌ Сообщение {msg_id} не найдено.")


@admin_router.message(Command("del_messages"))
async def delete_messages(message: types.Message):
    if not await database.is_admin(message.from_user.id):
        return await message.answer("❌ Нет доступа!")

    parts = message.text.split()
    if len(parts) != 4 or parts[2].upper() != "BETWEEN":
        return await message.answer("⚠️ Используй: /del_messages <от> BETWEEN <до>")

    try:
        start_id = int(parts[1])
        end_id = int(parts[3])
    except ValueError:
        return await message.answer("❌ ID должны быть числами!")

    deleted = await database.delete_messages_range(start_id, end_id)
    await message.answer(f"🗑 Удалено {deleted} сообщений (ID {start_id}–{end_id}).")
