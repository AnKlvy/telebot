from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from common.student_tests.states import StudentTestsStates
from common.student_tests.menu import show_tests_menu
from common.student_tests.handlers import (
    show_student_course_entry_microtopics_detailed,
    show_student_course_entry_microtopics_summary
)
# register_quiz_handlers уже используется в common/student_tests/handlers.py

# Используем базовые состояния из common.tests
class StudentTestStates(StudentTestsStates):
    pass

router = Router()

# Регистрируем обработчики для детальной аналитики входного теста курса
@router.callback_query(F.data.startswith("student_course_entry_detailed_"))
async def show_student_course_entry_detailed(callback: CallbackQuery, state: FSMContext):
    """Показать детальную статистику по микротемам входного теста курса для студента"""
    try:
        test_result_id = int(callback.data.replace("student_course_entry_detailed_", ""))
        await show_student_course_entry_microtopics_detailed(callback, state, test_result_id)
    except (ValueError, IndexError):
        from common.student_tests.keyboards import get_back_to_test_kb
        await callback.message.edit_text(
            "❌ Ошибка: неверные параметры",
            reply_markup=get_back_to_test_kb()
        )

@router.callback_query(F.data.startswith("student_course_entry_summary_"))
async def show_student_course_entry_summary(callback: CallbackQuery, state: FSMContext):
    """Показать сводку по сильным/слабым темам входного теста курса для студента"""
    try:
        test_result_id = int(callback.data.replace("student_course_entry_summary_", ""))
        await show_student_course_entry_microtopics_summary(callback, state, test_result_id)
    except (ValueError, IndexError):
        from common.student_tests.keyboards import get_back_to_test_kb
        await callback.message.edit_text(
            "❌ Ошибка: неверные параметры",
            reply_markup=get_back_to_test_kb()
        )

# Quiz обработчики уже зарегистрированы в common/student_tests/handlers.py
# Не дублируем регистрацию

@router.callback_query(F.data == "student_tests")
async def show_student_tests(callback: CallbackQuery, state: FSMContext):
    """Показать меню тестов для студента"""
    await show_tests_menu(callback, state, "student")

# Основные обработчики тестов уже зарегистрированы в common/student_tests/handlers.py
# Здесь оставляем только специфичные для студентов обработчики