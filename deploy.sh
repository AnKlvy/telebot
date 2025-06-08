#!/bin/bash

# Скрипт для деплоя телеграм бота на Beget

echo "🚀 Начинаем деплой телеграм бота..."

# Функция проверки интернет-соединения
check_internet() {
    echo "🌐 Проверяем интернет-соединение..."
    if ping -c 1 google.com &> /dev/null || ping -c 1 8.8.8.8 &> /dev/null; then
        echo "✅ Интернет-соединение работает"
        return 0
    else
        echo "❌ Нет интернет-соединения"
        echo "Проверьте подключение к интернету и запустите скрипт снова"
        exit 1
    fi
}

# Проверяем интернет
check_internet

# Проверяем права root для установки зависимостей
if [ "$EUID" -ne 0 ] && ! command -v docker &> /dev/null; then
    echo "⚠️ Для установки Docker требуются права root"
    echo "Запустите скрипт с sudo: sudo ./deploy.sh"
    echo "Или установите Docker вручную и запустите скрипт снова"
    exit 1
fi

# Функция установки Docker
install_docker() {
    echo "📦 Устанавливаем Docker..."

    # Определяем дистрибутив
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
    fi

    # Для Kali Linux используем специальную установку
    if [[ "$OS" == *"Kali"* ]]; then
        echo "🐉 Обнаружен Kali Linux, используем специальную установку..."

        # Удаляем старые версии Docker если есть
        echo "🗑️ Удаляем старые версии Docker..."
        sudo apt remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

        # Исправляем проблемы с пакетами
        echo "🔧 Исправляем проблемы с пакетами..."
        sudo apt update --fix-missing || true
        sudo apt install -f -y || true

        # Обновляем пакеты с повторными попытками
        echo "🔄 Обновляем систему..."
        for i in {1..3}; do
            if sudo apt update; then
                break
            else
                echo "⚠️ Попытка $i не удалась, повторяем..."
                sleep 2
            fi
        done

        # Устанавливаем зависимости
        echo "📦 Устанавливаем зависимости..."
        sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release software-properties-common

        # Добавляем ключ Docker
        echo "🔑 Добавляем GPG ключ Docker..."
        curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

        # Добавляем репозиторий Docker (используем Debian bullseye для совместимости)
        echo "📋 Добавляем репозиторий Docker..."
        echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian bullseye stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

        # Обновляем список пакетов
        echo "🔄 Обновляем список пакетов..."
        sudo apt update

        # Устанавливаем Docker с обработкой ошибок
        echo "🐳 Устанавливаем Docker..."
        if ! sudo apt install -y docker-ce docker-ce-cli containerd.io; then
            echo "⚠️ Ошибка установки некоторых пакетов, пробуем исправить..."
            sudo apt install -f -y
            sudo apt install -y docker-ce docker-ce-cli containerd.io --fix-missing || true
        fi

        # Устанавливаем недостающие пакеты отдельно
        echo "📦 Устанавливаем дополнительные пакеты..."
        sudo apt install -y slirp4netns --fix-missing || echo "⚠️ slirp4netns не установлен, но Docker может работать без него"

        # Создаем группу docker если не существует
        echo "👥 Настраиваем группу docker..."
        sudo groupadd docker 2>/dev/null || true

        # Добавляем пользователя в группу docker
        if [ -n "$SUDO_USER" ]; then
            sudo usermod -aG docker $SUDO_USER
            echo "✅ Пользователь $SUDO_USER добавлен в группу docker"
        else
            sudo usermod -aG docker $USER
            echo "✅ Пользователь $USER добавлен в группу docker"
        fi

        # Запускаем и включаем Docker с проверками
        echo "▶️ Запускаем Docker..."
        if sudo systemctl start docker; then
            echo "✅ Docker запущен"
        else
            echo "⚠️ Ошибка запуска Docker, пробуем перезапустить..."
            sudo systemctl daemon-reload
            sudo systemctl start docker || echo "❌ Не удалось запустить Docker"
        fi

        if sudo systemctl enable docker; then
            echo "✅ Docker добавлен в автозапуск"
        else
            echo "⚠️ Не удалось добавить Docker в автозапуск"
        fi

        # Проверяем статус Docker
        echo "📊 Проверяем статус Docker..."
        sudo systemctl status docker --no-pager || true

    else
        # Для других дистрибутивов используем стандартную установку
        echo "🐧 Используем стандартную установку Docker..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        sudo usermod -aG docker $USER
        rm get-docker.sh
    fi

    # Финальная проверка установки
    echo "🔍 Проверяем установку Docker..."
    if command -v docker &> /dev/null; then
        echo "✅ Docker успешно установлен"
        sudo docker --version

        # Тестируем Docker
        echo "🧪 Тестируем Docker..."
        if sudo docker run --rm hello-world; then
            echo "✅ Docker работает корректно"
        else
            echo "⚠️ Docker установлен, но тест не прошел"
        fi
    else
        echo "❌ Ошибка установки Docker"
        return 1
    fi
}

