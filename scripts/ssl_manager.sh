#!/bin/bash

# Универсальный SSL менеджер для телеграм бота
# Поддерживает Beget хостинг и обычные VPS
# Автоматически настраивает SSL сертификаты

set -e  # Выход при ошибке

echo "🔐 Универсальный SSL менеджер для телеграм бота"
echo "================================================"

# Загружаем переменные окружения
if [ -f "/etc/edu_telebot/env" ]; then
    source /etc/edu_telebot/env
    echo "✅ Переменные окружения загружены"
else
    echo "❌ Файл /etc/edu_telebot/env не найден"
    echo "💡 Запустите сначала: sudo ./scripts/setup_env.sh"
    exit 1
fi

# Проверяем наличие домена
if [ -z "$DOMAIN" ] || [ "$DOMAIN" = "your-domain.com" ]; then
    echo "❌ Домен не настроен в переменных окружения"
    echo "📝 Отредактируйте файл: sudo nano /etc/edu_telebot/env"
    echo "📝 Установите правильное значение для DOMAIN"
    exit 1
fi

echo "🌐 Настраиваем SSL для домена: $DOMAIN"

# Создаем директории
mkdir -p nginx/ssl
mkdir -p logs/ssl

# Функция для проверки DNS записей
check_dns() {
    echo "🔍 Проверяем DNS записи для $DOMAIN..."
    
    # Получаем IP адрес сервера
    SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s ipinfo.io/ip 2>/dev/null || echo "unknown")
    echo "📍 IP сервера: $SERVER_IP"
    
    # Проверяем A запись домена
    DOMAIN_IP=$(dig +short $DOMAIN 2>/dev/null | tail -1)
    if [ -n "$DOMAIN_IP" ]; then
        echo "📍 IP домена: $DOMAIN_IP"
        if [ "$SERVER_IP" = "$DOMAIN_IP" ]; then
            echo "✅ DNS записи настроены правильно"
            return 0
        else
            echo "⚠️ DNS записи указывают на другой IP"
            echo "💡 Убедитесь что A запись $DOMAIN указывает на $SERVER_IP"
            return 1
        fi
    else
        echo "❌ Домен $DOMAIN не разрешается"
        echo "💡 Настройте A запись в DNS панели вашего провайдера"
        return 1
    fi
}

