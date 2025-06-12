from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
import logging
import os

from common.keyboards import get_main_menu_back_button, get_home_and_back_kb
from common.manager_tests.register_handlers import register_test_handlers
from ..keyboards.homework import (
    get_courses_kb, get_subjects_kb, get_lessons_kb,
    get_time_limit_kb, get_correct_answer_kb, get_add_question_kb,
    get_confirm_homework_kb, get_homeworks_list_kb, get_photo_skip_kb, get_homework_management_kb
)
from .main import show_manager_main_menu
from database import (
    CourseRepository, SubjectRepository, LessonRepository, HomeworkRepository,
    QuestionRepository, AnswerOptionRepository, UserRepository, MicrotopicRepository
)

from aiogram.fsm.state import State, StatesGroup

class AddHomeworkStates(StatesGroup):
    main = State()
    select_course = State()
    select_subject = State()
    select_lesson = State()
    enter_test_name = State()
    add_question = State()
    select_topic = State()
    enter_question_text = State()
    add_question_photo = State()
    enter_answer_options = State()
    select_correct_answer = State()
    set_time_limit = State()
    confirm_test = State()
    delete_test = State()
    select_test_to_delete = State()
    request_topic = State()
    add_microtopic_name = State()  # Новое состояние для добавления микротемы
    process_topic = State()
    process_photo = State()
    skip_photo = State()

    # Состояния для редактирования
    edit_course = State()
    edit_subject = State()
    edit_lesson = State()
    edit_test_name = State()
    edit_question_text = State()
    edit_question_photo = State()
    edit_answer_options = State()
    edit_correct_answer = State()
    edit_time_limit = State()
    edit_topic = State()

# Настройка логгера
logger = logging.getLogger(__name__)

router = Router()

@router.callback_query(F.data == "manager_homework")
async def show_homework_management(callback: CallbackQuery, state: FSMContext):
    """Показ меню управления домашними заданиями"""
    logger.info("Вызван обработчик show_homework_management")

    await callback.message.edit_text(
        "Управление домашними заданиями",
        reply_markup=get_homework_management_kb()
    )
    await state.set_state(AddHomeworkStates.main)
    
@router.callback_query(AddHomeworkStates.main, F.data == "manager_add_homework")
async def start_add_homework(callback: CallbackQuery, state: FSMContext):
    """Начало добавления домашнего задания"""
    logger.info("Вызван обработчик start_add_homework")

    await callback.message.edit_text(
        "Выберите курс:",
        reply_markup=await get_courses_kb()
    )
    await state.set_state(AddHomeworkStates.select_course)

@router.callback_query(F.data == "manager_delete_homework")
async def start_delete_homework(callback: CallbackQuery, state: FSMContext):
    """Начало удаления домашнего задания"""
    logger.info("Вызван обработчик start_delete_homework")

    await callback.message.edit_text(
        "Выберите курс:",
        reply_markup=await get_courses_kb()
    )
    await state.set_state(AddHomeworkStates.delete_test)

@router.callback_query(AddHomeworkStates.select_course, F.data.startswith("course_"))
async def select_subject(callback: CallbackQuery, state: FSMContext):
    """Выбор предмета для ДЗ"""
    logger.info("Вызван обработчик select_subject")

    try:
        course_id = int(callback.data.replace("course_", ""))
        course = await CourseRepository.get_by_id(course_id)

        if not course:
            await callback.message.edit_text(
                "❌ Курс не найден. Попробуйте еще раз.",
                reply_markup=await get_courses_kb()
            )
            return

        await state.update_data(course_id=course_id, course_name=course.name)

        await callback.message.edit_text(
            f"Курс: {course.name}\n\n"
            "Выберите предмет для добавления домашнего задания:",
            reply_markup=await get_subjects_kb(course_id)
        )
        await state.set_state(AddHomeworkStates.select_subject)
    except Exception as e:
        logger.error(f"Ошибка при выборе курса: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка. Попробуйте еще раз.",
            reply_markup=await get_courses_kb()
        )

@router.callback_query(AddHomeworkStates.select_subject, F.data.startswith("subject_"))
async def select_lesson(callback: CallbackQuery, state: FSMContext):
    """Выбор урока для ДЗ"""
    logger.info("Вызван обработчик select_lesson")

    try:
        subject_id = int(callback.data.replace("subject_", ""))
        subject = await SubjectRepository.get_by_id(subject_id)

        if not subject:
            await callback.message.edit_text(
                "❌ Предмет не найден. Попробуйте еще раз.",
                reply_markup=await get_subjects_kb()
            )
            return

        user_data = await state.get_data()
        course_name = user_data.get("course_name", "")

        await state.update_data(subject_id=subject_id, subject_name=subject.name)

        await callback.message.edit_text(
            f"Курс: {course_name}\n"
            f"Предмет: {subject.name}\n\n"
            "Выберите урок для добавления домашнего задания:",
            reply_markup=await get_lessons_kb(subject_id)
        )
        await state.set_state(AddHomeworkStates.select_lesson)
    except Exception as e:
        logger.error(f"Ошибка при выборе предмета: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка. Попробуйте еще раз.",
            reply_markup=await get_subjects_kb()
        )

