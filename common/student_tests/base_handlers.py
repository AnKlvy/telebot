"""
Базовые обработчики для студентских тестов
"""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from .states import StudentTestsStates
from .keyboards import (
    get_test_subjects_kb,
    get_month_test_kb,
    get_back_to_test_kb
)
from .menu import show_tests_menu
from .course_entry_handlers import handle_course_entry_test_real
from .month_handlers import generate_month_test_questions, finish_month_entry_test, finish_month_control_test
from database.repositories.month_test_repository import MonthTestRepository
from database.repositories.month_entry_test_result_repository import MonthEntryTestResultRepository
from database.repositories.month_control_test_result_repository import MonthControlTestResultRepository
from database.repositories.microtopic_repository import MicrotopicRepository
from database.repositories.student_repository import StudentRepository
from database.repositories.user_repository import UserRepository
from database.repositories.subject_repository import SubjectRepository
from common.quiz_registrator import send_next_question
from common.statistics import (
    get_test_results,
    format_test_result,
    format_test_comparison
)
from ..utils import check_if_id_in_callback_data

# Настройка логгера
logger = logging.getLogger(__name__)

router = Router()


# Основные обработчики навигации
@router.callback_query(F.data == "student_tests")
async def show_student_tests(callback: CallbackQuery, state: FSMContext):
    """Показать меню тестов для студента"""
    await show_tests_menu(callback, state, "student")


# Удаляем дублирующий обработчик - он будет добавлен ниже с фильтрами состояний


# Входной тест курса
@router.callback_query(StudentTestsStates.main, F.data == "course_entry_test")
async def show_course_entry_subjects(callback: CallbackQuery, state: FSMContext):
    """Показать предметы для входного теста курса"""
    await callback.message.edit_text(
        "Выберите предмет для входного теста курса:",
        reply_markup=await get_test_subjects_kb("course_entry", user_id=callback.from_user.id)
    )
    await state.set_state(StudentTestsStates.course_entry_subjects)


