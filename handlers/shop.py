from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from keyboards.shop import get_shop_menu_kb, get_exchange_points_kb, get_back_to_shop_kb

router = Router()

class ShopStates(StatesGroup):
    main = State()
    exchange = State()
    catalog = State()
    my_bonuses = State()

@router.callback_query(F.data == "shop")
async def show_shop_menu(callback: CallbackQuery, state: FSMContext):
    """Показать меню магазина"""
    # В реальном приложении эти данные будут загружаться из базы данных
    points = 870
    coins = 210
    
    await callback.message.edit_text(
        "🎉 Добро пожаловать в магазин!\n"
        "Здесь ты можешь обменять баллы на монеты и потратить их на бонусы.\n"
        "💰 У тебя сейчас:\n"
        f"Баллы: {points}\n"
        f"Монеты: {coins}",
        reply_markup=get_shop_menu_kb()
    )
    await state.set_state(ShopStates.main)

@router.callback_query(ShopStates.main, F.data == "exchange_points")
async def show_exchange_options(callback: CallbackQuery, state: FSMContext):
    """Показать варианты обмена баллов на монеты"""
    await callback.message.edit_text(
        "Выбери, сколько баллов хочешь обменять на монеты:",
        reply_markup=get_exchange_points_kb()
    )
    await state.set_state(ShopStates.exchange)

@router.callback_query(ShopStates.exchange, F.data.startswith("exchange_"))
async def process_exchange(callback: CallbackQuery, state: FSMContext):
    """Обработать обмен баллов на монеты"""
    exchange_amount = int(callback.data.replace("exchange_", ""))
    
    # В реальном приложении здесь будет логика обновления баланса в базе данных
    # Для примера используем фиксированные значения
    old_points = 870
    old_coins = 210
    
    new_points = old_points - exchange_amount
    new_coins = old_coins + exchange_amount
    
    await callback.message.edit_text(
        "✅ Успешно!\n"
        f"Списано: {exchange_amount} баллов\n"
        f"Начислено: {exchange_amount} монет\n"
        f"💼 Новый баланс: {new_points} баллов | {new_coins} монет",
        reply_markup=get_back_to_shop_kb()
    )

@router.callback_query(ShopStates.main, F.data == "bonus_catalog")
async def show_bonus_catalog(callback: CallbackQuery, state: FSMContext):
    """Показать каталог бонусов"""
    # Здесь будет логика отображения каталога бонусов
    await callback.message.edit_text(
        "🛒 Каталог бонусов\n"
        "Здесь будут доступные бонусы, которые можно приобрести за монеты.",
        reply_markup=get_back_to_shop_kb()
    )
    await state.set_state(ShopStates.catalog)

@router.callback_query(ShopStates.main, F.data == "my_bonuses")
async def show_my_bonuses(callback: CallbackQuery, state: FSMContext):
    """Показать мои бонусы"""
    # Здесь будет логика отображения приобретенных бонусов
    await callback.message.edit_text(
        "📦 Мои бонусы\n"
        "Здесь будут отображаться приобретенные тобой бонусы.",
        reply_markup=get_back_to_shop_kb()
    )
    await state.set_state(ShopStates.my_bonuses)

@router.callback_query(F.data == "back_to_shop")
async def back_to_shop(callback: CallbackQuery, state: FSMContext):
    """Вернуться в меню магазина"""
    await show_shop_menu(callback, state)