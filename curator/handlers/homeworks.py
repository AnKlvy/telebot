from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from ..keyboards.main import get_curator_main_menu_kb
from common.keyboards import get_courses_kb, get_subjects_kb, get_lessons_kb
from ..keyboards.homeworks import get_homework_menu_kb, get_groups_kb, get_students_by_homework_kb

router = Router()

class HomeworkStates(StatesGroup):
    main = State()
    student_stats_course = State()
    student_stats_group = State()
    student_stats_subject = State()
    student_stats_lesson = State()
    student_stats_list = State()
    group_stats_group = State()
    group_stats_result = State()

@router.callback_query(F.data == "curator_homeworks")
async def show_homework_menu(callback: CallbackQuery, state: FSMContext):
    """Показать меню домашних заданий"""
    await callback.message.edit_text(
        "Выберите тип статистики:",
        reply_markup=get_homework_menu_kb()
    )
    await state.set_state(HomeworkStates.main)

# Обработчики для статистики по ученику
@router.callback_query(HomeworkStates.main, F.data == "hw_student_stats")
async def select_student_stats_course(callback: CallbackQuery, state: FSMContext):
    """Выбор курса для статистики по ученику"""
    await callback.message.edit_text(
        "Выберите курс:",
        reply_markup=get_courses_kb()
    )
    await state.set_state(HomeworkStates.student_stats_course)

@router.callback_query(HomeworkStates.student_stats_course, F.data.startswith("course_"))
async def select_student_stats_group(callback: CallbackQuery, state: FSMContext):
    """Выбор группы для статистики по ученику"""
    course_id = callback.data.replace("course_", "")
    await state.update_data(selected_course=course_id)
    
    await callback.message.edit_text(
        "Выберите группу:",
        reply_markup=get_groups_kb(course_id)
    )
    await state.set_state(HomeworkStates.student_stats_group)

@router.callback_query(HomeworkStates.student_stats_group, F.data.startswith("hw_group_"))
async def select_student_stats_subject(callback: CallbackQuery, state: FSMContext):
    """Выбор предмета для статистики по ученику"""
    group_id = callback.data.replace("hw_group_", "")
    await state.update_data(selected_group=group_id)
    
    await callback.message.edit_text(
        "Выберите предмет:",
        reply_markup=get_subjects_kb()
    )
    await state.set_state(HomeworkStates.student_stats_subject)

@router.callback_query(HomeworkStates.student_stats_subject, F.data.startswith("subject_"))
async def select_student_stats_lesson(callback: CallbackQuery, state: FSMContext):
    """Выбор урока для статистики по ученику"""
    subject_id = callback.data.replace("subject_", "")
    await state.update_data(selected_subject=subject_id)
    
    await callback.message.edit_text(
        "Выберите урок:",
        reply_markup=get_lessons_kb(subject_id)
    )
    await state.set_state(HomeworkStates.student_stats_lesson)

@router.callback_query(HomeworkStates.student_stats_lesson, F.data.startswith("lesson_"))
async def show_student_stats_list(callback: CallbackQuery, state: FSMContext):
    """Показать список учеников с выполненными и невыполненными ДЗ"""
    lesson_id = callback.data.replace("lesson_", "")
    await state.update_data(selected_lesson=lesson_id)
    
    # Получаем данные о выбранных параметрах
    user_data = await state.get_data()
    course_id = user_data.get("selected_course")
    group_id = user_data.get("selected_group")
    subject_id = user_data.get("selected_subject")
    
    # Определяем названия для отображения
    course_names = {"geo": "География", "math": "Математика"}
    subject_names = {
        "kz": "История Казахстана",
        "mathlit": "Математическая грамотность",
        "math": "Математика",
        "geo": "География",
        "bio": "Биология",
        "chem": "Химия",
        "inf": "Информатика",
        "world": "Всемирная история",
        "read": "Грамотность чтения"
    }
    lesson_names = {"lesson1": "Алканы", "lesson2": "Изомерия", "lesson3": "Кислоты"}
    
    course_name = course_names.get(course_id, "Неизвестный курс")
    subject_name = subject_names.get(subject_id, "Неизвестный предмет")
    lesson_name = lesson_names.get(lesson_id, "Неизвестный урок")
    
    await callback.message.edit_text(
        f"Статистика выполнения ДЗ\n"
        f"Курс: {course_name}\n"
        f"Предмет: {subject_name}\n"
        f"Урок: {lesson_name}\n\n"
        "Выберите ученика для просмотра детальной информации или напишите сообщение:",
        reply_markup=get_students_by_homework_kb(lesson_id)
    )
    await state.set_state(HomeworkStates.student_stats_list)

