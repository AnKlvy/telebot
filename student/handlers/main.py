from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from ..keyboards.main import get_student_main_menu_kb

router = Router()

class StudentMainStates(StatesGroup):
    main = State()

@router.message(CommandStart())
async def student_start(message: Message, state: FSMContext, user_role: str = None):
    """Начальное меню студента"""
    # Если роль не куратор, показываем меню студента
    if user_role == "student":
        await show_student_main_menu(message)
        await state.set_state(StudentMainStates.main)

async def show_student_main_menu(message: Message, user_role: str = None):
    """Возврат в главное меню студента"""
    # Студенческое меню доступно всем (включая админов и новых пользователей)
    # Не делаем проверку роли, так как это меню по умолчанию

    await message.answer(
        "Привет 👋\n"
        "Здесь ты можешь проходить домашки, прокачивать темы, отслеживать свой прогресс и готовиться к ЕНТ.\n"
        "Ниже — все разделы, которые тебе доступны:",
        reply_markup=get_student_main_menu_kb()
    )