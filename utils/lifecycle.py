"""
Управление жизненным циклом бота (startup/shutdown)
"""
import logging
import time
from datetime import datetime, timedelta
from aiogram import Bot
from aiogram.types import BotCommand
from database import init_database, close_database
from utils.config import WEBHOOK_MODE, WEBHOOK_URL, REDIS_ENABLED
from utils.redis_manager import RedisManager


async def on_startup(bot: Bot) -> None:
    """Действия при запуске бота"""
    try:
        # Инициализируем подключение к базе данных
        await init_database()
        logging.info("✅ База данных инициализирована")
    except Exception as e:
        logging.error(f"❌ Ошибка инициализации базы данных: {e}")
        logging.warning("⚠️ Продолжаем работу без базы данных")
        # Не прерываем запуск бота

    # Инициализируем Redis если включен
    if REDIS_ENABLED:
        try:
            redis_manager = RedisManager()
            await redis_manager.connect()
            if redis_manager.connected:
                logging.info("✅ Redis подключен успешно")
            else:
                logging.warning("⚠️ Redis недоступен")
        except Exception as e:
            logging.error(f"❌ Ошибка подключения к Redis: {e}")

    # Устанавливаем команды бота
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="admin", description="Панель администратора"),
        BotCommand(command="curator", description="Меню куратора"),
        BotCommand(command="teacher", description="Меню преподавателя"),
        BotCommand(command="manager", description="Меню менеджера"),
        BotCommand(command="student", description="Меню студента")
    ]
    
    try:
        await bot.set_my_commands(commands)
        logging.info("✅ Команды бота установлены")
    except Exception as e:
        logging.error(f"❌ Ошибка установки команд: {e}")
    
    if WEBHOOK_MODE:
        # Устанавливаем webhook
        logging.info(f"🔗 Начинаем установку webhook...")
        logging.info(f"🌐 WEBHOOK_URL: {WEBHOOK_URL}")
        logging.info(f"🔧 WEBHOOK_MODE: {WEBHOOK_MODE}")

        # Проверяем DNS перед установкой webhook
        import socket
        try:
            domain = WEBHOOK_URL.replace('https://', '').replace('http://', '').split('/')[0]
            logging.info(f"🔍 Проверяем DNS для домена: {domain}")
            ip = socket.gethostbyname(domain)
            logging.info(f"✅ DNS резолвинг успешен: {domain} -> {ip}")
        except Exception as dns_error:
            logging.error(f"❌ DNS ошибка для {domain}: {dns_error}")
            logging.error("🔧 Проверьте настройки DNS в docker-compose.yml")

        try:
            logging.info(f"📡 Отправляем запрос на установку webhook: {WEBHOOK_URL}")
            await bot.set_webhook(url=WEBHOOK_URL, drop_pending_updates=True)
            logging.info(f"✅ Webhook установлен успешно: {WEBHOOK_URL}")
        except Exception as e:
            logging.error(f"❌ Ошибка установки webhook: {e}")
            logging.error(f"🔧 URL: {WEBHOOK_URL}")
            logging.error(f"🔧 Тип ошибки: {type(e).__name__}")
            raise
    else:
        # Удаляем webhook для polling режима
        try:
            await bot.delete_webhook(drop_pending_updates=True)
            logging.info("✅ Webhook удален, используется polling")
        except Exception as e:
            logging.error(f"❌ Ошибка удаления webhook: {e}")


async def on_shutdown(bot: Bot) -> None:
    """Действия при остановке бота"""
    try:
        await close_database()
        logging.info("✅ База данных отключена")
    except Exception as e:
        logging.error(f"❌ Ошибка отключения БД: {e}")
    
    if WEBHOOK_MODE:
        try:
            await bot.delete_webhook()
            logging.info("✅ Webhook удален")
        except Exception as e:
            logging.error(f"❌ Ошибка удаления webhook: {e}")


# Глобальные переменные для отслеживания health check логов
_last_health_log_time = 0
_health_log_interval = 30 * 60  # 30 минут в секундах

async def health_check(request):
    """Healthcheck эндпоинт с умным логированием"""
    from aiohttp import web
    global _last_health_log_time

    current_time = time.time()
    should_log = False
    status_code = 200
    response_text = "OK"

    try:
        # Проверяем состояние базы данных
        from database import get_db_session
        async with get_db_session() as session:
            # Простой запрос для проверки соединения
            from sqlalchemy import text
            await session.execute(text("SELECT 1"))

        # Всё в порядке - логируем раз в 30 минут
        if current_time - _last_health_log_time >= _health_log_interval:
            should_log = True
            _last_health_log_time = current_time

    except Exception as e:
        # Проблемы с БД - всегда логируем
        should_log = True
        status_code = 503
        response_text = f"Database Error: {str(e)}"
        logging.error(f"❌ Health check failed: {e}")

    if should_log and status_code == 200:
        logging.info(f"✅ Health check OK (следующий лог через 30 минут)")

    return web.Response(text=response_text, status=status_code)
