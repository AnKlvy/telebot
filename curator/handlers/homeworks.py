from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from common.utils import check_if_id_in_callback_data
from ..keyboards.main import get_curator_main_menu_kb
from common.keyboards import get_courses_kb, get_subjects_kb, get_lessons_kb, get_main_menu_back_button
from ..keyboards.homeworks import get_homework_menu_kb, get_groups_kb
from common.analytics.keyboards import get_groups_for_analytics_kb
from database import (CuratorRepository, UserRepository, GroupRepository, StudentRepository,
                     CourseRepository, LessonRepository, HomeworkRepository, HomeworkResultRepository)

class CuratorHomeworkStates(StatesGroup):
    homework_menu = State()
    student_stats_course = State()
    student_stats_group = State()
    student_stats_lesson = State()
    student_stats_list = State()
    group_stats_group = State()
    group_stats_result = State()
    # Состояния для отправки сообщений
    enter_homework_message = State()
    confirm_homework_message = State()


router = Router()

@router.callback_query(F.data == "curator_homeworks")
async def show_homework_menu(callback: CallbackQuery, state: FSMContext):
    """Показать меню домашних заданий"""
    await callback.message.edit_text(
        "Выберите тип статистики:",
        reply_markup=get_homework_menu_kb()
    )
    await state.set_state(CuratorHomeworkStates.homework_menu)

# Обработчики для статистики по ученику
@router.callback_query(CuratorHomeworkStates.homework_menu, F.data == "hw_student_stats")
async def select_student_stats_course(callback: CallbackQuery, state: FSMContext):
    """Выбор курса для статистики по ученику"""
    try:
        # Получаем все курсы из базы данных
        courses = await CourseRepository.get_all()

        if not courses:
            await callback.message.edit_text(
                "❌ Курсы не найдены",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    *get_main_menu_back_button()
                ])
            )
            return

        # Создаем клавиатуру с курсами
        buttons = []
        for course in courses:
            buttons.append([
                InlineKeyboardButton(
                    text=course.name,
                    callback_data=f"course_{course.id}"
                )
            ])

        buttons.extend(get_main_menu_back_button())

        await callback.message.edit_text(
            "Выберите курс:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
        )
        await state.set_state(CuratorHomeworkStates.student_stats_course)

    except Exception as e:
        await callback.message.edit_text(
            f"❌ Ошибка при загрузке курсов: {str(e)}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                *get_main_menu_back_button()
            ])
        )
        print(f"Ошибка в select_student_stats_course: {e}")

@router.callback_query(CuratorHomeworkStates.student_stats_course, F.data.startswith("course_"))
async def select_student_stats_group(callback: CallbackQuery, state: FSMContext):
    """Выбор группы для статистики по ученику"""
    course_id = int(await check_if_id_in_callback_data("course_", callback, state, "course"))
    await state.update_data(selected_course=course_id)

    # Получаем группы куратора через аналитическую клавиатуру
    groups_kb = await get_groups_for_analytics_kb("curator", callback.from_user.id)

    await callback.message.edit_text(
        "Выберите группу:",
        reply_markup=groups_kb
    )
    await state.set_state(CuratorHomeworkStates.student_stats_group)