@router.callback_query(StudentTestsStates.course_entry_subjects, F.data.startswith("course_entry_sub_"))
async def handle_course_entry_subject(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора предмета для входного теста курса"""
    subject_id = callback.data.replace("course_entry_sub_", "")
    await handle_course_entry_test_real(callback, state, subject_id)


# Входной тест месяца
@router.callback_query(StudentTestsStates.main, F.data == "month_entry_test")
async def show_month_entry_subjects(callback: CallbackQuery, state: FSMContext):
    """Показать предметы для входного теста месяца"""
    await callback.message.edit_text(
        "Выберите предмет для входного теста месяца:",
        reply_markup=await get_test_subjects_kb("month_entry", user_id=callback.from_user.id)
    )
    await state.set_state(StudentTestsStates.month_entry_subjects)


@router.callback_query(StudentTestsStates.month_entry_subjects, F.data.startswith("month_entry_sub_"))
async def handle_month_entry_subject(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора предмета для входного теста месяца"""
    # Получаем subject_id и сохраняем в состоянии
    subject_id = await check_if_id_in_callback_data(
        callback_starts_with="month_entry_sub_",
        callback=callback,
        state=state,
        id_type="subject_id"
    )

    # Показываем доступные месяцы для выбранного предмета
    await callback.message.edit_text(
        f"Выберите месяц для входного теста:",
        reply_markup=await get_month_test_kb("month_entry", subject_id, user_id=callback.from_user.id)
    )
    await state.set_state(StudentTestsStates.month_entry_subject_selected)


@router.callback_query(StudentTestsStates.month_entry_subject_selected, F.data.startswith("month_entry_"))
async def handle_month_entry_month(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора месяца для входного теста месяца"""
    # Парсим данные: month_entry_subject_test_testid
    parts = callback.data.replace("month_entry_", "").split("_")
    if len(parts) >= 3 and parts[1] == "test":
        subject_id = parts[0]
        test_id = int(parts[2])
        await handle_month_entry_test_by_id(callback, state, subject_id, test_id)
    else:
        await callback.message.edit_text(
            "❌ Ошибка: неверные параметры теста",
            reply_markup=get_back_to_test_kb()
        )


# Контрольный тест месяца
@router.callback_query(StudentTestsStates.main, F.data == "month_control_test")
async def show_month_control_subjects(callback: CallbackQuery, state: FSMContext):
    """Показать предметы для контрольного теста месяца"""
    await callback.message.edit_text(
        "Выберите предмет для контрольного теста месяца:",
        reply_markup=await get_test_subjects_kb("month_control", user_id=callback.from_user.id)
    )
    await state.set_state(StudentTestsStates.month_control_subjects)


@router.callback_query(StudentTestsStates.month_control_subjects, F.data.startswith("month_control_sub_"))
async def handle_month_control_subject(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора предмета для контрольного теста месяца"""
    from common.utils import check_if_id_in_callback_data

    # Получаем subject_id и сохраняем в состоянии
    subject_id = await check_if_id_in_callback_data(
        callback_starts_with="month_control_sub_",
        callback=callback,
        state=state,
        id_type="subject_id"
    )


    # Показываем доступные месяцы для выбранного предмета
    await callback.message.edit_text(
        f"Выберите месяц для контрольного теста:",
        reply_markup=await get_month_test_kb("month_control", subject_id, user_id=callback.from_user.id)
    )
    await state.set_state(StudentTestsStates.month_control_subject_selected)


@router.callback_query(StudentTestsStates.month_control_subject_selected, F.data.startswith("month_control_"))
async def handle_month_control_month(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора месяца для контрольного теста месяца"""
    # Парсим данные: month_control_subject_test_testid
    parts = callback.data.replace("month_control_", "").split("_")
    if len(parts) >= 3 and parts[1] == "test":
        subject_id = parts[0]
        test_id = int(parts[2])
        await handle_month_control_test_by_id(callback, state, test_id)
    else:
        await callback.message.edit_text(
            "❌ Ошибка: неверные параметры теста",
            reply_markup=get_back_to_test_kb()
        )


async def handle_month_entry_test_by_id(callback: CallbackQuery, state: FSMContext, subject_id: str, test_id: int):
    """Обработчик для входного теста месяца по ID теста"""
    telegram_id = callback.from_user.id
    logger.info(f"ВЫЗОВ: handle_month_entry_test_by_id, telegram_id={telegram_id}, subject_id={subject_id}, test_id={test_id}")

    try:
        # Получаем пользователя и студента
        user = await UserRepository.get_by_telegram_id(telegram_id)
        if not user:
            await callback.message.edit_text(
                "❌ Пользователь не найден в системе",
                reply_markup=get_back_to_test_kb()
            )
            return

        student = await StudentRepository.get_by_user_id(user.id)
        if not student:
            await callback.message.edit_text(
                "❌ Студент не найден в системе",
                reply_markup=get_back_to_test_kb()
            )
            return

        # Получаем тест месяца по ID
        month_test = await MonthTestRepository.get_by_id(test_id)
        if not month_test:
            await callback.message.edit_text(
                "❌ Тест месяца не найден",
                reply_markup=get_back_to_test_kb()
            )
            return

        # Проверяем, не проходил ли студент уже этот тест
        existing_result = await MonthEntryTestResultRepository.get_by_student_and_month_test(
            student_id=student.id,
            month_test_id=month_test.id
        )

        if existing_result:
            # Тест уже пройден - показываем статистику
            await show_month_entry_test_statistics(callback, state, existing_result)
            return

        # Генерируем вопросы для теста
        test_questions = await generate_month_test_questions(month_test.id)
        if not test_questions:
            await callback.message.edit_text(
                "❌ Не удалось сгенерировать вопросы для теста",
                reply_markup=get_back_to_test_kb()
            )
            return

        # Переходим к подтверждению теста вместо прямого запуска
        from .month_handlers import show_month_entry_test_confirmation
        await show_month_entry_test_confirmation(callback, state, test_questions, student.id, month_test)

        logger.info(f"Показано подтверждение входного теста месяца: {len(test_questions)} вопросов")

    except Exception as e:
        logger.error(f"Ошибка при обработке входного теста месяца по ID: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка при запуске теста",
            reply_markup=get_back_to_test_kb()
        )


async def handle_month_control_test_by_id(callback: CallbackQuery, state: FSMContext, month_test_id: int):
    """Обработчик для контрольного теста месяца по ID теста"""
    telegram_id = callback.from_user.id
    logger.info(f"ВЫЗОВ: handle_month_control_test_by_id, telegram_id={telegram_id}, test_id={month_test_id}")

    try:
        # Получаем пользователя и студента
        user = await UserRepository.get_by_telegram_id(telegram_id)
        if not user:
            await callback.message.edit_text(
                "❌ Пользователь не найден в системе",
                reply_markup=get_back_to_test_kb()
            )
            return

        student = await StudentRepository.get_by_user_id(user.id)
        if not student:
            await callback.message.edit_text(
                "❌ Студент не найден в системе",
                reply_markup=get_back_to_test_kb()
            )
            return

        # Получаем тест месяца по ID
        month_test = await MonthTestRepository.get_by_id(month_test_id)
        if not month_test:
            await callback.message.edit_text(
                "❌ Тест месяца не найден",
                reply_markup=get_back_to_test_kb()
            )
            return

        # Проверяем, не проходил ли студент уже этот тест
        existing_result = await MonthControlTestResultRepository.get_by_student_and_month_test(
            student_id=student.id,
            month_test_id=month_test.id
        )

        if existing_result:
            # Тест уже пройден - показываем статистику
            await show_month_control_test_statistics(callback, state, existing_result)
            return

        # Проверяем, прошел ли студент соответствующий входной тест (теперь по тому же тесту)
        entry_result = await MonthEntryTestResultRepository.get_by_student_and_month_test(
            student_id=student.id,
            month_test_id=month_test.id
        )
        if not entry_result:
            await callback.message.edit_text(
                f"❌ Сначала необходимо пройти входной тест месяца '{month_test.name}'",
                reply_markup=get_back_to_test_kb()
            )
            return

        # Генерируем вопросы для теста (используем ту же функцию, что и для входного)
        test_questions = await generate_month_test_questions(month_test.id)
        if not test_questions:
            await callback.message.edit_text(
                "❌ Не удалось сгенерировать вопросы для теста",
                reply_markup=get_back_to_test_kb()
            )
            return

        # Переходим к подтверждению теста вместо прямого запуска
        from .month_handlers import show_month_control_test_confirmation
        await show_month_control_test_confirmation(callback, state, test_questions, student.id, month_test)

        logger.info(f"Показано подтверждение контрольного теста месяца: {len(test_questions)} вопросов")

    except Exception as e:
        logger.error(f"Ошибка при обработке контрольного теста месяца по ID: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка при запуске теста",
            reply_markup=get_back_to_test_kb()
        )


async def show_month_entry_test_statistics(callback: CallbackQuery, state: FSMContext, test_result):
    """Показать статистику уже пройденного входного теста месяца"""
    try:
        # Получаем полную информацию о тесте с загруженными связями
        from database.repositories.month_entry_test_result_repository import MonthEntryTestResultRepository
        full_test_result = await MonthEntryTestResultRepository.get_by_id(test_result.id)

        if not full_test_result:
            await callback.message.edit_text(
                "❌ Результат теста не найден",
                reply_markup=get_back_to_test_kb()
            )
            return

        # Получаем предмет и тест месяца
        from database.repositories.subject_repository import SubjectRepository
        from database.repositories.month_test_repository import MonthTestRepository

        subject = await SubjectRepository.get_by_id(full_test_result.month_test.subject_id)
        month_test = await MonthTestRepository.get_by_id(full_test_result.month_test_id)

        if not subject or not month_test:
            await callback.message.edit_text(
                "❌ Данные теста не найдены",
                reply_markup=get_back_to_test_kb()
            )
            return

        # Формируем основной текст результата
        result_text = f"📊 Результат входного теста месяца\n\n"
        result_text += f"📗 {subject.name}\n"
        result_text += f"Тест: {month_test.name}\n"
        result_text += f"Верных: {full_test_result.correct_answers} / {full_test_result.total_questions}\n"
        result_text += f"Процент: {full_test_result.score_percentage}%\n"
        result_text += f"Дата прохождения: {full_test_result.completed_at.strftime('%d.%m.%Y %H:%M')}\n\n"
        result_text += "Выберите тип аналитики:"

        # Создаем кнопки для детальной аналитики (как у куратора)
        from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
        buttons = [
            [InlineKeyboardButton(
                text="📊 Проценты по микротемам",
                callback_data=f"student_month_entry_detailed_{full_test_result.id}"
            )],
            [InlineKeyboardButton(
                text="💪 Сильные/слабые темы",
                callback_data=f"student_month_entry_summary_{full_test_result.id}"
            )]
        ]
        buttons.extend(get_back_to_test_kb().inline_keyboard)

        await callback.message.edit_text(
            result_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
        )
        await state.set_state(StudentTestsStates.month_entry_result)

        logger.info(f"Показана статистика теста месяца для студента {full_test_result.student_id}")

    except Exception as e:
        logger.error(f"Ошибка при показе статистики теста месяца: {e}")
        await callback.message.edit_text(
            "❌ Ошибка при загрузке статистики теста",
            reply_markup=get_back_to_test_kb()
        )


async def show_month_control_test_statistics(callback: CallbackQuery, state: FSMContext, test_result):
    """Показать статистику уже пройденного контрольного теста месяца"""
    try:
        # Получаем тест месяца отдельно (объект test_result может быть отвязан от сессии)
        month_test = await MonthTestRepository.get_by_id(test_result.month_test_id)
        if not month_test:
            logger.error(f"Тест месяца с ID {test_result.month_test_id} не найден")
            await callback.message.edit_text(
                "❌ Ошибка при загрузке данных теста",
                reply_markup=get_back_to_test_kb()
            )
            return

        # Получаем статистику по микротемам
        microtopic_stats = await MonthControlTestResultRepository.get_microtopic_statistics(test_result.id)

        # Получаем названия микротем
        microtopics = await MicrotopicRepository.get_by_subject(month_test.subject_id)
        microtopic_names = {mt.number: mt.name for mt in microtopics}

        # Пытаемся найти соответствующий входной результат для сравнения
        comparison_text = ""
        entry_result = await MonthEntryTestResultRepository.get_by_student_and_month_test(
            test_result.student_id, test_result.month_test_id
        )
        if entry_result:
            # Показываем сравнение с входным тестом
            comparison_text = f"\n📊 Сравнение с входным тестом:\n"
            comparison_text += f"Верных: {entry_result.correct_answers}/{entry_result.total_questions} → {test_result.correct_answers}/{test_result.total_questions}\n"

            # Рассчитываем общий рост
            if entry_result.score_percentage > 0:
                growth = ((test_result.score_percentage - entry_result.score_percentage) / entry_result.score_percentage) * 100
                if growth > 0:
                    comparison_text += f"📈 Общий рост: +{growth:.1f}%\n"
                elif growth < 0:
                    comparison_text += f"📉 Общее снижение: {growth:.1f}%\n"
                else:
                    comparison_text += f"📊 Результат остался на том же уровне\n"
            else:
                if test_result.score_percentage > 0:
                    comparison_text += f"📈 Рост: +{test_result.score_percentage:.1f} п.п.\n"

        # Формируем результат
        result_text = f"🎉 Контрольный тест месяца завершен!\n\n"
        result_text += f"📗 {month_test.subject.name}\n"
        result_text += f"Тест: {month_test.name}\n"
        result_text += f"Верных ответов: {test_result.correct_answers} / {test_result.total_questions}\n"
        result_text += f"Процент: {test_result.score_percentage}%\n"
        result_text += comparison_text

        result_text += "\nВыберите тип аналитики:"

        # Создаем кнопки для детальной аналитики (как у куратора)
        from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
        buttons = [
            [InlineKeyboardButton(
                text="📊 Проценты по микротемам",
                callback_data=f"student_month_control_detailed_{test_result.id}"
            )],
            [InlineKeyboardButton(
                text="💪 Сильные/слабые темы",
                callback_data=f"student_month_control_summary_{test_result.id}"
            )]
        ]
        buttons.extend(get_back_to_test_kb().inline_keyboard)

        await callback.message.edit_text(
            result_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
        )
        await state.set_state(StudentTestsStates.month_control_result)

        logger.info(f"Показана статистика контрольного теста месяца для студента {test_result.student_id}")

    except Exception as e:
        logger.error(f"Ошибка при показе статистики контрольного теста месяца: {e}")
        await callback.message.edit_text(
            "❌ Ошибка при получении статистики",
            reply_markup=get_back_to_test_kb()
        )


# Все обработчики "Назад" удалены - используется общая система навигации через common/navigation.py


# Обработчики детальной аналитики для студентов (как у куратора)
@router.callback_query(StudentTestsStates.test_result, F.data.startswith("student_month_entry_detailed_"))
async def show_student_month_entry_detailed(callback: CallbackQuery, state: FSMContext):
    """Показать детальную статистику по микротемам входного теста месяца для студента"""
    try:
        # Формат: student_month_entry_detailed_TEST_RESULT_ID
        test_result_id = int(callback.data.split("_")[-1])

        # Получаем результат теста
        from database.repositories.month_entry_test_result_repository import MonthEntryTestResultRepository
        test_result = await MonthEntryTestResultRepository.get_by_id(test_result_id)

        if not test_result:
            await callback.message.edit_text(
                "❌ Результат теста не найден",
                reply_markup=get_back_to_test_kb()
            )
            return

        # Получаем статистику по микротемам
        microtopic_stats = await MonthEntryTestResultRepository.get_microtopic_statistics(test_result.id)

        # Получаем тест месяца и названия микротем
        from database.repositories.microtopic_repository import MicrotopicRepository
        from database.repositories.subject_repository import SubjectRepository
        from database.repositories.month_test_repository import MonthTestRepository

        month_test = await MonthTestRepository.get_by_id(test_result.month_test_id)
        if not month_test:
            await callback.message.edit_text(
                "❌ Тест месяца не найден",
                reply_markup=get_back_to_test_kb()
            )
            return

        microtopics = await MicrotopicRepository.get_by_subject(month_test.subject_id)
        microtopic_names = {mt.number: mt.name for mt in microtopics}

        subject = await SubjectRepository.get_by_id(month_test.subject_id)

        # Формируем детальную статистику
        result_text = f"📊 Детальная статистика входного теста месяца\n\n"
        result_text += f"📗 {subject.name}\n"
        result_text += f"Тест: {month_test.name}\n"
        result_text += f"Верных: {test_result.correct_answers} / {test_result.total_questions}\n\n"
        result_text += "📈 % правильных ответов по микротемам:\n"

        if microtopic_stats:
            for microtopic_num in sorted(microtopic_stats.keys()):
                stats = microtopic_stats[microtopic_num]
                microtopic_name = microtopic_names.get(microtopic_num, f"Микротема {microtopic_num}")
                percentage = stats['percentage']

                # Определяем эмодзи статуса
                if percentage >= 80:
                    status = "✅"
                elif percentage <= 40:
                    status = "❌"
                else:
                    status = "⚠️"

                result_text += f"• {microtopic_name} — {percentage}% {status}\n"
        else:
            result_text += "Нет данных по микротемам\n"

        await callback.message.edit_text(
            result_text,
            reply_markup=get_back_to_test_kb()
        )

    except Exception as e:
        logger.error(f"Ошибка при получении детальной статистики входного теста месяца: {e}")
        await callback.message.edit_text(
            "❌ Ошибка при получении статистики",
            reply_markup=get_back_to_test_kb()
        )


@router.callback_query(StudentTestsStates.test_result, F.data.startswith("student_month_entry_summary_"))
async def show_student_month_entry_summary(callback: CallbackQuery, state: FSMContext):
    """Показать сводку по сильным/слабым темам входного теста месяца для студента"""
    try:
        # Формат: student_month_entry_summary_TEST_RESULT_ID
        test_result_id = int(callback.data.split("_")[-1])

        # Получаем результат теста
        from database.repositories.month_entry_test_result_repository import MonthEntryTestResultRepository
        test_result = await MonthEntryTestResultRepository.get_by_id(test_result_id)

        if not test_result:
            await callback.message.edit_text(
                "❌ Результат теста не найден",
                reply_markup=get_back_to_test_kb()
            )
            return

        # Получаем статистику по микротемам
        microtopic_stats = await MonthEntryTestResultRepository.get_microtopic_statistics(test_result.id)

        # Получаем названия микротем
        from database.repositories.subject_repository import SubjectRepository
        from database.repositories.month_test_repository import MonthTestRepository
        from database.repositories.microtopic_repository import MicrotopicRepository

        # Получаем тест месяца и предмет
        month_test = await MonthTestRepository.get_by_id(test_result.month_test_id)
        if not month_test:
            await callback.message.edit_text(
                "❌ Тест месяца не найден",
                reply_markup=get_back_to_test_kb()
            )
            return

        subject = await SubjectRepository.get_by_id(month_test.subject_id)
        microtopics = await MicrotopicRepository.get_by_subject(subject.id)
        microtopic_names = {mt.number: mt.name for mt in microtopics}

        # Разделяем на сильные и слабые темы
        strong_topics = []
        weak_topics = []

        if microtopic_stats:
            for microtopic_num, stats in microtopic_stats.items():
                microtopic_name = microtopic_names.get(microtopic_num, f"Микротема {microtopic_num}")
                percentage = stats['percentage']

                if percentage >= 80:
                    strong_topics.append((microtopic_name, percentage))
                elif percentage <= 40:
                    weak_topics.append((microtopic_name, percentage))

        # Формируем текст сводки
        result_text = f"💪 Сильные и слабые темы\n\n"
        result_text += f"📗 {subject.name}\n"
        result_text += f"Тест: {month_test.name}\n"
        result_text += f"Общий результат: {test_result.score_percentage}%\n\n"

        if strong_topics:
            result_text += "✅ Сильные темы (≥80%):\n"
            for name, percentage in sorted(strong_topics, key=lambda x: x[1], reverse=True):
                result_text += f"• {name} — {percentage}%\n"
            result_text += "\n"
        else:
            result_text += "✅ Сильных тем пока нет\n\n"

        if weak_topics:
            result_text += "❌ Слабые темы (≤40%):\n"
            for name, percentage in sorted(weak_topics, key=lambda x: x[1]):
                result_text += f"• {name} — {percentage}%\n"
            result_text += "\n"
        else:
            result_text += "❌ Слабых тем нет\n\n"

        # Добавляем рекомендации
        if strong_topics:
            result_text += "🎉 Отличная работа! Продолжайте в том же духе"

        await callback.message.edit_text(
            result_text,
            reply_markup=get_back_to_test_kb()
        )

    except Exception as e:
        logger.error(f"Ошибка при получении сводки входного теста месяца: {e}")
        await callback.message.edit_text(
            "❌ Ошибка при получении сводки",
            reply_markup=get_back_to_test_kb()
        )


@router.callback_query(StudentTestsStates.test_result, F.data.startswith("student_month_control_detailed_"))
async def show_student_month_control_detailed(callback: CallbackQuery, state: FSMContext):
    """Показать детальную статистику по микротемам контрольного теста месяца для студента"""
    try:
        # Формат: student_month_control_detailed_TEST_RESULT_ID
        test_result_id = int(callback.data.split("_")[-1])

        # Получаем результат теста
        from database.repositories.month_control_test_result_repository import MonthControlTestResultRepository
        test_result = await MonthControlTestResultRepository.get_by_id(test_result_id)

        if not test_result:
            await callback.message.edit_text(
                "❌ Результат теста не найден",
                reply_markup=get_back_to_test_kb()
            )
            return

        # Получаем статистику по микротемам
        microtopic_stats = await MonthControlTestResultRepository.get_microtopic_statistics(test_result.id)

        # Получаем тест месяца и названия микротем
        from database.repositories.microtopic_repository import MicrotopicRepository
        from database.repositories.subject_repository import SubjectRepository
        from database.repositories.month_test_repository import MonthTestRepository

        month_test = await MonthTestRepository.get_by_id(test_result.month_test_id)
        if not month_test:
            await callback.message.edit_text(
                "❌ Тест месяца не найден",
                reply_markup=get_back_to_test_kb()
            )
            return

        microtopics = await MicrotopicRepository.get_by_subject(month_test.subject_id)
        microtopic_names = {mt.number: mt.name for mt in microtopics}

        subject = await SubjectRepository.get_by_id(month_test.subject_id)

        # Формируем детальную статистику
        result_text = f"📊 Детальная статистика контрольного теста месяца\n\n"
        result_text += f"📗 {subject.name}\n"
        result_text += f"Тест: {month_test.name}\n"
        result_text += f"Верных: {test_result.correct_answers} / {test_result.total_questions}\n\n"
        result_text += "📈 % правильных ответов по микротемам:\n"

        if microtopic_stats:
            for microtopic_num in sorted(microtopic_stats.keys()):
                stats = microtopic_stats[microtopic_num]
                microtopic_name = microtopic_names.get(microtopic_num, f"Микротема {microtopic_num}")
                percentage = stats['percentage']

                # Определяем эмодзи статуса
                if percentage >= 80:
                    status = "✅"
                elif percentage <= 40:
                    status = "❌"
                else:
                    status = "⚠️"

                result_text += f"• {microtopic_name} — {percentage}% {status}\n"
        else:
            result_text += "Нет данных по микротемам\n"

        await callback.message.edit_text(
            result_text,
            reply_markup=get_back_to_test_kb()
        )

    except Exception as e:
        logger.error(f"Ошибка при получении детальной статистики контрольного теста месяца: {e}")
        await callback.message.edit_text(
            "❌ Ошибка при получении статистики",
            reply_markup=get_back_to_test_kb()
        )


@router.callback_query(StudentTestsStates.test_result, F.data.startswith("student_month_control_summary_"))
async def show_student_month_control_summary(callback: CallbackQuery, state: FSMContext):
    """Показать сводку по сильным/слабым темам контрольного теста месяца для студента"""
    try:
        # Формат: student_month_control_summary_TEST_RESULT_ID
        test_result_id = int(callback.data.split("_")[-1])

        # Получаем результат теста
        from database.repositories.month_control_test_result_repository import MonthControlTestResultRepository
        test_result = await MonthControlTestResultRepository.get_by_id(test_result_id)

        if not test_result:
            await callback.message.edit_text(
                "❌ Результат теста не найден",
                reply_markup=get_back_to_test_kb()
            )
            return

        # Получаем статистику по микротемам
        microtopic_stats = await MonthControlTestResultRepository.get_microtopic_statistics(test_result.id)

        # Получаем названия микротем
        from database.repositories.subject_repository import SubjectRepository
        from database.repositories.month_test_repository import MonthTestRepository
        from database.repositories.microtopic_repository import MicrotopicRepository

        month_test = await MonthTestRepository.get_by_id(test_result.month_test_id)
        if not month_test:
            await callback.message.edit_text(
                "❌ Тест месяца не найден",
                reply_markup=get_back_to_test_kb()
            )
            return

        subject = await SubjectRepository.get_by_id(month_test.subject_id)
        microtopics = await MicrotopicRepository.get_by_subject(subject.id)
        microtopic_names = {mt.number: mt.name for mt in microtopics}

        # Разделяем на сильные и слабые темы
        strong_topics = []
        weak_topics = []

        if microtopic_stats:
            for microtopic_num, stats in microtopic_stats.items():
                microtopic_name = microtopic_names.get(microtopic_num, f"Микротема {microtopic_num}")
                percentage = stats['percentage']

                if percentage >= 80:
                    strong_topics.append((microtopic_name, percentage))
                elif percentage <= 40:
                    weak_topics.append((microtopic_name, percentage))

        # Формируем текст сводки
        result_text = f"💪 Сильные и слабые темы\n\n"
        result_text += f"📗 {subject.name}\n"
        result_text += f"Тест: {month_test.name}\n"
        result_text += f"Общий результат: {test_result.score_percentage}%\n\n"

        if strong_topics:
            result_text += "✅ Сильные темы (≥80%):\n"
            for name, percentage in sorted(strong_topics, key=lambda x: x[1], reverse=True):
                result_text += f"• {name} — {percentage}%\n"
            result_text += "\n"
        else:
            result_text += "✅ Сильных тем пока нет\n\n"

        if weak_topics:
            result_text += "❌ Слабые темы (≤40%):\n"
            for name, percentage in sorted(weak_topics, key=lambda x: x[1]):
                result_text += f"• {name} — {percentage}%\n"
            result_text += "\n"
        else:
            result_text += "❌ Слабых тем нет\n\n"

        # Добавляем рекомендации
        if weak_topics:
            result_text += "💡 Рекомендация: Обратите внимание на слабые темы и повторите материал"
        elif strong_topics:
            result_text += "🎉 Отличная работа! Продолжайте в том же духе"
        else:
            result_text += "📚 Продолжайте изучение материала"

        await callback.message.edit_text(
            result_text,
            reply_markup=get_back_to_test_kb()
        )

    except Exception as e:
        logger.error(f"Ошибка при получении сводки контрольного теста месяца: {e}")
        await callback.message.edit_text(
            "❌ Ошибка при получении сводки",
            reply_markup=get_back_to_test_kb()
        )
