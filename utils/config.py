"""
Конфигурация приложения
"""
from os import getenv
from dotenv import load_dotenv

load_dotenv()

# Основные настройки
TOKEN = getenv("BOT_TOKEN")

# Webhook настройки
WEBHOOK_MODE = getenv("WEBHOOK_MODE", "false").lower() == "true"
WEBHOOK_HOST = getenv("WEBHOOK_HOST", "https://your-domain.com")
WEBHOOK_PATH = getenv("WEBHOOK_PATH", "/webhook")
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# Веб-сервер настройки
WEB_SERVER_HOST = getenv("WEB_SERVER_HOST", "0.0.0.0")
WEB_SERVER_PORT = int(getenv("WEB_SERVER_PORT", "8000"))

# Redis настройки
REDIS_ENABLED = getenv("REDIS_ENABLED", "false").lower() == "true"
REDIS_HOST = getenv("REDIS_HOST", "redis")
REDIS_PORT = int(getenv("REDIS_PORT", "6379"))
REDIS_DB = int(getenv("REDIS_DB", "0"))
REDIS_PASSWORD = getenv("REDIS_PASSWORD", None)

# Проверка обязательных переменных
if not TOKEN:
    raise ValueError("BOT_TOKEN не установлен в переменных окружения")

if WEBHOOK_MODE and WEBHOOK_HOST == "https://your-domain.com":
    raise ValueError("WEBHOOK_HOST должен быть настроен для webhook режима")
