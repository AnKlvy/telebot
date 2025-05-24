from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from common.keyboards import get_universal_back_button

def get_shop_menu_kb() -> InlineKeyboardMarkup:
    """Клавиатура главного меню магазина"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Обменять баллы", callback_data="exchange_points")],
        [InlineKeyboardButton(text="🛒 Каталог бонусов", callback_data="bonus_catalog")],
        [InlineKeyboardButton(text="📦 Мои бонусы", callback_data="my_bonuses")],
        get_universal_back_button("🏠 Главное меню", "back_to_main")
    ])

def get_exchange_points_kb() -> InlineKeyboardMarkup:
    """Клавиатура для обмена баллов на монеты"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="50 баллов → 50 монет", callback_data="exchange_50")],
        [InlineKeyboardButton(text="70 баллов → 70 монет", callback_data="exchange_70")],
        [InlineKeyboardButton(text="100 баллов → 100 монет", callback_data="exchange_100")],
        get_universal_back_button("⬅️ Назад", "back_to_shop")
    ])

def get_bonus_catalog_kb() -> InlineKeyboardMarkup:
    """Клавиатура каталога бонусов"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧪 Бонусный тест — 100 монет", callback_data="buy_bonus_test")],
        [InlineKeyboardButton(text="📘 PDF по ошибкам — 80 монет", callback_data="buy_pdf")],
        [InlineKeyboardButton(text="📩 5000 тенге — 150 монет", callback_data="buy_money")],
        get_universal_back_button("⬅️ Назад", "back_to_shop")
    ])

def get_back_to_shop_kb() -> InlineKeyboardMarkup:
    """Клавиатура для возврата в меню магазина"""
    return InlineKeyboardMarkup(inline_keyboard=[
        get_universal_back_button("⬅️ Назад в магазин", "back_to_shop"),
        get_universal_back_button("🏠 Главное меню", "back_to_main")
    ])