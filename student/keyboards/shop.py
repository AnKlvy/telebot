from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from common.keyboards import get_main_menu_back_button
from typing import List
from datetime import datetime


def format_date_russian(date: datetime) -> str:
    """Форматировать дату на русском языке"""
    months = {
        1: 'января', 2: 'февраля', 3: 'марта', 4: 'апреля',
        5: 'мая', 6: 'июня', 7: 'июля', 8: 'августа',
        9: 'сентября', 10: 'октября', 11: 'ноября', 12: 'декабря'
    }
    return f"{date.day} {months[date.month]}"

def get_shop_menu_kb() -> InlineKeyboardMarkup:
    """Клавиатура главного меню магазина"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Обменять баллы", callback_data="exchange_points")],
        [InlineKeyboardButton(text="🛒 Каталог бонусов", callback_data="bonus_catalog")],
        [InlineKeyboardButton(text="📦 Мои бонусы", callback_data="my_bonuses")],
        *get_main_menu_back_button()
    ])

async def get_exchange_points_kb(available_points: int) -> InlineKeyboardMarkup:
    """Клавиатура для обмена баллов на монеты"""
    buttons = []

    # Варианты обмена в зависимости от доступных баллов
    exchange_options = [50, 70, 100, 150, 200]

    for amount in exchange_options:
        if available_points >= amount:
            buttons.append([InlineKeyboardButton(
                text=f"{amount} баллов → {amount} монет",
                callback_data=f"exchange_{amount}"
            )])

    if not buttons:
        buttons.append([InlineKeyboardButton(
            text="❌ Недостаточно баллов",
            callback_data="no_points"
        )])

    buttons.extend(get_main_menu_back_button())
    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def get_bonus_catalog_kb(items: List, user_coins: int) -> InlineKeyboardMarkup:
    """Клавиатура каталога бонусов"""
    buttons = []

    for item in items:
        # Определяем эмодзи по типу товара
        emoji = {
            'bonus_test': '🧪',
            'bonus_task': '🎯',
            'pdf': '📘',
            'money': '💰',
            'other': '🎁'
        }.get(item['item_type'], '🎁')

        # Определяем callback_data в зависимости от типа товара
        if item['type'] == 'bonus_test':
            callback_prefix = "buy_bonus_"
        else:
            callback_prefix = "buy_item_"

        # Проверяем, хватает ли монет
        if user_coins >= item['price']:
            button_text = f"{emoji} {item['name']} — {item['price']} монет"
            callback_data = f"{callback_prefix}{item['id']}"
        else:
            button_text = f"❌ {emoji} {item['name']} — {item['price']} монет"
            callback_data = f"no_coins_{item['id']}"

        buttons.append([InlineKeyboardButton(
            text=button_text,
            callback_data=callback_data
        )])

    buttons.extend(get_main_menu_back_button())
    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def get_my_bonuses_kb(purchases: List, bonus_test_purchases: List) -> InlineKeyboardMarkup:
    """Клавиатура для раздела 'Мои покупки'"""
    buttons = []

    # Добавляем кнопки для обычных товаров (бонусные задания)
    for purchase in purchases:
        # Определяем эмодзи по типу товара
        emoji = {
            'bonus_task': '🎯',
            'pdf': '📘',
            'money': '💰',
            'other': '🎁'
        }.get(purchase.item.item_type, '🎁')

        # Форматируем дату
        date_str = format_date_russian(purchase.purchased_at)

        button_text = f"{emoji} {purchase.item.name} — {purchase.price_paid} монет — {date_str}"
        callback_data = f"use_bonus_{purchase.id}"

        buttons.append([InlineKeyboardButton(
            text=button_text,
            callback_data=callback_data
        )])

    # Добавляем кнопки для бонусных тестов
    for purchase in bonus_test_purchases:
        question_count = len(purchase.bonus_test.questions) if purchase.bonus_test.questions else 0
        date_str = format_date_russian(purchase.purchased_at)

        button_text = f"🧪 {purchase.bonus_test.name} — {purchase.price_paid} монет — {date_str}"
        callback_data = f"use_bonus_test_{purchase.id}"

        buttons.append([InlineKeyboardButton(
            text=button_text,
            callback_data=callback_data
        )])

    buttons.extend(get_main_menu_back_button())
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_back_to_shop_kb() -> InlineKeyboardMarkup:
    """Клавиатура для возврата в меню магазина"""
    return InlineKeyboardMarkup(inline_keyboard=[
        *get_main_menu_back_button(),
    ])

def get_purchase_confirmation_kb(item_id: int) -> InlineKeyboardMarkup:
    """Клавиатура подтверждения покупки бонусного теста"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить покупку", callback_data=f"confirm_purchase_bonus_{item_id}")],
        [InlineKeyboardButton(text="🛒 Вернуться к каталогу", callback_data="bonus_catalog")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_purchase")],
        *get_main_menu_back_button()
    ])

def get_item_purchase_confirmation_kb(item_id: int) -> InlineKeyboardMarkup:
    """Клавиатура подтверждения покупки обычного товара (бонусного задания)"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить покупку", callback_data=f"confirm_purchase_item_{item_id}")],
        [InlineKeyboardButton(text="🛒 Вернуться к каталогу", callback_data="bonus_catalog")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_purchase")],
        *get_main_menu_back_button()
    ])

def get_purchase_confirmation_kb(test_id: int) -> InlineKeyboardMarkup:
    """Клавиатура подтверждения покупки бонусного теста"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить покупку", callback_data=f"confirm_purchase_bonus_{test_id}")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_purchase")],
        [InlineKeyboardButton(text="🔙 Назад к каталогу", callback_data="bonus_catalog")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
    ])