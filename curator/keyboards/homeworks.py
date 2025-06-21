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


async def get_students_by_homework_kb(lesson_id: int) -> InlineKeyboardMarkup:
    """Клавиатура со списком учеников, выполнивших и не выполнивших ДЗ"""
    try:
        from database import HomeworkRepository, HomeworkResultRepository, StudentRepository

        # Получаем ДЗ по уроку
        homeworks = await HomeworkRepository.get_by_lesson(lesson_id)
        if not homeworks:
            return InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="❌ ДЗ не найдены", callback_data="no_homework")],
                *get_main_menu_back_button()
            ])

        # Берем первое ДЗ (обычно в уроке одно ДЗ)
        homework = homeworks[0]

        # Получаем всех студентов, которые должны выполнить это ДЗ
        # (студенты из групп, изучающих предмет этого ДЗ)
        all_students = await StudentRepository.get_by_subject(homework.subject_id)

        # Получаем результаты выполнения ДЗ
        homework_results = await HomeworkResultRepository.get_by_homework(homework.id)
        completed_student_ids = {result.student_id for result in homework_results}

        # Разделяем студентов на выполнивших и не выполнивших
        completed_students = [s for s in all_students if s.id in completed_student_ids]
        not_completed_students = [s for s in all_students if s.id not in completed_student_ids]

        buttons = []

        # Добавляем заголовок для выполнивших
        if completed_students:
            buttons.append([InlineKeyboardButton(text="✅ Выполнили:", callback_data="completed")])

            # Добавляем учеников, выполнивших ДЗ
            for student in completed_students:
                buttons.append([
                    InlineKeyboardButton(
                        text=student.user.name,
                        callback_data=f"hw_student_completed_{student.id}"
                    )
                ])

        # Добавляем заголовок для не выполнивших
        if not_completed_students:
            buttons.append([InlineKeyboardButton(text="❌ Не выполнили:", callback_data="not_completed")])

            # Добавляем учеников, не выполнивших ДЗ
            for student in not_completed_students:
                # Используем telegram_id для ссылки на профиль
                telegram_username = student.user.telegram_id
                buttons.append([
                    InlineKeyboardButton(
                        text=student.user.name,
                        url=f"tg://user?id={telegram_username}"  # Ссылка на пользователя по ID
                    )
                ])

        if not completed_students and not not_completed_students:
            buttons.append([InlineKeyboardButton(text="❌ Студенты не найдены", callback_data="no_students")])

        buttons.extend(get_main_menu_back_button())

        return InlineKeyboardMarkup(inline_keyboard=buttons)

    except Exception as e:
        print(f"❌ Ошибка при получении студентов по ДЗ: {e}")
        import traceback
        traceback.print_exc()

        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Ошибка загрузки данных", callback_data="error_homework_students")],
            *get_main_menu_back_button()
        ])
