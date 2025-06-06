from aiogram import Router, F
from aiogram.types import Poll, PollAnswer, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from datetime import datetime, timedelta


router = Router()

class QuizStates(StatesGroup):
    confirming = State()
    testing = State()

# Пример вопросов
QUIZ_QUESTIONS = [
    {
        "question": "Какой алкан имеет формулу C3H8?",
        "options": ["Метан", "Этан", "Пропан", "Бутан"],
        "correct_id": 2
    },
    {
        "question": "Сколько атомов водорода в метане?",
        "options": ["2", "4", "6", "8"],
        "correct_id": 1
    },
]

@router.message(F.text == "Базовое")  # после выбора дз
async def confirm_test(msg: Message):
    text = (
        "🔎 Урок: Изомерия\n"
        "📋 Вопросов: 15\n"
        "⏱ Время на прохождение одного вопроса: 10 секунд\n"
        "⚠️ Баллы будут начислены только за 100% правильных ответов.\n"
        "Ты готов?"
    )
    await msg.answer(text, reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="▶️ Начать тест", callback_data="start_quiz")]
        ]
    ))

@router.callback_query(F.data == "start_quiz")
async def start_quiz(callback: CallbackQuery, state: FSMContext):
    await state.set_state(QuizStates.testing)
    await state.update_data(score=0, q_index=0)
    await callback.answer()
    await send_next_question(callback.message.chat.id, state, callback.bot)


async def send_next_question(chat_id, state: FSMContext, bot):
    data = await state.get_data()
    index = data.get("q_index", 0)

    if index >= len(QUIZ_QUESTIONS):
        # ... (конец теста)
        return

    q = QUIZ_QUESTIONS[index]

    close_date = int((datetime.now() + timedelta(seconds=10)).timestamp())

    await bot.send_poll(
        chat_id=chat_id,
        question=q["question"],
        options=q["options"],
        type="quiz",
        correct_option_id=q["correct_id"],
        is_anonymous=False,
        close_date=close_date
    )



@router.poll_answer()
async def handle_poll_answer(poll: PollAnswer, state: FSMContext):
    data = await state.get_data()
    index = data.get("q_index", 0)

    if index < len(QUIZ_QUESTIONS):
        correct_id = QUIZ_QUESTIONS[index]["correct_id"]
        selected = poll.option_ids[0]

        score = data.get("score", 0)
        if selected == correct_id:
            score += 1

        await state.update_data(score=score, q_index=index + 1)

        # отправить след. вопрос
        await send_next_question(poll.user.id, state, poll.bot)
