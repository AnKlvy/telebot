from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from common.keyboards import get_universal_back_button

def get_homework_menu_kb() -> InlineKeyboardMarkup:
    """Клавиатура меню домашних заданий"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Статистика по ученику", callback_data="hw_student_stats")],
        [InlineKeyboardButton(text="Статистика по группе", callback_data="hw_group_stats")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_curator_main")]
    ])

def get_groups_kb(course_id: str = None) -> InlineKeyboardMarkup:
    """Клавиатура выбора группы"""
    # В реальном приложении здесь будет запрос к базе данных
    # для получения списка групп по конкретному курсу
    groups = [
        {"id": "group1", "name": "Интенсив. География"},
        {"id": "group2", "name": "Интенсив. Математика"}
    ]
    
    buttons = []
    for group in groups:
        buttons.append([
            InlineKeyboardButton(
                text=group["name"], 
                callback_data=f"hw_group_{group['id']}"
            )
        ])
    
    buttons.append(get_universal_back_button())
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_students_by_homework_kb(lesson_id: str) -> InlineKeyboardMarkup:
    """Клавиатура со списком учеников, выполнивших и не выполнивших ДЗ"""
    # В реальном приложении здесь будет запрос к базе данных
    # для получения списков учеников
    completed_students = [
        {"id": "student1", "name": "Ахметова Аружан"},
        {"id": "student2", "name": "Диана Сапарова"}
    ]
    
    not_completed_students = [
        {"id": "axaxaxaxaxxaxaxaxxaxaxaxaxxaxaxa", "name": "Медина Махамбет"},
        {"id": "anklvy", "name": "Андрей Климов"},
        {"id": "student5", "name": "Алтынай Ерланова"}
    ]
    
    buttons = []
    
    # Добавляем заголовок для выполнивших
    if completed_students:
        buttons.append([InlineKeyboardButton(text="✅ Выполнили:", callback_data="dummy")])
        
        # Добавляем учеников, выполнивших ДЗ
        for student in completed_students:
            buttons.append([
                InlineKeyboardButton(
                    text=student["name"], 
                    callback_data=f"hw_student_completed_{student['id']}"
                )
            ])
    
    # Добавляем заголовок для не выполнивших
    if not_completed_students:
        buttons.append([InlineKeyboardButton(text="❌ Не выполнили:", callback_data="dummy")])
        
        # Добавляем учеников, не выполнивших ДЗ
        for student in not_completed_students:
            buttons.append([
                InlineKeyboardButton(
                    text=student["name"], 
                    url=f"https://t.me/{student['id']}"  # Для перехода в ЛС
                )
            ])
    
    buttons.append(get_universal_back_button())
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)