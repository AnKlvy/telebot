from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

router = Router()

# Импортируем менеджер навигации
from common.navigation import navigation_manager

@router.callback_query(F.data == "back")
async def go_back(callback: CallbackQuery, state: FSMContext, user_role: str = None):
    await navigation_manager.handle_back(callback, state, user_role)