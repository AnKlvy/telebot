from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from common.student_tests.states import StudentTestsStates
from common.student_tests.menu import show_tests_menu
 # register_quiz_handlers уже используется в common/student_tests/handlers.py

# Используем базовые состояния из common.tests
class StudentTestStates(StudentTestsStates):
    pass

router = Router()

# Обработчики для детальной аналитики входного теста курса перенесены в common/student_tests/base_handlers.py

# Quiz обработчики уже зарегистрированы в common/student_tests/handlers.py
# Не дублируем регистрацию

@router.callback_query(F.data == "student_tests")
async def show_student_tests(callback: CallbackQuery, state: FSMContext):
    """Показать меню тестов для студента"""
    await show_tests_menu(callback, state, "student")

# Основные обработчики тестов уже зарегистрированы в common/student_tests/handlers.py
# Здесь оставляем только специфичные для студентов обработчики