@router.callback_query(CuratorHomeworkStates.student_stats_group, F.data.startswith("analytics_group_"))
async def select_student_stats_lesson(callback: CallbackQuery, state: FSMContext):
    """Выбор урока для статистики по ученику"""
    group_id = int(await check_if_id_in_callback_data("analytics_group_", callback, state, "group"))
    await state.update_data(selected_group=group_id)

    try:
        # Получаем данные о выбранном курсе и группе
        user_data = await state.get_data()
        course_id = user_data.get("selected_course")

        # Получаем информацию о группе
        group = await GroupRepository.get_by_id(group_id)
        if not group:
            await callback.message.edit_text(
                "❌ Группа не найдена",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    *get_main_menu_back_button()
                ])
            )
            return

        # Получаем уроки для выбранного курса и предмета группы
        lessons = await LessonRepository.get_by_subject_and_course(group.subject_id, course_id)

        if not lessons:
            await callback.message.edit_text(
                f"❌ Уроки не найдены для курса и предмета группы {group.name}",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    *get_main_menu_back_button()
                ])
            )
            return

        # Создаем клавиатуру с уроками
        buttons = []
        for lesson in lessons:
            buttons.append([
                InlineKeyboardButton(
                    text=lesson.name,
                    callback_data=f"lesson_{lesson.id}"
                )
            ])

        buttons.extend(get_main_menu_back_button())

        await callback.message.edit_text(
            f"Выберите урок для группы {group.name} ({group.subject.name}):",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
        )
        await state.set_state(CuratorHomeworkStates.student_stats_lesson)

    except Exception as e:
        await callback.message.edit_text(
            f"❌ Ошибка при загрузке уроков: {str(e)}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                *get_main_menu_back_button()
            ])
        )
        print(f"Ошибка в select_student_stats_group: {e}")



@router.callback_query(CuratorHomeworkStates.student_stats_lesson, F.data.startswith("lesson_"))
async def show_student_stats_list(callback: CallbackQuery, state: FSMContext):
    """Показать список учеников с выполненными и невыполненными ДЗ"""
    lesson_id = int(callback.data.replace("lesson_", ""))
    await state.update_data(selected_lesson=lesson_id)

    try:
        # Получаем данные о выбранных параметрах
        user_data = await state.get_data()
        course_id = user_data.get("selected_course")
        group_id = user_data.get("selected_group")

        # Получаем информацию из базы данных
        course = await CourseRepository.get_by_id(course_id)
        group = await GroupRepository.get_by_id(group_id)
        lesson = await LessonRepository.get_by_id(lesson_id)

        if not course or not group or not lesson:
            await callback.message.edit_text(
                "❌ Ошибка: не найдены данные о курсе, группе или уроке",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    *get_main_menu_back_button()
                ])
            )
            return

        # Получаем студентов группы
        students = await StudentRepository.get_by_group(group_id)

        # Получаем домашние задания для урока
        homeworks = await HomeworkRepository.get_by_subject_lesson(group.subject_id, lesson_id)

        # Формируем список студентов с их статусом выполнения ДЗ
        completed_students = []
        not_completed_students = []

        for student in students:
            # Проверяем выполнение всех ДЗ урока
            has_completed_all = True

            for homework in homeworks:
                # Проверяем, есть ли у студента результат по этому ДЗ
                attempts = await HomeworkResultRepository.get_student_homework_attempts(student.id, homework.id)
                if not attempts:
                    has_completed_all = False
                    break

            if has_completed_all and homeworks:  # Есть ДЗ и все выполнены
                completed_students.append(student)
            else:
                not_completed_students.append(student)

        # Формируем текст с выполнившими студентами
        completed_text = ""
        if completed_students:
            completed_text = "\n".join([f"• {student.user.name}" for student in completed_students])

        # Создаем клавиатуру только с не выполнившими студентами
        buttons = []

        if not_completed_students:
            for student in not_completed_students:
                buttons.append([
                    InlineKeyboardButton(
                        text=student.user.name,
                        callback_data=f"hw_message_student_{student.id}"
                    )
                ])

        buttons.extend(get_main_menu_back_button())

        # Формируем полный текст сообщения
        message_text = (
            f"📊 Статистика выполнения ДЗ\n"
            f"👥 Группа: {group.name} ({group.subject.name})\n"
            f"📚 Курс: {course.name}\n"
            f"📖 Урок: {lesson.name}\n\n"
            f"✅ Выполнили: {len(completed_students)}\n"
        )

        if completed_text:
            message_text += completed_text + "\n\n"

        message_text += f"❌ Не выполнили: {len(not_completed_students)}"

        if not_completed_students:
            message_text += "\n\nНажмите на имя ученика для отправки сообщения:"

        await callback.message.edit_text(
            message_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
        )
        await state.set_state(CuratorHomeworkStates.student_stats_list)

    except Exception as e:
        await callback.message.edit_text(
            f"❌ Ошибка при загрузке статистики: {str(e)}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                *get_main_menu_back_button()
            ])
        )
        print(f"Ошибка в show_student_stats_list: {e}")

