from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter

from admin.utils.common import (
    get_courses_list_kb, get_subjects_list_kb, get_groups_list_kb, get_curators_list_kb,
    get_confirmation_kb, add_curator, remove_curator,
    get_course_by_id, get_subject_by_id, get_group_by_id
)
from common.keyboards import get_home_kb

router = Router()

class AdminCuratorsStates(StatesGroup):
    # Состояния для добавления куратора
    enter_curator_name = State()
    enter_curator_telegram_id = State()
    select_curator_course = State()
    select_curator_subject = State()
    select_curator_group = State()
    confirm_add_curator = State()
    
    # Состояния для удаления куратора
    select_subject_for_curator_deletion = State()
    select_group_for_curator_deletion = State()
    select_curator_to_delete = State()
    confirm_delete_curator = State()

# === ДОБАВЛЕНИЕ КУРАТОРА ===

@router.callback_query(F.data == "add_curator")
async def start_add_curator(callback: CallbackQuery, state: FSMContext):
    """Начать добавление куратора"""
    await callback.message.edit_text(
        text="Введите имя и фамилию куратора:",
        reply_markup=get_home_kb()
    )
    await state.set_state(AdminCuratorsStates.enter_curator_name)

@router.message(StateFilter(AdminCuratorsStates.enter_curator_name))
async def process_curator_name(message: Message, state: FSMContext):
    """Обработать ввод имени куратора"""
    curator_name = message.text.strip()
    await state.update_data(curator_name=curator_name)
    await state.set_state(AdminCuratorsStates.enter_curator_telegram_id)
    
    await message.answer(
        text="Введите Telegram ID куратора:",
        reply_markup=get_home_kb()
    )

@router.message(StateFilter(AdminCuratorsStates.enter_curator_telegram_id))
async def process_curator_telegram_id(message: Message, state: FSMContext):
    """Обработать ввод Telegram ID куратора"""
    try:
        telegram_id = int(message.text.strip())

        # Проверяем, существует ли уже пользователь с таким Telegram ID
        from database import UserRepository
        existing_user = await UserRepository.get_by_telegram_id(telegram_id)

        if existing_user:
            await message.answer(
                text=f"❌ Пользователь с Telegram ID {telegram_id} уже существует!\n"
                     f"Имя: {existing_user.name}\n"
                     f"Роль: {existing_user.role}\n\n"
                     f"Введите другой Telegram ID:",
                reply_markup=get_home_kb()
            )
            return

        await state.update_data(curator_telegram_id=telegram_id)
        await state.set_state(AdminCuratorsStates.select_curator_course)

        await message.answer(
            text="Выберите курс для куратора:",
            reply_markup=await get_courses_list_kb("curator_course")
        )
    except ValueError:
        await message.answer(
            text="❌ Telegram ID должен быть числом. Попробуйте еще раз:",
            reply_markup=get_home_kb()
        )

@router.callback_query(AdminCuratorsStates.select_curator_course, F.data.startswith("curator_course_"))
async def select_curator_course(callback: CallbackQuery, state: FSMContext):
    """Выбрать курс для куратора"""
    course_id = int(callback.data.replace("curator_course_", ""))
    course = await get_course_by_id(course_id)
    
    if not course:
        await callback.message.edit_text(
            text="❌ Курс не найден!",
            reply_markup=get_home_kb()
        )
        return
    
    await state.update_data(curator_course_id=course_id, curator_course_name=course.name)
    await state.set_state(AdminCuratorsStates.select_curator_subject)
    
    await callback.message.edit_text(
        text=f"Курс: {course.name}\n\nВыберите предмет:",
        reply_markup=await get_subjects_list_kb("curator_subject", course_id)
    )

