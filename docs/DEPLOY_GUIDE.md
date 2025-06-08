# Инструкция по деплою телеграм бота на Beget с PostgreSQL в Docker

## 1. Подготовка сервера Beget

### Подключение к серверу
```bash
ssh your_username@your_server.beget.tech
```

### Установка Docker (если не установлен)
```bash
# Обновляем систему
sudo apt update && sudo apt upgrade -y

# Устанавливаем Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Добавляем пользователя в группу docker
sudo usermod -aG docker $USER

# Устанавливаем Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Перезагружаемся для применения изменений
sudo reboot
```

## 2. Загрузка проекта на сервер

### Вариант 1: Через Git (рекомендуется)
```bash
# Клонируем репозиторий
git clone https://github.com/your_username/your_repo.git telebot
cd telebot
```

### Вариант 2: Через SCP/SFTP
```bash
# Загружаем файлы через SCP
scp -r ./telebot your_username@your_server.beget.tech:~/
```

## 3. Безопасная настройка переменных окружения

### Вариант 1: Системные переменные (рекомендуется)
```bash
# Настройка безопасного хранения секретов
chmod +x scripts/setup_env.sh
sudo ./scripts/setup_env.sh

# Редактирование переменных окружения
sudo nano /etc/telebot/env
```

### Вариант 2: Управление секретами через скрипт
```bash
# Настройка секретов
chmod +x scripts/manage_secrets.sh
sudo ./scripts/manage_secrets.sh setup

# Проверка статуса
sudo ./scripts/manage_secrets.sh status
```

### ⚠️ ВАЖНО: Никогда не храните секреты в:
- Файлах проекта (`.env` в корне)
- Git репозитории
- Открытых директориях
- Файлах с широкими правами доступа

Заполните следующие переменные:
- `BOT_TOKEN` - токен от @BotFather
- `POSTGRES_PASSWORD` - надежный пароль для БД (минимум 16 символов)

## 4. Запуск проекта

### Автоматический запуск через скрипт
```bash
# Делаем скрипт исполняемым
chmod +x deploy.sh

# Запускаем деплой
./deploy.sh
```

### Ручной запуск
```bash
# Останавливаем существующие контейнеры
docker-compose down

# Собираем образы
docker-compose build

# Запускаем контейнеры
docker-compose up -d

# Проверяем статус
docker-compose ps

# Смотрим логи
docker-compose logs -f bot
```

## 5. Проверка работы

### Проверка контейнеров
```bash
# Статус всех контейнеров
docker-compose ps

# Логи бота
docker-compose logs bot

# Логи базы данных
docker-compose logs postgres
```

### Проверка базы данных
```bash
# Подключение к PostgreSQL
docker-compose exec postgres psql -U telebot_user -d telebot

# Проверка таблиц
\dt

# Выход из PostgreSQL
\q
```

## 6. Управление проектом

### Остановка
```bash
docker-compose down
```

### Перезапуск
```bash
docker-compose restart
```

### Обновление кода
```bash
# Получаем новый код
git pull origin main

# Пересобираем и перезапускаем
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Просмотр логов
```bash
# Логи в реальном времени
docker-compose logs -f bot

# Последние 100 строк логов
docker-compose logs --tail=100 bot
```

## 7. Резервное копирование

### Создание бэкапа базы данных
```bash
# Создаем бэкап
docker-compose exec postgres pg_dump -U telebot_user telebot > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Восстановление из бэкапа
```bash
# Восстанавливаем из бэкапа
docker-compose exec -T postgres psql -U telebot_user telebot < backup_20250101_120000.sql
```

## 8. Мониторинг

### Настройка автозапуска
```bash
# Создаем systemd сервис
sudo nano /etc/systemd/system/telebot.service
```

Содержимое файла:
```ini
[Unit]
Description=Telegram Bot
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/your_username/telebot
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

```bash
# Включаем автозапуск
sudo systemctl enable telebot.service
sudo systemctl start telebot.service
```

## 9. Безопасность

### Настройка файрвола
```bash
# Разрешаем только необходимые порты
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### Обновление системы
```bash
# Регулярно обновляйте систему
sudo apt update && sudo apt upgrade -y
```

## 10. Решение проблем

### Проблемы с Docker
```bash
# Очистка Docker
docker system prune -a

# Перезапуск Docker
sudo systemctl restart docker
```

### Проблемы с базой данных
```bash
# Пересоздание базы данных
docker-compose down -v
docker-compose up -d
```

### Проблемы с ботом
```bash
# Проверка логов
docker-compose logs bot

# Перезапуск только бота
docker-compose restart bot
```
