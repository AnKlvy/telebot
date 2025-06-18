"""
Главный файл телеграм бота
"""
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from utils.config import TOKEN, WEBHOOK_MODE, WEBHOOK_PATH, WEB_SERVER_HOST, WEB_SERVER_PORT, REDIS_ENABLED
from utils.logging_config import setup_logging
from utils.lifecycle import on_startup, on_shutdown, health_check
from utils.redis_manager import RedisManager
from utils.redis_storage import RedisStorage
from common.handlers import router as common_router
from common.register_handlers_and_transitions import register_handlers
from manager.handlers.main import show_manager_main_menu
from manager.handlers import router as manager_router
from student.handlers import router as student_router
from student.handlers.main import show_student_main_menu
from curator.handlers import router as curator_router
from curator.handlers.main import show_curator_main_menu
from teacher.handlers import router as teacher_router
from teacher.handlers.main import show_teacher_main_menu
from admin.handlers import router as admin_router
from admin.handlers.main import show_admin_main_menu
from middlewares.role_middleware import RoleMiddleware
from middlewares.performance_middleware import PerformanceMiddleware

async def start_command(message, user_role: str):
    """Обработчик команды /start, перенаправляющий на соответствующие функции"""
    if user_role == "admin":
        await show_admin_main_menu(message, user_role=user_role)
    elif user_role == "manager":
        await show_manager_main_menu(message, user_role=user_role)
    elif user_role == "curator":
        await show_curator_main_menu(message, user_role=user_role)
    elif user_role == "teacher":
        await show_teacher_main_menu(message, user_role=user_role)
    else:  # По умолчанию считаем пользователя студентом
        await show_student_main_menu(message, user_role=user_role)

async def setup_commands(dp: Dispatcher):
    """Настройка команд бота"""
    try:
        from database import get_db_session, User
        from sqlalchemy import select, func

        # Команда /start доступна всем
        dp.message.register(start_command, CommandStart())

        # Проверяем, есть ли админы в системе
        async with get_db_session() as session:
            result = await session.execute(
                select(func.count(User.id)).where(User.role == 'admin')
            )
            admin_count = result.scalar()

            if admin_count > 0:
                # Если есть админы, регистрируем все команды ролей
                # Доступ к ним будет контролироваться проверками внутри функций
                dp.message.register(show_admin_main_menu, Command("admin"))
                dp.message.register(show_manager_main_menu, Command("manager"))
                dp.message.register(show_curator_main_menu, Command("curator"))
                dp.message.register(show_teacher_main_menu, Command("teacher"))
                dp.message.register(show_student_main_menu, Command("student"))
                logging.info(f"✅ Зарегистрированы все команды ролей (админов в системе: {admin_count})")
            else:
                logging.warning("⚠️ В системе нет админов - команды ролей не зарегистрированы")

    except Exception as e:
        logging.error(f"❌ Ошибка настройки команд: {e}")
        # В случае ошибки регистрируем только базовую команду
        dp.message.register(start_command, CommandStart())

async def main() -> None:
    """Главная функция запуска бота"""
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # Инициализируем хранилище состояний
    storage = None
    if REDIS_ENABLED:
        redis_manager = RedisManager()
        await redis_manager.connect()
        if redis_manager.connected:
            storage = RedisStorage(redis_manager)
            logging.info("✅ Redis Storage инициализирован")
        else:
            logging.warning("⚠️ Redis недоступен, используется MemoryStorage")

    dp = Dispatcher(storage=storage)

    # Регистрируем startup и shutdown хуки
    async def startup_wrapper():
        await on_startup(bot)

    async def shutdown_wrapper():
        await on_shutdown(bot)

    dp.startup.register(startup_wrapper)
    dp.shutdown.register(shutdown_wrapper)

    # Регистрируем middleware для определения роли пользователя
    dp.message.middleware(RoleMiddleware())
    dp.callback_query.middleware(RoleMiddleware())

    # Регистрируем middleware для мониторинга производительности
    performance_middleware = PerformanceMiddleware()
    dp.message.middleware(performance_middleware)
    dp.callback_query.middleware(performance_middleware)

    # Настраиваем команды бота
    await setup_commands(dp)

    # Включаем роутеры для разных ролей
    dp.include_router(common_router)
    dp.include_router(admin_router)
    dp.include_router(student_router)
    dp.include_router(teacher_router)
    dp.include_router(curator_router)
    dp.include_router(manager_router)
    register_handlers()

    if WEBHOOK_MODE:
        # Webhook режим с aiohttp сервером
        app = web.Application()
        app.router.add_get("/health", health_check)

        # Добавляем endpoint для статистики производительности
        async def performance_stats(request):
            """Endpoint для получения статистики производительности"""
            try:
                stats = performance_middleware.get_current_stats()
                return web.json_response(stats)
            except Exception as e:
                return web.json_response({"error": str(e)}, status=500)

        app.router.add_get("/stats", performance_stats)

        # Настраиваем webhook handler
        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
        )
        webhook_requests_handler.register(app, path=WEBHOOK_PATH)
        setup_application(app, dp, bot=bot)

        # Запускаем веб-сервер
        logging.info(f"🚀 Запуск webhook сервера на {WEB_SERVER_HOST}:{WEB_SERVER_PORT}")
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, WEB_SERVER_HOST, WEB_SERVER_PORT)
        await site.start()

        # Ждем сигнал завершения
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            logging.info("🛑 Получен сигнал завершения")
        finally:
            await runner.cleanup()
    else:
        # Polling режим
        logging.info("🚀 Запуск в polling режиме")
        await dp.start_polling(bot)

if __name__ == "__main__":
    setup_logging()
    asyncio.run(main())
