from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter

from admin.utils.common import add_subject, remove_subject, get_confirmation_kb
from common.keyboards import back_to_main_button, get_home_kb

router = Router()

class AdminSubjectsStates(StatesGroup):
    # Состояния для добавления предмета
    enter_subject_name = State()
    confirm_add_subject = State()

    # Состояния для удаления предмета
    select_subject_to_delete = State()
    confirm_delete_subject = State()

# === ДОБАВЛЕНИЕ ПРЕДМЕТА ===

@router.callback_query(F.data == "add_subject")
async def start_add_subject(callback: CallbackQuery, state: FSMContext):
    """Начать добавление предмета"""
    await callback.message.edit_text(
        text="Введите название предмета:",
        reply_markup=get_home_kb()
    )
    await state.set_state(AdminSubjectsStates.enter_subject_name)

@router.message(StateFilter(AdminSubjectsStates.enter_subject_name))
async def process_subject_name(message: Message, state: FSMContext):
    """Обработать ввод названия предмета"""
    subject_name = message.text.strip()

    await state.update_data(subject_name=subject_name)
    await state.set_state(AdminSubjectsStates.confirm_add_subject)

    await message.answer(
        text=f"📋 Подтверждение создания предмета:\n\n"
             f"Название: {subject_name}",
        reply_markup=get_confirmation_kb("add", "subject")
    )

@router.callback_query(AdminSubjectsStates.confirm_add_subject, F.data.startswith("confirm_add_subject"))
async def confirm_add_subject(callback: CallbackQuery, state: FSMContext):
    """Подтвердить добавление предмета"""
    data = await state.get_data()
    subject_name = data.get("subject_name", "")

    success = await add_subject(subject_name)

    if success:
        await callback.message.edit_text(
            text=f"✅ Предмет '{subject_name}' успешно создан!",
            reply_markup=get_home_kb()
        )
    else:
        await callback.message.edit_text(
            text=f"❌ Ошибка при создании предмета '{subject_name}'!\n"
                 f"Возможно, предмет с таким названием уже существует.",
            reply_markup=get_home_kb()
        )
    await state.clear()

# === УДАЛЕНИЕ ПРЕДМЕТА ===

async def get_subjects_list_kb(callback_prefix: str = "select_subject"):
    """Клавиатура со списком предметов"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    from database import SubjectRepository

    subjects = await SubjectRepository.get_all()
    buttons = []

    for subject in subjects:
        buttons.append([
            InlineKeyboardButton(
                text=subject.name,
                callback_data=f"{callback_prefix}_{subject.id}"
            )
        ])

    buttons.append(back_to_main_button())
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@router.callback_query(F.data == "remove_subject")
async def start_remove_subject(callback: CallbackQuery, state: FSMContext):
    """Начать удаление предмета"""
    await callback.message.edit_text(
        text="Выберите предмет для удаления:",
        reply_markup=await get_subjects_list_kb("delete_subject")
    )
    await state.set_state(AdminSubjectsStates.select_subject_to_delete)

@router.callback_query(AdminSubjectsStates.select_subject_to_delete, F.data.startswith("delete_subject_"))
async def select_subject_to_delete(callback: CallbackQuery, state: FSMContext):
    """Выбрать предмет для удаления"""
    from database import SubjectRepository

    subject_id = int(callback.data.replace("delete_subject_", ""))
    subject = await SubjectRepository.get_by_id(subject_id)

    if not subject:
        await callback.message.edit_text(
            text="❌ Предмет не найден!",
            reply_markup=get_home_kb()
        )
        return

    await state.update_data(subject_to_delete=subject_id, subject_name=subject.name)
    await state.set_state(AdminSubjectsStates.confirm_delete_subject)

    await callback.message.edit_text(
        text=f"🗑 Подтверждение удаления предмета:\n\n"
             f"Название: {subject.name}\n\n"
             f"⚠️ Это действие нельзя отменить!",
        reply_markup=get_confirmation_kb("delete", "subject", str(subject_id))
    )

@router.callback_query(AdminSubjectsStates.confirm_delete_subject, F.data.startswith("confirm_delete_subject"))
async def confirm_delete_subject(callback: CallbackQuery, state: FSMContext):
    """Подтвердить удаление предмета"""
    data = await state.get_data()
    subject_id = data.get("subject_to_delete")
    subject_name = data.get("subject_name", "Неизвестный предмет")

    success = await remove_subject(subject_id)

    if success:
        await callback.message.edit_text(
            text=f"✅ Предмет '{subject_name}' успешно удален!",
            reply_markup=get_home_kb()
        )
    else:
        await callback.message.edit_text(
            text=f"❌ Ошибка при удалении предмета '{subject_name}'!",
            reply_markup=get_home_kb()
        )

    await state.clear()