# Функция установки Docker Compose
install_docker_compose() {
    echo "📦 Устанавливаем Docker Compose..."

    # Сначала пробуем установить через apt (проще и надежнее для Kali)
    echo "📦 Пробуем установить через apt..."
    if sudo apt install -y docker-compose; then
        echo "✅ Docker Compose установлен через apt"
        docker-compose --version
        return 0
    fi

    echo "⚠️ Установка через apt не удалась, пробуем скачать бинарник..."

    # Проверяем архитектуру
    ARCH=$(uname -m)
    if [ "$ARCH" = "x86_64" ]; then
        ARCH="x86_64"
    elif [ "$ARCH" = "aarch64" ]; then
        ARCH="aarch64"
    else
        echo "❌ Неподдерживаемая архитектура: $ARCH"
        return 1
    fi

    # Получаем последнюю версию с повторными попытками
    echo "🔍 Получаем информацию о последней версии..."
    COMPOSE_VERSION=""
    for i in {1..3}; do
        COMPOSE_VERSION=$(curl -s --connect-timeout 10 https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
        if [ -n "$COMPOSE_VERSION" ]; then
            break
        else
            echo "⚠️ Попытка $i получить версию не удалась, повторяем..."
            sleep 2
        fi
    done

    if [ -z "$COMPOSE_VERSION" ]; then
        echo "⚠️ Не удалось получить версию Docker Compose, используем v2.20.2"
        COMPOSE_VERSION="v2.20.2"
    fi

    echo "📥 Скачиваем Docker Compose $COMPOSE_VERSION..."

    # Скачиваем с повторными попытками
    DOWNLOAD_SUCCESS=false
    for i in {1..3}; do
        if sudo curl -L --connect-timeout 30 "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-${ARCH}" -o /usr/local/bin/docker-compose; then
            DOWNLOAD_SUCCESS=true
            break
        else
            echo "⚠️ Попытка $i скачивания не удалась, повторяем..."
            sleep 2
        fi
    done

    # Проверяем успешность скачивания
    if [ "$DOWNLOAD_SUCCESS" = true ] && [ -f "/usr/local/bin/docker-compose" ]; then
        sudo chmod +x /usr/local/bin/docker-compose

        # Создаем символическую ссылку для совместимости
        sudo ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose 2>/dev/null || true

        # Проверяем работу
        if /usr/local/bin/docker-compose --version; then
            echo "✅ Docker Compose установлен и работает"
        else
            echo "❌ Docker Compose установлен, но не работает"
            return 1
        fi
    else
        echo "❌ Ошибка скачивания Docker Compose"
        echo "🔄 Последняя попытка через pip..."

        # Пробуем установить через pip как последний вариант
        if command -v pip3 &> /dev/null; then
            sudo pip3 install docker-compose
        elif command -v pip &> /dev/null; then
            sudo pip install docker-compose
        else
            echo "❌ Все способы установки Docker Compose не удались"
            return 1
        fi
    fi
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
        if install_docker; then
            echo "✅ Docker установлен успешно"

            # Проверяем, можем ли мы запускать docker без sudo
            if docker ps &> /dev/null; then
                echo "✅ Docker готов к использованию"
            else
                echo "🔄 Необходимо перезайти в систему для применения прав Docker"
                echo "Выполните: newgrp docker"
                echo "Или перезайдите в систему и запустите скрипт снова"

                # Пробуем применить права сразу
                echo "🔧 Пробуем применить права сейчас..."
                if newgrp docker <<< "docker ps" &> /dev/null; then
                    echo "✅ Права применены успешно"
                else
                    echo "⚠️ Не удалось применить права автоматически"
                    read -p "Продолжить с sudo? (y/n): " -n 1 -r
                    echo
                    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                        exit 0
                    fi
                fi
            fi
        else
            echo "❌ Ошибка установки Docker"
            exit 1
        fi
    else
        echo "❌ Docker необходим для работы. Установите вручную и запустите скрипт снова."
        exit 1
    fi
else
    echo "✅ Docker уже установлен"
    docker --version

    # Проверяем, работает ли Docker
    if ! docker ps &> /dev/null; then
        echo "⚠️ Docker установлен, но не работает или нет прав"

        # Пробуем запустить Docker
        if sudo systemctl start docker; then
            echo "✅ Docker запущен"
        else
            echo "❌ Не удалось запустить Docker"
            exit 1
        fi

        # Проверяем права пользователя
        if ! groups $USER | grep -q docker; then
            echo "🔧 Добавляем пользователя в группу docker..."
            sudo usermod -aG docker $USER
            echo "🔄 Необходимо перезайти в систему или выполнить: newgrp docker"
        fi
    fi
fi

# Проверяем Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "⚠️ Docker Compose не установлен"
    read -p "Установить Docker Compose автоматически? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if install_docker_compose; then
            echo "✅ Docker Compose установлен успешно"
            docker-compose --version
        else
            echo "❌ Ошибка установки Docker Compose"
            exit 1
        fi
    else
        echo "❌ Docker Compose необходим для работы. Установите вручную и запустите скрипт снова."
        exit 1
    fi
else
    echo "✅ Docker Compose уже установлен"
    docker-compose --version
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

# Функция для проверки и исправления прав Docker
fix_docker_permissions() {
    echo "🔧 Проверяем права Docker..."

    # Проверяем, можем ли запускать docker без sudo
    if docker ps &> /dev/null; then
        echo "✅ Docker работает без sudo"
        return 0
    fi

    echo "⚠️ Docker требует sudo, исправляем права..."

    # Добавляем пользователя в группу docker если не добавлен
    if ! groups $USER | grep -q docker; then
        sudo usermod -aG docker $USER
        echo "✅ Пользователь добавлен в группу docker"
    fi

    # Пробуем применить права через newgrp
    echo "🔄 Применяем права группы..."
    if newgrp docker <<< "docker ps" &> /dev/null; then
        echo "✅ Права применены успешно"
        return 0
    fi

    # Если не получилось, предлагаем варианты
    echo "⚠️ Не удалось применить права автоматически"
    echo "Выберите вариант:"
    echo "1) Продолжить с sudo (может потребовать пароль)"
    echo "2) Перезайти в систему и запустить скрипт снова"
    echo "3) Выполнить 'newgrp docker' и запустить скрипт снова"

    read -p "Ваш выбор (1/2/3): " -n 1 -r
    echo

    case $REPLY in
        1)
            echo "✅ Продолжаем с sudo"
            # Создаем алиас для docker с sudo
            alias docker='sudo docker'
            alias docker-compose='sudo docker-compose'
            return 0
            ;;
        2|3)
            echo "🔄 Перезайдите в систему или выполните: newgrp docker"
            echo "Затем запустите: ./deploy.sh"
            exit 0
            ;;
        *)
            echo "❌ Неверный выбор, выходим"
            exit 1
            ;;
    esac
}

