from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from manager.keyboards.topics import (
    get_subjects_kb, 
    get_topics_list_kb, 
    confirm_delete_topic_kb, 
    TopicCallback,
    TopicActions
)
from manager.keyboards.main import get_manager_main_menu_kb
from aiogram.fsm.state import State, StatesGroup

class ManagerTopicStates(StatesGroup):
    main = State()  # Главное меню микротем (выбор предмета)
    topics_list = State()  # Список микротем предмета
    adding_topic = State()  # Добавление новой микротемы
    confirm_deletion = State()  # Подтверждение удаления
    process_topic_name = State()
    delete_topic = State()
    cancel_delete = State()

router = Router()

# Временное хранилище микротем (потом заменить на БД)
topics_db = {
    "Математика": ["Дроби", "Проценты"],
    "Русский язык": ["Причастия", "Наречия"],
    "Физика": ["Механика", "Оптика"]
}

@router.callback_query(F.data == "manager_topics")
async def show_subjects(callback: CallbackQuery, state: FSMContext):
    """Показываем список предметов"""
    await state.set_state(ManagerTopicStates.main)
    await callback.message.edit_text(
        text="Выберите предмет для работы с микротемами:",
        reply_markup=get_subjects_kb()
    )

@router.callback_query(TopicCallback.filter(F.action == TopicActions.VIEW))
async def show_topics(callback: CallbackQuery, callback_data: TopicCallback, state: FSMContext):
    """Показываем список микротем для выбранного предмета"""
    subject = callback_data.subject
    topics = topics_db.get(subject, [])
    
    await state.set_state(ManagerTopicStates.topics_list)
    await state.update_data(current_subject=subject)
    
    await callback.message.edit_text(
        text=f"📝 Микротемы по предмету {subject}:\n"
             f"Всего микротем: {len(topics)}",
        reply_markup=get_topics_list_kb(subject, topics)
    )

@router.callback_query(TopicCallback.filter(F.action == TopicActions.ADD))
async def start_add_topic(callback: CallbackQuery, callback_data: TopicCallback, state: FSMContext):
    """Начинаем процесс добавления микротемы"""
    await state.set_state(ManagerTopicStates.adding_topic)
    await state.update_data(subject=callback_data.subject)
    
    await callback.message.edit_text(
        text="Введите название новой микротемы:",
        reply_markup=get_home_kb()
    )

@router.message(StateFilter(ManagerTopicStates.adding_topic))
async def process_topic_name(message: Message, state: FSMContext):
    """Обрабатываем ввод названия микротемы"""
    data = await state.get_data()
    subject = data['subject']
    new_topic = message.text.strip()
    
    if subject not in topics_db:
        topics_db[subject] = []
    topics_db[subject].append(new_topic)
    
    await state.set_state(ManagerTopicStates.topics_list)
    await message.answer(
        text=f"✅ Микротема \"{new_topic}\" добавлена в предмет {subject}",
        reply_markup=get_topics_list_kb(subject, topics_db[subject])
    )

@router.callback_query(TopicCallback.filter(F.action == TopicActions.DELETE))
async def confirm_delete(callback: CallbackQuery, callback_data: TopicCallback, state: FSMContext):
    """Запрашиваем подтверждение удаления микротемы"""
    await state.set_state(ManagerTopicStates.confirm_deletion)
    await state.update_data(subject=callback_data.subject, topic=callback_data.topic)
    
    await callback.message.edit_text(
        text=f"❗️ Вы уверены, что хотите удалить микротему \"{callback_data.topic}\" из предмета {callback_data.subject}?",
        reply_markup=confirm_delete_topic_kb(callback_data.subject, callback_data.topic)
    )

@router.callback_query(TopicCallback.filter(F.action == TopicActions.CONFIRM_DELETE))
async def delete_topic(callback: CallbackQuery, callback_data: TopicCallback, state: FSMContext):
    """Удаляем микротему после подтверждения"""
    subject = callback_data.subject
    topic = callback_data.topic
    
    if subject in topics_db and topic in topics_db[subject]:
        topics_db[subject].remove(topic)
    
    await state.set_state(ManagerTopicStates.topics_list)
    await callback.message.edit_text(
        text=f"✅ Микротема \"{topic}\" удалена из предмета {subject}",
        reply_markup=get_topics_list_kb(subject, topics_db[subject])
    )

@router.callback_query(TopicCallback.filter(F.action == TopicActions.CANCEL))
async def cancel_delete(callback: CallbackQuery, callback_data: TopicCallback, state: FSMContext):
    """Отменяем удаление микротемы"""
    await state.set_state(ManagerTopicStates.topics_list)
    await callback.message.edit_text(
        text=f"📝 Микротемы по предмету {callback_data.subject}:",
        reply_markup=get_topics_list_kb(callback_data.subject, topics_db[callback_data.subject])
    )
