from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from common.keyboards import get_main_menu_back_button
import asyncio
import sys
import os

# Добавляем путь к корневой папке проекта для импорта database
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database import CuratorRepository, SubjectRepository

def get_manager_analytics_menu_kb() -> InlineKeyboardMarkup:
    """Клавиатура меню аналитики менеджера"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика по ученику", callback_data="manager_student_analytics")],
        [InlineKeyboardButton(text="📈 Статистика по группе", callback_data="manager_group_analytics")],
        [InlineKeyboardButton(text="📚 Статистика по предмету", callback_data="manager_subject_analytics")],
        [InlineKeyboardButton(text="📋 Общая статистика", callback_data="general_analytics")],
        *get_main_menu_back_button()
    ])

async def get_curators_kb() -> InlineKeyboardMarkup:
    """Клавиатура выбора куратора"""
    # Получаем реальных кураторов из базы данных
    try:
        curators = await CuratorRepository.get_all()
    except Exception as e:
        print(f"Ошибка при получении кураторов: {e}")
        curators = []

    buttons = []
    for curator in curators:
        # Показываем имя куратора с предметом и группой
        curator_info = f"{curator.user.name}"
        if curator.subject and curator.group:
            curator_info += f" ({curator.subject.name}, {curator.group.name})"
        elif curator.subject:
            curator_info += f" ({curator.subject.name})"

        buttons.append([
            InlineKeyboardButton(
                text=curator_info,
                callback_data=f"manager_curator_{curator.id}"
            )
        ])

    if not buttons:
        buttons.append([
            InlineKeyboardButton(
                text="❌ Кураторы не найдены",
                callback_data="no_curators"
            )
        ])

    buttons.extend(get_main_menu_back_button())

    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def get_subjects_kb() -> InlineKeyboardMarkup:
    """Клавиатура выбора предмета"""
    # Получаем реальные предметы из базы данных
    try:
        subjects = await SubjectRepository.get_all()
    except Exception as e:
        print(f"Ошибка при получении предметов: {e}")
        subjects = []

    buttons = []
    for subject in subjects:
        buttons.append([
            InlineKeyboardButton(
                text=subject.name,
                callback_data=f"manager_subject_{subject.id}"
            )
        ])

    if not buttons:
        buttons.append([
            InlineKeyboardButton(
                text="❌ Предметы не найдены",
                callback_data="no_subjects"
            )
        ])

    buttons.extend(get_main_menu_back_button())

    return InlineKeyboardMarkup(inline_keyboard=buttons)