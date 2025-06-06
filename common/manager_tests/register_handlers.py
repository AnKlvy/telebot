import logging
from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from .handlers import (
    enter_test_name, start_adding_questions, add_question_photo, process_question_photo, request_topic,
    enter_answer_options, select_correct_answer, save_question, add_more_question, set_time_limit, process_topic, confirm_test
)
import inspect


# Настройка логирования
logging.basicConfig(level=logging.INFO)

def register_test_handlers(router: Router, states_group, role: str):
    """Регистрация обработчиков тестов"""

    @router.callback_query(states_group.select_lesson, F.data.startswith("lesson_"))
    async def role_enter_test_name(callback: CallbackQuery, state: FSMContext):
        await log(inspect.currentframe().f_code.co_name, role, state)
        await enter_test_name(callback, state)
        await state.set_state(states_group.enter_test_name)

    @router.message(states_group.enter_test_name)
    async def role_start_adding_questions(message: Message, state: FSMContext):
        await log(inspect.currentframe().f_code.co_name, role, state)
        await start_adding_questions(message, state)
        await state.set_state(states_group.enter_question_text)

    @router.message(states_group.enter_question_text)
    async def role_add_question_photo(message: Message, state: FSMContext):
        await log(inspect.currentframe().f_code.co_name, role, state)
        await add_question_photo(message, state)
        await state.set_state(states_group.add_question_photo)

    @router.callback_query(states_group.add_question_photo, F.data == "skip_photo")
    async def skip_photo(callback: CallbackQuery, state: FSMContext):
        await log(inspect.currentframe().f_code.co_name, role, state)
        await state.set_state(states_group.request_topic)
        await request_topic(callback.message, state)


    @router.message(states_group.add_question_photo, F.photo)
    async def role_process_question_photo(message: Message, state: FSMContext):
        await log(inspect.currentframe().f_code.co_name, role, state)
        await state.set_state(states_group.request_topic)
        await process_question_photo(message, state)

    @router.message(states_group.request_topic)
    async def role_process_topic(message: Message, state: FSMContext):
        await log(inspect.currentframe().f_code.co_name, role, state)
        await process_topic(message, state, states_group)


    @router.callback_query(states_group.select_topic)
    async def role_enter_answer_options(message: Message, state: FSMContext):
        await log(inspect.currentframe().f_code.co_name, role, state)
        await enter_answer_options(message, state)
        await state.set_state(states_group.enter_answer_options)


    @router.message(states_group.enter_answer_options)
    async def role_select_correct_answer(message: Message, state: FSMContext):
        await log(inspect.currentframe().f_code.co_name, role, state)
        await select_correct_answer(message, state, states_group)
        # Состояние изменится только если валидация прошла успешно
        
    @router.message(states_group.enter_answer_options)
    async def role_select_correct_answer_retry(message: Message, state: FSMContext):
        await log(inspect.currentframe().f_code.co_name, role, state)
        await select_correct_answer(message, state, states_group)
        # Состояние изменится только если валидация прошла успешно

    @router.callback_query(states_group.select_correct_answer, F.data.startswith("correct_"))
    async def role_save_question(callback: CallbackQuery, state: FSMContext):
        await log(inspect.currentframe().f_code.co_name, role, state)
        await save_question(callback, state)
        await state.set_state(states_group.add_question)

    @router.callback_query(states_group.add_question, F.data == "add_more_question")
    async def role_add_more_question(callback: CallbackQuery, state: FSMContext):
        await log(inspect.currentframe().f_code.co_name, role, state)
        await add_more_question(callback, state)
        await state.set_state(states_group.enter_question_text)

    @router.callback_query(states_group.add_question, F.data == "finish_adding_questions")
    async def role_set_time_limit(callback: CallbackQuery, state: FSMContext):
        await log(inspect.currentframe().f_code.co_name, role, state)
        await set_time_limit(callback, state)
        await state.set_state(states_group.set_time_limit)

    @router.callback_query(states_group.set_time_limit, F.data.startswith("time_"))
    async def role_confirm_test(callback: CallbackQuery, state: FSMContext):
        await log(inspect.currentframe().f_code.co_name, role, state)
        await confirm_test(callback, state)
        await state.set_state(states_group.confirm_test)

async def log(name, role, state):
    logging.info(f"ВЫЗОВ: {name} | РОЛЬ: {role} | СОСТОЯНИЕ: {await state.get_state()}")

