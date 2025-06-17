from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from common.keyboards import get_main_menu_back_button, get_universal_back_button


def get_messages_menu_kb() -> InlineKeyboardMarkup:
    """Клавиатура меню сообщений"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📩 Индивидуальное сообщение", callback_data="individual_message")],
        [InlineKeyboardButton(text="📢 Массовая рассылка", callback_data="mass_message")],
        *get_main_menu_back_button()
    ])

async def get_groups_for_message_kb(user_telegram_id: int) -> InlineKeyboardMarkup:
    """Клавиатура выбора группы для сообщения - показывает только группы куратора"""
    try:
        from database import UserRepository, CuratorRepository

        # Получаем пользователя по telegram_id
        user = await UserRepository.get_by_telegram_id(user_telegram_id)

        if not user:
            return InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="❌ Пользователь не найден", callback_data="user_not_found")],
                *get_main_menu_back_button()
            ])

        # Получаем профиль куратора
        curator = await CuratorRepository.get_by_user_id(user.id)

        if not curator:
            return InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="❌ Вы не являетесь куратором", callback_data="not_curator")],
                *get_main_menu_back_button()
            ])

        # Получаем группы куратора
        groups = await CuratorRepository.get_curator_groups(curator.id)

        if not groups:
            return InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="❌ У вас нет групп", callback_data="no_groups")],
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
                    callback_data=f"msg_group_{group.id}"
                )
            ])

        buttons.extend(get_main_menu_back_button())
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    except Exception as e:
        print(f"❌ Ошибка при получении групп куратора: {e}")
        import traceback
        traceback.print_exc()
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Ошибка загрузки групп", callback_data="error_groups")],
            *get_main_menu_back_button()
        ])

async def get_students_for_message_kb(group_id: int) -> InlineKeyboardMarkup:
    """Клавиатура выбора ученика для сообщения"""
    try:
        from database import StudentRepository

        # Получаем реальных студентов группы из базы данных
        students = await StudentRepository.get_by_group(group_id)

        if not students:
            return InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="❌ Студенты не найдены", callback_data="no_students")],
                *get_main_menu_back_button()
            ])

        buttons = []
        for student in students:
            buttons.append([
                InlineKeyboardButton(
                    text=student.user.name,
                    callback_data=f"msg_student_{student.id}"
                )
            ])

        buttons.extend(get_main_menu_back_button())
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    except Exception as e:
        print(f"❌ Ошибка при получении студентов: {e}")
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Ошибка загрузки студентов", callback_data="error_students")],
            *get_main_menu_back_button()
        ])

def get_confirm_message_kb() -> InlineKeyboardMarkup:
    """Клавиатура подтверждения отправки сообщения"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Отправить", callback_data="send_message")],
        get_universal_back_button("❌ Отменить")
    ])