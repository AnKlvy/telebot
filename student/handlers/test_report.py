from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from common.student_tests.states import StudentTestsStates
from common.student_tests.menu import show_tests_menu
from common.student_tests.handlers import (
    show_course_entry_subjects,
    show_month_entry_subjects,
    show_month_control_subjects,
    handle_course_entry_subject,
    handle_month_entry_subject,
    handle_month_entry_month,
    handle_month_control_subject,
    handle_month_control_month,
    handle_test_answer,
    back_to_tests,
    show_student_course_entry_microtopics_detailed,
    show_student_course_entry_microtopics_summary
)
from common.quiz_registrator import register_quiz_handlers

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

# Регистрируем quiz обработчики для входного теста курса
register_quiz_handlers(
    router=router,
    test_state=StudentTestStates.test_in_progress,
    poll_answer_handler=None,  # Используем стандартный обработчик
    timeout_handler=None,      # Используем стандартный обработчик
    finish_handler=None        # Будем передавать в send_next_question
)

@router.callback_query(F.data == "student_tests")
async def show_student_tests(callback: CallbackQuery, state: FSMContext):
    """Показать меню тестов для студента"""
    await show_tests_menu(callback, state, "student")

# Входной тест курса
@router.callback_query(F.data == "course_entry_test")
async def student_course_entry_test(callback: CallbackQuery, state: FSMContext):
    """Показать предметы для входного теста курса"""
    await show_course_entry_subjects(callback, state)

@router.callback_query(StudentTestStates.select_group_entry, F.data.startswith("course_entry_sub_"))
async def student_handle_course_entry_subject(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора предмета для входного теста курса"""
    await handle_course_entry_subject(callback, state)

# Входной тест месяца
@router.callback_query(F.data == "month_entry_test")
async def student_month_entry_test(callback: CallbackQuery, state: FSMContext):
    """Показать предметы для входного теста месяца"""
    await show_month_entry_subjects(callback, state)

@router.callback_query(StudentTestStates.select_group_entry, F.data.startswith("month_entry_sub_"))
async def student_handle_month_entry_subject(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора предмета для входного теста месяца"""
    await handle_month_entry_subject(callback, state)

@router.callback_query(StudentTestStates.select_month_entry, F.data.startswith("month_entry_"))
async def student_handle_month_entry_month(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора месяца для входного теста месяца"""
    await handle_month_entry_month(callback, state)

# Контрольный тест месяца
@router.callback_query(F.data == "month_control_test")
async def student_month_control_test(callback: CallbackQuery, state: FSMContext):
    """Показать предметы для контрольного теста месяца"""
    await show_month_control_subjects(callback, state)

@router.callback_query(StudentTestStates.select_group_control, F.data.startswith("month_control_sub_"))
async def student_handle_month_control_subject(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора предмета для контрольного теста месяца"""
    await handle_month_control_subject(callback, state)

@router.callback_query(StudentTestStates.select_month_control, F.data.startswith("month_control_"))
async def student_handle_month_control_month(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора месяца для контрольного теста месяца"""
    await handle_month_control_month(callback, state)

# Обработка ответов на вопросы теста
@router.callback_query(StudentTestStates.test_in_progress, F.data.startswith("answer_"))
async def student_handle_test_answer(callback: CallbackQuery, state: FSMContext):
    """Обработка ответа на вопрос теста"""
    await handle_test_answer(callback, state)

# Навигация
@router.callback_query(F.data == "back_to_tests")
async def student_back_to_tests(callback: CallbackQuery, state: FSMContext):
    """Возврат в меню тестов"""
    await back_to_tests(callback, state)