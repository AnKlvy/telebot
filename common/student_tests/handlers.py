"""
Основной файл обработчиков для студентских тестов
Объединяет все модули в единый роутер
"""
import logging
from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from .states import StudentTestsStates

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


# Обработчики состояний для системы навигации
async def handle_main(callback, state=None, user_role: str = None):
    """Обработчик главного меню тестов"""
    from .menu import show_tests_menu_safe
    from aiogram.types import CallbackQuery, Message

    # Если state не передан, создаем фиктивный FSMContext
    if state is None:
        from aiogram.fsm.context import FSMContext
        state = FSMContext(storage=None, key=None)

    # Проверяем тип объекта
    if isinstance(callback, CallbackQuery):
        # Это CallbackQuery - используем безопасную версию
        await show_tests_menu_safe(callback, state, user_role)
    elif isinstance(callback, Message):
        # Это Message - создаем CallbackQuery-подобный объект
        class FakeCallback:
            def __init__(self, message):
                self.message = message
                self.from_user = message.from_user

        fake_callback = FakeCallback(callback)
        await show_tests_menu_safe(fake_callback, state, user_role)
    else:
        # Неизвестный тип - пытаемся обработать как CallbackQuery
        await show_tests_menu_safe(callback, state, user_role)

async def handle_test_result(callback, state=None, user_role: str = None):
    """Обработчик состояния результата теста"""
    await handle_main(callback, state, user_role)

async def handle_test_in_progress(callback, state=None, user_role: str = None):
    """Обработчик состояния прохождения теста"""
    await handle_main(callback, state, user_role)

# Обработчики для входного теста курса
async def handle_course_entry_subjects(callback, state=None, user_role: str = None):
    """Обработчик выбора предметов для входного теста курса"""
    from .keyboards import get_test_subjects_kb
    from aiogram.types import CallbackQuery, Message

    # Обработка разных типов callback
    if isinstance(callback, CallbackQuery):
        # Это CallbackQuery
        await callback.message.edit_text(
            "Выберите предмет для входного теста курса:",
            reply_markup=await get_test_subjects_kb("course_entry", user_id=callback.from_user.id)
        )
        if state:
            await state.set_state(StudentTestsStates.course_entry_subjects)
    elif isinstance(callback, Message):
        # Это Message
        await callback.edit_text(
            "Выберите предмет для входного теста курса:",
            reply_markup=await get_test_subjects_kb("course_entry", user_id=callback.from_user.id)
        )

async def handle_course_entry_subject_selected(callback, state=None, user_role: str = None):
    """Обработчик после выбора предмета для входного теста курса"""
    await handle_course_entry_subjects(callback, state, user_role)

# Обработчики для входного теста месяца
async def handle_month_entry_subjects(callback, state=None, user_role: str = None):
    """Обработчик выбора предметов для входного теста месяца"""
    from .keyboards import get_test_subjects_kb
    from aiogram.types import CallbackQuery, Message

    # Обработка разных типов callback
    if isinstance(callback, CallbackQuery):
        # Это CallbackQuery
        await callback.message.edit_text(
            "Выберите предмет для входного теста месяца:",
            reply_markup=await get_test_subjects_kb("month_entry", user_id=callback.from_user.id)
        )
        if state:
            await state.set_state(StudentTestsStates.month_entry_subjects)
    elif isinstance(callback, Message):
        # Это Message
        await callback.edit_text(
            "Выберите предмет для входного теста месяца:",
            reply_markup=await get_test_subjects_kb("month_entry", user_id=callback.from_user.id)
        )

async def handle_month_entry_subject_selected(callback, state=None, user_role: str = None):
    """Обработчик после выбора предмета для входного теста месяца"""
    await handle_month_entry_subjects(callback, state, user_role)

async def handle_month_entry_month_selected(callback, state=None, user_role: str = None):
    """Обработчик после выбора месяца для входного теста месяца"""
    await handle_month_entry_subjects(callback, state, user_role)

# Обработчики для контрольного теста месяца
async def handle_month_control_subjects(callback, state=None, user_role: str = None):
    """Обработчик выбора предметов для контрольного теста месяца"""
    from .keyboards import get_test_subjects_kb
    from aiogram.types import CallbackQuery, Message

    # Обработка разных типов callback
    if isinstance(callback, CallbackQuery):
        # Это CallbackQuery
        await callback.message.edit_text(
            "Выберите предмет для контрольного теста месяца:",
            reply_markup=await get_test_subjects_kb("month_control", user_id=callback.from_user.id)
        )
        if state:
            await state.set_state(StudentTestsStates.month_control_subjects)
    elif isinstance(callback, Message):
        # Это Message
        await callback.edit_text(
            "Выберите предмет для контрольного теста месяца:",
            reply_markup=await get_test_subjects_kb("month_control", user_id=callback.from_user.id)
        )

async def handle_month_control_subject_selected(callback, state=None, user_role: str = None):
    """Обработчик после выбора предмета для контрольного теста месяца"""
    await handle_month_control_subjects(callback, state, user_role)

async def handle_month_control_month_selected(callback, state=None, user_role: str = None):
    """Обработчик после выбора месяца для контрольного теста месяца"""
    await handle_month_control_subjects(callback, state, user_role)
