#!/bin/bash

# Простая установка SSL через acme.sh (альтернатива certbot)

DOMAIN="n70741z2.beget.tech"
EMAIL="admin@${DOMAIN}"

echo "🔒 Настройка SSL через acme.sh (проще чем certbot!)"
echo "=================================================="
echo "🌐 Домен: $DOMAIN"
echo "📧 Email: $EMAIL"
echo ""

# Запрашиваем подтверждение
read -p "Продолжить? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Отменено"
    exit 1
fi

# Останавливаем nginx чтобы освободить порт 80
echo "🛑 Останавливаем nginx..."
sudo docker-compose stop nginx

# Устанавливаем acme.sh
echo "📦 Устанавливаем acme.sh..."
if [ ! -d "$HOME/.acme.sh" ]; then
    curl https://get.acme.sh | sh -s email=$EMAIL
    
    # Добавляем в PATH
    echo 'export PATH="$HOME/.acme.sh:$PATH"' >> ~/.bashrc
    source ~/.bashrc
else
    echo "✅ acme.sh уже установлен"
fi

# Создаем директорию для SSL
mkdir -p nginx/ssl

# Получаем сертификат
echo "🔐 Получаем SSL сертификат..."
$HOME/.acme.sh/acme.sh --issue -d $DOMAIN --standalone --httpport 80

if [ $? -eq 0 ]; then
    echo "✅ Сертификат получен успешно!"
    
    # Копируем сертификаты
    echo "📋 Копируем сертификаты..."
    $HOME/.acme.sh/acme.sh --install-cert -d $DOMAIN \
        --cert-file $(pwd)/nginx/ssl/cert.pem \
        --key-file $(pwd)/nginx/ssl/privkey.pem \
        --fullchain-file $(pwd)/nginx/ssl/fullchain.pem \
        --reloadcmd "cd $(pwd) && sudo docker-compose restart nginx"
    
    # Устанавливаем права
    chmod 644 nginx/ssl/fullchain.pem nginx/ssl/cert.pem
    chmod 600 nginx/ssl/privkey.pem
    
    # Обновляем конфигурацию nginx для SSL
    echo "⚙️ Обновляем конфигурацию nginx..."
    if [ ! -f "nginx/nginx.conf.backup" ]; then
        cp nginx/nginx.conf nginx/nginx.conf.backup
    fi
    
    # Создаем SSL конфигурацию
    cat > nginx/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    # Redirect HTTP to HTTPS
    server {
        listen 80;
        server_name n70741z2.beget.tech;
        return 301 https://$server_name$request_uri;
    }

    # HTTPS server
    server {
        listen 443 ssl;
        server_name n70741z2.beget.tech;

        # SSL configuration
        ssl_certificate /etc/ssl/fullchain.pem;
        ssl_certificate_key /etc/ssl/privkey.pem;
        
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        client_max_body_size 50M;

        # Webhook endpoint
        location /webhook {
            proxy_pass http://bot:8000/webhook;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto https;
            
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # Health check
        location /health {
            proxy_pass http://bot:8000/health;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto https;
        }

        location / {
            return 200 "Telegram Bot is running with SSL!\n";
            add_header Content-Type text/plain;
        }

        server_tokens off;
    }
}
EOF
    
    # Обновляем переменные окружения
    echo "📝 Обновляем переменные окружения..."
    sudo sed -i "s|WEBHOOK_HOST=.*|WEBHOOK_HOST=https://$DOMAIN|" /etc/telebot/env
    sudo sed -i "s|WEBHOOK_MODE=.*|WEBHOOK_MODE=true|" /etc/telebot/env
    
    # Запускаем nginx
    echo "▶️ Запускаем nginx с SSL..."
    sudo docker-compose up -d nginx
    
    # Автообновление через acme.sh (встроенное, без crontab)
    echo "⏰ acme.sh автоматически настроит обновление сертификатов..."
    echo "💡 acme.sh использует встроенный механизм обновления без crontab"
    
    echo ""
    echo "🎉 SSL настроен успешно!"
    echo "🌐 HTTPS URL: https://$DOMAIN/webhook"
    echo "🔄 Автообновление: встроено в acme.sh (без crontab)"
    echo ""
    echo "🧪 Тестируем:"
    echo "curl -I https://$DOMAIN/health"
    
else
    echo "❌ Ошибка получения сертификата"
    echo "💡 Убедитесь что:"
    echo "   - Домен $DOMAIN указывает на этот сервер"
    echo "   - Порт 80 открыт и доступен"
    echo "   - Нет других процессов на порту 80"
    
    # Возвращаем nginx
    sudo docker-compose up -d nginx
    exit 1
fi
