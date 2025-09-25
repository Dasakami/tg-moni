

---

# tg-moni

**tg-moni** — Telegram-мониторинг с двумя ботами:

1. **Bot (BotFather)** — показывает уведомления о событиях и ключевых словах, найденных userbot.
2. **Userbot (Telethon)** — мониторит группы, ищет ключевые слова и передаёт найденное BotFather боту.

---

## 📦 Быстрый старт с Docker

### 1. Клонируем репозиторий

```bash
git clone https://github.com/Dasakami/tg-moni.git
cd tg-moni
```

### 2. Настраиваем `.env`

Скопируйте `.env.example` в `.env` и заполните свои данные:

```env
# PostgreSQL
DB_USER=postgres_or_you_user
DB_PASS=pass
DB_NAME=botdb_or_you_db_name
DB_HOST=postgres_or_localhost

# BotFather Bot
TOKEN=

# Userbot (Telethon)
API_ID=
API_HASH=
SESSION=/app/session.session
```

* `TOKEN` — токен BotFather бота.
* `API_ID` и `API_HASH` — для Telethon (my.telegram.org).
* `SESSION` — путь к сессии Userbot.

---

### 3. Запуск Docker

Собираем и запускаем всё сразу:

```bash
docker-compose up -d --build
```

* Контейнер `postgres` — база данных.
* Контейнер `bot` — BotFather бот.
* Контейнер `userbot` — Userbot, который мониторит группы.

Проверяем логи, чтобы убедиться, что всё запущено:

```bash
docker-compose logs -f bot
docker-compose logs -f userbot
```

---

### 4. Остановка и удаление контейнеров

```bash
docker-compose down
```

---

## 🐍 Без Docker (для локальной разработки)

1. Установите зависимости:

```bash
pip install -r requirements.txt
```

2. Запустите бота:

```bash
python bot-moni/bot.py
```

3. Запустите userbot:

```bash
python tg_userbot/userbot.py
```

---

## ⚙️ Настройка ключевых слов (Userbot)

* В `.env` задаёте список ключевых слов или отдельный файл.
* Userbot будет искать эти слова в группах.
* Найденное отправляется BotFather боту, который уведомляет вас.

---

## 🚀 Сценарий работы

1. Userbot подключается к Telegram, мониторит группы и ищет ключевые слова.
2. BotFather бот получает информацию от Userbot и показывает уведомления в личном чате или группе.

---

## 📂 Структура проекта

```
tg-moni/
│
├─ bot-moni/         # BotFather бот
├─ tg_userbot/       # Userbot на Telethon
├─ docker-compose.yml
├─ .env.example
├─ requirements.txt
└─ README.md
```

---