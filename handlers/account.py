from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from keyboards.account import get_account_kb

router = Router()

class AccountStates(StatesGroup):
    main = State()

@router.callback_query(F.data == "account")
async def show_account_info(callback: CallbackQuery, state: FSMContext):
    """Показать информацию об аккаунте пользователя"""
    # В реальном приложении здесь будет логика получения информации об аккаунте из базы данных
    # Для примера используем фиксированные значения
    account_info = {
        "course": "ЕНТ. Интенсив. Химия",
        "group": "Химия Премиум",
        "tariff": "Премиум",
        "start_date": "01.05.2025",
        "subjects": ["Химия", "Биология", "История Казахстана"]
    }
    
    subjects_str = ", ".join(account_info["subjects"])
    
    await callback.message.edit_text(
        "❓ Аккаунт\n"
        f"📚 Курс: {account_info['course']}\n"
        f"📋 Группа: {account_info['group']}\n"
        f"💼 Тариф: {account_info['tariff']}\n"
        f"📆 На курсе с: {account_info['start_date']}\n"
        f"🧪 Предметы: {subjects_str}",
        reply_markup=get_account_kb()
    )
    await state.set_state(AccountStates.main)