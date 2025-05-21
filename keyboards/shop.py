from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_shop_menu_kb() -> InlineKeyboardMarkup:
    """Клавиатура главного меню магазина"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Обменять баллы", callback_data="exchange_points")],
        [InlineKeyboardButton(text="🛒 Каталог бонусов", callback_data="bonus_catalog")],
        [InlineKeyboardButton(text="📦 Мои бонусы", callback_data="my_bonuses")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
    ])

def get_exchange_points_kb() -> InlineKeyboardMarkup:
    """Клавиатура для обмена баллов на монеты"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="50 баллов → 50 монет", callback_data="exchange_50")],
        [InlineKeyboardButton(text="70 баллов → 70 монет", callback_data="exchange_70")],
        [InlineKeyboardButton(text="100 баллов → 100 монет", callback_data="exchange_100")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_shop")]
    ])

def get_bonus_catalog_kb() -> InlineKeyboardMarkup:
    """Клавиатура каталога бонусов"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧪 Бонусный тест — 100 монет", callback_data="buy_bonus_test")],
        [InlineKeyboardButton(text="📘 PDF по ошибкам — 80 монет", callback_data="buy_pdf")],
        [InlineKeyboardButton(text="📩 5000 тенге — 150 монет", callback_data="buy_money")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_shop")]
    ])

def get_back_to_shop_kb() -> InlineKeyboardMarkup:
    """Клавиатура для возврата в меню магазина"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад в магазин", callback_data="back_to_shop")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
    ])