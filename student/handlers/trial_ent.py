from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import logging
from ..keyboards.trial_ent import (
    get_trial_ent_start_kb,
    get_required_subjects_kb,
    get_profile_subjects_kb,
    get_second_profile_subject_kb,
    get_after_trial_ent_kb,
    get_analytics_subjects_kb,
    get_back_to_analytics_kb
)
from common.keyboards import get_main_menu_back_button
# process_test_answer больше не используется, логика перенесена в homework_quiz.py

router = Router()

class TrialEntStates(StatesGroup):
    subject_analytics = State()
    main = State()
    required_subjects = State()
    profile_subjects = State()
    second_profile_subject = State()
    test_in_progress = State()
    results = State()
    analytics_subjects = State()
    confirming_end = State()
    # Новые состояния для истории
    history = State()
    history_detail = State()

@router.callback_query(F.data == "trial_ent")
async def show_trial_ent_menu(callback: CallbackQuery, state: FSMContext):
    """Показать меню пробного ЕНТ"""
    # НЕ очищаем состояние здесь, чтобы сохранить результаты для аналитики

    await callback.message.edit_text(
        "Это симуляция ЕНТ: 130 баллов (за исключением грамотности чтения).\n"
        "Для начала выбери обязательные и профильные предметы",
        reply_markup=get_trial_ent_start_kb()
    )
    await state.set_state(TrialEntStates.main)

@router.callback_query(TrialEntStates.main, F.data == "start_trial_ent")
async def choose_required_subjects(callback: CallbackQuery, state: FSMContext):
    """Выбор обязательных предметов"""
    # Очищаем все данные предыдущего теста при начале нового
    await state.clear()

    await callback.message.edit_text(
        "Обязательные предметы:",
        reply_markup=get_required_subjects_kb()
    )
    await state.set_state(TrialEntStates.required_subjects)

@router.callback_query(TrialEntStates.required_subjects, F.data.startswith("req_sub_"))
async def choose_profile_subjects(callback: CallbackQuery, state: FSMContext):
    """Выбор профильных предметов"""
    required_subjects = callback.data.replace("req_sub_", "")
    
    # Сохраняем выбранные обязательные предметы
    if required_subjects == "kz":
        selected_subjects = ["kz"]
    elif required_subjects == "mathlit":
        selected_subjects = ["mathlit"]
    else:  # both
        selected_subjects = ["kz", "mathlit"]
    
    await state.update_data(required_subjects=selected_subjects)
    
    await callback.message.edit_text(
        "Профильные предметы:",
        reply_markup=get_profile_subjects_kb()
    )
    await state.set_state(TrialEntStates.profile_subjects)

