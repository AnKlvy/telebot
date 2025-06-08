# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Создаем пользователя для запуска приложения с фиксированным UID
RUN useradd --uid 1001 --create-home --shell /bin/bash telebot

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . .

# Создаем директорию для логов и устанавливаем права доступа
RUN mkdir -p /app/logs && chown -R telebot:telebot /app

USER telebot

# Команда запуска
CMD ["python", "main.py"]
