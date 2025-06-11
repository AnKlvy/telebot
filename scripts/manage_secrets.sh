#!/bin/bash

# Скрипт для управления секретами телеграм бота

SECRETS_DIR="/etc/edu_telebot/secrets"
ENV_FILE="/etc/edu_telebot/env"

create_secrets_dir() {
    echo "📁 Создание директории для секретов..."
    sudo mkdir -p $SECRETS_DIR
    sudo chmod 700 $SECRETS_DIR
    sudo chown root:root $SECRETS_DIR
}

setup_secrets() {
    echo "🔐 Настройка секретов..."
    
    # Запрашиваем токен бота
    read -s -p "Введите токен бота: " BOT_TOKEN
    echo
    echo "$BOT_TOKEN" | sudo tee $SECRETS_DIR/bot_token.txt > /dev/null
    
    # Запрашиваем пароль базы данных
    read -s -p "Введите пароль для PostgreSQL: " POSTGRES_PASSWORD
    echo
    echo "$POSTGRES_PASSWORD" | sudo tee $SECRETS_DIR/postgres_password.txt > /dev/null
    
    # Устанавливаем права доступа
    sudo chmod 600 $SECRETS_DIR/*
    sudo chown root:root $SECRETS_DIR/*
    
    echo "✅ Секреты сохранены в $SECRETS_DIR"
}

create_env_file() {
    echo "📝 Создание файла переменных окружения..."
    
    sudo tee $ENV_FILE > /dev/null << EOF
# Telegram Bot Configuration
POSTGRES_DB=telebot
POSTGRES_USER=telebot_user
ENVIRONMENT=production
EOF
    
    sudo chmod 600 $ENV_FILE
    sudo chown root:root $ENV_FILE
    
    echo "✅ Файл окружения создан: $ENV_FILE"
}

show_status() {
    echo "📊 Статус секретов:"
    
    if [ -f $SECRETS_DIR/bot_token.txt ]; then
        echo "✅ Токен бота: настроен"
    else
        echo "❌ Токен бота: не настроен"
    fi
    
    if [ -f $SECRETS_DIR/postgres_password.txt ]; then
        echo "✅ Пароль PostgreSQL: настроен"
    else
        echo "❌ Пароль PostgreSQL: не настроен"
    fi
    
    if [ -f $ENV_FILE ]; then
        echo "✅ Файл окружения: создан"
    else
        echo "❌ Файл окружения: не создан"
    fi
}

case "$1" in
    "setup")
        create_secrets_dir
        setup_secrets
        create_env_file
        ;;
    "status")
        show_status
        ;;
    "clean")
        echo "🗑️ Удаление всех секретов..."
        sudo rm -rf $SECRETS_DIR
        sudo rm -f $ENV_FILE
        echo "✅ Секреты удалены"
        ;;
    *)
        echo "Использование: $0 {setup|status|clean}"
        echo "  setup  - Настройка секретов"
        echo "  status - Проверка статуса"
        echo "  clean  - Удаление секретов"
        exit 1
        ;;
esac