# Функция поиска существующих SSL сертификатов
find_existing_ssl() {
    echo "🔍 Ищем существующие SSL сертификаты..."
    
    # Возможные пути к сертификатам
    local cert_paths=(
        "/etc/letsencrypt/live/$DOMAIN"
        "/etc/letsencrypt/live"
        "$HOME/.acme.sh/$DOMAIN"
        "$HOME/.acme.sh"
        "/etc/ssl/certs"
        "/opt/ssl"
        "/var/ssl"
        "/home/*/ssl"
        "/home/*/.acme.sh"
    )

    for path in "${cert_paths[@]}"; do
        # Расширяем wildcards
        for expanded_path in $path; do
            if [ -d "$expanded_path" ]; then
                # Ищем fullchain.pem и privkey.pem
                local fullchain=$(find "$expanded_path" -name "fullchain.pem" -type f 2>/dev/null | head -1)
                local privkey=$(find "$expanded_path" -name "privkey.pem" -type f 2>/dev/null | head -1)

                # Также ищем cert.pem и key.pem
                if [ -z "$fullchain" ]; then
                    fullchain=$(find "$expanded_path" -name "cert.pem" -type f 2>/dev/null | head -1)
                fi
                if [ -z "$privkey" ]; then
                    privkey=$(find "$expanded_path" -name "key.pem" -type f 2>/dev/null | head -1)
                fi

                if [ -n "$fullchain" ] && [ -n "$privkey" ]; then
                    echo "✅ Найдены SSL сертификаты:"
                    echo "   Сертификат: $fullchain"
                    echo "   Ключ: $privkey"

                    # Проверяем срок действия сертификата
                    if command -v openssl &> /dev/null; then
                        local expiry=$(openssl x509 -enddate -noout -in "$fullchain" 2>/dev/null | cut -d= -f2)
                        if [ -n "$expiry" ]; then
                            echo "   Срок действия: $expiry"
                        fi
                    fi

                    read -p "Использовать эти сертификаты? (y/n): " -n 1 -r
                    echo
                    if [[ $REPLY =~ ^[Yy]$ ]]; then
                        # Копируем сертификаты
                        echo "📋 Копируем сертификаты..."
                        sudo cp "$fullchain" nginx/ssl/fullchain.pem
                        sudo cp "$privkey" nginx/ssl/privkey.pem

                        # Устанавливаем права
                        chmod 644 nginx/ssl/fullchain.pem
                        chmod 600 nginx/ssl/privkey.pem
                        chown $USER:$USER nginx/ssl/*.pem 2>/dev/null || true

                        echo "✅ SSL сертификаты настроены"
                        return 0
                    fi
                fi
            fi
        done
    done

    return 1
}

# Функция определения типа хостинга
detect_hosting() {
    echo "🔍 Определяем тип хостинга..."
    
    # Проверяем Beget
    if [ -d "/home/*/domains" ] || [ -d "/var/www/*/data" ] || grep -q "beget" /etc/hostname 2>/dev/null; then
        echo "🏢 Обнаружен Beget хостинг"
        return 1
    fi
    
    # Проверяем другие популярные хостинги
    if [ -d "/usr/local/mgr5" ]; then
        echo "🏢 Обнаружен ISPmanager"
        return 2
    fi
    
    if [ -d "/usr/local/cpanel" ]; then
        echo "🏢 Обнаружен cPanel"
        return 3
    fi
    
    echo "🖥️ Обычный VPS/сервер"
    return 0
}

# Функция установки зависимостей
install_dependencies() {
    echo "📦 Проверяем и устанавливаем зависимости..."
    
    # Обновляем пакеты
    sudo apt update -qq
    
    # Устанавливаем необходимые пакеты
    local packages=("curl" "socat" "cron" "openssl")
    for package in "${packages[@]}"; do
        if ! command -v $package &> /dev/null; then
            echo "📦 Устанавливаем $package..."
            sudo apt install -y $package
        else
            echo "✅ $package уже установлен"
        fi
    done
}

# Функция установки acme.sh
install_acme() {
    echo "📦 Устанавливаем acme.sh..."
    
    if [ -d "$HOME/.acme.sh" ]; then
        echo "✅ acme.sh уже установлен"
        return 0
    fi
    
    # Устанавливаем acme.sh
    curl https://get.acme.sh | sh -s email=admin@$DOMAIN
    
    if [ -d "$HOME/.acme.sh" ]; then
        echo "✅ acme.sh установлен успешно"
        # Добавляем в PATH
        export PATH="$HOME/.acme.sh:$PATH"
        return 0
    else
        echo "❌ Ошибка установки acme.sh"
        return 1
    fi
}

# Функция получения SSL через HTTP валидацию
get_ssl_http() {
    echo "🔐 Получаем SSL сертификат через HTTP валидацию..."
    
    # Создаем временную директорию для валидации
    local webroot="/tmp/acme_webroot"
    mkdir -p "$webroot"
    
    # Запускаем временный веб-сервер для валидации
    echo "🌐 Запускаем временный веб-сервер на порту 80..."
    
    # Останавливаем nginx если запущен
    if command -v docker-compose &> /dev/null && [ -f "docker-compose.yml" ]; then
        echo "🛑 Временно останавливаем nginx..."
        docker-compose stop nginx 2>/dev/null || true
    fi
    
    # Получаем сертификат
    if $HOME/.acme.sh/acme.sh --issue -d $DOMAIN --standalone --httpport 80; then
        echo "✅ SSL сертификат получен успешно"
        
        # Копируем сертификаты
        $HOME/.acme.sh/acme.sh --install-cert -d $DOMAIN \
            --cert-file nginx/ssl/cert.pem \
            --key-file nginx/ssl/privkey.pem \
            --fullchain-file nginx/ssl/fullchain.pem
        
        # Устанавливаем права
        chmod 644 nginx/ssl/*.pem
        chmod 600 nginx/ssl/privkey.pem
        chown $USER:$USER nginx/ssl/*.pem 2>/dev/null || true
        
        echo "✅ SSL сертификаты установлены"
        return 0
    else
        echo "❌ Ошибка получения SSL сертификата"
        return 1
    fi
}

# Функция получения SSL через DNS валидацию (для Beget)
get_ssl_dns() {
    echo "🔐 Получаем SSL сертификат через DNS валидацию..."
    echo "⚠️ Для DNS валидации потребуется ручное добавление TXT записи"

    # Запускаем процесс получения сертификата
    if $HOME/.acme.sh/acme.sh --issue -d $DOMAIN --dns --yes-I-know-dns-manual-mode-enough-go-ahead-please; then
        echo "✅ SSL сертификат получен через DNS"

        # Копируем сертификаты
        $HOME/.acme.sh/acme.sh --install-cert -d $DOMAIN \
            --cert-file nginx/ssl/cert.pem \
            --key-file nginx/ssl/privkey.pem \
            --fullchain-file nginx/ssl/fullchain.pem

        # Устанавливаем права
        chmod 644 nginx/ssl/*.pem
        chmod 600 nginx/ssl/privkey.pem
        chown $USER:$USER nginx/ssl/*.pem 2>/dev/null || true

        echo "✅ SSL сертификаты установлены"
        return 0
    else
        echo "❌ Ошибка получения SSL через DNS"
        return 1
    fi
}

# Функция для Beget хостинга
setup_beget_ssl() {
    echo "🏢 Настройка SSL для Beget хостинга..."
    echo "💡 На Beget рекомендуется использовать встроенные SSL сертификаты"
    echo "💡 Или загрузить сертификаты через панель управления"

    # Проверяем наличие встроенных сертификатов Beget
    local beget_ssl_paths=(
        "/home/*/ssl"
        "/var/www/*/ssl"
        "/home/*/domains/*/ssl"
    )

    for path in "${beget_ssl_paths[@]}"; do
        for expanded_path in $path; do
            if [ -d "$expanded_path" ]; then
                echo "🔍 Найдена SSL директория: $expanded_path"
                if find_ssl_in_path "$expanded_path"; then
                    return 0
                fi
            fi
        done
    done

    echo "⚠️ Встроенные SSL сертификаты Beget не найдены"
    echo "💡 Варианты для Beget:"
    echo "   1. Включить бесплатный SSL в панели управления"
    echo "   2. Загрузить собственный сертификат"
    echo "   3. Использовать DNS валидацию"

    read -p "Попробовать DNS валидацию? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        get_ssl_dns
        return $?

    fi

    return 1
}

