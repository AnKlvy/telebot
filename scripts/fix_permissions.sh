#!/bin/bash

# Скрипт для исправления прав доступа к логам

echo "🔐 Исправляем права доступа к директории логов..."

# Создаем директорию логов если не существует
mkdir -p logs
mkdir -p logs/nginx

# Устанавливаем полные права для директории логов
chmod -R 777 logs

# Создаем файл лога для сегодняшней даты
TODAY=$(date +%Y-%m-%d)
touch logs/bot_${TODAY}.log
chmod 666 logs/bot_${TODAY}.log

echo "✅ Права доступа исправлены"
echo "📁 Директория logs: $(ls -la logs/)"

# Если запущены контейнеры, перезапускаем бота
if docker-compose ps | grep -q "telebot_app"; then
    echo "🔄 Перезапускаем контейнер бота..."
    docker-compose restart bot
fi

echo "✅ Готово!"
