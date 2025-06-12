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
from database import SubjectRepository, MicrotopicRepository
from common.keyboards import get_home_kb

class ManagerTopicStates(StatesGroup):
    main = State()  # Главное меню микротем (выбор предмета)
    topics_list = State()  # Список микротем предмета
    adding_topic = State()  # Добавление новой микротемы
    confirm_deletion = State()  # Подтверждение удаления
    process_topic_name = State()
    delete_topic = State()
    cancel_delete = State()

router = Router()

@router.callback_query(F.data == "manager_topics")
async def show_subjects(callback: CallbackQuery, state: FSMContext):
    """Показываем список предметов"""
    await state.set_state(ManagerTopicStates.main)
    await callback.message.edit_text(
        text="Выберите предмет для работы с микротемами:",
        reply_markup=await get_subjects_kb()
    )

@router.callback_query(StateFilter(ManagerTopicStates.main), TopicCallback.filter(F.action == TopicActions.VIEW))
async def show_topics(callback: CallbackQuery, callback_data: TopicCallback, state: FSMContext):
    """Показываем список микротем для выбранного предмета"""
    subject_id = int(callback_data.subject)

    # Получаем предмет и его микротемы из базы данных
    subject = await SubjectRepository.get_by_id(subject_id)
    if not subject:
        await callback.message.edit_text(
            text="❌ Предмет не найден!",
            reply_markup=get_manager_main_menu_kb()
        )
        return

    microtopics = await MicrotopicRepository.get_by_subject(subject_id)

    await state.set_state(ManagerTopicStates.topics_list)
    await state.update_data(current_subject_id=subject_id, current_subject_name=subject.name)

    await callback.message.edit_text(
        text=f"📝 Микротемы по предмету {subject.name}:\n"
             f"Всего микротем: {len(microtopics)}",
        reply_markup=await get_topics_list_kb(subject.name, microtopics)
    )

@router.callback_query(StateFilter(ManagerTopicStates.topics_list), TopicCallback.filter(F.action == TopicActions.ADD))
async def start_add_topic(callback: CallbackQuery, callback_data: TopicCallback, state: FSMContext):
    """Начинаем процесс добавления микротемы"""
    subject_id = int(callback_data.subject)

    # Получаем название предмета для отображения
    subject = await SubjectRepository.get_by_id(subject_id)
    if not subject:
        await callback.message.edit_text(
            text="❌ Предмет не найден!",
            reply_markup=get_manager_main_menu_kb()
        )
        return

    await state.set_state(ManagerTopicStates.adding_topic)
    await state.update_data(subject_id=subject_id, subject_name=subject.name)

    await callback.message.edit_text(
        text=f"Предмет: {subject.name}\n\nВведите название новой микротемы:",
        reply_markup=get_home_kb()
    )

@router.message(StateFilter(ManagerTopicStates.adding_topic))
async def process_topic_name(message: Message, state: FSMContext):
    """Обрабатываем ввод названия микротемы"""
    data = await state.get_data()
    subject_id = data['subject_id']
    subject_name = data['subject_name']
    new_topic = message.text.strip()

    try:
        # Создаем микротему в базе данных
        microtopic = await MicrotopicRepository.create(new_topic, subject_id)

        # Получаем обновленный список микротем
        microtopics = await MicrotopicRepository.get_by_subject(subject_id)

        await state.set_state(ManagerTopicStates.topics_list)
        await message.answer(
            text=f"✅ Микротема \"{new_topic}\" добавлена в предмет {subject_name}",
            reply_markup=await get_topics_list_kb(subject_name, microtopics)
        )
    except ValueError as e:
        # Микротема уже существует
        await message.answer(
            text=f"❌ {str(e)}\n\nВведите другое название:",
            reply_markup=get_home_kb()
        )

@router.callback_query(StateFilter(ManagerTopicStates.topics_list), TopicCallback.filter(F.action == TopicActions.DELETE))
async def confirm_delete(callback: CallbackQuery, callback_data: TopicCallback, state: FSMContext):
    """Запрашиваем подтверждение удаления микротемы"""
    microtopic_id = int(callback_data.topic)

    # Получаем информацию о микротеме
    microtopic = await MicrotopicRepository.get_by_id(microtopic_id)
    if not microtopic:
        await callback.message.edit_text(
            text="❌ Микротема не найдена!",
            reply_markup=get_manager_main_menu_kb()
        )
        return

    await state.set_state(ManagerTopicStates.confirm_deletion)
    await state.update_data(
        microtopic_id=microtopic_id,
        microtopic_name=microtopic.name,
        subject_id=microtopic.subject_id,
        subject_name=microtopic.subject.name
    )

    await callback.message.edit_text(
        text=f"❗️ Вы уверены, что хотите удалить микротему \"{microtopic.name}\" из предмета {microtopic.subject.name}?",
        reply_markup=confirm_delete_topic_kb(str(microtopic.subject_id), str(microtopic_id))
    )

@router.callback_query(StateFilter(ManagerTopicStates.confirm_deletion), TopicCallback.filter(F.action == TopicActions.CONFIRM_DELETE))
async def delete_topic(callback: CallbackQuery, callback_data: TopicCallback, state: FSMContext):
    """Удаляем микротему после подтверждения"""
    data = await state.get_data()
    microtopic_id = data['microtopic_id']
    microtopic_name = data['microtopic_name']
    subject_id = data['subject_id']
    subject_name = data['subject_name']

    # Удаляем микротему из базы данных
    success = await MicrotopicRepository.delete(microtopic_id)

    if success:
        # Получаем обновленный список микротем
        microtopics = await MicrotopicRepository.get_by_subject(subject_id)

        await state.set_state(ManagerTopicStates.topics_list)
        await callback.message.edit_text(
            text=f"✅ Микротема \"{microtopic_name}\" удалена из предмета {subject_name}",
            reply_markup=await get_topics_list_kb(subject_name, microtopics)
        )
    else:
        await callback.message.edit_text(
            text=f"❌ Ошибка при удалении микротемы \"{microtopic_name}\"",
            reply_markup=get_manager_main_menu_kb()
        )

@router.callback_query(StateFilter(ManagerTopicStates.confirm_deletion), TopicCallback.filter(F.action == TopicActions.CANCEL))
async def cancel_delete(callback: CallbackQuery, callback_data: TopicCallback, state: FSMContext):
    """Отменяем удаление микротемы"""
    data = await state.get_data()
    subject_id = data['subject_id']
    subject_name = data['subject_name']

    # Получаем список микротем
    microtopics = await MicrotopicRepository.get_by_subject(subject_id)

    await state.set_state(ManagerTopicStates.topics_list)
    await callback.message.edit_text(
        text=f"📝 Микротемы по предмету {subject_name}:",
        reply_markup=await get_topics_list_kb(subject_name, microtopics)
    )
