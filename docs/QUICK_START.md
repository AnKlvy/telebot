# Быстрый старт деплоя на Beget

## 1. Подготовка файлов

1. Скопируйте все файлы проекта на сервер Beget
2. Настройте безопасное хранение переменных окружения:

```bash
# Настройка переменных окружения
chmod +x scripts/setup_env.sh
sudo ./scripts/setup_env.sh

# Редактирование переменных
sudo nano /etc/telebot/env
```

Обязательно заполните:
- `BOT_TOKEN` - токен от @BotFather
- `POSTGRES_PASSWORD` - надежный пароль для базы данных
- `WEBHOOK_HOST` - ваш домен (например: https://bot.example.com)

## 2. Настройка SSL (для максимальной скорости)

```bash
# Настраиваем SSL сертификат
chmod +x scripts/setup_ssl.sh
sudo ./scripts/setup_ssl.sh
```

## 3. Запуск

```bash
# Делаем скрипт исполняемым
chmod +x deploy.sh

# Запускаем деплой
./deploy.sh
```

## 4. Проверка

```bash
# Проверяем статус контейнеров
docker-compose ps

# Смотрим логи бота
docker-compose logs -f bot
```

## 5. Управление

```bash
# Остановка
docker-compose down

# Перезапуск
docker-compose restart

# Обновление кода
git pull && docker-compose down && docker-compose build --no-cache && docker-compose up -d
```

## 6. Первоначальная настройка

1. Найдите свой Telegram ID (напишите боту `/start`)
2. Временно добавьте свой ID в `admin_ids` в файле `middlewares/role_middleware.py` (строка 26)
3. Перезапустите бота: `docker-compose restart bot`
4. Используйте команду `/admin` для доступа к админ-панели
5. Через админ-панель добавьте себя как администратора в базу данных
6. Уберите свой ID из `admin_ids` в коде (для безопасности)

## Готово! 🚀

Ваш бот запущен и готов к работе. Полная документация в файле `DEPLOY_GUIDE.md`.
