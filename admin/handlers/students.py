from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter

from admin.utils.common import (
    get_courses_list_kb, get_groups_by_course_kb, get_students_list_kb,
    get_confirmation_kb, get_tariff_selection_kb, add_student, remove_student,
    get_course_by_id, get_group_by_id, get_courses_selection_kb, get_student_groups_selection_kb
)
from common.keyboards import get_home_kb

router = Router()

class AdminStudentsStates(StatesGroup):
    # Состояния для добавления ученика
    enter_student_name = State()
    enter_student_telegram_id = State()
    select_student_courses = State()  # Множественный выбор курсов
    select_student_groups = State()   # Множественный выбор групп
    select_student_tariff = State()
    confirm_add_student = State()

    # Состояния для удаления ученика
    select_course_for_student_deletion = State()
    select_group_for_student_deletion = State()
    select_student_to_delete = State()
    confirm_delete_student = State()

# === ДОБАВЛЕНИЕ УЧЕНИКА ===

@router.callback_query(F.data == "add_student")
async def start_add_student(callback: CallbackQuery, state: FSMContext):
    """Начать добавление ученика"""
    await callback.message.edit_text(
        text="Введите имя и фамилию ученика:",
        reply_markup=get_home_kb()
    )
    await state.set_state(AdminStudentsStates.enter_student_name)

@router.message(StateFilter(AdminStudentsStates.enter_student_name))
async def process_student_name(message: Message, state: FSMContext):
    """Обработать ввод имени ученика"""
    student_name = message.text.strip()
    await state.update_data(student_name=student_name)
    await state.set_state(AdminStudentsStates.enter_student_telegram_id)
    
    await message.answer(
        text="Введите Telegram ID ученика:",
        reply_markup=get_home_kb()
    )

@router.message(StateFilter(AdminStudentsStates.enter_student_telegram_id))
async def process_student_telegram_id(message: Message, state: FSMContext):
    """Обработать ввод Telegram ID ученика"""
    try:
        telegram_id = int(message.text.strip())

        # Проверяем существующего пользователя с учетом возможности самоназначения админа
        from admin.utils.common import check_existing_user_for_role_assignment
        check_result = await check_existing_user_for_role_assignment(
            telegram_id, 'student', message.from_user.id
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
                text=check_result['message'] + "\n\nПродолжаем назначение роли студента...",
                reply_markup=get_home_kb()
            )

        await state.update_data(student_telegram_id=telegram_id)
        await state.set_state(AdminStudentsStates.select_student_courses)

        await message.answer(
            text="Выберите курсы для ученика (можно выбрать несколько):\nВыбрано: 0",
            reply_markup=await get_courses_selection_kb([])
        )
    except ValueError:
        await message.answer(
            text="❌ Telegram ID должен быть числом. Попробуйте еще раз:",
            reply_markup=get_home_kb()
        )

# Обработчики множественного выбора курсов
@router.callback_query(AdminStudentsStates.select_student_courses, F.data.startswith("select_course_"))
async def select_course_for_student(callback: CallbackQuery, state: FSMContext):
    """Выбрать курс для студента"""
    course_id = int(callback.data.replace("select_course_", ""))
    data = await state.get_data()

    selected_course_ids = data.get("selected_course_ids", [])
    if course_id not in selected_course_ids:
        selected_course_ids.append(course_id)

    await state.update_data(selected_course_ids=selected_course_ids)

    await callback.message.edit_text(
        text=f"Выберите курсы для ученика (можно выбрать несколько):\nВыбрано: {len(selected_course_ids)}",
        reply_markup=await get_courses_selection_kb(selected_course_ids)
    )