# Обработчики для статистики по группе
@router.callback_query(HomeworkStates.main, F.data == "hw_group_stats")
async def select_group_stats_group(callback: CallbackQuery, state: FSMContext):
    """Выбор группы для статистики по группе"""
    await callback.message.edit_text(
        "Выберите группу для просмотра статистики:",
        reply_markup=get_groups_kb()
    )
    await state.set_state(HomeworkStates.group_stats_group)

@router.callback_query(HomeworkStates.group_stats_group, F.data.startswith("hw_group_"))
async def show_group_stats(callback: CallbackQuery, state: FSMContext):
    """Показать статистику по группе"""
    group_id = callback.data.replace("hw_group_", "")
    
    # В реальном приложении здесь будет запрос к базе данных
    # для получения статистики по группе
    group_stats = {
        "group1": {
            "name": "Интенсив. География",
            "avg_completion": 75,
            "lagging_students": [
                {"id": "user1", "name": "Алтынай Ерланова"}
            ]
        },
        "group2": {
            "name": "Интенсив. Математика",
            "avg_completion": 82,
            "lagging_students": [
                {"id": "user2", "name": "Арман Сериков"}
            ]
        }
    }
    
    stats = group_stats.get(group_id, {
        "name": "Неизвестная группа",
        "avg_completion": 0,
        "lagging_students": []
    })
    
    # Формируем текст с отстающими учениками
    lagging_text = ""
    if stats["lagging_students"]:
        lagging_text = "Список отстающих (не выполняют ДЗ 5 дней подряд):\n"
        for student in stats["lagging_students"]:
            lagging_text += f"• {student['name']}\n"
    else:
        lagging_text = "Отстающих учеников нет."
    
    # Добавляем пояснение к формуле расчета
    formula_explanation = "(формула: % выполнения ДЗ = (выполнено единожды / все дз курса) * 100% и после сумма всех процентов и деление на количество учеников в группе)"
    
    await callback.message.edit_text(
        f"Статистика по группе: {stats['name']}\n\n"
        f"Средний % выполнения: {stats['avg_completion']}% {formula_explanation}\n\n"
        f"{lagging_text}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_homework_menu")]
        ])
    )
    await state.set_state(HomeworkStates.group_stats_result)

# Обработчики для навигации
@router.callback_query(F.data == "back_to_curator_main")
async def back_to_main_menu(callback: CallbackQuery, state: FSMContext):
    """Вернуться в главное меню куратора"""
    await callback.message.edit_text(
        "Добро пожаловать в панель куратора!\n"
        "Выберите действие из меню ниже:",
        reply_markup=get_curator_main_menu_kb()
    )
    await state.clear()

@router.callback_query(F.data == "back_to_homework_menu")
async def back_to_homework_menu(callback: CallbackQuery, state: FSMContext):
    """Вернуться в меню домашних заданий"""
    await show_homework_menu(callback, state)

@router.callback_query(F.data == "back_to_previous")
async def back_to_previous_state(callback: CallbackQuery, state: FSMContext):
    """Вернуться на предыдущий шаг"""
    current_state = await state.get_state()
    
    # Определяем предыдущее состояние и соответствующий обработчик
    if current_state == HomeworkStates.student_stats_course.state:
        await show_homework_menu(callback, state)
    elif current_state == HomeworkStates.student_stats_group.state:
        await select_student_stats_course(callback, state)
    elif current_state == HomeworkStates.student_stats_subject.state:
        await select_student_stats_group(callback, state)
    elif current_state == HomeworkStates.student_stats_lesson.state:
        await select_student_stats_subject(callback, state)
    elif current_state == HomeworkStates.student_stats_list.state:
        await select_student_stats_lesson(callback, state)
    elif current_state == HomeworkStates.group_stats_group.state:
        await show_homework_menu(callback, state)
    else:
        # Если не удалось определить предыдущее состояние, возвращаемся в меню
        await show_homework_menu(callback, state)