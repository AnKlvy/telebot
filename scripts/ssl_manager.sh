#!/bin/bash

# Универсальный SSL менеджер для Beget VPS
# Всё в одном: проверка, создание, переключение SSL

# Универсальный SSL менеджер - всё встроено, дополнительные скрипты не нужны

echo "🔧 Универсальный SSL Менеджер"
echo "============================="

# Загружаем переменные окружения
if [ -f "/etc/edu_telebot/env" ]; then
    source /etc/edu_telebot/env
elif [ -f ".env" ]; then
    source .env
else
    echo "❌ Файл с переменными окружения не найден!"
    exit 1
fi

# Функция проверки системы
check_system() {
    echo "📊 Системная информация:"
    echo "ОС: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2 2>/dev/null || echo 'Неизвестно')"

    # Внешний IP
    EXTERNAL_IP=$(curl -s ifconfig.me 2>/dev/null || echo "Не удалось определить")
    echo "Внешний IP: $EXTERNAL_IP"

    # Проверяем порты
    echo ""
    echo "🔌 Порты:"
    if sudo netstat -tlnp | grep -q ":80 "; then
        echo "Порт 80: ✅ Занят"
    else
        echo "Порт 80: ⚪ Свободен"
    fi

    if sudo netstat -tlnp | grep -q ":443 "; then
        echo "Порт 443: ✅ Занят"
    else
        echo "Порт 443: ⚪ Свободен"
    fi
}

# Функция проверки домена
check_domain() {
    echo ""
    echo "🌍 Домен: ${DOMAIN:-не установлен}"

    if [ -n "$DOMAIN" ] && [ "$DOMAIN" != "localhost" ] && [ "$DOMAIN" != "your-domain.com" ]; then
        # Проверяем DNS
        DOMAIN_IP=$(dig +short $DOMAIN 2>/dev/null | tail -n1)
        if [ -n "$DOMAIN_IP" ]; then
            echo "IP домена: $DOMAIN_IP"
            EXTERNAL_IP=$(curl -s ifconfig.me 2>/dev/null)
            if [ "$EXTERNAL_IP" = "$DOMAIN_IP" ]; then
                echo "DNS: ✅ Домен указывает на этот сервер"
                return 0
            else
                echo "DNS: ⚠️ Домен указывает на другой сервер"
                return 1
            fi
        else
            echo "DNS: ❌ Домен не найден"
            return 1
        fi
    else
        echo "❌ Домен не настроен для SSL"
        return 1
    fi
}

# Функция проверки SSL сертификатов
check_ssl_certs() {
    echo ""
    echo "🔐 SSL сертификаты:"
    if [ -f "nginx/ssl/fullchain.pem" ] && [ -f "nginx/ssl/privkey.pem" ]; then
        echo "✅ Найдены в nginx/ssl/"

        # Проверяем срок действия
        if command -v openssl &> /dev/null; then
            echo "Срок действия:"
            openssl x509 -in nginx/ssl/fullchain.pem -noout -dates 2>/dev/null || echo "Не удалось проверить"
        fi
        return 0
    else
        echo "❌ Не найдены"
        return 1
    fi
}

