from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from common.keyboards import get_main_menu_back_button

async def get_groups_kb(role: str, user_telegram_id: int = None) -> InlineKeyboardMarkup:
    """Клавиатура выбора группы"""


    # Для куратора и учителя получаем их реальные группы из базы данных
    if (role == "curator" or role == "teacher") and user_telegram_id:
        try:
            from database import UserRepository, CuratorRepository, TeacherRepository

            # Получаем пользователя по telegram_id
            user = await UserRepository.get_by_telegram_id(user_telegram_id)

            if user:
                groups = []
                role_profile = None

                if role == "curator":
                    # Получаем профиль куратора по user_id
                    curator = await CuratorRepository.get_by_user_id(user.id)

                    if curator:
                        role_profile = curator
                        # Получаем группы куратора
                        groups = await CuratorRepository.get_curator_groups(curator.id)

                elif role == "teacher":
                    # Получаем профиль учителя по user_id
                    teacher = await TeacherRepository.get_by_user_id(user.id)

                    if teacher:
                        role_profile = teacher
                        # Получаем группы учителя
                        groups = await TeacherRepository.get_teacher_groups(teacher.id)

                if role_profile and groups:

                    # Создаем кнопки для реальных групп
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
                elif not groups and role_profile:
                    # Если у роли нет групп
                    print(f"❌ GROUPS: У {role} нет групп")
                    return InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="❌ Группы не найдены", callback_data="no_groups")],
                        *get_main_menu_back_button()
                    ])
                else:
                    # Пользователь не является куратором/учителем
                    role_name = "куратором" if role == "curator" else "учителем"
                    print(f"❌ GROUPS: {user.name} не является {role_name}")
                    return InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text=f"❌ Вы не являетесь {role_name}", callback_data=f"not_{role}")],
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
        print(f"❌ GROUPS: Для роли {role} требуется telegram_id для получения групп")

    # Если не передан telegram_id или роль не поддерживается - показываем сообщение об ошибке
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Группы не найдены", callback_data="no_groups")],
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
                print(f"   ⚠️ Студенты не найдены, возвращаем заглушку")
                return InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="❌ Студенты не найдены", callback_data="no_students")],
                    *get_main_menu_back_button()
                ])

            # Создаем кнопки для реальных студентов
            buttons = []
            for i, student in enumerate(students):
                callback_data = f"{role}_student_{student.id}"
                buttons.append([
                    InlineKeyboardButton(
                        text=f"👤 {student.user.name}",
                        callback_data=callback_data
                    )
                ])

            buttons.extend(get_main_menu_back_button())
            return InlineKeyboardMarkup(inline_keyboard=buttons)

        except Exception as e:
            print(f"   ❌ Ошибка при получении студентов группы: {e}")
            import traceback
            traceback.print_exc()
            # В случае ошибки показываем сообщение об ошибке
            return InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="❌ Ошибка загрузки студентов", callback_data="error_students")],
                *get_main_menu_back_button()
            ])

    # Если group_id не является числом - это ошибка, так как хардкод убран
    print(f"   ❌ Неверный group_id: {group_id}. Хардкодированные группы больше не поддерживаются")
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Студенты не найдены", callback_data="no_students")],
        *get_main_menu_back_button()
    ])

def get_student_profile_kb(role: str) -> InlineKeyboardMarkup:
    """Клавиатура для карточки ученика"""
    return InlineKeyboardMarkup(inline_keyboard=[
        *get_main_menu_back_button()
    ])