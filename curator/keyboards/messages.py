from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .common import get_universal_back_button

def get_messages_menu_kb() -> InlineKeyboardMarkup:
    """Клавиатура меню сообщений"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📩 Индивидуальное сообщение", callback_data="individual_message")],
        [InlineKeyboardButton(text="📢 Массовая рассылка", callback_data="mass_message")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_curator_main")]
    ])

def get_groups_for_message_kb() -> InlineKeyboardMarkup:
    """Клавиатура выбора группы для сообщения"""
    # В реальном приложении здесь будет запрос к базе данных
    groups = [
        {"id": "group1", "name": "Интенсив. География"},
        {"id": "group2", "name": "Интенсив. Математика"}
    ]
    
    buttons = []
    for group in groups:
        buttons.append([
            InlineKeyboardButton(
                text=group["name"], 
                callback_data=f"msg_group_{group['id']}"
            )
        ])
    
    buttons.append(get_universal_back_button())
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_students_for_message_kb(group_id: str) -> InlineKeyboardMarkup:
    """Клавиатура выбора ученика для сообщения"""
    # В реальном приложении здесь будет запрос к базе данных
    students = {
        "group1": [
            {"id": "student1", "name": "Медина Махамбет"},
            {"id": "student2", "name": "Алтынай Ерланова"}
        ],
        "group2": [
            {"id": "student3", "name": "Арман Сериков"},
            {"id": "student4", "name": "Аружан Ахметова"}
        ]
    }
    
    group_students = students.get(group_id, [])
    
    buttons = []
    for student in group_students:
        buttons.append([
            InlineKeyboardButton(
                text=student["name"], 
                callback_data=f"msg_student_{student['id']}"
            )
        ])
    
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_groups_message")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_confirm_message_kb() -> InlineKeyboardMarkup:
    """Клавиатура подтверждения отправки сообщения"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Отправить", callback_data="send_message")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_message")]
    ])