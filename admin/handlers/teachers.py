from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter

from admin.utils.common import (
    get_courses_list_kb, get_subjects_list_kb, get_groups_list_kb, get_teachers_list_kb,
    get_confirmation_kb, add_teacher, remove_teacher,
    get_course_by_id, get_subject_by_id, get_group_by_id
)
from common.keyboards import get_home_kb

router = Router()

class AdminTeachersStates(StatesGroup):
    # Состояния для добавления преподавателя
    enter_teacher_name = State()
    enter_teacher_telegram_id = State()
    select_teacher_course = State()
    select_teacher_subject = State()
    select_teacher_group = State()
    confirm_add_teacher = State()
    
    # Состояния для удаления преподавателя
    select_subject_for_teacher_deletion = State()
    select_group_for_teacher_deletion = State()
    select_teacher_to_delete = State()
    confirm_delete_teacher = State()

# === ДОБАВЛЕНИЕ ПРЕПОДАВАТЕЛЯ ===

@router.callback_query(F.data == "add_teacher")
async def start_add_teacher(callback: CallbackQuery, state: FSMContext):
    """Начать добавление преподавателя"""
    await callback.message.edit_text(
        text="Введите имя и фамилию преподавателя:",
        reply_markup=get_home_kb()
    )
    await state.set_state(AdminTeachersStates.enter_teacher_name)

@router.message(StateFilter(AdminTeachersStates.enter_teacher_name))
async def process_teacher_name(message: Message, state: FSMContext):
    """Обработать ввод имени преподавателя"""
    teacher_name = message.text.strip()
    await state.update_data(teacher_name=teacher_name)
    await state.set_state(AdminTeachersStates.enter_teacher_telegram_id)
    
    await message.answer(
        text="Введите Telegram ID преподавателя:",
        reply_markup=get_home_kb()
    )

@router.message(StateFilter(AdminTeachersStates.enter_teacher_telegram_id))
async def process_teacher_telegram_id(message: Message, state: FSMContext):
    """Обработать ввод Telegram ID преподавателя"""
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

        await state.update_data(teacher_telegram_id=telegram_id)
        await state.set_state(AdminTeachersStates.select_teacher_course)

        await message.answer(
            text="Выберите курс для преподавателя:",
            reply_markup=await get_courses_list_kb("teacher_course")
        )
    except ValueError:
        await message.answer(
            text="❌ Telegram ID должен быть числом. Попробуйте еще раз:",
            reply_markup=get_home_kb()
        )

@router.callback_query(AdminTeachersStates.select_teacher_course, F.data.startswith("teacher_course_"))
async def select_teacher_course(callback: CallbackQuery, state: FSMContext):
    """Выбрать курс для преподавателя"""
    course_id = int(callback.data.replace("teacher_course_", ""))
    course = await get_course_by_id(course_id)
    
    if not course:
        await callback.message.edit_text(
            text="❌ Курс не найден!",
            reply_markup=get_home_kb()
        )
        return
    
    await state.update_data(teacher_course_id=course_id, teacher_course_name=course.name)
    await state.set_state(AdminTeachersStates.select_teacher_subject)
    
    await callback.message.edit_text(
        text=f"Курс: {course.name}\n\nВыберите предмет:",
        reply_markup=await get_subjects_list_kb("teacher_subject", course_id)
    )

@router.callback_query(AdminTeachersStates.select_teacher_subject, F.data.startswith("teacher_subject_"))
async def select_teacher_subject(callback: CallbackQuery, state: FSMContext):
    """Выбрать предмет для преподавателя"""
    subject_id = int(callback.data.replace("teacher_subject_", ""))
    data = await state.get_data()
    course_name = data.get("teacher_course_name", "")
    
    # Получаем название предмета для отображения
    subject = await get_subject_by_id(subject_id)
    subject_name = subject.name if subject else "Неизвестный предмет"
    
    await state.update_data(teacher_subject_id=subject_id, teacher_subject_name=subject_name)
    await state.set_state(AdminTeachersStates.select_teacher_group)
    
    await callback.message.edit_text(
        text=f"Курс: {course_name}\nПредмет: {subject_name}\n\nВыберите группу:",
        reply_markup=await get_groups_list_kb("teacher_group", subject_id)
    )