@router.callback_query(AdminCuratorsStates.select_curator_subject, F.data.startswith("curator_subject_"))
async def select_curator_subject(callback: CallbackQuery, state: FSMContext):
    """Выбрать предмет для куратора"""
    subject_id = int(callback.data.replace("curator_subject_", ""))
    data = await state.get_data()
    course_name = data.get("curator_course_name", "")
    
    # Получаем название предмета для отображения
    subject = await get_subject_by_id(subject_id)
    subject_name = subject.name if subject else "Неизвестный предмет"
    
    await state.update_data(curator_subject_id=subject_id, curator_subject_name=subject_name)
    await state.set_state(AdminCuratorsStates.select_curator_group)
    
    await callback.message.edit_text(
        text=f"Курс: {course_name}\nПредмет: {subject_name}\n\nВыберите группу:",
        reply_markup=await get_groups_list_kb("curator_group", subject_id)
    )

@router.callback_query(AdminCuratorsStates.select_curator_group, F.data.startswith("curator_group_"))
async def select_curator_group(callback: CallbackQuery, state: FSMContext):
    """Выбрать группу для куратора"""
    group_id = int(callback.data.replace("curator_group_", ""))
    data = await state.get_data()
    course_name = data.get("curator_course_name", "")
    subject_name = data.get("curator_subject_name", "")
    
    # Получаем информацию о группе
    group = await get_group_by_id(group_id)
    group_name = group.name if group else "Неизвестная группа"
    
    await state.update_data(curator_group_id=group_id, curator_group_name=group_name)
    await state.set_state(AdminCuratorsStates.confirm_add_curator)
    
    curator_name = data.get("curator_name", "")
    telegram_id = data.get("curator_telegram_id", "")
    
    await callback.message.edit_text(
        text=f"📋 Подтверждение добавления куратора:\n\n"
             f"Имя: {curator_name}\n"
             f"Telegram ID: {telegram_id}\n"
             f"Курс: {course_name}\n"
             f"Предмет: {subject_name}\n"
             f"Группа: {group_name}",
        reply_markup=get_confirmation_kb("add", "curator")
    )

@router.callback_query(StateFilter(AdminCuratorsStates.confirm_add_curator), F.data.startswith("confirm_add_curator_"))
async def confirm_add_curator(callback: CallbackQuery, state: FSMContext):
    """Подтвердить добавление куратора"""
    data = await state.get_data()

    curator_name = data.get("curator_name", "")
    telegram_id = data.get("curator_telegram_id", "")
    course_id = data.get("curator_course_id")
    subject_id = data.get("curator_subject_id")
    group_id = data.get("curator_group_id")

    # Добавляем куратора
    success = await add_curator(curator_name, telegram_id, course_id, subject_id, group_id)

    if success:
        await callback.message.edit_text(
            text=f"✅ Куратор '{curator_name}' успешно добавлен!",
            reply_markup=get_home_kb()
        )
    else:
        await callback.message.edit_text(
            text=f"❌ Ошибка при добавлении куратора '{curator_name}'!\nВозможно, пользователь с таким Telegram ID уже существует.",
            reply_markup=get_home_kb()
        )
    
    await state.clear()

# === УДАЛЕНИЕ КУРАТОРА ===

@router.callback_query(F.data == "remove_curator")
async def start_remove_curator(callback: CallbackQuery, state: FSMContext):
    """Начать удаление куратора"""
    await callback.message.edit_text(
        text="Выберите предмет:",
        reply_markup=await get_subjects_list_kb("curator_delete_subject")
    )
    await state.set_state(AdminCuratorsStates.select_subject_for_curator_deletion)

@router.callback_query(AdminCuratorsStates.select_subject_for_curator_deletion, F.data.startswith("curator_delete_subject_"))
async def select_subject_for_curator_deletion(callback: CallbackQuery, state: FSMContext):
    """Выбрать предмет для удаления куратора"""
    subject_id = int(callback.data.replace("curator_delete_subject_", ""))
    
    # Получаем название предмета для отображения
    subject = await get_subject_by_id(subject_id)
    subject_name = subject.name if subject else "Неизвестный предмет"
    
    await state.update_data(deletion_subject_id=subject_id, deletion_subject_name=subject_name)
    await state.set_state(AdminCuratorsStates.select_group_for_curator_deletion)
    
    await callback.message.edit_text(
        text=f"Предмет: {subject_name}\n\nВыберите группу:",
        reply_markup=await get_groups_list_kb("curator_delete_group", subject_id)
    )