# Функция создания SSL сертификатов
create_ssl_certs() {
    echo "🔐 Создание SSL сертификатов..."

    # Проверяем домен
    if [ -z "$DOMAIN" ] || [ "$DOMAIN" = "localhost" ] || [ "$DOMAIN" = "your-domain.com" ]; then
        echo "❌ Для SSL нужен настоящий домен!"
        echo "Настройте домен в /etc/edu_telebot/env: DOMAIN=ваш-домен.com"
        return 1
    fi

    # БЕЗОПАСНОСТЬ: Предупреждаем о перезаписи существующих сертификатов
    if [ -f "nginx/ssl/fullchain.pem" ] && [ -f "nginx/ssl/privkey.pem" ]; then
        echo "⚠️ ВНИМАНИЕ: Найдены существующие SSL сертификаты!"
        echo "Срок действия:"
        openssl x509 -in nginx/ssl/fullchain.pem -noout -dates 2>/dev/null || echo "Не удалось проверить"
        echo ""
        echo "Создание новых сертификатов ПЕРЕЗАПИШЕТ существующие!"
        read -p "Вы уверены что хотите продолжить? (yes/no): " -r response
        if [[ "$response" != "yes" ]]; then
            echo "❌ Отменено. Существующие сертификаты сохранены."
            return 1
        fi
        echo "⚠️ Создаем резервную копию существующих сертификатов..."
        cp nginx/ssl/fullchain.pem nginx/ssl/fullchain.pem.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || true
        cp nginx/ssl/privkey.pem nginx/ssl/privkey.pem.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || true
    fi

    # Проверяем зависимости
    if ! command -v socat &> /dev/null; then
        echo "📦 Устанавливаем socat (нужен для SSL)..."
        sudo apt update -qq
        sudo apt install -y socat curl dig
    fi

    # Проверяем DNS перед созданием сертификатов
    echo "🔍 Проверяем DNS для домена $DOMAIN..."
    DOMAIN_IP=$(dig +short $DOMAIN 2>/dev/null | tail -n1)
    EXTERNAL_IP=$(curl -s ifconfig.me 2>/dev/null)

    if [ -z "$DOMAIN_IP" ]; then
        echo "❌ Домен $DOMAIN не найден в DNS!"
        echo "Убедитесь, что домен настроен и указывает на этот сервер"
        return 1
    fi

    if [ "$EXTERNAL_IP" != "$DOMAIN_IP" ]; then
        echo "⚠️ ВНИМАНИЕ: Домен указывает на IP $DOMAIN_IP, но внешний IP сервера $EXTERNAL_IP"
        echo "SSL сертификат может не создаться!"
        read -p "Продолжить? (y/n): " -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            echo "❌ Отменено"
            return 1
        fi
    else
        echo "✅ DNS настроен корректно"
    fi

    # Проверяем acme.sh
    if [ ! -d "$HOME/.acme.sh" ]; then
        echo "📦 Устанавливаем acme.sh..."
        # Устанавливаем без email - он будет запрошен при первом использовании
        curl https://get.acme.sh | sh
        source ~/.bashrc
    fi

    # Останавливаем nginx для освобождения порта 80
    echo "🛑 Останавливаем nginx..."
    sudo docker-compose stop nginx 2>/dev/null || true

    # Создаем директорию
    mkdir -p nginx/ssl

    # Переключаем на Let's Encrypt (надежнее чем ZeroSSL)
    echo "🔧 Настраиваем Let's Encrypt..."
    echo "🔍 Отладка: Проверяем acme.sh в $HOME/.acme.sh/"
    if [ -f "$HOME/.acme.sh/acme.sh" ]; then
        echo "✅ acme.sh найден"
        echo "🔍 Выполняем: $HOME/.acme.sh/acme.sh --set-default-ca --server letsencrypt"
        $HOME/.acme.sh/acme.sh --set-default-ca --server letsencrypt
        echo "🔍 Результат команды set-default-ca: $?"
    else
        echo "❌ acme.sh не найден в $HOME/.acme.sh/"
        return 1
    fi

    # Получаем сертификат
    echo "🔐 Получаем сертификат для $DOMAIN через Let's Encrypt..."
    $HOME/.acme.sh/acme.sh --issue -d $DOMAIN --standalone --httpport 80 --server letsencrypt --accountemail mkaribzanovs@gmail.com --debug

    if [ $? -eq 0 ]; then
        # Копируем сертификаты
        $HOME/.acme.sh/acme.sh --install-cert -d $DOMAIN \
            --cert-file $(pwd)/nginx/ssl/cert.pem \
            --key-file $(pwd)/nginx/ssl/privkey.pem \
            --fullchain-file $(pwd)/nginx/ssl/fullchain.pem

        # Устанавливаем права
        chmod 644 nginx/ssl/fullchain.pem nginx/ssl/cert.pem
        chmod 600 nginx/ssl/privkey.pem

        echo "✅ SSL сертификаты созданы успешно!"
        return 0
    else
        echo "❌ Let's Encrypt не сработал. Пробуем ZeroSSL..."

        # Пробуем ZeroSSL как альтернативу
        $HOME/.acme.sh/acme.sh --set-default-ca --server zerossl
        $HOME/.acme.sh/acme.sh --issue -d $DOMAIN --standalone --httpport 80 --server zerossl

        if [ $? -eq 0 ]; then
            # Копируем сертификаты
            $HOME/.acme.sh/acme.sh --install-cert -d $DOMAIN \
                --cert-file $(pwd)/nginx/ssl/cert.pem \
                --key-file $(pwd)/nginx/ssl/privkey.pem \
                --fullchain-file $(pwd)/nginx/ssl/fullchain.pem

            # Устанавливаем права
            chmod 644 nginx/ssl/fullchain.pem nginx/ssl/cert.pem
            chmod 600 nginx/ssl/privkey.pem

            echo "✅ SSL сертификаты созданы через ZeroSSL!"
            return 0
        else
            echo "❌ Ошибка создания сертификатов через все провайдеры"
            echo "💡 Возможные причины:"
            echo "   - Домен $DOMAIN не указывает на этот сервер (IP: $EXTERNAL_IP)"
            echo "   - Порт 80 заблокирован или занят"
            echo "   - Проблемы с DNS"
            echo "   - Превышен лимит запросов Let's Encrypt"
            echo ""
            echo "🔧 Попробуйте:"
            echo "   1. Проверить DNS: dig $DOMAIN"
            echo "   2. Проверить порт 80: sudo netstat -tlnp | grep :80"
            echo "   3. Подождать час и попробовать снова"
            return 1
        fi
    fi
}

