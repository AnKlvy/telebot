#!/bin/bash

# Скрипт для деплоя телеграм бота на Beget

echo "🚀 Начинаем деплой телеграм бота..."

# Проверяем наличие Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Установите Docker и попробуйте снова."
    exit 1
fi

# Проверяем наличие Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не установлен. Установите Docker Compose и попробуйте снова."
    exit 1
fi

# Проверяем наличие файла с переменными окружения
if [ ! -f /etc/telebot/env ]; then
    echo "❌ Файл /etc/telebot/env не найден."
    echo "📝 Запустите: chmod +x scripts/setup_env.sh && sudo ./scripts/setup_env.sh"
    echo "📝 Затем отредактируйте: sudo nano /etc/telebot/env"
    exit 1
fi

# Останавливаем существующие контейнеры
echo "🛑 Останавливаем существующие контейнеры..."
docker-compose down

# Удаляем старые образы
echo "🗑️ Удаляем старые образы..."
docker-compose down --rmi all

# Собираем новые образы
echo "🔨 Собираем новые образы..."
docker-compose build --no-cache

# Запускаем контейнеры
echo "▶️ Запускаем контейнеры..."
docker-compose up -d

# Проверяем статус
echo "📊 Проверяем статус контейнеров..."
docker-compose ps

# Показываем логи
echo "📝 Показываем логи бота..."
docker-compose logs -f bot
