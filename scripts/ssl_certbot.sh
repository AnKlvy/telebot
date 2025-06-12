#!/bin/bash

# Альтернативный SSL менеджер с certbot

echo "🔐 SSL менеджер с Certbot"
echo "========================"

# Загружаем переменные окружения
if [ -f "/etc/edu_telebot/env" ]; then
    source /etc/edu_telebot/env
    echo "✅ Переменные окружения загружены"
else
    echo "❌ Файл /etc/edu_telebot/env не найден"
    exit 1
fi

# Проверяем домен
if [ -z "$DOMAIN" ] || [ "$DOMAIN" = "your-domain.com" ]; then
    echo "❌ Домен не настроен: '$DOMAIN'"
    exit 1
fi

echo "🌐 Настраиваем SSL для домена: $DOMAIN"

# Создаем директории
mkdir -p nginx/ssl
mkdir -p logs/ssl

# Устанавливаем certbot
echo "📦 Устанавливаем certbot..."
sudo apt update -qq
sudo apt install -y certbot

# Проверяем установку
if ! command -v certbot &> /dev/null; then
    echo "❌ Не удалось установить certbot"
    exit 1
fi

echo "✅ Certbot установлен: $(certbot --version)"

# Останавливаем веб-сервисы
echo "🛑 Останавливаем веб-сервисы на порту 80..."
if command -v docker-compose &> /dev/null && [ -f "docker-compose.yml" ]; then
    docker-compose stop nginx 2>/dev/null || true
fi
sudo systemctl stop apache2 2>/dev/null || true
sudo systemctl stop nginx 2>/dev/null || true

# Получаем сертификат
echo "🔐 Получаем SSL сертификат через certbot..."
if sudo certbot certonly \
    --standalone \
    --non-interactive \
    --agree-tos \
    --email admin@$DOMAIN \
    --domains $DOMAIN; then
    
    echo "✅ SSL сертификат получен успешно"
    
    # Копируем сертификаты
    echo "📋 Копируем сертификаты в nginx/ssl/..."
    sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem nginx/ssl/fullchain.pem
    sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem nginx/ssl/privkey.pem
    
    # Устанавливаем права
    sudo chmod 644 nginx/ssl/fullchain.pem
    sudo chmod 600 nginx/ssl/privkey.pem
    sudo chown $USER:$USER nginx/ssl/*.pem
    
    echo "✅ SSL сертификаты установлены в nginx/ssl/"
    
    # Настраиваем автообновление
    echo "🔄 Настраиваем автообновление..."
    cat > /tmp/certbot_renewal.sh << EOF
#!/bin/bash
# Автообновление SSL сертификатов через certbot

cd $(pwd)
source /etc/edu_telebot/env

# Проверяем и обновляем сертификаты
if sudo certbot renew --quiet; then
    echo "\$(date): SSL сертификаты обновлены" >> logs/ssl/renewal.log
    
    # Копируем обновленные сертификаты
    sudo cp /etc/letsencrypt/live/\$DOMAIN/fullchain.pem nginx/ssl/fullchain.pem
    sudo cp /etc/letsencrypt/live/\$DOMAIN/privkey.pem nginx/ssl/privkey.pem
    sudo chmod 644 nginx/ssl/fullchain.pem
    sudo chmod 600 nginx/ssl/privkey.pem
    sudo chown $USER:$USER nginx/ssl/*.pem
    
    # Перезапускаем nginx
    if command -v docker-compose &> /dev/null; then
        docker-compose restart nginx
    fi
    
    echo "\$(date): Nginx перезапущен" >> logs/ssl/renewal.log
else
    echo "\$(date): Ошибка обновления SSL сертификатов" >> logs/ssl/renewal.log
fi
EOF
    
    sudo cp /tmp/certbot_renewal.sh /etc/cron.daily/certbot-renewal
    sudo chmod +x /etc/cron.daily/certbot-renewal
    rm /tmp/certbot_renewal.sh
    
    echo "✅ Автообновление настроено"
    
    # Проверяем сертификат
    echo "📋 Информация о сертификате:"
    openssl x509 -in nginx/ssl/fullchain.pem -text -noout | grep -E "(Subject:|Issuer:|Not After)"
    
    echo ""
    echo "🎉 SSL настройка завершена успешно!"
    echo "📁 Сертификаты: nginx/ssl/"
    echo "🔄 Автообновление: /etc/cron.daily/certbot-renewal"
    echo "📝 Логи: logs/ssl/renewal.log"
    
else
    echo "❌ Не удалось получить SSL сертификат"
    echo "💡 Возможные причины:"
    echo "   - Домен $DOMAIN не указывает на этот сервер"
    echo "   - Порт 80 заблокирован файрволом"
    echo "   - Проблемы с DNS записями"
    echo "   - Домен недоступен из интернета"
    echo ""
    echo "🔍 Проверьте DNS записи:"
    echo "   nslookup $DOMAIN"
    echo "   dig $DOMAIN"
    exit 1
fi
