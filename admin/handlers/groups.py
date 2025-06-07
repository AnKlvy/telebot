from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter

from admin.utils.common import (
    groups_db, subjects_db, add_group, remove_group,
    get_subjects_list_kb, get_groups_list_kb, get_confirmation_kb
)
from common.keyboards import get_home_kb

router = Router()

class AdminGroupsStates(StatesGroup):
    # Состояния для добавления группы
    enter_group_name = State()
    select_group_subject = State()
    confirm_add_group = State()
    
    # Состояния для удаления группы
    select_subject_for_group_deletion = State()
    select_group_to_delete = State()
    confirm_delete_group = State()

# === ДОБАВЛЕНИЕ ГРУППЫ ===

@router.callback_query(F.data == "add_group")
async def start_add_group(callback: CallbackQuery, state: FSMContext):
    """Начать добавление группы"""
    await callback.message.edit_text(
        text="Введите название группы:",
        reply_markup=get_home_kb()
    )
    await state.set_state(AdminGroupsStates.enter_group_name)

@router.message(StateFilter(AdminGroupsStates.enter_group_name))
async def process_group_name(message: Message, state: FSMContext):
    """Обработать ввод названия группы"""
    group_name = message.text.strip()
    
    await state.update_data(group_name=group_name)
    await state.set_state(AdminGroupsStates.select_group_subject)
    
    await message.answer(
        text=f"Группа: {group_name}\n\nВыберите предмет, к которому относится группа:",
        reply_markup=get_subjects_list_kb("group_subject")
    )

@router.callback_query(AdminGroupsStates.select_group_subject, F.data.startswith("group_subject_"))
async def select_subject_for_group(callback: CallbackQuery, state: FSMContext):
    """Выбрать предмет для группы"""
    subject = callback.data.replace("group_subject_", "")
    data = await state.get_data()
    group_name = data.get("group_name", "")
    
    await state.update_data(group_subject=subject)
    await state.set_state(AdminGroupsStates.confirm_add_group)
    
    await callback.message.edit_text(
        text=f"📋 Подтверждение создания группы:\n\n"
             f"Название: {group_name}\n"
             f"Предмет: {subject}",
        reply_markup=get_confirmation_kb("add", "group")
    )

@router.callback_query(AdminGroupsStates.confirm_add_group, F.data.startswith("confirm_add_group"))
async def confirm_add_group(callback: CallbackQuery, state: FSMContext):
    """Подтвердить добавление группы"""
    data = await state.get_data()
    group_name = data.get("group_name", "")
    subject = data.get("group_subject", "")
    
    success = add_group(group_name, subject)
    
    if success:
        await callback.message.edit_text(
            text=f"✅ Группа '{group_name}' успешно создана для предмета '{subject}'!",
            reply_markup=get_home_kb()
        )
    else:
        await callback.message.edit_text(
            text=f"❌ Группа '{group_name}' уже существует для предмета '{subject}'!",
            reply_markup=get_home_kb()
        )
    
    await state.clear()

# === УДАЛЕНИЕ ГРУППЫ ===

@router.callback_query(F.data == "remove_group")
async def start_remove_group(callback: CallbackQuery, state: FSMContext):
    """Начать удаление группы"""
    await callback.message.edit_text(
        text="Выберите предмет:",
        reply_markup=get_subjects_list_kb("group_delete_subject")
    )
    await state.set_state(AdminGroupsStates.select_subject_for_group_deletion)

@router.callback_query(AdminGroupsStates.select_subject_for_group_deletion, F.data.startswith("group_delete_subject_"))
async def select_subject_for_group_deletion(callback: CallbackQuery, state: FSMContext):
    """Выбрать предмет для удаления группы"""
    subject = callback.data.replace("group_delete_subject_", "")
    
    await state.update_data(deletion_subject=subject)
    await state.set_state(AdminGroupsStates.select_group_to_delete)
    
    await callback.message.edit_text(
        text=f"Предмет: {subject}\n\nВыберите группу для удаления:",
        reply_markup=get_groups_list_kb("delete_group", subject)
    )

@router.callback_query(AdminGroupsStates.select_group_to_delete, F.data.startswith("delete_group_"))
async def select_group_to_delete(callback: CallbackQuery, state: FSMContext):
    """Выбрать группу для удаления"""
    group_name = callback.data.replace("delete_group_", "")
    data = await state.get_data()
    subject = data.get("deletion_subject", "")
    
    await state.update_data(group_to_delete=group_name)
    await state.set_state(AdminGroupsStates.confirm_delete_group)
    
    await callback.message.edit_text(
        text=f"🗑 Подтверждение удаления группы:\n\n"
             f"Группа: {group_name}\n"
             f"Предмет: {subject}\n\n"
             f"⚠️ Это действие нельзя отменить!",
        reply_markup=get_confirmation_kb("delete", "group", group_name)
    )

@router.callback_query(AdminGroupsStates.confirm_delete_group, F.data.startswith("confirm_delete_group"))
async def confirm_delete_group(callback: CallbackQuery, state: FSMContext):
    """Подтвердить удаление группы"""
    data = await state.get_data()
    group_name = data.get("group_to_delete", "")
    subject = data.get("deletion_subject", "")
    
    success = remove_group(group_name, subject)
    
    if success:
        await callback.message.edit_text(
            text=f"✅ Группа '{group_name}' успешно удалена из предмета '{subject}'!",
            reply_markup=get_home_kb()
        )
    else:
        await callback.message.edit_text(
            text=f"❌ Группа '{group_name}' не найдена в предмете '{subject}'!",
            reply_markup=get_home_kb()
        )
    
    await state.clear()

# === ОТМЕНА ДЕЙСТВИЙ ===

@router.callback_query(F.data.startswith("cancel_add_group") | F.data.startswith("cancel_delete_group"))
async def cancel_group_action(callback: CallbackQuery, state: FSMContext):
    """Отменить действие с группой"""
    await callback.message.edit_text(
        text="❌ Действие отменено",
        reply_markup=get_home_kb()
    )
    await state.clear()