@router.callback_query(AdminTeachersStates.select_teacher_group, F.data.startswith("teacher_group_"))
async def select_teacher_group(callback: CallbackQuery, state: FSMContext):
    """Выбрать группу для преподавателя"""
    group_id = int(callback.data.replace("teacher_group_", ""))
    data = await state.get_data()
    course_name = data.get("teacher_course_name", "")
    subject_name = data.get("teacher_subject_name", "")
    
    # Получаем информацию о группе
    group = await get_group_by_id(group_id)
    group_name = group.name if group else "Неизвестная группа"
    
    await state.update_data(teacher_group_id=group_id, teacher_group_name=group_name)
    await state.set_state(AdminTeachersStates.confirm_add_teacher)
    
    teacher_name = data.get("teacher_name", "")
    telegram_id = data.get("teacher_telegram_id", "")
    
    await callback.message.edit_text(
        text=f"📋 Подтверждение добавления преподавателя:\n\n"
             f"Имя: {teacher_name}\n"
             f"Telegram ID: {telegram_id}\n"
             f"Курс: {course_name}\n"
             f"Предмет: {subject_name}\n"
             f"Группа: {group_name}",
        reply_markup=get_confirmation_kb("add", "teacher")
    )

@router.callback_query(StateFilter(AdminTeachersStates.confirm_add_teacher), F.data.startswith("confirm_add_teacher_"))
async def confirm_add_teacher(callback: CallbackQuery, state: FSMContext):
    """Подтвердить добавление преподавателя"""
    data = await state.get_data()

    teacher_name = data.get("teacher_name", "")
    telegram_id = data.get("teacher_telegram_id", "")
    course_id = data.get("teacher_course_id")
    subject_id = data.get("teacher_subject_id")
    group_id = data.get("teacher_group_id")

    # Добавляем преподавателя
    success = await add_teacher(teacher_name, telegram_id, course_id, subject_id, group_id)

    if success:
        await callback.message.edit_text(
            text=f"✅ Преподаватель '{teacher_name}' успешно добавлен!",
            reply_markup=get_home_kb()
        )
    else:
        await callback.message.edit_text(
            text=f"❌ Ошибка при добавлении преподавателя '{teacher_name}'!\nВозможно, пользователь с таким Telegram ID уже существует.",
            reply_markup=get_home_kb()
        )
    
    await state.clear()

# === УДАЛЕНИЕ ПРЕПОДАВАТЕЛЯ ===

@router.callback_query(F.data == "remove_teacher")
async def start_remove_teacher(callback: CallbackQuery, state: FSMContext):
    """Начать удаление преподавателя"""
    await callback.message.edit_text(
        text="Выберите предмет:",
        reply_markup=await get_subjects_list_kb("teacher_delete_subject")
    )
    await state.set_state(AdminTeachersStates.select_subject_for_teacher_deletion)

@router.callback_query(AdminTeachersStates.select_subject_for_teacher_deletion, F.data.startswith("teacher_delete_subject_"))
async def select_subject_for_teacher_deletion(callback: CallbackQuery, state: FSMContext):
    """Выбрать предмет для удаления преподавателя"""
    subject_id = int(callback.data.replace("teacher_delete_subject_", ""))
    
    # Получаем название предмета для отображения
    subject = await get_subject_by_id(subject_id)
    subject_name = subject.name if subject else "Неизвестный предмет"
    
    await state.update_data(deletion_subject_id=subject_id, deletion_subject_name=subject_name)
    await state.set_state(AdminTeachersStates.select_group_for_teacher_deletion)
    
    await callback.message.edit_text(
        text=f"Предмет: {subject_name}\n\nВыберите группу:",
        reply_markup=await get_groups_list_kb("teacher_delete_group", subject_id)
    )

