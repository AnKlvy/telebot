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

async def show_student_main_menu(message: Message):
    """Возврат в главное меню студента"""
    await message.answer(
        "Привет 👋\n"
        "Здесь ты можешь проходить домашки, прокачивать темы, отслеживать свой прогресс и готовиться к ЕНТ.\n"
        "Ниже — все разделы, которые тебе доступны:",
        reply_markup=get_student_main_menu_kb()
    )

@router.callback_query(F.data == "back_to_main")
async def back_to_main_menu(callback: CallbackQuery, state: FSMContext):
    """Возврат в главное меню"""
    await callback.message.delete()
    await show_student_main_menu(callback.message)
    await state.clear()