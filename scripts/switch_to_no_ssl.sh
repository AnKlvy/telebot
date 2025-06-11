#!/bin/bash

# Скрипт для переключения на конфигурацию без SSL

echo "🔄 Переключаемся на конфигурацию без SSL..."

# Останавливаем контейнеры
echo "🛑 Останавливаем контейнеры..."
sudo docker-compose down

# Создаем резервную копию текущей конфигурации
if [ -f "nginx/nginx.conf" ]; then
    echo "💾 Создаем резервную копию nginx.conf..."
    sudo cp nginx/nginx.conf nginx/nginx.conf.backup
fi

# Копируем конфигурацию без SSL
echo "📝 Устанавливаем конфигурацию без SSL..."
sudo cp nginx/nginx-no-ssl.conf nginx/nginx.conf

# Обновляем переменные окружения для HTTP режима
echo "⚙️ Обновляем переменные окружения..."
sudo sed -i 's/WEBHOOK_MODE=true/WEBHOOK_MODE=false/' /etc/edu_telebot/env
sudo sed -i 's/https:/http:/' /etc/edu_telebot/env

echo "✅ Конфигурация обновлена"
echo ""
echo "🚀 Запускаем контейнеры..."
sudo docker-compose up -d

echo ""
echo "✅ Готово! Бот работает в HTTP режиме"
echo "🌐 Webhook URL: http://n70741z2.beget.tech/webhook"
echo ""
echo "💡 Для включения SSL позже запустите:"
echo "   ./scripts/setup_ssl.sh"
echo "   ./scripts/switch_to_ssl.sh"
