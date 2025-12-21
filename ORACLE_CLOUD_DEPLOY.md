# ☁️ Развертывание бота на Oracle Cloud (БЕСПЛАТНО НАВСЕГДА)

Oracle Cloud предлагает бесплатный VPS навсегда - идеально для бота!

## 📋 Подготовка

1. ✅ Аккаунт на [Oracle Cloud](https://www.oracle.com/cloud/free/) (требует кредитную карту, но не списывает деньги)
2. ✅ Токен бота от [@BotFather](https://t.me/BotFather)
3. ✅ Код проекта в GitHub репозитории

## 🚀 Пошаговая инструкция

### Шаг 1: Регистрация на Oracle Cloud

1. Перейдите на [oracle.com/cloud/free](https://www.oracle.com/cloud/free/)
2. Нажмите **"Start for free"**
3. Заполните форму (требуется кредитная карта, но деньги не списываются)
4. Подтвердите email

### Шаг 2: Создание VM Instance

1. В Dashboard найдите **"Compute"** → **"Instances"**
2. Нажмите **"Create Instance"**
3. Настройте:
   - **Name:** `telegram-bot`
   - **Image:** Oracle Linux или Ubuntu (рекомендуется Ubuntu)
   - **Shape:** Always Free Eligible (AMD или ARM)
   - **SSH Keys:** Создайте новую пару ключей или загрузите существующую
4. Нажмите **"Create"**

### Шаг 3: Подключение к серверу

**Windows (через PowerShell):**
```powershell
ssh -i путь_к_ключу opc@ваш_IP_адрес
```

**Или используйте PuTTY** для Windows

### Шаг 4: Установка зависимостей

На сервере выполните:

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Python
sudo apt install python3 python3-pip git -y

# Клонирование репозитория
cd ~
git clone https://github.com/shelpakovzhenya-art/telegram-bot.git
cd telegram-bot

# Установка зависимостей
pip3 install -r requirements.txt
```

### Шаг 5: Настройка переменных окружения

```bash
cd ~/telegram-bot
nano .env
```

Добавьте:
```
BOT_TOKEN=8449446845:AAHQLxHSFvR6NeGSOzEto2HoczJbeJFhv0E
```

Сохраните: `Ctrl+O`, `Enter`, `Ctrl+X`

### Шаг 6: Создание systemd service (для автозапуска)

```bash
sudo nano /etc/systemd/system/telegram-bot.service
```

Добавьте:
```ini
[Unit]
Description=Telegram Bot
After=network.target

[Service]
Type=simple
User=opc
WorkingDirectory=/home/opc/telegram-bot
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/python3 -m app.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Сохраните и выполните:
```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
```

### Шаг 7: Проверка работы

```bash
sudo systemctl status telegram-bot
```

Должен показать `active (running)`

### Шаг 8: Просмотр логов

```bash
sudo journalctl -u telegram-bot -f
```

## 💰 Бесплатный план Oracle Cloud

**Что включено НАВСЕГДА:**
- ✅ 2 VM instances (AMD или ARM)
- ✅ 200GB storage
- ✅ 10TB outbound data transfer
- ✅ Работает 24/7

## ✅ Готово!

Бот работает на Oracle Cloud 24/7 бесплатно навсегда! 🎉

---

## 🔧 Настройка Firewall

Если нужно открыть порты (для бота не требуется, но на всякий случай):

```bash
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --reload
```


