#!/bin/bash

# Скрипт для установки Docker на Kali Linux

echo "🐉 Установка Docker на Kali Linux..."

# Проверяем права root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Этот скрипт должен запускаться с правами root"
    echo "Запустите: sudo ./scripts/install_docker_kali.sh"
    exit 1
fi

# Удаляем старые версии Docker если есть
echo "🗑️ Удаляем старые версии Docker..."
apt remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

# Обновляем систему
echo "🔄 Обновляем систему..."
apt update

# Устанавливаем зависимости
echo "📦 Устанавливаем зависимости..."
apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    software-properties-common

# Добавляем GPG ключ Docker
echo "🔑 Добавляем GPG ключ Docker..."
curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Добавляем репозиторий Docker (используем Debian bullseye для совместимости с Kali)
echo "📋 Добавляем репозиторий Docker..."
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian bullseye stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Обновляем список пакетов
echo "🔄 Обновляем список пакетов..."
apt update

# Устанавливаем Docker
echo "🐳 Устанавливаем Docker..."
apt install -y docker-ce docker-ce-cli containerd.io

# Проверяем установку
if command -v docker &> /dev/null; then
    echo "✅ Docker успешно установлен"
    docker --version
else
    echo "❌ Ошибка установки Docker"
    exit 1
fi

# Создаем группу docker если не существует
echo "👥 Настраиваем группу docker..."
groupadd docker 2>/dev/null || true

# Добавляем текущего пользователя в группу docker
if [ -n "$SUDO_USER" ]; then
    usermod -aG docker $SUDO_USER
    echo "✅ Пользователь $SUDO_USER добавлен в группу docker"
else
    echo "⚠️ Не удалось определить пользователя для добавления в группу docker"
    echo "Выполните вручную: sudo usermod -aG docker ваш_пользователь"
fi

# Запускаем и включаем Docker
echo "▶️ Запускаем Docker..."
systemctl start docker
systemctl enable docker

# Проверяем статус
echo "📊 Проверяем статус Docker..."
systemctl status docker --no-pager

# Устанавливаем Docker Compose
echo "📦 Устанавливаем Docker Compose..."

# Получаем последнюю версию
COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)

if [ -z "$COMPOSE_VERSION" ]; then
    echo "⚠️ Не удалось получить версию Docker Compose, используем v2.20.2"
    COMPOSE_VERSION="v2.20.2"
fi

echo "📥 Скачиваем Docker Compose $COMPOSE_VERSION..."
curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Проверяем успешность скачивания
if [ $? -eq 0 ]; then
    chmod +x /usr/local/bin/docker-compose
    
    # Создаем символическую ссылку для совместимости
    ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose 2>/dev/null || true
    
    echo "✅ Docker Compose установлен"
    docker-compose --version
else
    echo "❌ Ошибка скачивания Docker Compose"
    echo "Попробуем установить через apt..."
    apt install -y docker-compose
fi

echo ""
echo "🎉 Установка завершена!"
echo ""
echo "📝 Важно:"
echo "   1. Перезайдите в систему или выполните: newgrp docker"
echo "   2. Проверьте работу: docker run hello-world"
echo "   3. Теперь можете запустить: ./deploy.sh"
echo ""