@router.callback_query(AdminCuratorsStates.select_group_for_curator_deletion, F.data.startswith("curator_delete_group_"))
async def select_group_for_curator_deletion(callback: CallbackQuery, state: FSMContext):
    """Выбрать группу для удаления куратора"""
    group_id = int(callback.data.replace("curator_delete_group_", ""))
    data = await state.get_data()
    subject_name = data.get("deletion_subject_name", "")
    
    # Получаем информацию о группе
    group = await get_group_by_id(group_id)
    group_name = group.name if group else "Неизвестная группа"
    
    await state.update_data(deletion_group_id=group_id, deletion_group_name=group_name)
    await state.set_state(AdminCuratorsStates.select_curator_to_delete)
    
    await callback.message.edit_text(
        text=f"Предмет: {subject_name}\nГруппа: {group_name}\n\nВыберите куратора для удаления:",
        reply_markup=await get_curators_list_kb("delete_curator", group_id=group_id)
    )

@router.callback_query(AdminCuratorsStates.select_curator_to_delete, F.data.startswith("delete_curator_"))
async def select_curator_to_delete(callback: CallbackQuery, state: FSMContext):
    """Выбрать куратора для удаления"""
    curator_id = int(callback.data.replace("delete_curator_", ""))
    data = await state.get_data()
    subject_name = data.get("deletion_subject_name", "")
    group_name = data.get("deletion_group_name", "")
    
    # Получаем информацию о кураторе
    from database import CuratorRepository
    curator = await CuratorRepository.get_by_id(curator_id)
    
    if not curator:
        await callback.message.edit_text(
            text="❌ Куратор не найден!",
            reply_markup=get_home_kb()
        )
        return
    
    await state.update_data(curator_to_delete_id=curator_id)
    await state.set_state(AdminCuratorsStates.confirm_delete_curator)
    
    await callback.message.edit_text(
        text=f"🗑 Подтверждение удаления куратора:\n\n"
             f"Имя: {curator.user.name}\n"
             f"Telegram ID: {curator.user.telegram_id}\n"
             f"Предмет: {subject_name}\n"
             f"Группа: {group_name}\n\n"
             f"⚠️ Это действие нельзя отменить!",
        reply_markup=get_confirmation_kb("delete", "curator", str(curator_id))
    )

@router.callback_query(StateFilter(AdminCuratorsStates.confirm_delete_curator), F.data.startswith("confirm_delete_curator_"))
async def confirm_delete_curator(callback: CallbackQuery, state: FSMContext):
    """Подтвердить удаление куратора"""
    data = await state.get_data()
    curator_id = data.get("curator_to_delete_id")

    # Получаем имя куратора перед удалением
    from database import CuratorRepository
    curator = await CuratorRepository.get_by_id(curator_id)
    curator_name = curator.user.name if curator else "Неизвестно"

    success = await remove_curator(curator_id)

    if success:
        await callback.message.edit_text(
            text=f"✅ Куратор '{curator_name}' успешно удален!",
            reply_markup=get_home_kb()
        )
    else:
        await callback.message.edit_text(
            text="❌ Куратор не найден!",
            reply_markup=get_home_kb()
        )

    await state.clear()

# === ОТМЕНА ДЕЙСТВИЙ ===

@router.callback_query(StateFilter(AdminCuratorsStates.confirm_add_curator), F.data.startswith("cancel_add_curator"))
async def cancel_add_curator(callback: CallbackQuery, state: FSMContext):
    """Отменить добавление куратора"""
    await callback.message.edit_text(
        text="❌ Добавление куратора отменено",
        reply_markup=get_home_kb()
    )
    await state.clear()

@router.callback_query(StateFilter(AdminCuratorsStates.confirm_delete_curator), F.data.startswith("cancel_delete_curator"))
async def cancel_delete_curator(callback: CallbackQuery, state: FSMContext):
    """Отменить удаление куратора"""
    await callback.message.edit_text(
        text="❌ Удаление куратора отменено",
        reply_markup=get_home_kb()
    )
    await state.clear()