@router.callback_query(AdminStudentsStates.select_student_courses, F.data.startswith("unselect_course_"))
async def unselect_course_for_student(callback: CallbackQuery, state: FSMContext):
    """Отменить выбор курса для студента"""
    course_id = int(callback.data.replace("unselect_course_", ""))
    data = await state.get_data()

    selected_course_ids = data.get("selected_course_ids", [])
    if course_id in selected_course_ids:
        selected_course_ids.remove(course_id)

    await state.update_data(selected_course_ids=selected_course_ids)

    await callback.message.edit_text(
        text=f"Выберите курсы для ученика (можно выбрать несколько):\nВыбрано: {len(selected_course_ids)}",
        reply_markup=await get_courses_selection_kb(selected_course_ids)
    )

@router.callback_query(AdminStudentsStates.select_student_courses, F.data == "finish_course_selection")
async def finish_course_selection_for_student(callback: CallbackQuery, state: FSMContext):
    """Завершить выбор курсов для студента"""
    data = await state.get_data()
    selected_course_ids = data.get("selected_course_ids", [])

    if not selected_course_ids:
        await callback.answer("❌ Выберите хотя бы один курс", show_alert=True)
        return

    # Получаем названия курсов по ID
    from database import CourseRepository
    course_names = []
    for course_id in selected_course_ids:
        course = await CourseRepository.get_by_id(course_id)
        if course:
            course_names.append(course.name)

    await state.update_data(student_course_names=course_names)
    await state.set_state(AdminStudentsStates.select_student_groups)

    await callback.message.edit_text(
        text=f"Курсы: {', '.join(course_names)}\n\nВыберите группы (можно выбрать несколько):\nВыбрано: 0",
        reply_markup=await get_student_groups_selection_kb([], selected_course_ids)
    )

# Обработчики множественного выбора групп для студентов
@router.callback_query(AdminStudentsStates.select_student_groups, F.data.startswith("select_student_group_"))
async def select_group_for_student(callback: CallbackQuery, state: FSMContext):
    """Выбрать группу для студента"""
    group_id = int(callback.data.replace("select_student_group_", ""))
    data = await state.get_data()

    selected_group_ids = data.get("selected_group_ids", [])
    selected_course_ids = data.get("selected_course_ids", [])
    course_names = data.get("student_course_names", [])

    if group_id not in selected_group_ids:
        selected_group_ids.append(group_id)

    await state.update_data(selected_group_ids=selected_group_ids)

    await callback.message.edit_text(
        text=f"Курсы: {', '.join(course_names)}\n\nВыберите группы (можно выбрать несколько):\nВыбрано: {len(selected_group_ids)}",
        reply_markup=await get_student_groups_selection_kb(selected_group_ids, selected_course_ids)
    )

@router.callback_query(AdminStudentsStates.select_student_groups, F.data.startswith("unselect_student_group_"))
async def unselect_group_for_student(callback: CallbackQuery, state: FSMContext):
    """Отменить выбор группы для студента"""
    group_id = int(callback.data.replace("unselect_student_group_", ""))
    data = await state.get_data()

    selected_group_ids = data.get("selected_group_ids", [])
    selected_course_ids = data.get("selected_course_ids", [])
    course_names = data.get("student_course_names", [])

    if group_id in selected_group_ids:
        selected_group_ids.remove(group_id)

    await state.update_data(selected_group_ids=selected_group_ids)

    await callback.message.edit_text(
        text=f"Курсы: {', '.join(course_names)}\n\nВыберите группы (можно выбрать несколько):\nВыбрано: {len(selected_group_ids)}",
        reply_markup=await get_student_groups_selection_kb(selected_group_ids, selected_course_ids)
    )

@router.callback_query(AdminStudentsStates.select_student_groups, F.data == "finish_student_group_selection")
async def finish_group_selection_for_student(callback: CallbackQuery, state: FSMContext):
    """Завершить выбор групп для студента"""
    data = await state.get_data()
    selected_group_ids = data.get("selected_group_ids", [])
    course_names = data.get("student_course_names", [])

    if not selected_group_ids:
        await callback.answer("❌ Выберите хотя бы одну группу", show_alert=True)
        return

    # Получаем названия групп по ID
    from database import GroupRepository
    group_names = []
    for group_id in selected_group_ids:
        group = await GroupRepository.get_by_id(group_id)
        if group:
            group_names.append(f"{group.name} ({group.subject.name})")

    await state.update_data(student_group_names=group_names)
    await state.set_state(AdminStudentsStates.select_student_tariff)

    await callback.message.edit_text(
        text=f"Курсы: {', '.join(course_names)}\nГруппы: {', '.join(group_names)}\n\nВыберите тариф:",
        reply_markup=get_tariff_selection_kb()
    )