# Функция переключения на HTTPS
enable_ssl() {
    echo "🔒 Включаем HTTPS режим..."

    # Проверяем домен
    if [ -z "$DOMAIN" ] || [ "$DOMAIN" = "localhost" ] || [ "$DOMAIN" = "your-domain.com" ]; then
        echo "❌ Для SSL нужен настоящий домен!"
        return 1
    fi

    # Проверяем сертификаты
    if ! check_ssl_certs >/dev/null 2>&1; then
        echo "⚠️ SSL сертификаты не найдены!"
        echo "Создать их сейчас? (y/n)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            if ! create_ssl_certs; then
                return 1
            fi
        else
            echo "❌ Без SSL сертификатов HTTPS режим невозможен"
            return 1
        fi
    else
        echo "✅ Используем существующие SSL сертификаты"
    fi

    # Останавливаем контейнеры
    sudo docker-compose down

    # Восстанавливаем SSL конфигурацию
    if [ -f "nginx/nginx.conf.ssl-backup" ]; then
        cp nginx/nginx.conf.ssl-backup nginx/nginx.conf
    elif ! grep -q "listen 443 ssl" nginx/nginx.conf; then
        echo "❌ В nginx.conf нет SSL конфигурации"
        return 1
    fi

    # Обновляем домен в конфигурации
    sed -i "s/server_name \${DOMAIN};/server_name $DOMAIN;/g" nginx/nginx.conf
    sed -i "s/server_name _;/server_name $DOMAIN;/g" nginx/nginx.conf

    # Обновляем переменные окружения
    sudo sed -i 's/WEBHOOK_MODE=false/WEBHOOK_MODE=true/' /etc/edu_telebot/env
    sudo sed -i 's|WEBHOOK_HOST=http://|WEBHOOK_HOST=https://|' /etc/edu_telebot/env
    sudo sed -i "s|DOMAIN=.*|DOMAIN=$DOMAIN|" /etc/edu_telebot/env

    # Запускаем контейнеры
    sudo docker-compose up -d

    echo "✅ HTTPS режим включен"
    echo "🌐 Webhook URL: https://$DOMAIN:8443/webhook"
    echo "💡 Для стандартного порта 443 настройте reverse proxy"
}

