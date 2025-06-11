import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter

from admin.utils.common import add_subject, remove_subject, get_confirmation_kb, get_subjects_list_kb, get_subjects_list, get_subject_by_id
from common.keyboards import back_to_main_button, get_home_kb

async def log(name, role, state):
    logging.info(f"ВЫЗОВ: {name} | РОЛЬ: {role} | СОСТОЯНИЕ: {await state.get_state()}")

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
async def start_add_subject(callback: CallbackQuery, state: FSMContext, user_role: str = None):
    """Начать добавление предмета"""
    await log("start_add_subject", user_role, state)
    await callback.message.edit_text(
        text="Введите название предмета:",
        reply_markup=get_home_kb()
    )
    await state.set_state(AdminSubjectsStates.enter_subject_name)
    await log("start_add_subject_AFTER", user_role, state)

@router.message(StateFilter(AdminSubjectsStates.enter_subject_name))
async def process_subject_name(message: Message, state: FSMContext, user_role: str = None):
    """Обработать ввод названия предмета"""
    await log("process_subject_name", user_role, state)
    subject_name = message.text.strip()

    await state.update_data(subject_name=subject_name)
    await state.set_state(AdminSubjectsStates.confirm_add_subject)

    await message.answer(
        text=f"📋 Подтверждение создания предмета:\n\n"
             f"Название: {subject_name}",
        reply_markup=get_confirmation_kb("add", "subject")
    )
    await log("process_subject_name_AFTER", user_role, state)

@router.callback_query(StateFilter(AdminSubjectsStates.confirm_add_subject), F.data.startswith("confirm_add_subject_"))
async def confirm_add_subject(callback: CallbackQuery, state: FSMContext, user_role: str = None):
    """Подтвердить добавление предмета"""
    await log("confirm_add_subject", user_role, state)
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
    await log("confirm_add_subject_AFTER", user_role, state)

# === УДАЛЕНИЕ ПРЕДМЕТА ===

@router.callback_query(F.data == "remove_subject")
async def start_remove_subject(callback: CallbackQuery, state: FSMContext, user_role: str = None):
    """Начать удаление предмета"""
    await log("start_remove_subject", user_role, state)

    try:
        # Проверяем, есть ли предметы
        subjects = await get_subjects_list()

        if not subjects:
            await callback.message.edit_text(
                text="📋 Список предметов пуст!\n\n"
                     "Сначала добавьте предметы для управления ими.",
                reply_markup=get_home_kb()
            )
            return

        subjects_kb = await get_subjects_list_kb("delete_subject")
        await callback.message.edit_text(
            text="Выберите предмет для удаления:",
            reply_markup=subjects_kb
        )
        await state.set_state(AdminSubjectsStates.select_subject_to_delete)

    except Exception as e:
        await callback.message.edit_text(
            text=f"❌ Ошибка при загрузке списка предметов!\n\n"
                 f"Причина: {str(e)}",
            reply_markup=get_home_kb()
        )

    await log("start_remove_subject_AFTER", user_role, state)

@router.callback_query(StateFilter(AdminSubjectsStates.select_subject_to_delete), F.data.startswith("delete_subject_"))
async def select_subject_to_delete(callback: CallbackQuery, state: FSMContext, user_role: str = None):
    """Выбрать предмет для удаления"""
    await log("select_subject_to_delete", user_role, state)

    try:
        subject_id = int(callback.data.replace("delete_subject_", ""))
        subject = await get_subject_by_id(subject_id)

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

    except ValueError as e:
        await callback.message.edit_text(
            text=f"❌ Ошибка при обработке ID предмета!\n\n"
                 f"Причина: {str(e)}",
            reply_markup=get_home_kb()
        )
    except Exception as e:
        await callback.message.edit_text(
            text=f"❌ Ошибка при загрузке данных предмета!\n\n"
                 f"Причина: {str(e)}",
            reply_markup=get_home_kb()
        )

    await log("select_subject_to_delete_AFTER", user_role, state)

@router.callback_query(StateFilter(AdminSubjectsStates.confirm_delete_subject), F.data.startswith("confirm_delete_subject_"))
async def confirm_delete_subject(callback: CallbackQuery, state: FSMContext, user_role: str = None):
    """Подтвердить удаление предмета"""
    await log("confirm_delete_subject", user_role, state)
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
    await log("confirm_delete_subject_AFTER", user_role, state)

# === ОБРАБОТЧИКИ ОТМЕНЫ ===

@router.callback_query(StateFilter(AdminSubjectsStates.confirm_add_subject), F.data.startswith("cancel_add_subject"))
async def cancel_add_subject(callback: CallbackQuery, state: FSMContext, user_role: str = None):
    """Отменить добавление предмета"""
    await log("cancel_add_subject", user_role, state)
    await callback.message.edit_text(
        text="❌ Добавление предмета отменено",
        reply_markup=get_home_kb()
    )
    await state.clear()
    await log("cancel_add_subject_AFTER", user_role, state)

@router.callback_query(StateFilter(AdminSubjectsStates.confirm_delete_subject), F.data.startswith("cancel_delete_subject"))
async def cancel_delete_subject(callback: CallbackQuery, state: FSMContext, user_role: str = None):
    """Отменить удаление предмета"""
    await log("cancel_delete_subject", user_role, state)
    await callback.message.edit_text(
        text="❌ Удаление предмета отменено",
        reply_markup=get_home_kb()
    )
    await state.clear()
    await log("cancel_delete_subject_AFTER", user_role, state)