# Обработчики для статистики по группе
@router.callback_query(CuratorHomeworkStates.homework_menu, F.data == "hw_group_stats")
async def select_group_stats_group(callback: CallbackQuery, state: FSMContext):
    """Выбор группы для статистики по группе"""
    # Получаем группы куратора через аналитическую клавиатуру
    groups_kb = await get_groups_for_analytics_kb("curator", callback.from_user.id)

    await callback.message.edit_text(
        "Выберите группу для просмотра статистики:",
        reply_markup=groups_kb
    )
    await state.set_state(CuratorHomeworkStates.group_stats_group)

@router.callback_query(CuratorHomeworkStates.group_stats_group, F.data.startswith("analytics_group_"))
async def show_group_stats(callback: CallbackQuery, state: FSMContext):
    """Показать статистику по группе"""
    group_id = int(callback.data.replace("analytics_group_", ""))
    
    # В реальном приложении здесь будет запрос к базе данных
    # для получения статистики по группе
    group_data = {
        "group1": {
            "name": "Интенсив. География",
            "subject": "Химия",
            "homework_completion": 75,
            "topics": {
                "Алканы": 82,
                "Изомерия": 37,
                "Кислоты": 66
            },
            "rating": [
                {"name": "Аружан", "points": 870},
                {"name": "Диана", "points": 800},
                {"name": "Мадияр", "points": 780}
            ]
        },
        "group2": {
            "name": "Интенсив. Математика",
            "subject": "Химия",
            "homework_completion": 80,
            "topics": {
                "Алканы": 78,
                "Изомерия": 42,
                "Кислоты": 70
            },
            "rating": [
                {"name": "Арман", "points": 850},
                {"name": "Алия", "points": 820},
                {"name": "Диас", "points": 790}
            ]
        }
    }
    
    stats = group_data.get(group_id, {
        "name": "Неизвестная группа",
        "subject": "Неизвестный предмет",
        "homework_completion": 0,
        "topics": {},
        "rating": []
    })
    
    # Формируем текст с рейтингом
    rating_text = ""
    if stats["rating"]:
        rating_text = "📋 Рейтинг по баллам:\n"
        for i, student in enumerate(stats["rating"], 1):
            rating_text += f"{i}. {student['name']} — {student['points']} баллов\n"
    
    # Формируем текст с темами с единым форматированием
    topics_text = "📈 Средний % понимания по микротемам:\n"
    for topic, percentage in stats["topics"].items():
        # Добавляем эмодзи статуса для групповой статистики
        status = "✅" if percentage >= 80 else "❌" if percentage <= 40 else "⚠️"
        topics_text += f"• {topic} — {percentage}% {status}\n"
    
    await callback.message.edit_text(
        f"📗 {stats['subject']}\n"
        f"📊 Средний % выполнения ДЗ: {stats['homework_completion']}%\n"
        f"{topics_text}\n"
        f"{rating_text}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            *get_main_menu_back_button()
        ])
    )
    await state.set_state(CuratorHomeworkStates.group_stats_result)