@router.callback_query(TrialEntStates.profile_subjects, F.data.startswith("prof_sub_"))
async def process_profile_subject(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора профильного предмета"""
    profile_subject = callback.data
    
    if profile_subject == "prof_sub_none":
        # Если выбрано "Нет профильных предметов", переходим к началу теста
        await state.update_data(profile_subjects=[])
        await start_trial_ent_test(callback, state)
    else:
        # Сохраняем первый выбранный профильный предмет
        await state.update_data(first_profile_subject=profile_subject)
        
        # Предлагаем выбрать второй профильный предмет
        await callback.message.edit_text(
            "Выберите второй профильный предмет:",
            reply_markup=get_second_profile_subject_kb(profile_subject)
        )
        await state.set_state(TrialEntStates.second_profile_subject)

@router.callback_query(TrialEntStates.second_profile_subject, F.data.startswith("second_prof_sub_"))
async def process_second_profile_subject(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора второго профильного предмета"""
    second_profile_subject = callback.data.replace("second_", "")
    
    # Получаем данные о первом выбранном профильном предмете
    user_data = await state.get_data()
    first_profile_subject = user_data.get("first_profile_subject", "")
    
    # Сохраняем оба профильных предмета
    profile_subjects = [
        first_profile_subject.replace("prof_sub_", ""),
        second_profile_subject.replace("prof_sub_", "")
    ]
    await state.update_data(profile_subjects=profile_subjects)
    
    # Переходим к началу теста
    await start_trial_ent_test(callback, state)

async def start_trial_ent_test(callback: CallbackQuery, state: FSMContext):
    """Начало пробного ЕНТ"""
    user_data = await state.get_data()
    required_subjects = user_data.get("required_subjects", [])
    profile_subjects = user_data.get("profile_subjects", [])

    # Генерируем вопросы из базы данных
    from common.trial_ent_service import TrialEntService

    try:
        all_questions, total_questions = await TrialEntService.generate_trial_ent_questions(
            required_subjects, profile_subjects
        )

        if not all_questions:
            await callback.message.edit_text(
                "❌ Не удалось загрузить вопросы для теста. Попробуйте позже.",
                reply_markup=get_trial_ent_start_kb()
            )
            await state.set_state(TrialEntStates.main)
            return

        # Подготавливаем данные для quiz_registrator
        await state.update_data(
            questions=all_questions,
            q_index=0,
            score=0,
            question_results=[],
            user_id=callback.from_user.id,
            required_subjects=required_subjects,
            profile_subjects=profile_subjects,
            messages_to_delete=[]
        )

        # Удаляем текущее сообщение
        try:
            await callback.message.delete()
        except:
            pass

        # Запускаем тест через общий модуль
        from common.quiz_registrator import send_next_question
        await send_next_question(
            chat_id=callback.from_user.id,
            state=state,
            bot=callback.bot,
            finish_callback=finish_trial_ent_quiz
        )
        await state.set_state(TrialEntStates.test_in_progress)

    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Ошибка при генерации вопросов пробного ЕНТ: {e}")

        await callback.message.edit_text(
            "❌ Произошла ошибка при подготовке теста. Попробуйте позже.",
            reply_markup=get_trial_ent_start_kb()
        )
        await state.set_state(TrialEntStates.main)

def get_subject_name(subject_code):
    """Получить название предмета по коду"""
    subject_names = {
        "kz": "История Казахстана",
        "mathlit": "Математическая грамотность",
        "math": "Математика",
        "geo": "География",
        "bio": "Биология",
        "chem": "Химия",
        "inf": "Информатика",
        "world": "Всемирная история"
    }
    return subject_names.get(subject_code, "")

async def finish_trial_ent_quiz(chat_id: int, state: FSMContext, bot):
    """Завершение пробного ЕНТ через quiz_registrator"""
    import logging
    import asyncio
    logger = logging.getLogger(__name__)
    logger.info(f"🏁 TRIAL_ENT: Начинаем завершение теста для пользователя {chat_id}")

    user_data = await state.get_data()
    required_subjects = user_data.get("required_subjects", [])
    profile_subjects = user_data.get("profile_subjects", [])
    questions = user_data.get("questions", [])
    question_results = user_data.get("question_results", [])

    logger.info(f"📊 TRIAL_ENT: Получено {len(question_results)} результатов ответов")

    try:
        # Получаем ID студента
        from database import UserRepository, StudentRepository
        user = await UserRepository.get_by_telegram_id(chat_id)
        if not user:
            await bot.send_message(
                chat_id,
                "❌ Пользователь не найден в системе",
                reply_markup=get_trial_ent_start_kb()
            )
            await state.set_state(TrialEntStates.main)
            return

        student = await StudentRepository.get_by_user_id(user.id)
        if not student:
            await bot.send_message(
                chat_id,
                "❌ Профиль студента не найден",
                reply_markup=get_trial_ent_start_kb()
            )
            await state.set_state(TrialEntStates.main)
            return

        # Преобразуем результаты в формат для сохранения
        answers = {}
        for i, result in enumerate(question_results, 1):
            answers[i] = result.get("selected_answer_id")

        # Сохраняем результат в базу данных
        logger.info(f"💾 TRIAL_ENT: Сохраняем результат в базу данных...")
        from common.trial_ent_service import TrialEntService
        trial_ent_result_id = await TrialEntService.save_trial_ent_result(
            student_id=student.id,
            required_subjects=required_subjects,
            profile_subjects=profile_subjects,
            questions_data=questions,
            answers=answers
        )
        logger.info(f"✅ TRIAL_ENT: Результат сохранен с ID {trial_ent_result_id}")

        # Получаем статистику
        logger.info(f"📈 TRIAL_ENT: Получаем статистику...")
        statistics = await TrialEntService.get_trial_ent_statistics(trial_ent_result_id)
        logger.info(f"📊 TRIAL_ENT: Статистика получена")

        # Формируем текст с результатами
        total_correct = statistics["total_correct"]
        total_questions = statistics["total_questions"]

        result_text = f"🧾 Верных баллов: {total_correct}/{total_questions}\n"

        # Добавляем информацию о каждом предмете
        subject_stats = statistics.get("subject_statistics", {})

        # Обязательные предметы
        for subject_code in required_subjects:
            subject_name = TrialEntService.get_subject_name(subject_code)
            stats = subject_stats.get(subject_code, {})
            if stats:
                result_text += f"🧾 Верных баллов по {subject_name}: {stats['correct']}/{stats['total']}\n"

        # Профильные предметы
        for subject_code in profile_subjects:
            subject_name = TrialEntService.get_subject_name(subject_code)
            stats = subject_stats.get(subject_code, {})
            if stats:
                result_text += f"🧾 Верных баллов по {subject_name}: {stats['correct']}/{stats['total']}\n"

        result_text += "\nХочешь посмотреть свою аналитику по темам?"

        # Сохраняем только сериализуемые данные для последующего использования
        serializable_stats = {
            "required_subjects": statistics["required_subjects"],
            "profile_subjects": statistics["profile_subjects"],
            "subject_statistics": statistics["subject_statistics"],
            "microtopic_statistics": statistics["microtopic_statistics"],
            "total_correct": statistics["total_correct"],
            "total_questions": statistics["total_questions"]
        }

        await state.update_data(
            test_results=serializable_stats,
            trial_ent_result_id=trial_ent_result_id
        )

        logger.info(f"📤 TRIAL_ENT: Отправляем результаты пользователю...")
        await bot.send_message(
            chat_id,
            result_text,
            reply_markup=get_after_trial_ent_kb()
        )
        await state.set_state(TrialEntStates.results)
        logger.info(f"🎉 TRIAL_ENT: Результаты отправлены пользователю {chat_id}")

        # Очищаем сообщения теста асинхронно (не блокируя показ результатов)
        logger.info(f"🧹 TRIAL_ENT: Запускаем очистку сообщений...")
        from common.quiz_registrator import cleanup_test_messages, cleanup_test_data

        # Запускаем очистку в фоне
        asyncio.create_task(cleanup_test_messages(chat_id, user_data, bot))
        asyncio.create_task(cleanup_test_data(chat_id))

        logger.info(f"✅ TRIAL_ENT: Завершение теста успешно завершено для пользователя {chat_id}")

    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Ошибка при сохранении результатов пробного ЕНТ: {e}")

        await bot.send_message(
            chat_id,
            "❌ Произошла ошибка при сохранении результатов. Попробуйте пройти тест еще раз.",
            reply_markup=get_trial_ent_start_kb()
        )
        await state.set_state(TrialEntStates.main)



@router.callback_query(TrialEntStates.test_in_progress, F.data == "end_trial_ent")
async def end_trial_ent_early(callback: CallbackQuery, state: FSMContext):
    """Досрочное завершение пробного ЕНТ"""
    # Получаем данные о текущем тесте
    data = await state.get_data()
    current_question = data.get("current_question", 1)
    total_questions = data.get("total_questions", 130)
    
    # Спрашиваем подтверждение
    await callback.message.edit_text(
        f"Вы уверены, что хотите завершить тест?\n"
        f"Вы ответили на {current_question-1} из {total_questions} вопросов.\n"
        f"Результаты будут сохранены только для отвеченных вопросов.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Да, завершить", callback_data="confirm_end_test")],
            [InlineKeyboardButton(text="🔄 Нет, продолжить", callback_data="continue_test")]
        ])
    )
    # Сохраняем текущее состояние, чтобы можно было вернуться к тесту
    await state.update_data(previous_state="test_in_progress")
    # Временно меняем состояние для обработки подтверждения
    await state.set_state("confirming_end")

