from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter

from admin.utils.common import (
    get_courses_list_kb, get_subjects_list_kb, get_groups_list_kb, get_teachers_list_kb,
    get_confirmation_kb, add_teacher, remove_teacher,
    get_course_by_id, get_subject_by_id, get_group_by_id, get_groups_selection_kb
)
from common.keyboards import get_home_kb

router = Router()

class AdminTeachersStates(StatesGroup):
    # Состояния для добавления преподавателя
    enter_teacher_name = State()
    enter_teacher_telegram_id = State()
    select_teacher_course = State()
    select_teacher_subject = State()
    select_teacher_groups = State()  # Множественный выбор групп
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

        # Проверяем существующего пользователя с учетом возможности самоназначения админа
        from admin.utils.common import check_existing_user_for_role_assignment
        check_result = await check_existing_user_for_role_assignment(
            telegram_id, 'teacher', message.from_user.id
        )

        if check_result['exists'] and not check_result['can_assign']:
            await message.answer(
                text=check_result['message'],
                reply_markup=get_home_kb()
            )
            return

        # Если пользователь существует и может быть назначен (админ добавляет себя)
        if check_result['exists'] and check_result['can_assign']:
            await message.answer(
                text=check_result['message'] + "\n\nПродолжаем назначение роли преподавателя...",
                reply_markup=get_home_kb()
            )

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
    
    await state.update_data(teacher_subject_id=subject_id, teacher_subject_name=subject_name, selected_group_ids=[])
    await state.set_state(AdminTeachersStates.select_teacher_groups)

    await callback.message.edit_text(
        text=f"Курс: {course_name}\nПредмет: {subject_name}\n\n"
             f"Выберите группы для преподавателя (можно выбрать несколько):\n"
             f"Выбрано: 0",
        reply_markup=await get_groups_selection_kb([], subject_id)
    )

@router.callback_query(AdminTeachersStates.select_teacher_groups, F.data.startswith("select_group_"))
async def select_group_for_teacher(callback: CallbackQuery, state: FSMContext):
    """Выбрать группу для преподавателя"""
    group_id = int(callback.data.replace("select_group_", ""))
    data = await state.get_data()

    selected_group_ids = data.get("selected_group_ids", [])
    if group_id not in selected_group_ids:
        selected_group_ids.append(group_id)

    await state.update_data(selected_group_ids=selected_group_ids)

    course_name = data.get("teacher_course_name", "")
    subject_name = data.get("teacher_subject_name", "")
    subject_id = data.get("teacher_subject_id")

    await callback.message.edit_text(
        text=f"Курс: {course_name}\nПредмет: {subject_name}\n\n"
             f"Выберите группы для преподавателя (можно выбрать несколько):\n"
             f"Выбрано: {len(selected_group_ids)}",
        reply_markup=await get_groups_selection_kb(selected_group_ids, subject_id)
    )

@router.callback_query(AdminTeachersStates.select_teacher_groups, F.data.startswith("unselect_group_"))
async def unselect_group_for_teacher(callback: CallbackQuery, state: FSMContext):
    """Отменить выбор группы для преподавателя"""
    group_id = int(callback.data.replace("unselect_group_", ""))
    data = await state.get_data()

    selected_group_ids = data.get("selected_group_ids", [])
    if group_id in selected_group_ids:
        selected_group_ids.remove(group_id)

    await state.update_data(selected_group_ids=selected_group_ids)

    course_name = data.get("teacher_course_name", "")
    subject_name = data.get("teacher_subject_name", "")
    subject_id = data.get("teacher_subject_id")

    await callback.message.edit_text(
        text=f"Курс: {course_name}\nПредмет: {subject_name}\n\n"
             f"Выберите группы для преподавателя (можно выбрать несколько):\n"
             f"Выбрано: {len(selected_group_ids)}",
        reply_markup=await get_groups_selection_kb(selected_group_ids, subject_id)
    )

@router.callback_query(AdminTeachersStates.select_teacher_groups, F.data == "finish_group_selection")
async def finish_group_selection_for_teacher(callback: CallbackQuery, state: FSMContext):
    """Завершить выбор групп для преподавателя"""
    data = await state.get_data()
    course_name = data.get("teacher_course_name", "")
    subject_name = data.get("teacher_subject_name", "")
    selected_group_ids = data.get("selected_group_ids", [])

    # Получаем названия групп по ID
    group_names = []
    for group_id in selected_group_ids:
        group = await get_group_by_id(group_id)
        if group:
            group_names.append(group.name)

    groups_text = "\n".join([f"• {name}" for name in group_names])

    await state.update_data(teacher_group_ids=selected_group_ids, teacher_group_names=group_names)
    await state.set_state(AdminTeachersStates.confirm_add_teacher)

    teacher_name = data.get("teacher_name", "")
    telegram_id = data.get("teacher_telegram_id", "")

    await callback.message.edit_text(
        text=f"📋 Подтверждение добавления преподавателя:\n\n"
             f"Имя: {teacher_name}\n"
             f"Telegram ID: {telegram_id}\n"
             f"Курс: {course_name}\n"
             f"Предмет: {subject_name}\n"
             f"Группы ({len(selected_group_ids)}):\n{groups_text}",
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
    group_ids = data.get("teacher_group_ids", [])

    # Добавляем преподавателя
    success = await add_teacher(teacher_name, telegram_id, course_id, subject_id, group_ids)

    if success:
        group_names = data.get("teacher_group_names", [])
        await callback.message.edit_text(
            text=f"✅ Преподаватель '{teacher_name}' успешно добавлен в группы: {', '.join(group_names)}!",
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