# Добавляем обработчик выбора урока
@router.callback_query(AddHomeworkStates.select_lesson, F.data.startswith("lesson_"))
async def select_homework_lesson(callback: CallbackQuery, state: FSMContext):
    """Выбор урока для ДЗ"""
    logger.info("Вызван обработчик select_homework_lesson")

    try:
        lesson_id = int(callback.data.replace("lesson_", ""))
        lesson = await LessonRepository.get_by_id(lesson_id)

        if not lesson:
            await callback.message.edit_text(
                "❌ Урок не найден. Попробуйте еще раз.",
                reply_markup=await get_lessons_kb()
            )
            return

        user_data = await state.get_data()
        course_name = user_data.get("course_name", "")
        subject_name = user_data.get("subject_name", "")

        await state.update_data(lesson_id=lesson_id, lesson_name=lesson.name)

        await callback.message.edit_text(
            f"Курс: {course_name}\n"
            f"Предмет: {subject_name}\n"
            f"Урок: {lesson.name}\n\n"
            "Введите название домашнего задания:"
        )
        await state.set_state(AddHomeworkStates.enter_test_name)
    except Exception as e:
        logger.error(f"Ошибка при выборе урока: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка. Попробуйте еще раз.",
            reply_markup=await get_lessons_kb()
        )

register_test_handlers(router, AddHomeworkStates, "manager")

# Регистрируем обработчики редактирования
from common.manager_tests.handlers import register_edit_handlers
register_edit_handlers(router, AddHomeworkStates)

@router.callback_query(AddHomeworkStates.confirm_test, F.data == "confirm_test")
async def save_homework(callback: CallbackQuery, state: FSMContext):
    """Сохранение ДЗ в базу данных"""
    logger.info("Вызван обработчик save_homework")
    user_data = await state.get_data()

    try:
        # Получаем данные из состояния
        test_name = user_data.get("test_name")
        course_id = user_data.get("course_id")
        subject_id = user_data.get("subject_id")
        lesson_id = user_data.get("lesson_id")
        questions = user_data.get("questions", [])

        # Получаем ID пользователя (менеджера)
        user = await UserRepository.get_by_telegram_id(callback.from_user.id)
        if not user:
            await callback.message.edit_text(
                "❌ Ошибка: пользователь не найден.",
                reply_markup=await get_courses_kb()
            )
            return

        # Создаем домашнее задание
        homework = await HomeworkRepository.create(
            name=test_name,
            course_id=course_id,
            subject_id=subject_id,
            lesson_id=lesson_id,
            created_by=user.id
        )

        # Создаем вопросы и варианты ответов
        for question_data in questions:
            # Получаем photo_path из photo_id (file_id от Telegram)
            photo_path = question_data.get("photo_id")  # Используем photo_id как photo_path

            # Получаем microtopic_id (может быть None)
            microtopic_id = question_data.get("microtopic_id")

            # Создаем вопрос
            question = await QuestionRepository.create(
                homework_id=homework.id,
                text=question_data.get("text", ""),
                photo_path=photo_path,
                microtopic_id=microtopic_id,
                time_limit=question_data.get("time_limit", 30)
            )

            # Создаем варианты ответов
            options = question_data.get("options", {})  # Словарь {A: "текст", B: "текст", ...}
            correct_answer = question_data.get("correct_answer", "0")  # Строка "0", "1", "2"...

            # Преобразуем correct_answer в индекс
            try:
                correct_answer_index = int(correct_answer)
            except (ValueError, TypeError):
                correct_answer_index = 0

            # Создаем список вариантов ответов в правильном порядке
            answer_options = []
            if options:
                # Сортируем по буквам (A, B, C, D...)
                sorted_options = sorted(options.items())
                answer_options = [text for letter, text in sorted_options]

            options_data = []
            for i, option_text in enumerate(answer_options):
                options_data.append({
                    "text": option_text,
                    "is_correct": i == correct_answer_index
                })

            if options_data:
                await AnswerOptionRepository.create_multiple(question.id, options_data)

        await callback.message.edit_text(
            f"✅ Домашнее задание '{test_name}' успешно создано и сохранено!\n"
            f"📊 Создано вопросов: {len(questions)}",
            reply_markup=await get_courses_kb()
        )
        await state.set_state(AddHomeworkStates.select_course)

    except ValueError as e:
        logger.error(f"Ошибка валидации при сохранении ДЗ: {e}")
        await callback.message.edit_text(
            f"❌ Ошибка: {str(e)}",
            reply_markup=await get_courses_kb()
        )
    except Exception as e:
        logger.error(f"Ошибка при сохранении ДЗ: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка при сохранении домашнего задания. Попробуйте еще раз.",
            reply_markup=await get_courses_kb()
        )

