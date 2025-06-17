from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from common.keyboards import get_main_menu_back_button


def get_homework_menu_kb() -> InlineKeyboardMarkup:
    """Клавиатура меню домашних заданий"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Статистика по ученику", callback_data="hw_student_stats")],
        [InlineKeyboardButton(text="Статистика по группе", callback_data="hw_group_stats")],
        *get_main_menu_back_button()
    ])


async def get_groups_kb(course_id: str = None) -> InlineKeyboardMarkup:
    """Клавиатура выбора группы"""
    try:
        from database import GroupRepository

        # Получаем реальные группы из базы данных
        groups = await GroupRepository.get_all()

        if not groups:
            return InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="❌ Группы не найдены", callback_data="no_groups")],
                *get_main_menu_back_button()
            ])

        buttons = []
        for group in groups:
            group_name = f"{group.name}"
            if group.subject:
                group_name += f" ({group.subject.name})"

            buttons.append([
                InlineKeyboardButton(
                    text=group_name,
                    callback_data=f"hw_group_{group.id}"
                )
            ])

        buttons.extend(get_main_menu_back_button())
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    except Exception as e:
        print(f"❌ Ошибка при получении групп: {e}")
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Ошибка загрузки групп", callback_data="error_groups")],
            *get_main_menu_back_button()
        ])


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
        buttons.append([InlineKeyboardButton(text="✅ Выполнили:", callback_data="completed")])

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
        buttons.append([InlineKeyboardButton(text="❌ Не выполнили:", callback_data="not_completed")])

        # Добавляем учеников, не выполнивших ДЗ
        for student in not_completed_students:
            buttons.append([
                InlineKeyboardButton(
                    text=student["name"],
                    url=f"https://t.me/{student['id']}"  # Для перехода в ЛС
                )
            ])

    buttons.extend(get_main_menu_back_button())

    return InlineKeyboardMarkup(inline_keyboard=buttons)
