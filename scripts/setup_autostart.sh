#!/bin/bash

# Скрипт для настройки автозапуска телеграм бота через systemd

echo "⏰ Настройка автозапуска телеграм бота..."
echo "=========================================="

# Получаем текущую директорию проекта
PROJECT_DIR=$(pwd)
USER=$(whoami)

# Проверяем, что мы находимся в корне проекта
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Ошибка: скрипт должен запускаться из корневой директории проекта"
    echo "📝 Перейдите в директорию, где находится файл docker-compose.yml"
    exit 1
fi

# Проверяем наличие docker-compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Ошибка: docker-compose не установлен"
    echo "📝 Установите docker-compose перед настройкой автозапуска"
    exit 1
fi

# Получаем полный путь к docker-compose
DOCKER_COMPOSE_PATH=$(which docker-compose)

# Создаем systemd сервис
echo "📝 Создаем systemd сервис..."

sudo tee /etc/systemd/system/telebot.service > /dev/null << EOF
[Unit]
Description=Telegram Bot
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=${PROJECT_DIR}
ExecStart=${DOCKER_COMPOSE_PATH} up -d
ExecStop=${DOCKER_COMPOSE_PATH} down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

# Перезагружаем systemd
echo "🔄 Перезагружаем systemd..."
sudo systemctl daemon-reload

# Включаем автозапуск
echo "✅ Включаем автозапуск..."
sudo systemctl enable telebot.service

# Запускаем сервис
echo "▶️ Запускаем сервис..."
sudo systemctl start telebot.service

# Проверяем статус
echo "📊 Проверяем статус сервиса..."
sudo systemctl status telebot.service

echo ""
echo "🎉 Настройка автозапуска завершена!"
echo "📝 Команды управления сервисом:"
echo "   - Проверка статуса: sudo systemctl status telebot.service"
echo "   - Запуск: sudo systemctl start telebot.service"
echo "   - Остановка: sudo systemctl stop telebot.service"
echo "   - Перезапуск: sudo systemctl restart telebot.service"
echo "   - Отключение автозапуска: sudo systemctl disable telebot.service"