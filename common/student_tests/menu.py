from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from .keyboards import get_tests_menu_kb
from .states import StudentTestsStates

async def show_tests_menu(callback: CallbackQuery, state: FSMContext, user_role: str = None):
    """
    Показать главное меню тестов

    Args:
        callback: Объект CallbackQuery
        state: Контекст состояния FSM
        user_role: Роль пользователя (student, curator)
    """
    text = (
        "🧠 Тест-отчет\n\n"
        "В этом разделе ты можешь пройти входные и контрольные тесты "
        "и посмотреть, как растёт твой уровень знаний.\n\n"
        "Выбери тип теста:"
    )

    await callback.message.edit_text(
        text,
        reply_markup=get_tests_menu_kb()
    )
    await state.set_state(StudentTestsStates.main)


async def show_tests_menu_safe(callback: CallbackQuery, state: FSMContext, user_role: str = None):
    """
    Безопасная версия показа главного меню тестов (для системы навигации)

    Args:
        callback: Объект CallbackQuery
        state: Контекст состояния FSM
        user_role: Роль пользователя (student, curator)
    """
    text = (
        "🧠 Тест-отчет\n\n"
        "В этом разделе ты можешь пройти входные и контрольные тесты "
        "и посмотреть, как растёт твой уровень знаний.\n\n"
        "Выбери тип теста:"
    )

    try:
        # Пытаемся отредактировать сообщение
        await callback.message.edit_text(
            text,
            reply_markup=get_tests_menu_kb()
        )
    except Exception as e:
        # Если не получается отредактировать, отправляем новое сообщение
        await callback.message.answer(
            text,
            reply_markup=get_tests_menu_kb()
        )

    # Устанавливаем состояние только если state не None
    if state:
        await state.set_state(StudentTestsStates.main)