@router.callback_query(AdminStudentsStates.select_student_tariff, F.data.startswith("tariff_"))
async def select_student_tariff(callback: CallbackQuery, state: FSMContext):
    """Выбрать тариф для ученика"""
    tariff = callback.data.replace("tariff_", "")
    tariff_name = "Стандарт" if tariff == "standard" else "Премиум"

    data = await state.get_data()
    student_name = data.get("student_name", "")
    telegram_id = data.get("student_telegram_id", "")
    course_names = data.get("student_course_names", [])
    group_names = data.get("student_group_names", [])

    await state.update_data(student_tariff=tariff, student_tariff_name=tariff_name)
    await state.set_state(AdminStudentsStates.confirm_add_student)

    await callback.message.edit_text(
        text=f"📋 Подтверждение добавления:\n\n"
             f"Имя: {student_name}\n"
             f"Telegram ID: {telegram_id}\n"
             f"Курсы: {', '.join(course_names)}\n"
             f"Группы: {', '.join(group_names)}\n"
             f"Тариф: {tariff_name}",
        reply_markup=get_confirmation_kb("add", "student")
    )

@router.callback_query(StateFilter(AdminStudentsStates.confirm_add_student), F.data.startswith("confirm_add_student_"))
async def confirm_add_student(callback: CallbackQuery, state: FSMContext):
    """Подтвердить добавление ученика"""
    data = await state.get_data()

    student_name = data.get("student_name", "")
    telegram_id = data.get("student_telegram_id", "")
    tariff = data.get("student_tariff", "")
    selected_course_ids = data.get("selected_course_ids", [])
    selected_group_ids = data.get("selected_group_ids", [])

    # Добавляем ученика
    success = await add_student(student_name, telegram_id, tariff, selected_course_ids, selected_group_ids)

    if success:
        await callback.message.edit_text(
            text=f"✅ Ученик '{student_name}' успешно добавлен!",
            reply_markup=get_home_kb()
        )
    else:
        await callback.message.edit_text(
            text=f"❌ Ошибка при добавлении ученика '{student_name}'!\nВозможно, пользователь с таким Telegram ID уже существует.",
            reply_markup=get_home_kb()
        )

    await state.clear()

# === УДАЛЕНИЕ УЧЕНИКА ===

@router.callback_query(F.data == "remove_student")
async def start_remove_student(callback: CallbackQuery, state: FSMContext):
    """Начать удаление ученика"""
    await callback.message.edit_text(
        text="Выберите курс:",
        reply_markup=await get_courses_list_kb("student_delete_course")
    )
    await state.set_state(AdminStudentsStates.select_course_for_student_deletion)

@router.callback_query(AdminStudentsStates.select_course_for_student_deletion, F.data.startswith("student_delete_course_"))
async def select_course_for_student_deletion(callback: CallbackQuery, state: FSMContext):
    """Выбрать курс для удаления ученика"""
    course_id = int(callback.data.replace("student_delete_course_", ""))
    course = await get_course_by_id(course_id)

    if not course:
        await callback.message.edit_text(
            text="❌ Курс не найден!",
            reply_markup=get_home_kb()
        )
        return

    await state.update_data(deletion_course_id=course_id, deletion_course_name=course.name)
    await state.set_state(AdminStudentsStates.select_group_for_student_deletion)

    await callback.message.edit_text(
        text=f"Курс: {course.name}\n\nВыберите группу:",
        reply_markup=await get_groups_by_course_kb("student_delete_group", course_id)
    )

