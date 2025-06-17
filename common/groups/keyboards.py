from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from common.keyboards import get_main_menu_back_button

async def get_groups_kb(role: str, user_telegram_id: int = None) -> InlineKeyboardMarkup:
    """Клавиатура выбора группы"""

    print(f"🔍 GROUPS: role={role}, telegram_id={user_telegram_id}")

    # Для куратора получаем его реальные группы из базы данных
    if role == "curator" and user_telegram_id:
        try:
            from database import UserRepository, CuratorRepository

            # Получаем пользователя по telegram_id
            user = await UserRepository.get_by_telegram_id(user_telegram_id)
            print(f"🔍 GROUPS: Пользователь: {user.name if user else 'НЕ НАЙДЕН'}")

            if user:
                # Получаем профиль куратора по user_id
                curator = await CuratorRepository.get_by_user_id(user.id)
                print(f"🔍 GROUPS: Куратор: {'ID=' + str(curator.id) if curator else 'НЕ НАЙДЕН'}")

                if curator:
                    # Получаем группы куратора
                    groups = await CuratorRepository.get_curator_groups(curator.id)
                    print(f"🔍 GROUPS: Найдено групп: {len(groups)}")

                    if not groups:
                        # Если у куратора нет групп
                        print("❌ GROUPS: У куратора нет групп")
                        return InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text="❌ Группы не найдены", callback_data="no_groups")],
                            *get_main_menu_back_button()
                        ])

                    # Создаем кнопки для реальных групп куратора
                    print(f"✅ GROUPS: Создаем {len(groups)} кнопок")
                    buttons = []
                    for group in groups:
                        group_name = f"{group.name}"
                        if group.subject:
                            group_name += f" ({group.subject.name})"

                        buttons.append([
                            InlineKeyboardButton(
                                text=f"👥 {group_name}",
                                callback_data=f"{role}_group_{group.id}"
                            )
                        ])

                    buttons.extend(get_main_menu_back_button())
                    return InlineKeyboardMarkup(inline_keyboard=buttons)
                else:
                    # Пользователь не является куратором
                    print(f"❌ GROUPS: {user.name} не является куратором")
                    return InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="❌ Вы не являетесь куратором", callback_data="not_curator")],
                        *get_main_menu_back_button()
                    ])
            else:
                # Пользователь не найден
                print(f"❌ GROUPS: Пользователь не найден")
                return InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="❌ Пользователь не найден", callback_data="user_not_found")],
                    *get_main_menu_back_button()
                ])

        except Exception as e:
            print(f"❌ GROUPS: Ошибка - {e}")
            import traceback
            traceback.print_exc()
            # В случае ошибки показываем сообщение об ошибке
            return InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="❌ Ошибка загрузки групп", callback_data="error_groups")],
                *get_main_menu_back_button()
            ])
    else:
        print(f"🔍 GROUPS: Хардкодированные группы (role={role})")

    # Для других ролей или если не передан telegram_id - показываем хардкодированные группы
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📗 Химия — Премиум", callback_data=f"{role}_group_chem_premium")],
        [InlineKeyboardButton(text="📘 Биология — Интенсив", callback_data=f"{role}_group_bio_intensive")],
        [InlineKeyboardButton(text="📕 История — Базовый", callback_data=f"{role}_group_history_basic")],
        *get_main_menu_back_button()
    ])

async def get_students_kb(role: str, group_id) -> InlineKeyboardMarkup:
    """Клавиатура выбора ученика в группе"""

    # Если group_id - это число (реальный ID группы), получаем студентов из БД
    if isinstance(group_id, int):
        try:
            from database import StudentRepository

            # Получаем студентов группы из базы данных
            students = await StudentRepository.get_by_group(group_id)

            if not students:
                # Если в группе нет студентов
                return InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="❌ Студенты не найдены", callback_data="no_students")],
                    *get_main_menu_back_button()
                ])

            # Создаем кнопки для реальных студентов
            buttons = []
            for student in students:
                buttons.append([
                    InlineKeyboardButton(
                        text=f"👤 {student.user.name}",
                        callback_data=f"{role}_student_{student.id}"
                    )
                ])

            buttons.extend(get_main_menu_back_button())
            return InlineKeyboardMarkup(inline_keyboard=buttons)

        except Exception as e:
            print(f"Ошибка при получении студентов группы: {e}")
            # В случае ошибки показываем сообщение об ошибке
            return InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="❌ Ошибка загрузки студентов", callback_data="error_students")],
                *get_main_menu_back_button()
            ])

    # Для хардкодированных групп показываем хардкодированных студентов
    buttons = [
        [InlineKeyboardButton(text="👤 Аружан Ахметова", callback_data=f"{role}_student_1")],
        [InlineKeyboardButton(text="👤 Мадияр Сапаров", callback_data=f"{role}_student_2")],
        [InlineKeyboardButton(text="👤 Диана Ержанова", callback_data=f"{role}_student_3")],
        *get_main_menu_back_button()
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_student_profile_kb(role: str) -> InlineKeyboardMarkup:
    """Клавиатура для карточки ученика"""
    return InlineKeyboardMarkup(inline_keyboard=[
        *get_main_menu_back_button()
    ])