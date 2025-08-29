from telethon import events
import database

def setup(client, pool):

    @client.on(events.NewMessage())
    async def track_keywords(event):
        if event.sender.bot or not event.text:
            return
        keywords = await database.get_keywords(pool)
        text = event.text.lower()
        found = [word for word in keywords if word in text]
        if found:
            await database.save_message(
                pool,
                user_id=event.sender_id,
                username=event.sender.username or "Нет username",
                chat_title=event.chat.title or "Личный чат",
                chat_username=event.chat.username,
                message=event.text
            )