# Функция переключения на HTTP
disable_ssl() {
    echo "🔓 Включаем HTTP режим..."

    # Останавливаем контейнеры
    sudo docker-compose down

    # Создаем резервную копию SSL конфигурации
    if [ -f "nginx/nginx.conf" ] && grep -q "listen 443 ssl" nginx/nginx.conf && [ ! -f "nginx/nginx.conf.ssl-backup" ]; then
        cp nginx/nginx.conf nginx/nginx.conf.ssl-backup
    fi

    # Копируем конфигурацию без SSL и подставляем домен
    cp nginx/nginx-no-ssl.conf nginx/nginx.conf

    # Подставляем домен в конфигурацию
    if [ -n "$DOMAIN" ]; then
        sed -i "s/\${DOMAIN}/$DOMAIN/g" nginx/nginx.conf
    fi

    # Обновляем переменные окружения
    sudo sed -i 's/WEBHOOK_MODE=true/WEBHOOK_MODE=false/' /etc/edu_telebot/env
    sudo sed -i 's|WEBHOOK_HOST=https://|WEBHOOK_HOST=http://|' /etc/edu_telebot/env

    # Запускаем контейнеры
    sudo docker-compose up -d

    echo "✅ HTTP режим включен"
    echo "🌐 Webhook URL: http://${DOMAIN}:8080/webhook"
    echo "💡 Для стандартного порта 80 настройте reverse proxy"
}

# Функция показа статуса
show_status() {
    echo "📊 Полный статус системы:"
    echo "========================="

    # Основная информация
    echo "Домен: ${DOMAIN:-не установлен}"
    echo "Webhook режим: ${WEBHOOK_MODE:-false}"
    echo "Webhook URL: ${WEBHOOK_HOST:-http://$DOMAIN}/webhook"

    # Проверка внешнего IP и DNS
    EXTERNAL_IP=$(curl -s ifconfig.me 2>/dev/null || echo "Не определен")
    echo "Внешний IP: $EXTERNAL_IP"

    if [ -n "$DOMAIN" ] && [ "$DOMAIN" != "localhost" ] && [ "$DOMAIN" != "your-domain.com" ]; then
        DOMAIN_IP=$(dig +short $DOMAIN 2>/dev/null | tail -n1)
        if [ -n "$DOMAIN_IP" ]; then
            echo "IP домена: $DOMAIN_IP"
            if [ "$EXTERNAL_IP" = "$DOMAIN_IP" ]; then
                echo "DNS: ✅ Домен указывает на этот сервер"
            else
                echo "DNS: ⚠️ Домен указывает на другой сервер"
            fi
        else
            echo "DNS: ❌ Домен не найден"
        fi
    fi

    echo ""

    # SSL сертификаты
    if check_ssl_certs; then
        echo "SSL сертификаты: ✅ Найдены"
        if command -v openssl &> /dev/null; then
            echo "Срок действия:"
            openssl x509 -in nginx/ssl/fullchain.pem -noout -dates 2>/dev/null || echo "Не удалось проверить"
        fi
    else
        echo "SSL сертификаты: ❌ Не найдены"
    fi

    # Порты
    echo ""
    echo "🔌 Порты:"
    if sudo netstat -tlnp | grep -q ":80 "; then
        echo "Порт 80: ✅ Занят"
    else
        echo "Порт 80: ⚪ Свободен"
    fi

    if sudo netstat -tlnp | grep -q ":443 "; then
        echo "Порт 443: ✅ Занят"
    else
        echo "Порт 443: ⚪ Свободен"
    fi

    echo ""
    echo "🐳 Статус контейнеров:"
    sudo docker-compose ps 2>/dev/null || echo "Docker Compose недоступен"
}

# Главное меню
echo "Выберите действие:"
echo "1) Показать статус"
echo "2) Включить HTTPS (SSL)"
echo "3) Включить HTTP (без SSL)"
echo "4) Создать новые SSL сертификаты"
echo "5) Выход"
echo ""
read -p "Ваш выбор (1-5): " choice

case $choice in
    1)
        show_status
        ;;
    2)
        enable_ssl
        ;;
    3)
        disable_ssl
        ;;
    4)
        create_ssl_certs
        ;;
    5)
        echo "👋 До свидания!"
        exit 0
        ;;
    *)
        echo "❌ Неверный выбор"
        exit 1
        ;;
esac

echo ""
echo "✅ Готово! Проверьте статус: ./scripts/ssl_manager.sh"