@router.callback_query(AddHomeworkStates.confirm_test, F.data == "edit_test")
async def edit_homework(callback: CallbackQuery, state: FSMContext):
    """Редактирование ДЗ"""
    logger.info("Вызван обработчик edit_homework")
    # Показываем сводку с возможностью редактирования
    from common.manager_tests.handlers import show_test_summary_with_edit
    await show_test_summary_with_edit(callback, state)

@router.callback_query(AddHomeworkStates.confirm_test, F.data == "cancel_test")
async def cancel_homework(callback: CallbackQuery, state: FSMContext):
    """Отмена создания ДЗ"""
    logger.info("Вызван обработчик cancel_homework")
    await callback.message.edit_text(
        "❌ Создание домашнего задания отменено."
    )
    await show_manager_main_menu(callback, state)

# Обработчики для удаления ДЗ
@router.callback_query(AddHomeworkStates.main, F.data == "manager_delete_homework")
async def select_homework_to_delete(callback: CallbackQuery, state: FSMContext):
    """Выбор ДЗ для удаления"""
    logger.info("Вызван обработчик select_homework_to_delete")
    # Сначала выбираем курс, предмет и урок
    await callback.message.edit_text(
        "Выберите курс:",
        reply_markup=await get_courses_kb()
    )
    await state.set_state(AddHomeworkStates.delete_test)

@router.callback_query(AddHomeworkStates.delete_test, F.data.startswith("course_"))
async def select_subject_for_delete(callback: CallbackQuery, state: FSMContext):
    """Выбор предмета для удаления ДЗ"""
    logger.info("Вызван обработчик select_subject_for_delete")

    try:
        course_id = int(callback.data.replace("course_", ""))
        course = await CourseRepository.get_by_id(course_id)

        if not course:
            await callback.message.edit_text(
                "❌ Курс не найден. Попробуйте еще раз.",
                reply_markup=await get_courses_kb()
            )
            return

        await state.update_data(course_id=course_id, course_name=course.name)

        await callback.message.edit_text(
            f"Курс: {course.name}\n\nВыберите предмет:",
            reply_markup=await get_subjects_kb(course_id)
        )
    except Exception as e:
        logger.error(f"Ошибка при выборе курса для удаления: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка. Попробуйте еще раз.",
            reply_markup=await get_courses_kb()
        )

@router.callback_query(AddHomeworkStates.delete_test, F.data.startswith("subject_"))
async def select_lesson_for_delete(callback: CallbackQuery, state: FSMContext):
    """Выбор урока для удаления ДЗ"""
    logger.info("Вызван обработчик select_lesson_for_delete")

    try:
        subject_id = int(callback.data.replace("subject_", ""))
        subject = await SubjectRepository.get_by_id(subject_id)

        if not subject:
            await callback.message.edit_text(
                "❌ Предмет не найден. Попробуйте еще раз.",
                reply_markup=await get_subjects_kb()
            )
            return

        user_data = await state.get_data()
        course_name = user_data.get("course_name", "")

        await state.update_data(subject_id=subject_id, subject_name=subject.name)

        await callback.message.edit_text(
            f"Курс: {course_name}\n"
            f"Предмет: {subject.name}\n\n"
            "Выберите урок:",
            reply_markup=await get_lessons_kb(subject_id)
        )
    except Exception as e:
        logger.error(f"Ошибка при выборе предмета для удаления: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка. Попробуйте еще раз.",
            reply_markup=await get_subjects_kb()
        )

@router.callback_query(AddHomeworkStates.delete_test, F.data.startswith("lesson_"))
async def show_homeworks_to_delete(callback: CallbackQuery, state: FSMContext):
    """Показ списка ДЗ для удаления"""
    logger.info("Вызван обработчик show_homeworks_to_delete")

    try:
        lesson_id = int(callback.data.replace("lesson_", ""))
        lesson = await LessonRepository.get_by_id(lesson_id)

        if not lesson:
            await callback.message.edit_text(
                "❌ Урок не найден. Попробуйте еще раз.",
                reply_markup=await get_lessons_kb()
            )
            return

        user_data = await state.get_data()
        course_name = user_data.get("course_name", "")
        subject_name = user_data.get("subject_name", "")

        await state.update_data(lesson_id=lesson_id, lesson_name=lesson.name)

        await callback.message.edit_text(
            f"Курс: {course_name}\n"
            f"Предмет: {subject_name}\n"
            f"Урок: {lesson.name}\n\n"
            "Выберите домашнее задание для удаления:",
            reply_markup=await get_homeworks_list_kb(lesson_id)
        )
        await state.set_state(AddHomeworkStates.select_test_to_delete)
    except Exception as e:
        logger.error(f"Ошибка при выборе урока для удаления: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка. Попробуйте еще раз.",
            reply_markup=await get_lessons_kb()
        )

