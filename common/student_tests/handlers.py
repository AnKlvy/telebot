"""
Основной файл обработчиков для студентских тестов
Объединяет все модули в единый роутер
"""
import logging
from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

# Импортируем все модули
from .base_handlers import router as base_router
from .course_entry_handlers import router as course_entry_router
from .month_handlers import router as month_handlers_router

# Импортируем функции для использования в других модулях
from .course_entry_handlers import (
    show_course_entry_test_results,
    show_course_entry_test_results_final
)
from .month_handlers import (
    generate_month_test_questions,
    finish_month_entry_test,
    finish_month_control_test,
    show_month_control_test_statistics_final
)
from .base_handlers import (
    show_course_entry_subjects,
    show_month_entry_subjects,
    show_month_control_subjects,
    handle_course_entry_subject,
    handle_month_entry_subject,
    handle_month_entry_month,
    handle_month_control_subject,
    handle_month_control_month,
    back_to_tests,
    show_month_entry_test_statistics,
    show_month_control_test_statistics
)

# Настройка логгера
logger = logging.getLogger(__name__)

# Создаем основной роутер и подключаем все модули
router = Router()
router.include_router(base_router)
router.include_router(course_entry_router)
router.include_router(month_handlers_router)

# Регистрируем обработчики quiz_registrator
from common.quiz_registrator import register_quiz_handlers
from .states import StudentTestsStates

register_quiz_handlers(
    router=router,
    test_state=StudentTestsStates.test_in_progress
)

# Функции для детальной аналитики входного теста курса
async def show_student_course_entry_microtopics_detailed(callback: CallbackQuery, state: FSMContext, test_result_id: int):
    """Показать детальную статистику по микротемам входного теста курса для студента"""
    from database import CourseEntryTestResultRepository
    from common.statistics import format_course_entry_test_detailed_microtopics
    from .keyboards import get_back_to_test_kb

    try:
        test_result = await CourseEntryTestResultRepository.get_by_id(test_result_id)
        if not test_result:
            await callback.message.edit_text(
                "❌ Результат теста не найден",
                reply_markup=get_back_to_test_kb()
            )
            return

        result_text = await format_course_entry_test_detailed_microtopics(test_result)
        await callback.message.edit_text(result_text, reply_markup=get_back_to_test_kb())

    except Exception as e:
        logger.error(f"Ошибка при получении детальной статистики: {e}")
        await callback.message.edit_text(
            "❌ Ошибка при получении детальной статистики",
            reply_markup=get_back_to_test_kb()
        )


async def show_student_course_entry_microtopics_summary(callback: CallbackQuery, state: FSMContext, test_result_id: int):
    """Показать сводку по сильным/слабым темам входного теста курса для студента"""
    from database import CourseEntryTestResultRepository
    from common.statistics import format_course_entry_test_summary_microtopics
    from .keyboards import get_back_to_test_kb

    try:
        test_result = await CourseEntryTestResultRepository.get_by_id(test_result_id)
        if not test_result:
            await callback.message.edit_text(
                "❌ Результат теста не найден",
                reply_markup=get_back_to_test_kb()
            )
            return

        result_text = await format_course_entry_test_summary_microtopics(test_result)
        await callback.message.edit_text(result_text, reply_markup=get_back_to_test_kb())

    except Exception as e:
        logger.error(f"Ошибка при получении сводки: {e}")
        await callback.message.edit_text(
            "❌ Ошибка при получении сводки",
            reply_markup=get_back_to_test_kb()
        )
