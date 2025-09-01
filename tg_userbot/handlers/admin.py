from telethon import events
import database

def setup(client, pool):
    # Отслеживаем ключевые слова
    @client.on(events.NewMessage())
    async def track_keywords(event):
        if not event.text:
            return

        sender = await event.get_sender()
        user_id = sender.id if sender else None
        username = sender.username if sender and sender.username else "Нет username"

        if sender and getattr(sender, "bot", False):
            return

        chat_title = event.chat.title if event.chat and getattr(event.chat, "title", None) else "Личный чат"
        chat_username = event.chat.username if event.chat and getattr(event.chat, "username", None) else None

        keywords = await database.get_keywords(pool)
        text = event.text.lower()
        found = [word for word in keywords if word in text]

        if found:
            # Проверка на дубликат
            exists = await database.message_exists(pool, event.chat_id, event.id)
            if not exists:
                await database.save_message(
                    pool,
                    user_id=user_id,
                    username=username,
                    chat_title=chat_title,
                    chat_username=chat_username,
                    message=event.text,
                    message_id=event.id,
                    chat_id=event.chat_id
                )

    # ------------------ Команды ------------------

    @client.on(events.NewMessage(pattern='/iamadmin'))
    async def iam_admin(event):
        sender = await event.get_sender()
        sender_id = sender.id
        username = sender.username or "Нет username"

    # Если уже админ
        if await database.is_admin(pool, sender_id):
            return await event.reply("✅ Вы уже админ.")

    # Попытка обновить запись username-only (bind_admin_id)
        updated = await database.bind_admin_id(pool, sender_id, username)
        if updated:
            return await event.reply("🎉 Вы назначены админом!")

    # Иначе создаём нового админа
        await database.add_admin(pool, sender_id, username)
        await event.reply("🎉 Вы назначены админом!")


    @client.on(events.NewMessage(pattern='/start'))
    async def start(event):
        sender_id = event.sender_id
        if await database.is_admin(pool, sender_id):
            # админ → показываем команды админа
            text = (
                "👑 Админ-панель:\n\n"
                "/add <слово> — добавить ключ\n"
                "/del <слово> — удалить ключ\n"
                "/list — список ключей\n"
                "/add_admin <id или @username> — добавить админа\n"
                "/del_admin <id> — удалить админа\n"
                "/admins — список админов"
            )
        else:
            # обычный пользователь
            text = (
                " У тебя с головой все нормально?\n"
                "Болван, я не бот!"
            )

        await event.respond(text)

    @client.on(events.NewMessage(pattern='/add '))
    async def add_key(event):
        sender_id = event.sender_id
        if not await database.is_admin(pool, sender_id):
            return

        parts = event.text.split(maxsplit=1)
        if len(parts) < 2:
            return await event.reply("⚠️ Напишите слово после /add")
        await database.add_keyword(pool, parts[1])
        await event.reply(f"✅ Слово '{parts[1]}' добавлено.")

    @client.on(events.NewMessage(pattern='/del '))
    async def del_key(event):
        sender_id = event.sender_id
        if not await database.is_admin(pool, sender_id):
            return
        parts = event.text.split(maxsplit=1)
        if len(parts) < 2:
            return await event.reply('⚠️ Используй: /del <слово>')
        
        word = parts[1]
        deleted =await database.delete_keyword(pool, word)
        if deleted:
            await event.reply(f"🗑 Слово '{word}' удалено.")
        else:
            await event.reply(f"❌ Слово '{word}' не найдено.")

    @client.on(events.NewMessage(pattern='/list'))
    async def list_keys(event):
        sender_id = event.sender_id
        if not await database.is_admin(pool, sender_id):
            return

        keys = await database.get_keywords(pool)
        if not keys:
            return await event.reply("⚠️ Нет ключевых слов.")
        await event.reply("📌 Ключевые слова:\n" + "\n".join(keys))

    @client.on(events.NewMessage(pattern='/done '))
    async def mark_done(event):
        sender_id = event.sender_id
        if not await database.is_admin(pool, sender_id):
            return

        parts = event.text.split()
        if len(parts) < 2:
            return await event.reply("⚠️ Используй: /done <id сообщения>")
        msg_id = int(parts[1])
        await database.update_message_status(pool, msg_id, "Отвеченные")
        await event.reply(f"✅ Сообщение {msg_id} помечено как Отвеченное")

    @client.on(events.NewMessage(pattern='/add_admin '))
    async def add_new_admin(event):
        sender_id = event.sender_id
        if not await database.is_admin(pool, sender_id):
            return await event.reply("❌ Нет доступа!")

        parts = event.text.split()
        if len(parts) < 2:
            return await event.reply("⚠️ Используй: /add_admin <user_id или @username>")
        target = parts[1]
        if target.startswith("@"):
            await database.add_admin(pool, 0, target)
            await event.reply(f"✅ Пользователь {target} добавлен как админ (надо написать боту).")
        else:
            await database.add_admin(pool, int(target), "ID-only")
            await event.reply(f"✅ ID {target} добавлен как админ.")

    @client.on(events.NewMessage(pattern='/del_admin '))
    async def del_admin(event):
        sender_id = event.sender_id
        if not await database.is_admin(pool, sender_id):
            return await event.reply("❌ Нет доступа!")

        parts = event.text.split()
        if len(parts) < 2:
            return await event.reply("⚠️ Используй: /del_admin <user_id>")
        target_id = int(parts[1])
        await database.remove_admin(pool, target_id)
        await event.reply(f"🗑 Админ {target_id} удалён.")

    @client.on(events.NewMessage(pattern='/admins'))
    async def list_admins(event):
        sender_id = event.sender_id
        if not await database.is_admin(pool, sender_id):
            return
        admins = await database.get_admins(pool)
        if not admins:
            return await event.reply("⚠️ Админов пока нет.")
        text = "👑 Список админов:\n\n"
        for a in admins:
            text += f"ID: {a['user_id']} | {a['username']}\n"
        await event.reply(text)