echo "✅ Все зависимости проверены"

# Исправляем права Docker если нужно
fix_docker_permissions

# Определяем команды docker и docker-compose (с sudo или без)
if docker ps &> /dev/null; then
    DOCKER_CMD="docker"
    DOCKER_COMPOSE_CMD="docker-compose"
    echo "✅ Используем docker без sudo"
else
    DOCKER_CMD="sudo docker"
    DOCKER_COMPOSE_CMD="sudo docker-compose"
    echo "⚠️ Используем docker с sudo"
fi

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
$DOCKER_COMPOSE_CMD down

# Удаляем старые образы
echo "🗑️ Удаляем старые образы..."
$DOCKER_COMPOSE_CMD down --rmi all

# Собираем новые образы
echo "🔨 Собираем новые образы..."
if ! $DOCKER_COMPOSE_CMD build --no-cache; then
    echo "❌ Ошибка при сборке образов"
    read -p "Продолжить несмотря на ошибки? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Запускаем контейнеры
echo "▶️ Запускаем контейнеры..."
if ! $DOCKER_COMPOSE_CMD up -d; then
    echo "❌ Ошибка при запуске контейнеров"
    $DOCKER_COMPOSE_CMD logs
    exit 1
fi

# Проверяем статус
echo "📊 Проверяем статус контейнеров..."
$DOCKER_COMPOSE_CMD ps

# Ждем запуска контейнеров
echo "⏳ Ждем запуска контейнеров..."
sleep 10

# Проверяем что все контейнеры запущены
if $DOCKER_COMPOSE_CMD ps | grep -q "Up"; then
    echo "✅ Контейнеры запущены успешно"

    # Проверяем nginx
    if $DOCKER_COMPOSE_CMD ps nginx | grep -q "Up"; then
        echo "✅ Nginx запущен"
    else
        echo "⚠️ Nginx не запущен, проверьте конфигурацию"
    fi

    # Проверяем бота
    if $DOCKER_COMPOSE_CMD ps bot | grep -q "Up"; then
        echo "✅ Бот запущен"
    else
        echo "⚠️ Бот не запущен, проверьте логи"
    fi

    # Проверяем базу данных
    if $DOCKER_COMPOSE_CMD ps postgres | grep -q "Up"; then
        echo "✅ База данных запущена"
    else
        echo "⚠️ База данных не запущена, проверьте конфигурацию"
    fi
else
    echo "❌ Ошибка запуска контейнеров"
    $DOCKER_COMPOSE_CMD logs
    exit 1
fi

echo ""
echo "🎉 Деплой завершен!"
echo "📝 Для просмотра логов: $DOCKER_COMPOSE_CMD logs -f bot"
echo "🌐 Для проверки nginx: $DOCKER_COMPOSE_CMD logs -f nginx"
echo "🛑 Для остановки: $DOCKER_COMPOSE_CMD down"

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