@router.callback_query(AdminTeachersStates.select_group_for_teacher_deletion, F.data.startswith("teacher_delete_group_"))
async def select_group_for_teacher_deletion(callback: CallbackQuery, state: FSMContext):
    """Выбрать группу для удаления преподавателя"""
    group_id = int(callback.data.replace("teacher_delete_group_", ""))
    data = await state.get_data()
    subject_name = data.get("deletion_subject_name", "")
    
    # Получаем информацию о группе
    group = await get_group_by_id(group_id)
    group_name = group.name if group else "Неизвестная группа"
    
    await state.update_data(deletion_group_id=group_id, deletion_group_name=group_name)
    await state.set_state(AdminTeachersStates.select_teacher_to_delete)
    
    await callback.message.edit_text(
        text=f"Предмет: {subject_name}\nГруппа: {group_name}\n\nВыберите преподавателя для удаления:",
        reply_markup=await get_teachers_list_kb("delete_teacher", group_id=group_id)
    )

@router.callback_query(AdminTeachersStates.select_teacher_to_delete, F.data.startswith("delete_teacher_"))
async def select_teacher_to_delete(callback: CallbackQuery, state: FSMContext):
    """Выбрать преподавателя для удаления"""
    teacher_id = int(callback.data.replace("delete_teacher_", ""))
    data = await state.get_data()
    subject_name = data.get("deletion_subject_name", "")
    group_name = data.get("deletion_group_name", "")
    
    # Получаем информацию о преподавателе
    from database import TeacherRepository
    teacher = await TeacherRepository.get_by_id(teacher_id)
    
    if not teacher:
        await callback.message.edit_text(
            text="❌ Преподаватель не найден!",
            reply_markup=get_home_kb()
        )
        return
    
    await state.update_data(teacher_to_delete_id=teacher_id)
    await state.set_state(AdminTeachersStates.confirm_delete_teacher)
    
    await callback.message.edit_text(
        text=f"🗑 Подтверждение удаления преподавателя:\n\n"
             f"Имя: {teacher.user.name}\n"
             f"Telegram ID: {teacher.user.telegram_id}\n"
             f"Предмет: {subject_name}\n"
             f"Группа: {group_name}\n\n"
             f"⚠️ Это действие нельзя отменить!",
        reply_markup=get_confirmation_kb("delete", "teacher", str(teacher_id))
    )

@router.callback_query(StateFilter(AdminTeachersStates.confirm_delete_teacher), F.data.startswith("confirm_delete_teacher_"))
async def confirm_delete_teacher(callback: CallbackQuery, state: FSMContext):
    """Подтвердить удаление преподавателя"""
    data = await state.get_data()
    teacher_id = data.get("teacher_to_delete_id")

    # Получаем имя преподавателя перед удалением
    from database import TeacherRepository
    teacher = await TeacherRepository.get_by_id(teacher_id)
    teacher_name = teacher.user.name if teacher else "Неизвестно"

    success = await remove_teacher(teacher_id)

    if success:
        await callback.message.edit_text(
            text=f"✅ Преподаватель '{teacher_name}' успешно удален!",
            reply_markup=get_home_kb()
        )
    else:
        await callback.message.edit_text(
            text="❌ Преподаватель не найден!",
            reply_markup=get_home_kb()
        )

    await state.clear()

# === ОТМЕНА ДЕЙСТВИЙ ===

@router.callback_query(StateFilter(AdminTeachersStates.confirm_add_teacher), F.data.startswith("cancel_add_teacher"))
async def cancel_add_teacher(callback: CallbackQuery, state: FSMContext):
    """Отменить добавление преподавателя"""
    await callback.message.edit_text(
        text="❌ Добавление преподавателя отменено",
        reply_markup=get_home_kb()
    )
    await state.clear()

@router.callback_query(StateFilter(AdminTeachersStates.confirm_delete_teacher), F.data.startswith("cancel_delete_teacher"))
async def cancel_delete_teacher(callback: CallbackQuery, state: FSMContext):
    """Отменить удаление преподавателя"""
    await callback.message.edit_text(
        text="❌ Удаление преподавателя отменено",
        reply_markup=get_home_kb()
    )
    await state.clear()
