from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from common.keyboards import get_main_menu_back_button, get_universal_back_button
import asyncio
import sys
import os

# Добавляем путь к корневой папке проекта для импорта database
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database import StudentRepository, GroupRepository, CuratorRepository, UserRepository, TeacherRepository

def get_analytics_menu_kb(role: str) -> InlineKeyboardMarkup:
    """Клавиатура меню аналитики"""
    buttons = [
        [InlineKeyboardButton(text="📊 Статистика по ученику", callback_data="student_analytics")],
        [InlineKeyboardButton(text="📈 Статистика по группе", callback_data="group_analytics")],
    ]

    # Добавляем общую статистику только для менеджеров
    if role == "manager":
        buttons.append([InlineKeyboardButton(text="📋 Общая статистика", callback_data="general_analytics")])

    buttons.extend(get_main_menu_back_button())
    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def get_groups_for_analytics_kb(role: str, user_telegram_id: int = None) -> InlineKeyboardMarkup:
    """Клавиатура выбора группы для аналитики"""
    print(f"🔍 ANALYTICS: role={role}, telegram_id={user_telegram_id}")

    # Получаем реальные группы из базы данных
    try:
        # Проверяем, нужно ли получать группы конкретного куратора/учителя
        # Это происходит если:
        # 1. role == "curator" и есть telegram_id
        # 2. role == "teacher" и есть telegram_id
        # 3. role == "admin" и есть telegram_id (админ работает в контексте куратора)
        # 4. role == "manager" - менеджер всегда получает все группы
        should_get_role_specific_groups = (
            (role == "curator" or role == "teacher" or role == "admin") and user_telegram_id
        )

        if should_get_role_specific_groups:
            # Для куратора/учителя (или админа в контексте куратора) получаем только их группы
            user = await UserRepository.get_by_telegram_id(user_telegram_id)
            print(f"🔍 ANALYTICS: Пользователь: {user.name if user else 'НЕ НАЙДЕН'}")

            if user:
                groups = []

                # Проверяем роль и получаем соответствующие группы
                if role == "curator" or role == "admin":
                    # Получаем профиль куратора по user_id
                    curator = await CuratorRepository.get_by_user_id(user.id)
                    print(f"🔍 ANALYTICS: Куратор: {'ID=' + str(curator.id) if curator else 'НЕ НАЙДЕН'}")

                    if curator:
                        groups = await CuratorRepository.get_curator_groups(curator.id)
                        print(f"🔍 ANALYTICS: Найдено групп куратора: {len(groups)}")
                    else:
                        print(f"❌ ANALYTICS: Не является куратором")

                elif role == "teacher":
                    # Получаем профиль учителя по user_id
                    teacher = await TeacherRepository.get_by_user_id(user.id)
                    print(f"🔍 ANALYTICS: Учитель: {'ID=' + str(teacher.id) if teacher else 'НЕ НАЙДЕН'}")

                    if teacher:
                        groups = await TeacherRepository.get_teacher_groups(teacher.id)
                        print(f"🔍 ANALYTICS: Найдено групп учителя: {len(groups)}")
                    else:
                        print(f"❌ ANALYTICS: Не является учителем")
            else:
                groups = []
        else:
            # Для других ролей (включая manager) получаем все группы
            groups = await GroupRepository.get_all()
            print(f"🔍 ANALYTICS: Всего групп для {role}: {len(groups)}")
    except Exception as e:
        print(f"❌ ANALYTICS: Ошибка - {e}")
        import traceback
        traceback.print_exc()
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


def get_student_microtopics_kb(student_id: int, subject_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для просмотра статистики по микротемам студента"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📈 % понимания по микротемам",
            callback_data=f"microtopics_detailed_{student_id}_{subject_id}"
        )],
        [InlineKeyboardButton(
            text="🟢🔴 Сильные и слабые темы",
            callback_data=f"microtopics_summary_{student_id}_{subject_id}"
        )],
        *get_main_menu_back_button()
    ])


def get_back_to_analytics_kb() -> InlineKeyboardMarkup:
    """Клавиатура возврата в меню аналитики"""
    return InlineKeyboardMarkup(inline_keyboard=[
        *get_main_menu_back_button()
    ])


def get_back_to_student_analytics_kb(student_id: int, subject_id: int) -> InlineKeyboardMarkup:
    """Клавиатура возврата к статистике студента"""
    return InlineKeyboardMarkup(inline_keyboard=[
        *get_main_menu_back_button()
    ])


def get_general_microtopics_kb() -> InlineKeyboardMarkup:
    """Клавиатура для просмотра общей статистики по микротемам"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📈 % понимания по микротемам",
            callback_data="general_microtopics_detailed"
        )],
        [InlineKeyboardButton(
            text="🟢🔴 Сильные и слабые темы",
            callback_data="general_microtopics_summary"
        )],
        *get_main_menu_back_button()
    ])


async def get_subjects_for_analytics_kb(role: str) -> InlineKeyboardMarkup:
    """Клавиатура выбора предмета для аналитики"""
    try:
        from database.repositories import SubjectRepository
        subjects = await SubjectRepository.get_all()
    except Exception as e:
        print(f"Ошибка при получении предметов: {e}")
        subjects = []

    buttons = []
    for subject in subjects:
        # Используем разные callback_data в зависимости от роли
        if role == "manager":
            callback_data = f"manager_subject_{subject.id}"
        else:
            callback_data = f"analytics_subject_{subject.id}"

        buttons.append([
            InlineKeyboardButton(
                text=subject.name,
                callback_data=callback_data
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


def get_subject_microtopics_kb(subject_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для просмотра статистики по микротемам предмета"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📈 % понимания по микротемам",
            callback_data=f"subject_microtopics_detailed_{subject_id}"
        )],
        [InlineKeyboardButton(
            text="🟢🔴 Сильные и слабые темы",
            callback_data=f"subject_microtopics_summary_{subject_id}"
        )],
        *get_main_menu_back_button()
    ])


def get_back_to_subject_analytics_kb(subject_id: int) -> InlineKeyboardMarkup:
    """Клавиатура возврата к статистике предмета"""
    return InlineKeyboardMarkup(inline_keyboard=[
        *get_main_menu_back_button()
    ])


def get_general_microtopics_kb() -> InlineKeyboardMarkup:
    """Клавиатура для просмотра общей статистики по микротемам"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📈 % понимания по микротемам",
            callback_data="general_microtopics_detailed"
        )],
        [InlineKeyboardButton(
            text="🟢🔴 Сильные и слабые темы",
            callback_data="general_microtopics_summary"
        )],
        *get_main_menu_back_button()
    ])


def get_back_to_general_analytics_kb() -> InlineKeyboardMarkup:
    """Клавиатура возврата к общей статистике"""
    return InlineKeyboardMarkup(inline_keyboard=[
        *get_main_menu_back_button()
    ])


def get_group_analytics_kb(group_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для просмотра статистики по группе"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📈 % понимания по микротемам",
            callback_data=f"group_microtopics_detailed_{group_id}"
        )],
        [InlineKeyboardButton(
            text="📋 Рейтинг по баллам",
            callback_data=f"group_rating_{group_id}"
        )],
        *get_main_menu_back_button()
    ])


def get_back_to_group_analytics_kb(group_id: int) -> InlineKeyboardMarkup:
    """Клавиатура возврата к статистике группы"""
    return InlineKeyboardMarkup(inline_keyboard=[
        *get_main_menu_back_button()
    ])