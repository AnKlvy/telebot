from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List

from common.keyboards import get_main_menu_back_button, back_to_main_button


async def get_test_subjects_kb(test_type: str, user_id: int = None) -> InlineKeyboardMarkup:
    """
    Клавиатура с предметами для тестов

    Args:
        test_type: Тип теста (course_entry, month_entry, month_control)
        user_id: ID пользователя для фильтрации предметов
    """
    if user_id:
        # Получаем предметы студента из базы данных
        try:
            from database import SubjectRepository
            subjects_db = await SubjectRepository.get_by_user_id(user_id)

            subjects = []
            for subject_db in subjects_db:
                # Используем реальный ID предмета из БД
                subjects.append({
                    "id": str(subject_db.id),  # Используем реальный ID
                    "name": subject_db.name
                })

        except Exception as e:
            print(f"Ошибка при получении предметов студента: {e}")
            # Fallback к пустому списку
            subjects = []
    else:
        # Получаем все предметы из БД (для обратной совместимости)
        try:
            from database import SubjectRepository
            subjects_db = await SubjectRepository.get_all()
            subjects = []
            for subject_db in subjects_db:
                subjects.append({
                    "id": str(subject_db.id),
                    "name": subject_db.name
                })
        except Exception as e:
            print(f"Ошибка при получении всех предметов: {e}")
            subjects = []

    buttons = []
    for subject in subjects:
        buttons.append([
            InlineKeyboardButton(
                text=subject["name"],
                callback_data=f"{test_type}_sub_{subject['id']}"
            )
        ])
    
    # Добавляем кнопку "Назад"
    buttons.extend(get_main_menu_back_button())
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def get_month_test_kb(test_type: str, subject_id: str, user_id: int = None) -> InlineKeyboardMarkup:
    """
    Клавиатура с доступными тестами месяца для предмета

    Args:
        test_type: Тип теста (month_entry, month_control)
        subject_id: ID предмета (строковый, например "math", "chem")
        user_id: ID пользователя для получения его курсов
    """
    buttons = []

    if user_id:
        try:
            from database.repositories.user_repository import UserRepository
            from database.repositories.student_repository import StudentRepository
            from database.repositories.subject_repository import SubjectRepository
            from database.repositories.month_test_repository import MonthTestRepository

            # Получаем пользователя и студента
            user = await UserRepository.get_by_telegram_id(user_id)
            if user:
                student = await StudentRepository.get_by_user_id(user.id)
                if student:
                    # Получаем предмет по ID (теперь subject_id - это реальный ID из БД)
                    try:
                        subject_id_int = int(subject_id)
                        subject = await SubjectRepository.get_by_id(subject_id_int)
                    except (ValueError, TypeError):
                        # Если subject_id не число, пытаемся найти по имени
                        subject = await SubjectRepository.get_by_name(subject_id)

                    if subject:
                        # Получаем курсы студента
                        from database.repositories.course_repository import CourseRepository
                        student_courses = await CourseRepository.get_by_student(student.id)

                        # Ищем тесты месяца для данного предмета в курсах студента
                        available_tests = []
                        for course in student_courses:
                            tests = await MonthTestRepository.get_by_course_subject(course.id, subject.id)
                            # Фильтруем по типу теста
                            test_filter_type = 'entry' if test_type == 'month_entry' else 'control'
                            filtered_tests = [t for t in tests if t.test_type == test_filter_type]
                            available_tests.extend(filtered_tests)

                        # Создаем кнопки для доступных тестов
                        for test in available_tests:
                            buttons.append([
                                InlineKeyboardButton(
                                    text=test.name,
                                    callback_data=f"{test_type}_{subject_id}_test_{test.id}"
                                )
                            ])

        except Exception as e:
            print(f"Ошибка при получении тестов месяца: {e}")

    # Если нет доступных тестов, показываем сообщение
    if not buttons:
        buttons.append([
            InlineKeyboardButton(
                text="📝 Нет доступных тестов",
                callback_data="no_tests_available"
            )
        ])

    # Добавляем кнопку "Назад"
    # back_action = "back_to_month_entry_subjects" if test_type == "month_entry" else "back_to_month_control_subjects"
    buttons.extend(
        get_main_menu_back_button()
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_back_to_test_kb() -> InlineKeyboardMarkup:
    """Клавиатура для возврата в меню тестов"""
    return InlineKeyboardMarkup(inline_keyboard=[
        *get_main_menu_back_button()
    ]
    )

def get_tests_menu_kb() -> InlineKeyboardMarkup:
    """Клавиатура главного меню тестов"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Входной тест курса", callback_data="course_entry_test")],
        [InlineKeyboardButton(text="📊 Входной тест месяца", callback_data="month_entry_test")],
        [InlineKeyboardButton(text="📈 Контрольный тест месяца", callback_data="month_control_test")],
        *get_main_menu_back_button()
    ])