@router.callback_query(lambda c: c.data == "confirm_end_test" and c.message.chat.id)
async def confirm_end_test(callback: CallbackQuery, state: FSMContext):
    """Подтверждение завершения теста"""
    # Вызываем finish_trial_ent для сохранения результатов и показа итогов
    await finish_trial_ent(callback, state)

@router.callback_query(lambda c: c.data == "continue_test" and c.message.chat.id)
async def continue_test(callback: CallbackQuery, state: FSMContext):
    """Продолжение теста после отмены завершения"""
    # Получаем данные о текущем вопросе
    data = await state.get_data()
    current_question = data.get("current_question", 1)
    
    # Возвращаемся к тесту
    await show_question(callback, state, current_question)
    await state.set_state(TrialEntStates.test_in_progress)



@router.callback_query(F.data == "view_analytics")
async def show_analytics_menu(callback: CallbackQuery, state: FSMContext):
    """Показать меню выбора типа аналитики"""
    user_data = await state.get_data()
    test_results = user_data.get("test_results", {})

    # Проверяем, есть ли текущие результаты теста
    has_current_results = test_results and "total_correct" in test_results

    # Получаем ID студента для проверки истории
    from database import UserRepository, StudentRepository
    user = await UserRepository.get_by_telegram_id(callback.from_user.id)
    has_history = False

    if user:
        student = await StudentRepository.get_by_user_id(user.id)
        if student:
            from common.trial_ent_service import TrialEntService
            history = await TrialEntService.get_student_trial_ent_history(student.id, 1)
            has_history = len(history) > 0

    # Формируем клавиатуру в зависимости от доступных данных
    buttons = []

    if has_current_results:
        buttons.append([InlineKeyboardButton(text="📊 Текущий тест", callback_data="current_test_analytics")])

    if has_history:
        buttons.append([InlineKeyboardButton(text="📈 История тестов", callback_data="view_history")])

    if not has_current_results and not has_history:
        await callback.message.edit_text(
            "❌ Нет данных для аналитики.\nСначала пройдите пробный ЕНТ.",
            reply_markup=get_trial_ent_start_kb()
        )
        await state.set_state(TrialEntStates.main)
        return

    buttons.extend(get_main_menu_back_button())

    await callback.message.edit_text(
        "📊 Выберите тип аналитики:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )


@router.callback_query(F.data == "current_test_analytics")
async def show_current_test_subjects(callback: CallbackQuery, state: FSMContext):
    """Показать список предметов для просмотра аналитики текущего теста"""
    user_data = await state.get_data()
    required_subjects = user_data.get("required_subjects", [])
    profile_subjects = user_data.get("profile_subjects", [])

    # Сохраняем текущее состояние, чтобы знать, куда возвращаться
    current_state = await state.get_state()
    await state.update_data(previous_analytics_state=current_state)

    # Проверяем, есть ли результаты теста
    test_results = user_data.get("test_results", {})

    # Проверяем, что есть завершенные результаты теста (не просто выбранные предметы)
    if not test_results or "total_correct" not in test_results:
        # Если нет завершенных результатов теста
        await callback.message.edit_text(
            "❌ Результаты текущего теста не найдены",
            reply_markup=get_trial_ent_start_kb()
        )
        await state.set_state(TrialEntStates.main)
        return

    # Формируем список всех предметов, по которым проходил тест
    all_subjects = required_subjects + profile_subjects

    await callback.message.edit_text(
        "Выбери предмет для просмотра аналитики:",
        reply_markup=get_analytics_subjects_kb(all_subjects)
    )
    await state.set_state(TrialEntStates.analytics_subjects)


@router.callback_query(F.data == "view_history")
async def show_trial_ent_history(callback: CallbackQuery, state: FSMContext):
    """Показать историю пробных ЕНТ"""
    try:
        # Получаем ID студента
        from database import UserRepository, StudentRepository
        user = await UserRepository.get_by_telegram_id(callback.from_user.id)
        if not user:
            await callback.message.edit_text(
                "❌ Пользователь не найден в системе",
                reply_markup=get_trial_ent_start_kb()
            )
            await state.set_state(TrialEntStates.main)
            return

        student = await StudentRepository.get_by_user_id(user.id)
        if not student:
            await callback.message.edit_text(
                "❌ Профиль студента не найден",
                reply_markup=get_trial_ent_start_kb()
            )
            await state.set_state(TrialEntStates.main)
            return

        # Получаем историю тестов
        from common.trial_ent_service import TrialEntService
        history = await TrialEntService.get_student_trial_ent_history(student.id, 10)

        if not history:
            await callback.message.edit_text(
                "📈 История пробных ЕНТ пуста.\nПройдите первый тест!",
                reply_markup=get_trial_ent_start_kb()
            )
            await state.set_state(TrialEntStates.main)
            return

        # Формируем текст с историей
        history_text = "📈 История ваших пробных ЕНТ:\n\n"

        buttons = []
        for i, result in enumerate(history, 1):
            # Форматируем дату
            date_str = result["completed_at"].strftime("%d.%m.%Y %H:%M")

            # Формируем список предметов
            all_subjects = result["required_subjects"] + result["profile_subjects"]
            subjects_text = ", ".join([TrialEntService.get_subject_name(code) for code in all_subjects])

            # Добавляем в текст
            history_text += f"{i}. {date_str}\n"
            history_text += f"   📊 {result['correct_answers']}/{result['total_questions']} ({result['percentage']}%)\n"
            history_text += f"   📚 {subjects_text}\n\n"

            # Добавляем кнопку для детального просмотра
            buttons.append([InlineKeyboardButton(
                text=f"📊 Тест {i} ({result['percentage']}%)",
                callback_data=f"history_detail_{result['id']}"
            )])

        buttons.extend(get_main_menu_back_button())

        await callback.message.edit_text(
            history_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
        )
        await state.set_state(TrialEntStates.history)

    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Ошибка при получении истории пробных ЕНТ: {e}")

        await callback.message.edit_text(
            "❌ Произошла ошибка при загрузке истории",
            reply_markup=get_trial_ent_start_kb()
        )
        await state.set_state(TrialEntStates.main)


@router.callback_query(TrialEntStates.history, F.data.startswith("history_detail_"))
async def show_history_detail(callback: CallbackQuery, state: FSMContext):
    """Показать детальную информацию о конкретном тесте из истории"""
    try:
        # Извлекаем ID результата
        result_id = int(callback.data.replace("history_detail_", ""))

        # Получаем статистику
        from common.trial_ent_service import TrialEntService
        statistics = await TrialEntService.get_trial_ent_statistics(result_id)

        if not statistics:
            await callback.message.edit_text(
                "❌ Результаты теста не найдены",
                reply_markup=get_trial_ent_start_kb()
            )
            await state.set_state(TrialEntStates.main)
            return

        # Формируем детальный текст
        required_subjects = statistics.get("required_subjects", [])
        profile_subjects = statistics.get("profile_subjects", [])
        total_correct = statistics["total_correct"]
        total_questions = statistics["total_questions"]

        detail_text = f"📊 Детальные результаты теста:\n\n"
        detail_text += f"🧾 Общий результат: {total_correct}/{total_questions} ({round((total_correct/total_questions)*100)}%)\n\n"

        # Добавляем информацию по предметам
        subject_stats = statistics.get("subject_statistics", {})

        if required_subjects:
            detail_text += "📚 Обязательные предметы:\n"
            for subject_code in required_subjects:
                subject_name = TrialEntService.get_subject_name(subject_code)
                stats = subject_stats.get(subject_code, {})
                if stats:
                    detail_text += f"• {subject_name}: {stats['correct']}/{stats['total']}\n"
            detail_text += "\n"

        if profile_subjects:
            detail_text += "🎯 Профильные предметы:\n"
            for subject_code in profile_subjects:
                subject_name = TrialEntService.get_subject_name(subject_code)
                stats = subject_stats.get(subject_code, {})
                if stats:
                    detail_text += f"• {subject_name}: {stats['correct']}/{stats['total']}\n"

        # Сохраняем ID результата для возможного просмотра аналитики
        await state.update_data(
            trial_ent_result_id=result_id,
            required_subjects=required_subjects,
            profile_subjects=profile_subjects
        )

        # Кнопки для действий
        buttons = [
            [InlineKeyboardButton(text="📈 Аналитика по предметам", callback_data="history_analytics")],
            [InlineKeyboardButton(text="⬅️ Назад к истории", callback_data="view_history")],
        ]
        buttons.extend(get_main_menu_back_button())

        await callback.message.edit_text(
            detail_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
        )
        await state.set_state(TrialEntStates.history_detail)

    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Ошибка при получении детальной информации о тесте: {e}")

        await callback.message.edit_text(
            "❌ Произошла ошибка при загрузке данных",
            reply_markup=get_trial_ent_start_kb()
        )
        await state.set_state(TrialEntStates.main)


@router.callback_query(TrialEntStates.history_detail, F.data == "history_analytics")
async def show_history_analytics_subjects(callback: CallbackQuery, state: FSMContext):
    """Показать список предметов для аналитики исторического теста"""
    user_data = await state.get_data()
    required_subjects = user_data.get("required_subjects", [])
    profile_subjects = user_data.get("profile_subjects", [])

    # Формируем список всех предметов
    all_subjects = required_subjects + profile_subjects

    if not all_subjects:
        await callback.message.edit_text(
            "❌ Данные о предметах не найдены",
            reply_markup=get_trial_ent_start_kb()
        )
        await state.set_state(TrialEntStates.main)
        return

    await callback.message.edit_text(
        "Выберите предмет для просмотра аналитики:",
        reply_markup=get_analytics_subjects_kb(all_subjects)
    )
    await state.set_state(TrialEntStates.analytics_subjects)


@router.callback_query(TrialEntStates.analytics_subjects, F.data.startswith("analytics_"))
async def show_subject_analytics(callback: CallbackQuery, state: FSMContext):
    """Показать аналитику по выбранному предмету"""
    subject_code = callback.data.replace("analytics_", "")

    try:
        user_data = await state.get_data()
        trial_ent_result_id = user_data.get("trial_ent_result_id")

        if not trial_ent_result_id:
            await callback.message.edit_text(
                "❌ Результаты теста не найдены",
                reply_markup=get_trial_ent_start_kb()
            )
            await state.set_state(TrialEntStates.main)
            return

        # Получаем статистику из базы данных
        from common.trial_ent_service import TrialEntService
        from database import TrialEntQuestionResultRepository, MicrotopicRepository

        statistics = await TrialEntService.get_trial_ent_statistics(trial_ent_result_id)
        subject_name = TrialEntService.get_subject_name(subject_code)

        # Получаем статистику по предмету
        subject_stats = statistics.get("subject_statistics", {}).get(subject_code, {})
        microtopic_stats = statistics.get("microtopic_statistics", {})

        if not subject_stats:
            await callback.message.edit_text(
                f"❌ Статистика по предмету {subject_name} не найдена",
                reply_markup=get_back_to_analytics_kb()
            )
            return

        # Формируем текст с аналитикой
        analytics_text = f"Твоя аналитика по предмету {subject_name} по пробному ЕНТ:\n"
        analytics_text += f"🧾 Верных баллов по {subject_name}: {subject_stats['correct']}/{subject_stats['total']}\n"

        # Получаем названия микротем для данного предмета
        from database import SubjectRepository
        subject_id = await TrialEntService.get_subject_id_by_code(subject_code)

        if subject_id and microtopic_stats:
            microtopics = await MicrotopicRepository.get_by_subject(subject_id)
            microtopic_names = {mt.number: mt.name for mt in microtopics}

            # Показываем статистику по микротемам
            analytics_text += "\n📈 % правильных ответов по темам:\n"

            topics_analytics = {}
            for microtopic_num, stats in microtopic_stats.items():
                microtopic_name = microtopic_names.get(microtopic_num, f"Тема {microtopic_num}")
                percentage = stats['percentage']
                topics_analytics[microtopic_name] = percentage

                # Определяем эмодзи статуса
                status = "✅" if percentage >= 80 else "❌" if percentage <= 40 else "⚠️"
                analytics_text += f"• {microtopic_name} — {percentage}% {status}\n"

            # Используем единую функцию для добавления сильных и слабых тем
            from common.statistics import add_strong_and_weak_topics
            analytics_text = add_strong_and_weak_topics(analytics_text, topics_analytics)

        await callback.message.edit_text(
            analytics_text,
            reply_markup=get_back_to_analytics_kb()
        )
        await state.set_state(TrialEntStates.subject_analytics)

    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Ошибка при получении аналитики по предмету: {e}")

        await callback.message.edit_text(
            "❌ Произошла ошибка при получении аналитики",
            reply_markup=get_back_to_analytics_kb()
        )

@router.callback_query(TrialEntStates.results, F.data == "retry_trial_ent")
async def retry_trial_ent(callback: CallbackQuery, state: FSMContext):
    """Пройти пробный ЕНТ еще раз"""
    # Очищаем все данные предыдущего теста
    await state.clear()
    await show_trial_ent_menu(callback, state)

@router.callback_query(F.data == "back_to_trial_ent_results")
async def back_to_trial_ent_results(callback: CallbackQuery, state: FSMContext):
    """Вернуться к результатам пробного ЕНТ"""
    try:
        user_data = await state.get_data()
        trial_ent_result_id = user_data.get("trial_ent_result_id")

        if not trial_ent_result_id:
            await callback.message.edit_text(
                "❌ Результаты теста не найдены",
                reply_markup=get_trial_ent_start_kb()
            )
            await state.set_state(TrialEntStates.main)
            return

        # Получаем статистику из базы данных
        from common.trial_ent_service import TrialEntService
        statistics = await TrialEntService.get_trial_ent_statistics(trial_ent_result_id)

        required_subjects = statistics.get("required_subjects", [])
        profile_subjects = statistics.get("profile_subjects", [])

        # Формируем текст с результатами
        total_correct = statistics["total_correct"]
        total_questions = statistics["total_questions"]

        result_text = f"🧾 Верных баллов: {total_correct}/{total_questions}\n"

        # Добавляем информацию о каждом предмете
        subject_stats = statistics.get("subject_statistics", {})

        # Обязательные предметы
        for subject_code in required_subjects:
            subject_name = TrialEntService.get_subject_name(subject_code)
            stats = subject_stats.get(subject_code, {})
            if stats:
                result_text += f"🧾 Верных баллов по {subject_name}: {stats['correct']}/{stats['total']}\n"

        # Профильные предметы
        for subject_code in profile_subjects:
            subject_name = TrialEntService.get_subject_name(subject_code)
            stats = subject_stats.get(subject_code, {})
            if stats:
                result_text += f"🧾 Верных баллов по {subject_name}: {stats['correct']}/{stats['total']}\n"

        result_text += "\nХочешь посмотреть свою аналитику по темам?"

        await callback.message.edit_text(
            result_text,
            reply_markup=get_after_trial_ent_kb()
        )
        await state.set_state(TrialEntStates.results)

    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Ошибка при получении результатов теста: {e}")

        await callback.message.edit_text(
            "❌ Произошла ошибка при получении результатов",
            reply_markup=get_trial_ent_start_kb()
        )
        await state.set_state(TrialEntStates.main)


# Регистрируем обработчики quiz_registrator для пробного ЕНТ
from common.quiz_registrator import register_quiz_handlers
register_quiz_handlers(
    router=router,
    test_state=TrialEntStates.test_in_progress
)

@router.callback_query(F.data == "back_to_analytics_subjects")
async def back_to_analytics_subjects(callback: CallbackQuery, state: FSMContext):
    """Вернуться к выбору предмета для аналитики"""
    user_data = await state.get_data()
    previous_state = user_data.get("previous_analytics_state")
    
    if previous_state == TrialEntStates.results:
        # Если пришли из результатов теста, возвращаемся туда
        await back_to_trial_ent_results(callback, state)
    else:
        # В остальных случаях показываем список предметов
        await show_subjects(callback, state)