from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from ..keyboards.main import get_teacher_main_menu_kb

router = Router()

class TeacherMainStates(StatesGroup):
    main = State()

@router.message(CommandStart())
async def teacher_start(message: Message, state: FSMContext, user_role: str = None):
    """Начальное меню преподавателя"""
    # Если роль преподаватель, показываем меню преподавателя
    if user_role == "teacher":
        await show_teacher_main_menu(message)
        await state.set_state(TeacherMainStates.main)

async def show_teacher_main_menu(message: Message | CallbackQuery, state: FSMContext = None, user_role: str = None):
    """Показать главное меню преподавателя"""
    # Проверяем права доступа (админы тоже могут заходить в меню преподавателя)
    if user_role not in ["admin", "teacher"]:
        return

    text = "👨‍🏫 Добро пожаловать в панель <b>преподавателя</b>!\n\nВыберите нужный раздел:"

    if isinstance(message, Message):
        await message.answer(text, reply_markup=get_teacher_main_menu_kb())
    else:  # CallbackQuery
        await message.message.edit_text(text, reply_markup=get_teacher_main_menu_kb())

    if state:
        await state.set_state(TeacherMainStates.main)

@router.callback_query(F.data == "back_to_teacher_main_menu")
async def back_to_teacher_main_menu(callback: CallbackQuery, state: FSMContext):
    """Вернуться в главное меню преподавателя"""
    await show_teacher_main_menu(callback, state)