@router.callback_query(AdminStudentsStates.select_group_for_student_deletion, F.data.startswith("student_delete_group_"))
async def select_group_for_student_deletion(callback: CallbackQuery, state: FSMContext):
    """Выбрать группу для удаления ученика"""
    group_id = int(callback.data.replace("student_delete_group_", ""))
    data = await state.get_data()
    course_name = data.get("deletion_course_name", "")

    # Получаем информацию о группе
    group = await get_group_by_id(group_id)
    group_name = f"{group.name} ({group.subject.name})" if group else "Неизвестная группа"

    await state.update_data(deletion_group_id=group_id, deletion_group_name=group_name)
    await state.set_state(AdminStudentsStates.select_student_to_delete)

    await callback.message.edit_text(
        text=f"Курс: {course_name}\nГруппа: {group_name}\n\nВыберите ученика для удаления:",
        reply_markup=await get_students_list_kb("delete_student", group_id=group_id)
    )

@router.callback_query(AdminStudentsStates.select_student_to_delete, F.data.startswith("delete_student_"))
async def select_student_to_delete(callback: CallbackQuery, state: FSMContext):
    """Выбрать ученика для удаления"""
    student_id = int(callback.data.replace("delete_student_", ""))
    data = await state.get_data()
    course_name = data.get("deletion_course_name", "")
    group_name = data.get("deletion_group_name", "")

    # Получаем информацию о студенте
    from database import StudentRepository
    student = await StudentRepository.get_by_id(student_id)

    if not student:
        await callback.message.edit_text(
            text="❌ Ученик не найден!",
            reply_markup=get_home_kb()
        )
        return

    await state.update_data(student_to_delete_id=student_id)
    await state.set_state(AdminStudentsStates.confirm_delete_student)

    await callback.message.edit_text(
        text=f"🗑 Подтверждение удаления:\n\n"
             f"Имя: {student.user.name}\n"
             f"Telegram ID: {student.user.telegram_id}\n"
             f"Курс: {course_name}\n"
             f"Группа: {group_name}\n"
             f"Тариф: {student.tariff or 'Не указан'}\n"
             f"Баллы: {student.points}\n"
             f"Уровень: {student.level}\n\n"
             f"⚠️ Это действие нельзя отменить!",
        reply_markup=get_confirmation_kb("delete", "student", str(student_id))
    )

@router.callback_query(StateFilter(AdminStudentsStates.confirm_delete_student), F.data.startswith("confirm_delete_student_"))
async def confirm_delete_student(callback: CallbackQuery, state: FSMContext):
    """Подтвердить удаление ученика"""
    data = await state.get_data()
    student_id = data.get("student_to_delete_id")

    # Получаем имя студента перед удалением
    from database import StudentRepository
    student = await StudentRepository.get_by_id(student_id)
    student_name = student.user.name if student else "Неизвестно"

    success = await remove_student(student_id)

    if success:
        await callback.message.edit_text(
            text=f"✅ Ученик '{student_name}' успешно удален!",
            reply_markup=get_home_kb()
        )
    else:
        await callback.message.edit_text(
            text="❌ Ученик не найден!",
            reply_markup=get_home_kb()
        )

    await state.clear()

# === ОТМЕНА ДЕЙСТВИЙ ===

@router.callback_query(StateFilter(AdminStudentsStates.confirm_add_student), F.data.startswith("cancel_add_student"))
async def cancel_add_student(callback: CallbackQuery, state: FSMContext):
    """Отменить добавление ученика"""
    await callback.message.edit_text(
        text="❌ Добавление ученика отменено",
        reply_markup=get_home_kb()
    )
    await state.clear()

@router.callback_query(StateFilter(AdminStudentsStates.confirm_delete_student), F.data.startswith("cancel_delete_student"))
async def cancel_delete_student(callback: CallbackQuery, state: FSMContext):
    """Отменить удаление ученика"""
    await callback.message.edit_text(
        text="❌ Удаление ученика отменено",
        reply_markup=get_home_kb()
    )
    await state.clear()