# Обработчики для отправки сообщений студентам
@router.callback_query(CuratorHomeworkStates.student_stats_list, F.data.startswith("hw_message_student_"))
async def enter_homework_message(callback: CallbackQuery, state: FSMContext):
    """Ввод сообщения для студента, не выполнившего ДЗ"""
    student_id = int(callback.data.replace("hw_message_student_", ""))

    try:
        # Получаем информацию о студенте
        student = await StudentRepository.get_by_id(student_id)
        if not student:
            await callback.message.edit_text(
                "❌ Студент не найден",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    *get_main_menu_back_button()
                ])
            )
            return

        # Сохраняем данные о студенте
        await state.update_data(
            selected_student_id=student_id,
            student_name=student.user.name
        )

        await callback.message.edit_text(
            f"Введите текст сообщения для ученика {student.user.name}:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                *get_main_menu_back_button()
            ])
        )
        await state.set_state(CuratorHomeworkStates.enter_homework_message)

    except Exception as e:
        await callback.message.edit_text(
            f"❌ Ошибка при выборе студента: {str(e)}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                *get_main_menu_back_button()
            ])
        )
        print(f"Ошибка в enter_homework_message: {e}")


@router.message(CuratorHomeworkStates.enter_homework_message)
async def confirm_homework_message(message, state: FSMContext):
    """Подтверждение отправки сообщения студенту"""
    message_text = message.text
    user_data = await state.get_data()
    student_name = user_data.get("student_name", "Неизвестный ученик")

    await state.update_data(message_text=message_text)

    # Удаляем сообщение пользователя
    await message.delete()

    await message.answer(
        f"Отправить сообщение ученику {student_name}?\n\n"
        f"Текст сообщения:\n{message_text}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Отправить", callback_data="send_homework_message")],
            [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_homework_message")]
        ])
    )
    await state.set_state(CuratorHomeworkStates.confirm_homework_message)


@router.callback_query(CuratorHomeworkStates.confirm_homework_message, F.data == "send_homework_message")
async def send_homework_message(callback: CallbackQuery, state: FSMContext):
    """Отправка сообщения студенту"""
    user_data = await state.get_data()
    student_id = user_data.get("selected_student_id")
    student_name = user_data.get("student_name", "Неизвестный ученик")
    message_text = user_data.get("message_text", "")

    try:
        # Получаем студента для получения telegram_id
        student = await StudentRepository.get_by_id(student_id)
        if not student:
            await callback.message.edit_text(
                "❌ Студент не найден",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    *get_main_menu_back_button()
                ])
            )
            return

        telegram_id = student.user.telegram_id
        success = False
        error_message = ""

        if telegram_id:
            try:
                # Отправляем сообщение ученику
                await callback.bot.send_message(
                    chat_id=telegram_id,
                    text=f"Сообщение от куратора:\n\n{message_text}"
                )
                success = True
            except Exception as e:
                print(f"Ошибка при отправке сообщения: {e}")
                error_str = str(e)
                if "Forbidden" in error_str or "bot was blocked" in error_str or "chat not found" in error_str:
                    error_message = f"❌ Ученик {student_name} никогда не писал боту.\n\nПопросите ученика написать боту любое сообщение (например, /start), а затем попробуйте снова."
                else:
                    error_message = f"❌ Не удалось отправить сообщение ученику {student_name}.\nОшибка: {error_str}"
        else:
            error_message = f"❌ У ученика {student_name} не указан Telegram ID."

        if success:
            await callback.message.edit_text(
                f"✅ Сообщение успешно отправлено ученику {student_name}",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    *get_main_menu_back_button()
                ])
            )
        else:
            await callback.message.edit_text(
                error_message,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    *get_main_menu_back_button()
                ])
            )

        # Очищаем состояние
        await state.clear()

    except Exception as e:
        await callback.message.edit_text(
            f"❌ Ошибка при отправке сообщения: {str(e)}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                *get_main_menu_back_button()
            ])
        )
        print(f"Ошибка в send_homework_message: {e}")


@router.callback_query(CuratorHomeworkStates.confirm_homework_message, F.data == "cancel_homework_message")
async def cancel_homework_message(callback: CallbackQuery, state: FSMContext):
    """Отмена отправки сообщения"""
    await callback.message.edit_text(
        "❌ Отправка сообщения отменена",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            *get_main_menu_back_button()
        ])
    )
    await state.clear()

