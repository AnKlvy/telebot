from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from ..keyboards.main import get_manager_main_menu_kb

router = Router()

class ManagerMainStates(StatesGroup):
    main = State()

@router.message(CommandStart())
async def manager_start(message: Message, state: FSMContext, user_role: str = None):
    """Начальное меню менеджера"""
    # Если роль менеджер, показываем меню менеджера
    if user_role == "manager":
        await show_manager_main_menu(message)
        await state.set_state(ManagerMainStates.main)

async def show_manager_main_menu(message: Message | CallbackQuery, state: FSMContext = None):
    """Показать главное меню менеджера"""
    text = "👨‍💼 <b>Меню менеджера</b>\n\nВыберите нужный раздел:"
    
    if isinstance(message, Message):
        await message.answer(text, reply_markup=get_manager_main_menu_kb())
    else:  # CallbackQuery
        await message.message.edit_text(text, reply_markup=get_manager_main_menu_kb())
    
    if state:
        await state.set_state(ManagerMainStates.main)