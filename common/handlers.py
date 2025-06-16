import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

router = Router()

# Импортируем менеджер навигации
from common.register_handlers_and_transitions import navigation_manager

async def log(name, role, state):
    logging.info(f"ВЫЗОВ: {name} | РОЛЬ: {role} | СОСТОЯНИЕ: {await state.get_state()}")

@router.callback_query(F.data == "back")
async def go_back(callback: CallbackQuery, state: FSMContext, user_role: str = None):
    await log("go_back", user_role, state)
    await navigation_manager.handle_back(callback, state, user_role)

# Регистрация обработчика кнопки "Главное меню"
@router.callback_query(F.data == "back_to_main")
async def back_to_main_handler(callback: CallbackQuery, state: FSMContext, user_role: str):
    await log("back_to_main_handler", user_role, state)

    # Очищаем состояние FSM при переходе в главное меню
    await state.clear()
    logging.info(f"🧹 Состояние FSM очищено для пользователя {callback.from_user.id} при переходе в главное меню")

    await navigation_manager.handle_main_menu(callback, state, user_role)
