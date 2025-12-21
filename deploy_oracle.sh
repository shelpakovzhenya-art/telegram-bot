#!/bin/bash
# Скрипт для автоматической установки бота на Oracle Cloud

echo "🚀 Установка Telegram бота на Oracle Cloud..."

# Обновление системы
echo "📦 Обновление системы..."
sudo apt update && sudo apt upgrade -y

# Установка Python и зависимостей
echo "🐍 Установка Python..."
sudo apt install python3 python3-pip python3-venv git -y

# Создание директории для бота
echo "📁 Создание директории..."
cd ~
if [ -d "telegram-bot" ]; then
    echo "Директория уже существует, обновляю..."
    cd telegram-bot
    git pull
else
    echo "Клонирование репозитория..."
    git clone https://github.com/shelpakovzhenya-art/telegram-bot.git
    cd telegram-bot
fi

# Создание виртуального окружения
echo "🔧 Создание виртуального окружения..."
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
echo "📚 Установка зависимостей..."
pip install --upgrade pip
pip install -r requirements.txt

# Создание директории для данных
echo "💾 Создание директории для данных..."
mkdir -p data

# Создание .env файла (если его нет)
if [ ! -f ".env" ]; then
    echo "📝 Создание .env файла..."
    cat > .env << EOF
BOT_TOKEN=8449446845:AAHQLxHSFvR6NeGSOzEto2HoczJbeJFhv0E
EOF
    echo "⚠️  ВАЖНО: Отредактируйте .env файл и добавьте ваш токен!"
    echo "Выполните: nano .env"
fi

# Создание systemd service
echo "⚙️  Создание systemd service..."
sudo tee /etc/systemd/system/telegram-bot.service > /dev/null << EOF
[Unit]
Description=Telegram Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$HOME/telegram-bot
Environment="PATH=$HOME/telegram-bot/venv/bin:/usr/bin:/usr/local/bin"
ExecStart=$HOME/telegram-bot/venv/bin/python -m app.main
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Перезагрузка systemd
echo "🔄 Перезагрузка systemd..."
sudo systemctl daemon-reload

# Включение автозапуска
echo "✅ Включение автозапуска..."
sudo systemctl enable telegram-bot

echo ""
echo "✅ Установка завершена!"
echo ""
echo "📝 Следующие шаги:"
echo "1. Отредактируйте .env файл: nano .env"
echo "2. Добавьте ваш BOT_TOKEN"
echo "3. Запустите бота: sudo systemctl start telegram-bot"
echo "4. Проверьте статус: sudo systemctl status telegram-bot"
echo "5. Просмотр логов: sudo journalctl -u telegram-bot -f"
echo ""