# Функция поиска SSL в конкретном пути
find_ssl_in_path() {
    local search_path="$1"
    local fullchain=$(find "$search_path" -name "*.crt" -o -name "*.pem" -o -name "*cert*" 2>/dev/null | head -1)
    local privkey=$(find "$search_path" -name "*.key" -o -name "*private*" 2>/dev/null | head -1)

    if [ -n "$fullchain" ] && [ -n "$privkey" ]; then
        echo "✅ Найдены SSL файлы:"
        echo "   Сертификат: $fullchain"
        echo "   Ключ: $privkey"

        read -p "Использовать эти файлы? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            sudo cp "$fullchain" nginx/ssl/fullchain.pem
            sudo cp "$privkey" nginx/ssl/privkey.pem
            chmod 644 nginx/ssl/fullchain.pem
            chmod 600 nginx/ssl/privkey.pem
            chown $USER:$USER nginx/ssl/*.pem 2>/dev/null || true
            return 0
        fi
    fi

    return 1
}

# Функция настройки автообновления
setup_auto_renewal() {
    echo "🔄 Настраиваем автообновление SSL сертификатов..."

    # Создаем директорию для логов
    mkdir -p logs/ssl

    # Создаем скрипт обновления
    cat > /tmp/ssl_renewal.sh << 'EOF'
#!/bin/bash
# Скрипт автообновления SSL сертификатов

PROJECT_DIR="/path/to/project"
cd "$PROJECT_DIR"

# Загружаем переменные окружения
if [ -f "/etc/edu_telebot/env" ]; then
    source /etc/edu_telebot/env
else
    echo "$(date): Ошибка - файл переменных окружения не найден" >> logs/ssl/renewal.log
    exit 1
fi

# Логируем начало процесса
echo "$(date): Начинаем проверку SSL сертификатов для $DOMAIN" >> logs/ssl/renewal.log

# Проверяем срок действия текущего сертификата
if [ -f "nginx/ssl/fullchain.pem" ]; then
    EXPIRY_DATE=$(openssl x509 -enddate -noout -in nginx/ssl/fullchain.pem 2>/dev/null | cut -d= -f2)
    EXPIRY_TIMESTAMP=$(date -d "$EXPIRY_DATE" +%s 2>/dev/null || echo "0")
    CURRENT_TIMESTAMP=$(date +%s)
    DAYS_LEFT=$(( (EXPIRY_TIMESTAMP - CURRENT_TIMESTAMP) / 86400 ))

    echo "$(date): Сертификат действителен еще $DAYS_LEFT дней" >> logs/ssl/renewal.log

    # Обновляем если осталось меньше 30 дней
    if [ $DAYS_LEFT -lt 30 ]; then
        echo "$(date): Обновляем сертификат (осталось $DAYS_LEFT дней)" >> logs/ssl/renewal.log

        # Обновляем сертификаты через acme.sh
        if [ -d "$HOME/.acme.sh" ]; then
            if $HOME/.acme.sh/acme.sh --renew -d $DOMAIN; then
                echo "$(date): SSL сертификат успешно обновлен" >> logs/ssl/renewal.log

                # Перезапускаем nginx
                if command -v docker-compose &> /dev/null && [ -f "docker-compose.yml" ]; then
                    docker-compose restart nginx
                    echo "$(date): Nginx перезапущен" >> logs/ssl/renewal.log
                fi
            else
                echo "$(date): Ошибка обновления SSL сертификата" >> logs/ssl/renewal.log
            fi
        else
            echo "$(date): acme.sh не найден, пропускаем обновление" >> logs/ssl/renewal.log
        fi
    else
        echo "$(date): Обновление не требуется" >> logs/ssl/renewal.log
    fi
else
    echo "$(date): SSL сертификат не найден" >> logs/ssl/renewal.log
fi
EOF

    # Заменяем путь к проекту
    sed -i "s|/path/to/project|$(pwd)|g" /tmp/ssl_renewal.sh

    # Копируем скрипт
    sudo cp /tmp/ssl_renewal.sh /etc/cron.daily/ssl-renewal
    sudo chmod +x /etc/cron.daily/ssl-renewal
    sudo chown root:root /etc/cron.daily/ssl-renewal

    echo "✅ Автообновление настроено (ежедневная проверка)"
    echo "📝 Логи обновлений: logs/ssl/renewal.log"
    rm /tmp/ssl_renewal.sh
}

# Функция проверки SSL сертификатов
check_ssl_status() {
    echo "🔍 Проверяем статус SSL сертификатов..."

    if [ -f "nginx/ssl/fullchain.pem" ] && [ -f "nginx/ssl/privkey.pem" ]; then
        echo "✅ SSL файлы найдены"

        # Проверяем срок действия
        if command -v openssl &> /dev/null; then
            local expiry=$(openssl x509 -enddate -noout -in nginx/ssl/fullchain.pem 2>/dev/null | cut -d= -f2)
            if [ -n "$expiry" ]; then
                local expiry_timestamp=$(date -d "$expiry" +%s 2>/dev/null || echo "0")
                local current_timestamp=$(date +%s)
                local days_left=$(( (expiry_timestamp - current_timestamp) / 86400 ))

                echo "📅 Срок действия: $expiry"
                echo "⏰ Осталось дней: $days_left"

                if [ $days_left -lt 30 ]; then
                    echo "⚠️ Сертификат скоро истечет, рекомендуется обновление"
                    return 1
                else
                    echo "✅ Сертификат действителен"
                    return 0
                fi
            fi
        fi

        echo "✅ SSL сертификаты настроены"
        return 0
    else
        echo "❌ SSL сертификаты не найдены"
        return 1
    fi
}

# Функция интерактивного выбора метода
choose_ssl_method() {
    echo ""
    echo "🔐 Выберите метод получения SSL сертификата:"
    echo "1) HTTP валидация (рекомендуется для VPS)"
    echo "2) DNS валидация (для хостингов с ограничениями)"
    echo "3) Поиск существующих сертификатов"
    echo "4) Пропустить SSL (только HTTP режим)"

    read -p "Ваш выбор (1-4): " -n 1 -r
    echo

    case $REPLY in
        1)
            return 1  # HTTP
            ;;
        2)
            return 2  # DNS
            ;;
        3)
            return 3  # Search
            ;;
        4)
            return 4  # Skip
            ;;
        *)
            echo "⚡ По умолчанию: HTTP валидация"
            return 1
            ;;
    esac
}

# Основная функция
main() {
    echo "🚀 Начинаем настройку SSL..."

    # Проверяем текущий статус SSL
    if check_ssl_status; then
        echo "🎉 SSL сертификаты уже настроены и действительны"
        read -p "Обновить сертификаты принудительно? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "✅ Используем существующие сертификаты"
            setup_auto_renewal
            return 0
        fi
    fi

    # Проверяем DNS (не критично)
    if ! check_dns; then
        echo "⚠️ DNS записи не настроены правильно"
        echo "💡 Это может повлиять на получение SSL сертификатов"
    fi

    # Определяем тип хостинга
    detect_hosting
    hosting_type=$?

    # Для Beget предлагаем специальную настройку
    if [ $hosting_type -eq 1 ]; then
        echo "🏢 Обнаружен Beget хостинг"
        if setup_beget_ssl; then
            echo "🎉 SSL настроен для Beget"
            setup_auto_renewal
            return 0
        fi
    fi

    # Ищем существующие сертификаты
    if find_existing_ssl; then
        echo "🎉 Используем найденные SSL сертификаты"
        setup_auto_renewal
        return 0
    fi

    # Выбираем метод получения SSL
    choose_ssl_method
    method=$?

    case $method in
        1)  # HTTP валидация
            echo "🌐 Используем HTTP валидацию..."
            install_dependencies
            install_acme
            if get_ssl_http; then
                echo "🎉 SSL настроен через HTTP валидацию"
                setup_auto_renewal
                return 0
            fi
            ;;
        2)  # DNS валидация
            echo "🔍 Используем DNS валидацию..."
            install_dependencies
            install_acme
            if get_ssl_dns; then
                echo "🎉 SSL настроен через DNS валидацию"
                setup_auto_renewal
                return 0
            fi
            ;;
        3)  # Поиск существующих
            echo "🔍 Повторный поиск сертификатов..."
            if find_existing_ssl; then
                setup_auto_renewal
                return 0
            else
                echo "❌ Сертификаты не найдены"
            fi
            ;;
        4)  # Пропустить
            echo "⚠️ SSL пропущен, бот будет работать только по HTTP"
            return 0
            ;;
    esac

    echo "❌ Не удалось настроить SSL"
    echo "💡 Возможные решения:"
    echo "   - Проверьте DNS записи домена"
    echo "   - Убедитесь что порт 80 открыт"
    echo "   - Попробуйте DNS валидацию"
    echo "   - Настройте SSL вручную"
    return 1
}

# Функция показа справки
show_help() {
    echo "🔐 SSL менеджер для телеграм бота"
    echo ""
    echo "Использование:"
    echo "  ./scripts/ssl_manager.sh [опция]"
    echo ""
    echo "Опции:"
    echo "  --check     Проверить статус SSL сертификатов"
    echo "  --renew     Принудительно обновить сертификаты"
    echo "  --help      Показать эту справку"
    echo ""
    echo "Без опций: интерактивная настройка SSL"
}

# Обработка аргументов командной строки
case "${1:-}" in
    --check)
        check_ssl_status
        exit $?
        ;;
    --renew)
        echo "🔄 Принудительное обновление SSL сертификатов..."
        if [ -d "$HOME/.acme.sh" ]; then
            $HOME/.acme.sh/acme.sh --renew -d $DOMAIN --force
        else
            echo "❌ acme.sh не установлен"
            exit 1
        fi
        ;;
    --help)
        show_help
        exit 0
        ;;
    "")
        # Запускаем основную функцию без аргументов
        main "$@"
        ;;
    *)
        echo "❌ Неизвестная опция: $1"
        show_help
        exit 1
        ;;
esac

# Функция для Beget хостинга
setup_beget_ssl() {
    echo "🏢 Настройка SSL для Beget хостинга..."

    echo "💡 На Beget хостинге SSL сертификаты обычно предоставляются автоматически"
    echo "💡 Проверьте панель управления хостингом для настройки SSL"

    # Ищем сертификаты в стандартных местах Beget
    local beget_paths=(
        "/home/*/ssl"
        "/var/www/*/ssl"
        "/home/*/domains/*/ssl"
    )

    for path in "${beget_paths[@]}"; do
        for expanded_path in $path; do
            if [ -d "$expanded_path" ]; then
                echo "🔍 Проверяем: $expanded_path"
                local cert=$(find "$expanded_path" -name "*.crt" -o -name "*.pem" | head -1)
                local key=$(find "$expanded_path" -name "*.key" | head -1)

                if [ -n "$cert" ] && [ -n "$key" ]; then
                    echo "✅ Найдены сертификаты Beget:"
                    echo "   Сертификат: $cert"
                    echo "   Ключ: $key"

                    read -p "Использовать эти сертификаты? (y/n): " -n 1 -r
                    echo
                    if [[ $REPLY =~ ^[Yy]$ ]]; then
                        cp "$cert" nginx/ssl/fullchain.pem
                        cp "$key" nginx/ssl/privkey.pem
                        chmod 644 nginx/ssl/fullchain.pem
                        chmod 600 nginx/ssl/privkey.pem
                        echo "✅ Сертификаты Beget настроены"
                        return 0
                    fi
                fi
            fi
        done
    done

    echo "⚠️ Автоматические сертификаты Beget не найдены"
    echo "💡 Настройте SSL в панели управления Beget или используйте Let's Encrypt"
    return 1
}

