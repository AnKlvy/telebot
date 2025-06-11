#!/bin/bash

# Скрипт восстановления из бэкапа
echo "🔄 Восстановление базы данных из бэкапа"

# Проверяем аргументы
if [ $# -eq 0 ]; then
    echo "❌ Укажите файл бэкапа!"
    echo "Использование: $0 backup_file.sql.gz"
    echo ""
    echo "Доступные бэкапы:"
    ls -la ~/backups/telebot/backup_*.sql.gz 2>/dev/null || echo "Бэкапы не найдены"
    exit 1
fi

BACKUP_FILE=$1

# Проверяем существование файла
if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Файл не найден: $BACKUP_FILE"
    exit 1
fi

echo "📁 Восстанавливаем из: $BACKUP_FILE"

# Ищем директорию проекта (где есть docker-compose.yml)
PROJECT_DIR=""
if [ -f "docker-compose.yml" ]; then
    PROJECT_DIR=$(pwd)
elif [ -f "../docker-compose.yml" ]; then
    PROJECT_DIR=$(cd .. && pwd)
elif [ -f "~/telebot/docker-compose.yml" ]; then
    PROJECT_DIR="$HOME/telebot"
else
    echo "❌ Не найден docker-compose.yml"
    echo "Запустите скрипт из директории проекта"
    exit 1
fi

echo "📍 Используем проект: $PROJECT_DIR"
cd "$PROJECT_DIR"

# Проверяем, что контейнер запущен
if ! docker-compose ps postgres | grep -q "Up"; then
    echo "❌ Контейнер PostgreSQL не запущен!"
    echo "Запустите: docker-compose up -d postgres"
    exit 1
fi

# Предупреждение
echo "⚠️  ВНИМАНИЕ: Это удалит все текущие данные!"
read -p "Продолжить? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Отменено"
    exit 1
fi

# Восстанавливаем
echo "🔄 Восстановление..."

if [[ $BACKUP_FILE == *.gz ]]; then
    # Если файл сжат
    gunzip -c "$BACKUP_FILE" | docker-compose exec -T postgres psql -U telebot_user telebot
else
    # Если файл не сжат
    docker-compose exec -T postgres psql -U telebot_user telebot < "$BACKUP_FILE"
fi

if [ $? -eq 0 ]; then
    echo "✅ База данных восстановлена успешно!"
else
    echo "❌ Ошибка при восстановлении!"
    exit 1
fi
