"""
Управление жизненным циклом бота (startup/shutdown)
"""
import logging
from aiogram import Bot
from aiogram.types import BotCommand
from database import init_database, close_database
from utils.config import WEBHOOK_MODE, WEBHOOK_URL


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
        try:
            await bot.set_webhook(url=WEBHOOK_URL, drop_pending_updates=True)
            logging.info(f"✅ Webhook установлен: {WEBHOOK_URL}")
        except Exception as e:
            logging.error(f"❌ Ошибка установки webhook: {e}")
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


async def health_check(request):
    """Healthcheck эндпоинт"""
    from aiohttp import web
    return web.Response(text="OK")
