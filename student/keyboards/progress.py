from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from common.keyboards import get_main_menu_back_button

def get_progress_menu_kb() -> InlineKeyboardMarkup:
    """Клавиатура меню прогресса"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Общая статистика", callback_data="general_stats")],
        [InlineKeyboardButton(text="📈 Понимание по темам", callback_data="topics_understanding")],
         *get_main_menu_back_button()
    ])

async def get_subjects_progress_kb(user_id: int = None) -> InlineKeyboardMarkup:
    """Клавиатура выбора предмета для просмотра прогресса (получает данные из БД)"""
    from database import SubjectRepository

    try:
        if user_id:
            # Получаем только предметы студента из его курсов
            subjects = await SubjectRepository.get_by_user_id(user_id)
        else:
            # Получаем все предметы (для обратной совместимости)
            subjects = await SubjectRepository.get_all()

        buttons = []
        for subject in subjects:
            buttons.append([
                InlineKeyboardButton(
                    text=subject.name,
                    callback_data=f"progress_sub_{subject.id}"
                )
            ])

        if not subjects:
            buttons.append([
                InlineKeyboardButton(text="❌ Нет доступных предметов", callback_data="no_subjects")
            ])

        # Добавляем кнопку "Назад"
        buttons.extend(get_main_menu_back_button())

        return InlineKeyboardMarkup(inline_keyboard=buttons)

    except Exception as e:
        print(f"Ошибка при получении предметов: {e}")
        # Возвращаем базовую клавиатуру в случае ошибки
        buttons = [
            [InlineKeyboardButton(text="❌ Ошибка загрузки предметов", callback_data="error")],
            *get_main_menu_back_button()
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_back_to_progress_kb() -> InlineKeyboardMarkup:
    """Клавиатура для возврата в меню прогресса"""
    return InlineKeyboardMarkup(inline_keyboard=[
        *get_main_menu_back_button()
    ])