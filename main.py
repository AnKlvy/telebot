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
from student.handlers import router as student_router
from student.handlers.main import show_student_main_menu
from curator.handlers import router as curator_router
from curator.handlers.main import show_curator_main_menu
from middlewares.role_middleware import RoleMiddleware

load_dotenv()

TOKEN = getenv("BOT_TOKEN")

async def start_command(message: Message, user_role: str):
    """Обработчик команды /start, перенаправляющий на соответствующие функции"""
    if user_role == "curator":
        await show_curator_main_menu(message)
    else:  # По умолчанию считаем пользователя студентом
        await show_student_main_menu(message)

async def curator_command(message: Message):
    """Обработчик команды /curator, открывающий меню куратора"""
    await show_curator_main_menu(message)

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
    
    # Включаем роутеры для разных ролей
    dp.include_router(common_router)  # Добавляем первым, чтобы команды /start и /curator были обработаныasync def go_back(callback: CallbackQuery, state: FSMContext, **data):
    dp.include_router(student_router)
    dp.include_router(curator_router)
    register_handlers()  # ← перенос сюда
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
