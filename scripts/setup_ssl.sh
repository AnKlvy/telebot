#!/bin/bash

# Скрипт для настройки SSL сертификата через Let's Encrypt

DOMAIN=""
EMAIL=""

echo "🔒 Настройка SSL сертификата для телеграм бота"
echo "=============================================="

# Запрашиваем домен
read -p "Введите ваш домен (например: bot.example.com): " DOMAIN
if [ -z "$DOMAIN" ]; then
    echo "❌ Домен не указан"
    exit 1
fi

# Запрашиваем email
read -p "Введите ваш email для Let's Encrypt: " EMAIL
if [ -z "$EMAIL" ]; then
    echo "❌ Email не указан"
    exit 1
fi

echo "📋 Домен: $DOMAIN"
echo "📧 Email: $EMAIL"
echo ""

# Проверяем наличие certbot
if ! command -v certbot &> /dev/null; then
    echo "📦 Certbot не найден, устанавливаем..."

    # Определяем дистрибутив
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
    fi

    # Для Kali Linux используем snap
    if [[ "$OS" == *"Kali"* ]]; then
        echo "🐉 Kali Linux обнаружен, устанавливаем через snap..."

        # Устанавливаем snapd если нет
        if ! command -v snap &> /dev/null; then
            sudo apt update
            sudo apt install -y snapd
            sudo systemctl enable --now snapd
            sudo systemctl start snapd
            sleep 5
        fi

        # Устанавливаем certbot через snap
        sudo snap install --classic certbot
        sudo ln -sf /snap/bin/certbot /usr/bin/certbot
    else
        # Для других дистрибутивов
        sudo apt update
        sudo apt install -y certbot
    fi

    # Проверяем установку
    if ! command -v certbot &> /dev/null; then
        echo "❌ Не удалось установить certbot"
        echo "💡 Установите вручную и запустите скрипт снова"
        exit 1
    fi

    echo "✅ Certbot установлен"
fi

# Создаем директорию для SSL
sudo mkdir -p nginx/ssl

# Получаем сертификат
echo "🔐 Получаем SSL сертификат..."
sudo certbot certonly \
    --standalone \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN

if [ $? -eq 0 ]; then
    echo "✅ SSL сертификат получен успешно"
    
    # Копируем сертификаты в папку nginx
    sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem nginx/ssl/
    sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem nginx/ssl/
    
    # Устанавливаем права доступа
    sudo chmod 644 nginx/ssl/fullchain.pem
    sudo chmod 600 nginx/ssl/privkey.pem
    
    # Обновляем конфигурацию nginx
    sed -i "s/your-domain.com/$DOMAIN/g" nginx/nginx.conf

    # Обновляем домен в файле переменных окружения
    sudo sed -i "s/your-domain.com/$DOMAIN/g" /etc/telebot/env

    echo "✅ Конфигурация nginx и переменные окружения обновлены"
    echo ""
    echo "🎯 Следующие шаги:"
    echo "1. ✅ WEBHOOK_HOST автоматически обновлен на: https://$DOMAIN"
    echo ""
    echo "2. Перезапустите контейнеры:"
    echo "   docker-compose down && docker-compose up -d"
    echo ""
    echo "3. Проверьте webhook:"
    echo "   curl -X POST https://$DOMAIN/webhook"
    
    # Настраиваем автообновление сертификата
    echo "⏰ Настраиваем автообновление сертификата..."
    (crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet && docker-compose restart nginx") | crontab -
    
    echo "✅ Автообновление сертификата настроено"
else
    echo "❌ Ошибка получения SSL сертификата"
    echo "💡 Убедитесь что:"
    echo "   - Домен $DOMAIN указывает на этот сервер"
    echo "   - Порт 80 открыт и доступен"
    echo "   - Нет других веб-серверов на порту 80"
    exit 1
fi