# Функция для получения SSL через DNS валидацию
get_ssl_dns() {
    echo "🔐 Получаем SSL сертификат через DNS валидацию..."
    echo "💡 Этот метод подходит если порт 80 недоступен"

    # Запускаем процесс получения сертификата
    if $HOME/.acme.sh/acme.sh --issue -d $DOMAIN --dns --yes-I-know-dns-manual-mode-enough-go-ahead-please; then
        echo "📝 Добавьте TXT запись в DNS:"
        echo "Имя: _acme-challenge.$DOMAIN"
        echo "Значение: (будет показано выше)"
        echo ""
        read -p "После добавления записи нажмите Enter для продолжения..."

        # Завершаем валидацию
        if $HOME/.acme.sh/acme.sh --renew -d $DOMAIN --yes-I-know-dns-manual-mode-enough-go-ahead-please; then
            # Устанавливаем сертификаты
            $HOME/.acme.sh/acme.sh --install-cert -d $DOMAIN \
                --cert-file nginx/ssl/cert.pem \
                --key-file nginx/ssl/privkey.pem \
                --fullchain-file nginx/ssl/fullchain.pem

            chmod 644 nginx/ssl/*.pem
            chmod 600 nginx/ssl/privkey.pem
            chown $USER:$USER nginx/ssl/*.pem 2>/dev/null || true

            echo "✅ SSL сертификаты получены через DNS"
            return 0
        fi
    fi

    echo "❌ Ошибка получения SSL через DNS"
    return 1
}

# Функция проверки SSL сертификатов
check_ssl_status() {
    echo "🔍 Проверяем статус SSL сертификатов..."

    if [ ! -f "nginx/ssl/fullchain.pem" ] || [ ! -f "nginx/ssl/privkey.pem" ]; then
        echo "❌ SSL сертификаты не найдены"
        return 1
    fi

    echo "✅ SSL файлы найдены"

    # Проверяем срок действия
    if command -v openssl &> /dev/null; then
        local expiry=$(openssl x509 -enddate -noout -in nginx/ssl/fullchain.pem 2>/dev/null | cut -d= -f2)
        if [ -n "$expiry" ]; then
            echo "📅 Срок действия: $expiry"

            # Проверяем, не истекает ли сертификат в ближайшие 30 дней
            local expiry_timestamp=$(date -d "$expiry" +%s 2>/dev/null || echo "0")
            local current_timestamp=$(date +%s)
            local days_left=$(( (expiry_timestamp - current_timestamp) / 86400 ))

            if [ $days_left -lt 30 ]; then
                echo "⚠️ Сертификат истекает через $days_left дней"
                echo "💡 Рекомендуется обновить сертификат"
            else
                echo "✅ Сертификат действителен еще $days_left дней"
            fi
        fi
    fi

    # Проверяем права доступа
    local cert_perms=$(stat -c %a nginx/ssl/fullchain.pem 2>/dev/null)
    local key_perms=$(stat -c %a nginx/ssl/privkey.pem 2>/dev/null)

    if [ "$cert_perms" != "644" ] || [ "$key_perms" != "600" ]; then
        echo "⚠️ Неправильные права доступа к сертификатам"
        echo "🔧 Исправляем права..."
        chmod 644 nginx/ssl/fullchain.pem
        chmod 600 nginx/ssl/privkey.pem
        echo "✅ Права доступа исправлены"
    else
        echo "✅ Права доступа к сертификатам корректны"
    fi

    return 0
}

# Функция интерактивного меню
interactive_menu() {
    while true; do
        echo ""
        echo "🔐 SSL Менеджер - Интерактивное меню"
        echo "=================================="
        echo "1) Автоматическая настройка SSL"
        echo "2) Поиск существующих сертификатов"
        echo "3) Получить новый сертификат (HTTP)"
        echo "4) Получить новый сертификат (DNS)"
        echo "5) Проверить статус SSL"
        echo "6) Настроить автообновление"
        echo "7) Настройка для Beget хостинга"
        echo "0) Выход"
        echo ""
        read -p "Выберите действие (0-7): " -n 1 -r
        echo

        case $REPLY in
            1)
                main
                ;;
            2)
                find_existing_ssl
                ;;
            3)
                install_dependencies
                install_acme
                get_ssl_http
                ;;
            4)
                install_dependencies
                install_acme
                get_ssl_dns
                ;;
            5)
                check_ssl_status
                ;;
            6)
                setup_auto_renewal
                ;;
            7)
                setup_beget_ssl
                ;;
            0)
                echo "👋 До свидания!"
                exit 0
                ;;
            *)
                echo "❌ Неверный выбор"
                ;;
        esac

        echo ""
        read -p "Нажмите Enter для продолжения..."
    done
}

# Проверяем аргументы командной строки
if [ "$1" = "--interactive" ] || [ "$1" = "-i" ]; then
    interactive_menu
elif [ "$1" = "--check" ] || [ "$1" = "-c" ]; then
    check_ssl_status
elif [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "🔐 SSL Менеджер для телеграм бота"
    echo ""
    echo "Использование:"
    echo "  $0                 - Автоматическая настройка SSL"
    echo "  $0 --interactive   - Интерактивное меню"
    echo "  $0 --check         - Проверить статус SSL"
    echo "  $0 --help          - Показать эту справку"
    echo ""
    exit 0
else
    # Запускаем основную функцию
    main "$@"
fi
