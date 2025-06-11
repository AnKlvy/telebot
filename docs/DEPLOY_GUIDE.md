# Инструкция по деплою телеграм бота на Beget с PostgreSQL в Docker

## 1. Подготовка сервера Beget

### Подключение к серверу
```bash
ssh your_username@your_server.beget.tech
```

### Установка зависимостей
Все необходимые зависимости будут установлены автоматически скриптом `deploy.sh`. Скрипт проверит наличие и при необходимости установит:

- Docker
- Docker Compose
- Git
- Certbot (для SSL сертификатов)

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

Скрипт `deploy.sh` автоматически предложит настроить переменные окружения, если они не настроены. Вы также можете настроить их вручную:

```bash
# Настройка безопасного хранения секретов
chmod +x scripts/setup_env.sh
sudo ./scripts/setup_env.sh

# Редактирование переменных окружения
sudo nano /etc/edu_telebot/env
```

### Обязательные переменные окружения:
- `BOT_TOKEN` - токен от @BotFather
- `POSTGRES_PASSWORD` - надежный пароль для БД (минимум 16 символов)
- `WEBHOOK_HOST` - ваш домен (например: https://bot.example.com)

### ⚠️ ВАЖНО: Никогда не храните секреты в:
- Файлах проекта (`.env` в корне)
- Git репозитории
- Открытых директориях
- Файлах с широкими правами доступа

## 4. Настройка SSL для webhook (для максимальной скорости)

Если вы включили режим webhook (`WEBHOOK_MODE=true` в `/etc/edu_telebot/env`), скрипт `deploy.sh` автоматически проверит наличие SSL сертификатов и предложит их настроить. Вы также можете настроить их вручную:

```bash
# Настраиваем SSL сертификат
chmod +x scripts/setup_ssl.sh
sudo ./scripts/setup_ssl.sh
```

## 5. Запуск проекта

### Автоматический запуск через скрипт
```bash
# Делаем скрипт исполняемым
chmod +x deploy.sh

# Запускаем деплой
./deploy.sh
```

Скрипт `deploy.sh` выполнит следующие действия:
1. Проверит и установит все необходимые зависимости
2. Проверит наличие файла с переменными окружения
3. Проверит наличие SSL сертификатов (если включен webhook)
4. Остановит существующие контейнеры
5. Соберет новые образы
6. Запустит контейнеры
7. Проверит статус запущенных контейнеров

### Ручной запуск (если нужно)
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

## 6. Проверка работы

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

## 7. Управление проектом

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
./deploy.sh
```

### Просмотр логов
```bash
# Логи в реальном времени
docker-compose logs -f bot

# Последние 100 строк логов
docker-compose logs --tail=100 bot
```

## 8. Резервное копирование

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

## 9. Мониторинг

### Настройка автозапуска

#### Автоматическая настройка (рекомендуется)
```bash
# Используем готовый скрипт
chmod +x scripts/setup_autostart.sh
./scripts/setup_autostart.sh
```

#### Ручная настройка (если нужно)
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
WorkingDirectory=${PROJECT_DIR}
ExecStart=${DOCKER_COMPOSE_PATH} up -d
ExecStop=${DOCKER_COMPOSE_PATH} down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

**Примечание:** Переменные `${PROJECT_DIR}` и `${DOCKER_COMPOSE_PATH}` будут автоматически заменены скриптом `setup_autostart.sh` на правильные пути.

```bash
# Включаем автозапуск
sudo systemctl enable telebot.service
sudo systemctl start telebot.service
```

## 10. Безопасность

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

## 11. Первоначальная настройка бота

1. Найдите свой Telegram ID (напишите боту `/start`)
2. Временно добавьте свой ID в `admin_ids` в файле `middlewares/role_middleware.py` (строка 26)
3. Перезапустите бота: `docker-compose restart bot`
4. Используйте команду `/admin` для доступа к админ-панели
5. Через админ-панель добавьте себя как администратора в базу данных
6. Уберите свой ID из `admin_ids` в коде (для безопасности)

## 12. Решение проблем

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

### Проблемы с SSL сертификатами
```bash
# Перезапуск скрипта настройки SSL
chmod +x scripts/setup_ssl.sh
sudo ./scripts/setup_ssl.sh
```

### Проблемы с переменными окружения
```bash
# Проверка переменных окружения
sudo cat /etc/edu_telebot/env

# Перенастройка переменных окружения
chmod +x scripts/setup_env.sh
sudo ./scripts/setup_env.sh
```

## Готово! 🚀

Ваш бот запущен и готов к работе.
