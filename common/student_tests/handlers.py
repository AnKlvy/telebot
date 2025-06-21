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
from .menu import show_tests_menu_safe
from ..utils import check_if_id_in_callback_data

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

# Основная функция для обработки главного меню тестов
async def handle_main(callback, state=None, user_role: str = None):
    """Обработчик главного меню тестов"""
    from aiogram.types import CallbackQuery, Message
    from .keyboards import get_tests_menu_kb
    from .states import StudentTestsStates

    text = (
        "🧠 Тест-отчет\n\n"
        "В этом разделе ты можешь пройти входные и контрольные тесты "
        "и посмотреть, как растёт твой уровень знаний.\n\n"
        "Выбери тип теста:"
    )

    if isinstance(callback, CallbackQuery):
        try:
            await callback.message.edit_text(text, reply_markup=get_tests_menu_kb())
        except Exception:
            await callback.message.answer(text, reply_markup=get_tests_menu_kb())
    elif isinstance(callback, Message):
        await callback.answer(text, reply_markup=get_tests_menu_kb())

    if state:
        await state.set_state(StudentTestsStates.main)

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
        await callback.answer(
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
        await callback.answer(
            "Выберите предмет для входного теста месяца:",
            reply_markup=await get_test_subjects_kb("month_entry", user_id=callback.from_user.id)
        )

async def handle_month_entry_subject_selected(callback, state=None, user_role: str = None):
    """Обработчик после выбора предмета для входного теста месяца"""
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
        await callback.answer(
            "Выберите предмет для контрольного теста месяца:",
            reply_markup=await get_test_subjects_kb("month_control", user_id=callback.from_user.id)
        )

async def handle_month_control_subject_selected(callback, state=None, user_role: str = None):
    """Обработчик после выбора предмета для контрольного теста месяца"""
    await handle_month_control_subjects(callback, state, user_role)



# Обработчики для состояний подтверждения
async def handle_course_entry_confirmation(callback, state=None, user_role: str = None):
    """Обработчик состояния подтверждения входного теста курса для навигации"""
    await handle_course_entry_subjects(callback, state, user_role)

async def handle_month_entry_confirmation(callback, state=None, user_role: str = None):
    """Обработчик состояния подтверждения входного теста месяца для навигации"""
    await handle_month_entry_subjects(callback, state, user_role)

async def handle_month_control_confirmation(callback, state=None, user_role: str = None):
    """Обработчик состояния подтверждения контрольного теста месяца для навигации"""
    await handle_month_control_subjects(callback, state, user_role)

# Обработчики для состояний "выбор месяца" (для возврата из результатов)
async def handle_month_entry_month_selected(callback, state=None, user_role: str = None):
    """Обработчик состояния выбора месяца для входного теста месяца"""
    from common.utils import check_if_id_in_callback_data
    from .keyboards import get_month_test_kb
    from aiogram.types import CallbackQuery, Message

    if isinstance(callback, CallbackQuery) and state:
        # Получаем subject_id из callback_data или из состояния
        subject_id = await check_if_id_in_callback_data(
            callback_starts_with="month_entry_sub_",
            callback=callback,
            state=state,
            id_type="subject_id"
        )

        if subject_id:
            await callback.message.edit_text(
                f"Выберите месяц для входного теста:",
                reply_markup=await get_month_test_kb("month_entry", str(subject_id), user_id=callback.from_user.id)
            )
            await state.set_state(StudentTestsStates.month_entry_subject_selected)
            return

    # Если нет данных о предмете, возвращаемся к выбору предмета
    await handle_month_entry_subjects(callback, state, user_role)

async def handle_month_control_month_selected(callback, state=None, user_role: str = None):
    """Обработчик состояния выбора месяца для контрольного теста месяца"""
    print(f"🔥 handle_month_control_month_selected ВЫЗВАН!")
    print(f"🔥 callback.data: {callback.data if hasattr(callback, 'data') else 'НЕТ DATA'}")
    print(f"🔥 callback type: {type(callback)}")

    from .keyboards import get_month_test_kb
    from aiogram.types import CallbackQuery, Message

    if isinstance(callback, CallbackQuery) and state:
        # Получаем subject_id из callback_data или из состояния
        subject_id = await check_if_id_in_callback_data(
            callback_starts_with="month_control_sub_",
            callback=callback,
            state=state,
            id_type="subject_id"
        )

        if subject_id:
            await callback.message.edit_text(
                f"Выберите месяц для контрольного теста:",
                reply_markup=await get_month_test_kb("month_control", str(subject_id), user_id=callback.from_user.id)
            )
            await state.set_state(StudentTestsStates.month_control_subject_selected)
            return

    # Если нет данных о предмете, возвращаемся к выбору предмета
    await handle_month_control_subjects(callback, state, user_role)
