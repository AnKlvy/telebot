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

from utils.config import TOKEN, WEBHOOK_MODE, WEBHOOK_PATH, WEB_SERVER_HOST, WEB_SERVER_PORT
from utils.logging_config import setup_logging
from utils.lifecycle import on_startup, on_shutdown, health_check
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

async def start_command(message, user_role: str):
    """Обработчик команды /start, перенаправляющий на соответствующие функции"""
    if user_role == "admin":
        await show_admin_main_menu(message)
    elif user_role == "manager":
        await show_manager_main_menu(message)
    elif user_role == "curator":
        await show_curator_main_menu(message)
    elif user_role == "teacher":
        await show_teacher_main_menu(message)
    else:  # По умолчанию считаем пользователя студентом
        await show_student_main_menu(message)

async def main() -> None:
    """Главная функция запуска бота"""
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # Регистрируем startup и shutdown хуки
    dp.startup.register(lambda: on_startup(bot))
    dp.shutdown.register(lambda: on_shutdown(bot))

    # Регистрируем middleware для определения роли пользователя
    dp.message.middleware(RoleMiddleware())
    dp.callback_query.middleware(RoleMiddleware())

    # Регистрируем команды
    dp.message.register(start_command, CommandStart())
    dp.message.register(show_admin_main_menu, Command("admin"))
    dp.message.register(show_manager_main_menu, Command("manager"))
    dp.message.register(show_curator_main_menu, Command("curator"))
    dp.message.register(show_teacher_main_menu, Command("teacher"))
    dp.message.register(show_student_main_menu, Command("student"))

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
