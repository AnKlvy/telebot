from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter

from admin.utils.common import (
    students_db, groups_db,
    get_courses_list_kb, get_groups_list_kb, get_people_list_kb, 
    get_confirmation_kb, get_tariff_selection_kb, add_person, remove_person
)
from common.keyboards import get_home_kb
from manager.handlers.lessons import courses_db

router = Router()

class AdminStudentsStates(StatesGroup):
    # Состояния для добавления ученика
    enter_student_name = State()
    enter_student_telegram_id = State()
    select_student_course = State()
    select_student_group = State()
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

        await state.update_data(student_telegram_id=telegram_id)
        await state.set_state(AdminStudentsStates.select_student_course)

        await message.answer(
            text="Выберите курс для ученика:",
            reply_markup=await get_courses_list_kb("student_course")
        )
    except ValueError:
        await message.answer(
            text="❌ Telegram ID должен быть числом. Попробуйте еще раз:",
            reply_markup=get_home_kb()
        )

@router.callback_query(AdminStudentsStates.select_student_course, F.data.startswith("student_course_"))
async def select_student_course(callback: CallbackQuery, state: FSMContext):
    """Выбрать курс для ученика"""
    course_id = int(callback.data.replace("student_course_", ""))
    course = courses_db.get(course_id)
    
    if not course:
        await callback.message.edit_text(
            text="❌ Курс не найден!",
            reply_markup=get_home_kb()
        )
        return
    
    await state.update_data(student_course=course["name"], student_course_id=course_id)
    await state.set_state(AdminStudentsStates.select_student_group)
    
    # Получаем все группы для предметов этого курса
    course_groups = []
    for subject in course["subjects"]:
        if subject in groups_db:
            course_groups.extend(groups_db[subject])
    
    # Создаем клавиатуру с группами курса
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    buttons = []
    
    if not course_groups:
        buttons.append([
            InlineKeyboardButton(text="📝 Групп пока нет", callback_data="no_groups")
        ])
    else:
        for group in course_groups:
            buttons.append([
                InlineKeyboardButton(
                    text=group,
                    callback_data=f"student_group_{group}"
                )
            ])
    
    buttons.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")])
    course_groups_kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback.message.edit_text(
        text=f"Курс: {course['name']}\n\nВыберите группу:",
        reply_markup=course_groups_kb
    )

