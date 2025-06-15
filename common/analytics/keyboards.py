from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from common.keyboards import get_main_menu_back_button, get_universal_back_button
import asyncio
import sys
import os

# Добавляем путь к корневой папке проекта для импорта database
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database import StudentRepository, GroupRepository, CuratorRepository

def get_analytics_menu_kb(role: str) -> InlineKeyboardMarkup:
    """Клавиатура меню аналитики"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика по ученику", callback_data="student_analytics")],
        [InlineKeyboardButton(text="📈 Статистика по группе", callback_data="group_analytics")],
        *get_main_menu_back_button()
    ])

async def get_groups_for_analytics_kb(role: str) -> InlineKeyboardMarkup:
    """Клавиатура выбора группы для аналитики"""
    # Получаем реальные группы из базы данных
    try:
        groups = await GroupRepository.get_all()
    except Exception as e:
        print(f"Ошибка при получении групп: {e}")
        groups = []

    buttons = []
    for group in groups:
        # Показываем название группы с предметом
        group_name = f"{group.name} ({group.subject.name})" if group.subject else group.name
        buttons.append([
            InlineKeyboardButton(
                text=group_name,
                callback_data=f"analytics_group_{group.id}"
            )
        ])

    if not buttons:
        buttons.append([
            InlineKeyboardButton(
                text="❌ Группы не найдены",
                callback_data="no_groups"
            )
        ])

    buttons.extend(get_main_menu_back_button())

    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def get_students_for_analytics_kb(group_id: str) -> InlineKeyboardMarkup:
    """Клавиатура выбора ученика для аналитики"""
    # Получаем реальных студентов из базы данных
    try:
        students = await StudentRepository.get_by_group(int(group_id))
    except Exception as e:
        print(f"Ошибка при получении студентов: {e}")
        students = []

    buttons = []
    for student in students:
        buttons.append([
            InlineKeyboardButton(
                text=student.user.name,
                callback_data=f"analytics_student_{student.id}"
            )
        ])

    if not buttons:
        buttons.append([
            InlineKeyboardButton(
                text="❌ Студенты не найдены",
                callback_data="no_students"
            )
        ])

    buttons.extend(get_main_menu_back_button())

    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def get_groups_by_curator_kb(curator_id: str) -> InlineKeyboardMarkup:
    """Клавиатура выбора группы конкретного куратора для аналитики"""
    try:
        # Получаем все группы куратора через новый метод
        groups = await CuratorRepository.get_curator_groups(int(curator_id))

        if not groups:
            # Если у куратора нет групп, показываем все группы
            return await get_groups_for_analytics_kb("manager")

        # Показываем все группы этого куратора
        buttons = []
        for group in groups:
            group_name = f"{group.name} ({group.subject.name})" if group.subject else group.name
            buttons.append([
                InlineKeyboardButton(
                    text=group_name,
                    callback_data=f"analytics_group_{group.id}"
                )
            ])

    except Exception as e:
        print(f"Ошибка при получении групп куратора: {e}")
        # В случае ошибки показываем все группы
        return await get_groups_for_analytics_kb("manager")

    buttons.extend(get_main_menu_back_button())

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_back_to_analytics_kb() -> InlineKeyboardMarkup:
    """Клавиатура возврата в меню аналитики"""
    return InlineKeyboardMarkup(inline_keyboard=[
        *get_main_menu_back_button()
    ])