@router.callback_query(AddHomeworkStates.select_test_to_delete, F.data.startswith("delete_hw_"))
async def confirm_delete_homework(callback: CallbackQuery, state: FSMContext):
    """Подтверждение удаления ДЗ"""
    logger.info("Вызван обработчик confirm_delete_homework")

    try:
        homework_id = int(callback.data.replace("delete_hw_", ""))
        homework = await HomeworkRepository.get_by_id(homework_id)

        if not homework:
            await callback.message.edit_text(
                "❌ Домашнее задание не найдено.",
                reply_markup=await get_homeworks_list_kb(0)
            )
            return

        await state.update_data(homework_id=homework_id)

        await callback.message.edit_text(
            f"Вы действительно хотите удалить домашнее задание '{homework.name}'?\n\n"
            f"⚠️ Это действие нельзя отменить. Будут удалены все вопросы и варианты ответов.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Да, удалить", callback_data="confirm_delete")],
                [InlineKeyboardButton(text="❌ Нет, отмена", callback_data="cancel_delete")]
            ])
        )
    except Exception as e:
        logger.error(f"Ошибка при подтверждении удаления ДЗ: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка. Попробуйте еще раз.",
            reply_markup=await get_homeworks_list_kb(0)
        )

@router.callback_query(F.data == "confirm_delete")
async def delete_homework(callback: CallbackQuery, state: FSMContext):
    """Удаление ДЗ"""
    logger.info("Вызван обработчик delete_homework")
    user_data = await state.get_data()
    homework_id = user_data.get("homework_id")

    try:
        if not homework_id:
            await callback.message.edit_text(
                "❌ Ошибка: ID домашнего задания не найден.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                   *get_main_menu_back_button()
                ])
            )
            return

        # Получаем информацию о ДЗ перед удалением
        homework = await HomeworkRepository.get_by_id(homework_id)
        homework_name = homework.name if homework else "Неизвестное ДЗ"

        # Удаляем ДЗ (каскадно удалятся вопросы и варианты ответов)
        success = await HomeworkRepository.delete(homework_id)

        if success:
            await callback.message.edit_text(
                f"✅ Домашнее задание '{homework_name}' успешно удалено!",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                   *get_main_menu_back_button()
                ])
            )
        else:
            await callback.message.edit_text(
                "❌ Не удалось удалить домашнее задание. Попробуйте еще раз.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                   *get_main_menu_back_button()
                ])
            )
    except Exception as e:
        logger.error(f"Ошибка при удалении ДЗ: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка при удалении домашнего задания.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
               *get_main_menu_back_button()
            ])
        )

@router.callback_query(F.data == "cancel_delete")
async def cancel_delete_homework(callback: CallbackQuery, state: FSMContext):
    """Отмена удаления ДЗ"""
    logger.info("Вызван обработчик cancel_delete_homework")
    user_data = await state.get_data()
    lesson_id = user_data.get("lesson_id", 0)

    await callback.message.edit_text(
        "Выберите домашнее задание для удаления:",
        reply_markup=await get_homeworks_list_kb(lesson_id)
    )
    await state.set_state(AddHomeworkStates.select_test_to_delete)


# Обработчики для микротем
@router.callback_query(F.data == "retry_microtopic")
async def retry_microtopic_selection(callback: CallbackQuery, state: FSMContext):
    """Повторный ввод номера микротемы"""
    from common.manager_tests.handlers import handle_microtopic_retry
    await handle_microtopic_retry(callback, state)
    await state.set_state(AddHomeworkStates.request_topic)


@router.callback_query(F.data.startswith("add_microtopic_"))
async def add_new_microtopic(callback: CallbackQuery, state: FSMContext):
    """Добавление новой микротемы"""
    from common.manager_tests.handlers import handle_add_microtopic
    await handle_add_microtopic(callback, state)


@router.message(AddHomeworkStates.add_microtopic_name)
async def process_microtopic_name(message: Message, state: FSMContext):
    """Обработка названия новой микротемы"""
    from common.manager_tests.handlers import process_new_microtopic_name
    await process_new_microtopic_name(message, state)



