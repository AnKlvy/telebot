#!/bin/sh

# Проверяем, что переменная REDIS_PASSWORD установлена
if [ -z "$REDIS_PASSWORD" ]; then
    echo "❌ REDIS_PASSWORD не установлен!"
    exit 1
fi

echo "🔧 Настройка Redis с паролем..."

# Создаем конфигурационный файл из шаблона
envsubst '${REDIS_PASSWORD}' < /etc/redis/redis.conf.template > /etc/redis/redis.conf

echo "✅ Конфигурация Redis создана"
echo "🚀 Запуск Redis сервера..."

# Запускаем Redis с нашей конфигурацией
exec redis-server /etc/redis/redis.conf
