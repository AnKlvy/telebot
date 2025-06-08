#!/bin/bash

# Скрипт для деплоя телеграм бота на Beget

echo "🚀 Начинаем деплой телеграм бота..."

# Функция установки Docker
install_docker() {
    echo "📦 Устанавливаем Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo "✅ Docker установлен"
}

# Функция установки Docker Compose
install_docker_compose() {
    echo "📦 Устанавливаем Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose установлен"
}

# Функция установки Git
install_git() {
    echo "📦 Устанавливаем Git..."
    sudo apt update
    sudo apt install -y git
    echo "✅ Git установлен"
}

# Функция установки Certbot
install_certbot() {
    echo "📦 Устанавливаем Certbot..."
    sudo apt update
    sudo apt install -y certbot
    echo "✅ Certbot установлен"
}

# Проверяем и устанавливаем зависимости
echo "🔍 Проверяем системные зависимости..."

# Проверяем Docker
if ! command -v docker &> /dev/null; then
    echo "⚠️ Docker не установлен"
    read -p "Установить Docker автоматически? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        install_docker
        echo "🔄 Перезайдите в систему для применения прав Docker"
        echo "Затем запустите скрипт снова"
        exit 0
    else
        echo "❌ Docker необходим для работы. Установите вручную и запустите скрипт снова."
        exit 1
    fi
fi

# Проверяем Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "⚠️ Docker Compose не установлен"
    read -p "Установить Docker Compose автоматически? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        install_docker_compose
    else
        echo "❌ Docker Compose необходим для работы. Установите вручную и запустите скрипт снова."
        exit 1
    fi
fi

# Проверяем Git
if ! command -v git &> /dev/null; then
    echo "⚠️ Git не установлен"
    read -p "Установить Git автоматически? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        install_git
    fi
fi

# Проверяем Certbot
if ! command -v certbot &> /dev/null; then
    echo "⚠️ Certbot не установлен (нужен для SSL)"
    read -p "Установить Certbot автоматически? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        install_certbot
    fi
fi

echo "✅ Все зависимости проверены"

# Проверяем наличие файла с переменными окружения
if [ ! -f /etc/telebot/env ]; then
    echo "❌ Файл /etc/telebot/env не найден."
    read -p "Настроить переменные окружения сейчас? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        chmod +x scripts/setup_env.sh
        sudo ./scripts/setup_env.sh
        echo "📝 Теперь отредактируйте файл: sudo nano /etc/telebot/env"
        echo "После редактирования запустите скрипт снова"
        exit 0
    else
        echo "📝 Запустите позже: chmod +x scripts/setup_env.sh && sudo ./scripts/setup_env.sh"
        echo "📝 Затем отредактируйте: sudo nano /etc/telebot/env"
        exit 1
    fi
fi

# Проверяем наличие директории для логов
if [ ! -d "logs" ]; then
    echo "📁 Создаем директорию для логов..."
    mkdir -p logs
    mkdir -p logs/nginx
    chmod -R 755 logs
fi

# Проверяем наличие SSL сертификатов для webhook режима
if grep -q "WEBHOOK_MODE=true" /etc/telebot/env; then
    # Создаем директорию для SSL, если она не существует
    if [ ! -d "nginx/ssl" ]; then
        echo "📁 Создаем директорию для SSL сертификатов..."
        mkdir -p nginx/ssl
    fi
    
    # Проверяем наличие сертификатов
    if [ ! -f "nginx/ssl/fullchain.pem" ] || [ ! -f "nginx/ssl/privkey.pem" ]; then
        echo "⚠️ Режим webhook включен, но SSL сертификаты не найдены"
        read -p "Настроить SSL сертификаты сейчас? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            chmod +x scripts/setup_ssl.sh
            sudo ./scripts/setup_ssl.sh
        else
            echo "⚠️ Без SSL сертификатов webhook работать не будет"
            echo "📝 Запустите позже: chmod +x scripts/setup_ssl.sh && sudo ./scripts/setup_ssl.sh"
        fi
    else
        # Проверяем права доступа к сертификатам
        if [ "$(stat -c %a nginx/ssl/fullchain.pem)" != "644" ] || [ "$(stat -c %a nginx/ssl/privkey.pem)" != "600" ]; then
            echo "🔐 Исправляем права доступа к SSL сертификатам..."
            chmod 644 nginx/ssl/fullchain.pem
            chmod 600 nginx/ssl/privkey.pem
        fi
    fi
fi

# Останавливаем существующие контейнеры
echo "🛑 Останавливаем существующие контейнеры..."
docker-compose down

# Удаляем старые образы
echo "🗑️ Удаляем старые образы..."
docker-compose down --rmi all

# Собираем новые образы
echo "🔨 Собираем новые образы..."
if ! docker-compose build --no-cache; then
    echo "❌ Ошибка при сборке образов"
    read -p "Продолжить несмотря на ошибки? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Запускаем контейнеры
echo "▶️ Запускаем контейнеры..."
if ! docker-compose up -d; then
    echo "❌ Ошибка при запуске контейнеров"
    docker-compose logs
    exit 1
fi

# Проверяем статус
echo "📊 Проверяем статус контейнеров..."
docker-compose ps

# Ждем запуска контейнеров
echo "⏳ Ждем запуска контейнеров..."
sleep 10

# Проверяем что все контейнеры запущены
if docker-compose ps | grep -q "Up"; then
    echo "✅ Контейнеры запущены успешно"

    # Проверяем nginx
    if docker-compose ps nginx | grep -q "Up"; then
        echo "✅ Nginx запущен"
    else
        echo "⚠️ Nginx не запущен, проверьте конфигурацию"
    fi

    # Проверяем бота
    if docker-compose ps bot | grep -q "Up"; then
        echo "✅ Бот запущен"
    else
        echo "⚠️ Бот не запущен, проверьте логи"
    fi

    # Проверяем базу данных
    if docker-compose ps postgres | grep -q "Up"; then
        echo "✅ База данных запущена"
    else
        echo "⚠️ База данных не запущена, проверьте конфигурацию"
    fi
else
    echo "❌ Ошибка запуска контейнеров"
    docker-compose logs
    exit 1
fi

echo ""
echo "🎉 Деплой завершен!"
echo "📝 Для просмотра логов: docker-compose logs -f bot"
echo "🌐 Для проверки nginx: docker-compose logs -f nginx"
echo "🛑 Для остановки: docker-compose down"

# Предлагаем настроить автозапуск
read -p "Настроить автозапуск бота при перезагрузке сервера? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -f "scripts/setup_autostart.sh" ]; then
        chmod +x scripts/setup_autostart.sh
        ./scripts/setup_autostart.sh
    else
        echo "❌ Скрипт scripts/setup_autostart.sh не найден"
        echo "📝 Вы можете настроить автозапуск вручную:"
        echo "   sudo nano /etc/systemd/system/telebot.service"
        echo "   sudo systemctl enable telebot.service"
        echo "   sudo systemctl start telebot.service"
    fi
fi
