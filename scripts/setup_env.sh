#!/bin/bash

# Скрипт для безопасной настройки переменных окружения на сервере

echo "🔐 Настройка переменных окружения для телеграм бота..."

# Создаем пользователя для бота (если не существует)
if ! id "telebot" &>/dev/null; then
    sudo useradd --system --uid 1001 --no-create-home --shell /bin/false telebot
    echo "✅ Создан системный пользователь 'telebot' с UID 1001"
fi

# Создаем защищенную директорию для конфигов
sudo mkdir -p /etc/telebot
sudo chmod 750 /etc/telebot  # rwx для root, r-x для группы telebot
sudo chown root:telebot /etc/telebot

# Создаем файл с переменными окружения
sudo tee /etc/telebot/env > /dev/null << EOF
# Telegram Bot Configuration
BOT_TOKEN=your_bot_token_here

# Настройки PostgreSQL
POSTGRES_DB=telebot
POSTGRES_USER=telebot_user
POSTGRES_PASSWORD=your_secure_password_here

# DATABASE_URL формируется автоматически в коде из переменных выше

# Настройки окружения
ENVIRONMENT=production

# Домен для nginx и webhook
DOMAIN=your-domain.com

# Webhook настройки (для максимальной скорости)
WEBHOOK_MODE=true
WEBHOOK_HOST=https://your-domain.com
WEBHOOK_PATH=/webhook
WEB_SERVER_HOST=0.0.0.0
WEB_SERVER_PORT=8000
EOF

# Устанавливаем безопасные права доступа
sudo chmod 640 /etc/telebot/env  # rw- для root, r-- для группы telebot
sudo chown root:telebot /etc/telebot/env

echo "✅ Файл конфигурации создан: /etc/telebot/env"
echo "📝 Отредактируйте файл и добавьте реальные значения:"
echo "sudo nano /etc/telebot/env"
