#!/bin/bash

# Скрипт для разработки с ngrok
# Используется только для локального тестирования

echo "🚀 Запуск бота в режиме разработки с ngrok..."

# Проверить, установлен ли ngrok
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok не установлен. Установите его сначала."
    exit 1
fi

# Проверить, запущен ли Docker
if ! docker-compose ps | grep -q "Up"; then
    echo "🐳 Запуск Docker контейнеров..."
    docker-compose up -d
    sleep 10
fi

# Запустить ngrok в фоне
echo "🌐 Запуск ngrok туннеля..."
ngrok http https://localhost:443 > /dev/null 2>&1 &
NGROK_PID=$!

# Подождать запуска ngrok
sleep 5

# Получить ngrok URL
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o '"public_url":"https://[^"]*' | cut -d'"' -f4)

if [ -z "$NGROK_URL" ]; then
    echo "❌ Не удалось получить ngrok URL"
    kill $NGROK_PID 2>/dev/null
    exit 1
fi

echo "✅ ngrok URL: $NGROK_URL"

# Установить webhook
echo "🔗 Установка webhook..."
WEBHOOK_RESPONSE=$(curl -s -F "url=$NGROK_URL/webhook" "https://api.telegram.org/bot$BOT_TOKEN/setWebhook")

if echo "$WEBHOOK_RESPONSE" | grep -q '"ok":true'; then
    echo "✅ Webhook установлен успешно!"
    echo "🎉 Бот готов к работе!"
    echo ""
    echo "📱 Напишите боту /start в Telegram"
    echo "📊 Логи: docker-compose logs -f bot"
    echo "🌐 ngrok интерфейс: http://localhost:4040"
    echo ""
    echo "⚠️  Для остановки нажмите Ctrl+C"
    
    # Ждать сигнала остановки
    trap "echo '🛑 Остановка ngrok...'; kill $NGROK_PID 2>/dev/null; exit 0" INT
    wait $NGROK_PID
else
    echo "❌ Ошибка установки webhook: $WEBHOOK_RESPONSE"
    kill $NGROK_PID 2>/dev/null
    exit 1
fi
