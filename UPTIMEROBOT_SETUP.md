# 🤖 Настройка UptimeRobot для Replit (чтобы бот работал 24/7)

UptimeRobot будет "будить" ваш Replit каждые 5 минут, чтобы он не выключался.

## 📋 Подготовка

1. ✅ Replit с запущенным ботом
2. ✅ Публичный URL вашего Repl (Replit дает его автоматически)

## 🚀 Пошаговая инструкция

### Шаг 1: Регистрация на UptimeRobot

1. Перейдите на [uptimerobot.com](https://uptimerobot.com)
2. Нажмите **"Sign Up"** (бесплатная регистрация)
3. Заполните форму:
   - Email
   - Пароль
   - Имя пользователя
4. Подтвердите email (проверьте почту)

### Шаг 2: Получение URL вашего Repl

**Вариант А: Если у вас есть веб-сервер в Repl**

1. В Replit найдите публичный URL (обычно в правом верхнем углу)
2. URL выглядит так: `https://ваш-реп.ваш-юзер.repl.co`
3. Скопируйте этот URL

**Вариант Б: Если нет веб-сервера (нужно добавить)**

Добавьте простой веб-сервер в `app/main.py` или создайте отдельный файл `keep_alive.py`:

```python
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()
```

И измените `app/main.py`:

```python
"""Main entry point for the bot."""
import asyncio
import logging
import sys

from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession

from app.bot.dispatcher import create_bot, setup_dispatcher
from app.core.settings import Settings
from app.db.base import init_db

# Keep-alive для Replit
try:
    from keep_alive import keep_alive
    keep_alive()
except ImportError:
    pass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)

# ... остальной код без изменений
```

После этого Replit даст вам публичный URL.

### Шаг 3: Создание монитора в UptimeRobot

1. В Dashboard UptimeRobot нажмите **"Add New Monitor"** (или **"+"**)
2. Заполните форму:

**Monitor Type:**
- Выберите **"HTTP(s)"**

**Friendly Name:**
- Введите: `Telegram Bot Replit`

**URL (or IP):**
- Вставьте URL вашего Repl (например: `https://telegram-bot.ваш-юзер.repl.co`)
- Или просто: `https://ваш-реп.ваш-юзер.repl.co`

**Monitoring Interval:**
- Выберите **"Every 5 minutes"** (бесплатный план позволяет до 5 минут)

**Alert Contacts:**
- Выберите способ уведомлений (Email, Telegram, и т.д.)
- Или оставьте только Email

3. Нажмите **"Create Monitor"**

### Шаг 4: Проверка работы

1. UptimeRobot начнет проверять ваш Repl каждые 5 минут
2. В Dashboard вы увидите статус:
   - 🟢 **"Up"** - Repl работает
   - 🔴 **"Down"** - Repl не отвечает

3. Если статус "Down", UptimeRobot попытается "разбудить" Repl

### Шаг 5: Настройка уведомлений (опционально)

1. В Dashboard перейдите в **"My Settings"** → **"Alert Contacts"**
2. Добавьте способы уведомлений:
   - Email (уже есть)
   - Telegram (можно добавить бота @UptimeRobotBot)
   - SMS (платно)

## 💰 Бесплатный план UptimeRobot

**Что включено:**
- ✅ 50 мониторов
- ✅ Проверка каждые 5 минут
- ✅ Email уведомления
- ✅ История до 2 месяцев

**Достаточно для одного Repl!**

## ✅ Готово!

Теперь ваш Replit будет "просыпаться" каждые 5 минут, и бот будет работать 24/7! 🎉

---

## 🔧 Альтернатива: Keep-Alive скрипт в самом Replit

Если не хотите использовать UptimeRobot, можно добавить keep-alive прямо в код:

1. Создайте файл `keep_alive.py` в корне проекта:

```python
from flask import Flask
from threading import Thread
import requests
import time

app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()
    
    # Периодически пингуем себя
    while True:
        try:
            requests.get('https://ваш-реп.ваш-юзер.repl.co')
        except:
            pass
        time.sleep(300)  # Каждые 5 минут
```

2. Импортируйте в `app/main.py`:

```python
from keep_alive import keep_alive
keep_alive()
```

Но UptimeRobot надежнее! 👍

