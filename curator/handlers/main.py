from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from ..keyboards.main import get_curator_main_menu_kb

router = Router()

class CuratorMainStates(StatesGroup):
    main = State()

@router.message(CommandStart())
async def curator_start(message: Message, state: FSMContext, user_role: str = None):
    """Начальное меню куратора"""
    # Если роль куратор, показываем меню куратора
    if user_role == "curator":
        await show_curator_main_menu(message)
        await state.set_state(CuratorMainStates.main)

async def show_curator_main_menu(message: Message):
    """Показать главное меню куратора"""
    await message.answer(
        "Добро пожаловать в панель куратора!\n"
        "Выберите действие из меню ниже:",
        reply_markup=get_curator_main_menu_kb()
    )