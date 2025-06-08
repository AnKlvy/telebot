# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . .

# Создаем директорию для логов с правами для всех
RUN mkdir -p /app/logs && chmod 777 /app/logs

# Создаем пользователя для запуска приложения с фиксированным UID
RUN useradd --uid 1001 --create-home --shell /bin/bash telebot && \
    chown -R telebot:telebot /app && \
    chmod 777 /app/logs

USER telebot

# Команда запуска
CMD ["python", "main.py"]
