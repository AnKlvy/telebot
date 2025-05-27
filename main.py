import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from dotenv import load_dotenv
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
from middlewares.role_middleware import RoleMiddleware

load_dotenv()

TOKEN = getenv("BOT_TOKEN")

async def start_command(message: Message, user_role: str):
    """Обработчик команды /start, перенаправляющий на соответствующие функции"""
    if user_role == "manager":
        await show_manager_main_menu(message)
    elif user_role == "curator":
        await show_curator_main_menu(message)
    elif user_role == "teacher":
        await show_teacher_main_menu(message)
    else:  # По умолчанию считаем пользователя студентом
        await show_student_main_menu(message)

async def curator_command(message: Message):
    """Обработчик команды /curator, открывающий меню куратора"""
    await show_curator_main_menu(message)

async def teacher_command(message: Message):
    """Обработчик команды /teacher, открывающий меню преподавателя"""
    await show_teacher_main_menu(message)

async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    
    # Регистрируем middleware для определения роли пользователя
    dp.message.middleware(RoleMiddleware())
    dp.callback_query.middleware(RoleMiddleware())
    
    # Регистрируем обработчик команды /start
    dp.message.register(start_command, CommandStart())
    
    # Регистрируем обработчик команды /curator
    dp.message.register(curator_command, Command("curator"))
    
    # Регистрируем обработчик команды /teacher
    dp.message.register(teacher_command, Command("teacher"))
    
    # Регистрируем обработчик команды /student
    dp.message.register(show_student_main_menu, Command("student"))

    dp.message.register(show_manager_main_menu, Command("manager"))

    # Устанавливаем команды бота в меню
    from aiogram.types import BotCommand
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="curator", description="Меню куратора"),
        BotCommand(command="teacher", description="Меню преподавателя"),
        BotCommand(command="manager", description="Меню менеджера"),
        BotCommand(command="student", description="Меню студента")
    ]
    
    try:
        await bot.set_my_commands(commands)
        logging.info("Команды бота успешно установлены")
    except Exception as e:
        logging.error(f"Ошибка при установке команд бота: {e}")

    # Включаем роутеры для разных ролей
    dp.include_router(common_router)
    dp.include_router(student_router)
    dp.include_router(teacher_router)
    dp.include_router(curator_router)
    dp.include_router(manager_router)
    register_handlers()
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
