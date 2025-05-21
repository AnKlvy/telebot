from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from keyboards import get_test_answers_kb, get_after_test_kb

# Словарь с вопросами и правильными ответами
TEST_QUESTIONS = {
    1: {
        "text": "Какое из следующих соединений является изомером бутана?",
        "options": {
            "A": "Пропан",
            "B": "2-метилпропан",
            "C": "Пентан",
            "D": "Этан"
        },
        "correct": "B"
    },
    2: {
        "text": "Какой тип изомерии характерен для алканов?",
        "options": {
            "A": "Геометрическая",
            "B": "Структурная",
            "C": "Оптическая",
            "D": "Таутомерия"
        },
        "correct": "B"
    },
    # Здесь можно добавить остальные вопросы
}

async def start_test_process(callback: CallbackQuery, state: FSMContext):
    """Начало теста"""
    user_data = await state.get_data()
    
    # Сохраняем информацию для последующего использования
    await state.update_data(
        test_started=True,
        total_questions=len(TEST_QUESTIONS),
        current_question=1,
        correct_answers=0,
        user_answers={}
    )
    
    # Показываем первый вопрос
    await show_question(callback, state, 1)

async def show_question(callback: CallbackQuery, state: FSMContext, question_number: int):
    """Показать вопрос теста"""
    if question_number not in TEST_QUESTIONS:
        # Если вопрос не найден, завершаем тест
        await finish_test(callback, state)
        return
    
    question = TEST_QUESTIONS[question_number]
    options_text = "\n".join([f"{key}) {value}" for key, value in question["options"].items()])
    
    await callback.message.edit_text(
        f"Вопрос {question_number}/{len(TEST_QUESTIONS)}\n\n"
        f"{question['text']}\n\n"
        f"{options_text}",
        reply_markup=get_test_answers_kb()
    )

async def process_test_answer(callback: CallbackQuery, state: FSMContext, selected_answer: str):
    """Обработка ответа на вопрос теста"""
    user_data = await state.get_data()
    current_question = user_data.get("current_question", 1)
    
    # Проверяем правильность ответа
    is_correct = selected_answer == TEST_QUESTIONS[current_question]["correct"]
    
    # Сохраняем ответ пользователя
    user_answers = user_data.get("user_answers", {})
    user_answers[current_question] = {
        "selected": selected_answer,
        "correct": is_correct
    }
    
    # Обновляем счетчик правильных ответов
    correct_answers = user_data.get("correct_answers", 0)
    if is_correct:
        correct_answers += 1
    
    # Обновляем данные состояния
    next_question = current_question + 1
    await state.update_data(
        current_question=next_question,
        correct_answers=correct_answers,
        user_answers=user_answers
    )
    
    # Если есть следующий вопрос, показываем его
    if next_question <= len(TEST_QUESTIONS):
        await show_question(callback, state, next_question)
    else:
        # Иначе завершаем тест
        await finish_test(callback, state)

async def finish_test(callback: CallbackQuery, state: FSMContext):
    """Завершение теста и показ результатов"""
    user_data = await state.get_data()
    total_questions = user_data.get("total_questions", len(TEST_QUESTIONS))
    correct_answers = user_data.get("correct_answers", 0)
    
    # Проверяем, все ли ответы правильные
    success = correct_answers == total_questions
    
    if success:
        await callback.message.edit_text(
            "✅ Тест завершён!\n"
            f"Верных: {correct_answers} / {total_questions}\n"
            "🎯 Начислено: 45 баллов\n"
            "📈 Понимание по микротемам обновлено.",
            reply_markup=get_after_test_kb()
        )
    else:
        await callback.message.edit_text(
            "❌ Тест завершён!\n"
            f"Верных: {correct_answers} / {total_questions}\n"
            "Баллы не начислены — для получения баллов нужно пройти тест на 100%\n"
            "Ты можешь пройти снова!\n"
            "📈 Понимание по микротемам обновлено.",
            reply_markup=get_after_test_kb()
        )