@router.callback_query(AdminStudentsStates.select_student_group, F.data.startswith("student_group_"))
async def select_student_group(callback: CallbackQuery, state: FSMContext):
    """Выбрать группу для ученика"""
    group = callback.data.replace("student_group_", "")
    data = await state.get_data()
    course_name = data.get("student_course", "")
    
    await state.update_data(student_group=group)
    await state.set_state(AdminStudentsStates.select_student_tariff)
    
    await callback.message.edit_text(
        text=f"Курс: {course_name}\nГруппа: {group}\n\nВыберите тариф:",
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
    course_name = data.get("student_course", "")
    group = data.get("student_group", "")
    
    await state.update_data(student_tariff=tariff_name)
    await state.set_state(AdminStudentsStates.confirm_add_student)
    
    await callback.message.edit_text(
        text=f"📋 Подтверждение добавления:\n\n"
             f"Имя: {student_name}\n"
             f"Telegram ID: {telegram_id}\n"
             f"Курс: {course_name}\n"
             f"Группа: {group}\n"
             f"Тариф: {tariff_name}",
        reply_markup=get_confirmation_kb("add", "student")
    )

@router.callback_query(AdminStudentsStates.confirm_add_student, F.data.startswith("confirm_add_student"))
async def confirm_add_student(callback: CallbackQuery, state: FSMContext):
    """Подтвердить добавление ученика"""
    data = await state.get_data()
    
    student_name = data.get("student_name", "")
    telegram_id = data.get("student_telegram_id", "")
    course = data.get("student_course", "")
    group = data.get("student_group", "")
    tariff = data.get("student_tariff", "")
    
    # Добавляем ученика
    student_id = add_person(students_db, student_name, telegram_id, 
                           course=course, group=group, tariff=tariff)
    
    await callback.message.edit_text(
        text=f"✅ Ученик '{student_name}' успешно добавлен!",
        reply_markup=get_home_kb()
    )
    await state.clear()

# === УДАЛЕНИЕ УЧЕНИКА ===

@router.callback_query(F.data == "remove_student")
async def start_remove_student(callback: CallbackQuery, state: FSMContext):
    """Начать удаление ученика"""
    await callback.message.edit_text(
        text="Выберите курс:",
        reply_markup=get_courses_list_kb("student_delete_course")
    )
    await state.set_state(AdminStudentsStates.select_course_for_student_deletion)

@router.callback_query(AdminStudentsStates.select_course_for_student_deletion, F.data.startswith("student_delete_course_"))
async def select_course_for_student_deletion(callback: CallbackQuery, state: FSMContext):
    """Выбрать курс для удаления ученика"""
    course_id = int(callback.data.replace("student_delete_course_", ""))
    course = courses_db.get(course_id)
    
    if not course:
        await callback.message.edit_text(
            text="❌ Курс не найден!",
            reply_markup=get_home_kb()
        )
        return
    
    await state.update_data(deletion_course=course["name"])
    await state.set_state(AdminStudentsStates.select_group_for_student_deletion)
    
    # Получаем все группы для предметов этого курса
    course_groups = []
    for subject in course["subjects"]:
        if subject in groups_db:
            course_groups.extend(groups_db[subject])
    
    # Создаем клавиатуру с группами курса
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    buttons = []
    
    if not course_groups:
        buttons.append([
            InlineKeyboardButton(text="📝 Групп пока нет", callback_data="no_groups")
        ])
    else:
        for group in course_groups:
            buttons.append([
                InlineKeyboardButton(
                    text=group,
                    callback_data=f"student_delete_group_{group}"
                )
            ])
    
    buttons.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")])
    course_groups_kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback.message.edit_text(
        text=f"Курс: {course['name']}\n\nВыберите группу:",
        reply_markup=course_groups_kb
    )

@router.callback_query(AdminStudentsStates.select_group_for_student_deletion, F.data.startswith("student_delete_group_"))
async def select_group_for_student_deletion(callback: CallbackQuery, state: FSMContext):
    """Выбрать группу для удаления ученика"""
    group = callback.data.replace("student_delete_group_", "")
    data = await state.get_data()
    course = data.get("deletion_course", "")
    
    await state.update_data(deletion_group=group)
    await state.set_state(AdminStudentsStates.select_student_to_delete)
    
    # Фильтруем учеников по курсу и группе
    filtered_students = []
    for student_id, student_data in students_db.items():
        if (student_data.get("course") == course and 
            student_data.get("group") == group):
            filtered_students.append({
                "id": student_id,
                "name": student_data.get("name", "Неизвестно")
            })
    
    from admin.utils.common import get_entity_list_kb
    await callback.message.edit_text(
        text=f"Курс: {course}\nГруппа: {group}\n\nВыберите ученика для удаления:",
        reply_markup=get_entity_list_kb(filtered_students, "delete_student")
    )

@router.callback_query(AdminStudentsStates.select_student_to_delete, F.data.startswith("delete_student_"))
async def select_student_to_delete(callback: CallbackQuery, state: FSMContext):
    """Выбрать ученика для удаления"""
    student_id = callback.data.replace("delete_student_", "")
    student = students_db.get(student_id)
    
    if not student:
        await callback.message.edit_text(
            text="❌ Ученик не найден!",
            reply_markup=get_home_kb()
        )
        return
    
    await state.update_data(student_to_delete=student_id)
    await state.set_state(AdminStudentsStates.confirm_delete_student)
    
    await callback.message.edit_text(
        text=f"🗑 Подтверждение удаления:\n\n"
             f"Имя: {student.get('name', 'Неизвестно')}\n"
             f"Курс: {student.get('course', 'Неизвестно')}\n"
             f"Группа: {student.get('group', 'Неизвестно')}\n"
             f"Тариф: {student.get('tariff', 'Неизвестно')}\n\n"
             f"⚠️ Это действие нельзя отменить!",
        reply_markup=get_confirmation_kb("delete", "student", student_id)
    )

@router.callback_query(AdminStudentsStates.confirm_delete_student, F.data.startswith("confirm_delete_student"))
async def confirm_delete_student(callback: CallbackQuery, state: FSMContext):
    """Подтвердить удаление ученика"""
    data = await state.get_data()
    student_id = data.get("student_to_delete", "")
    
    student = students_db.get(student_id)
    student_name = student.get("name", "Неизвестно") if student else "Неизвестно"
    
    success = remove_person(students_db, student_id)
    
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

@router.callback_query(F.data.startswith("cancel_add_student") | F.data.startswith("cancel_delete_student"))
async def cancel_student_action(callback: CallbackQuery, state: FSMContext):
    """Отменить действие с учеником"""
    await callback.message.edit_text(
        text="❌ Действие отменено",
        reply_markup=get_home_kb()
    )
    await state.clear()
