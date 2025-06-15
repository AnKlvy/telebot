from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from manager.keyboards.topics import (
    get_subjects_kb,
    get_topics_list_kb,
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
    delete_by_number = State()  # Удаление микротемы по номеру

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
        text=f"Предмет: {subject.name}\n\n"
             f"📝 Введите названия микротем:\n"
             f"• Одну микротему на строку\n"
             f"• Можно ввести до 200 микротем за раз\n"
             f"• Пустые строки будут пропущены\n\n"
             f"Пример:\n"
             f"Алканы\n"
             f"Алкены\n"
             f"Алкины",
        reply_markup=get_home_kb()
    )

@router.message(StateFilter(ManagerTopicStates.adding_topic))
async def process_topic_name(message: Message, state: FSMContext):
    """Обрабатываем ввод названий микротем (одну или несколько построчно)"""
    data = await state.get_data()
    subject_id = data['subject_id']
    subject_name = data['subject_name']

    # Разбиваем текст на строки и очищаем от пустых
    lines = [line.strip() for line in message.text.split('\n') if line.strip()]

    if not lines:
        await message.answer(
            text="❌ Введите хотя бы одно название микротемы:",
            reply_markup=get_home_kb()
        )
        return

    # Проверяем лимит (примерно 200 строк в пределах 4096 символов)
    if len(lines) > 200:
        await message.answer(
            text=f"❌ Слишком много микротем за раз (максимум 200, введено {len(lines)}).\n"
                 f"Разделите на несколько сообщений:",
            reply_markup=get_home_kb()
        )
        return

    try:
        if len(lines) == 1:
            # Одна микротема - используем старый метод
            microtopic = await MicrotopicRepository.create(lines[0], subject_id)
            created_count = 1
            result_text = f"✅ Микротема добавлена в предмет {subject_name}:\n{microtopic.number}. {microtopic.name}"
        else:
            # Несколько микротем - используем массовое создание
            created_microtopics = await MicrotopicRepository.create_multiple(lines, subject_id)
            created_count = len(created_microtopics)

            if created_count == len(lines):
                result_text = f"✅ Добавлено {created_count} микротем в предмет {subject_name}:\n"
                for mt in created_microtopics:
                    result_text += f"{mt.number}. {mt.name}\n"
            else:
                skipped = len(lines) - created_count
                result_text = f"✅ Добавлено {created_count} микротем в предмет {subject_name}:\n"
                for mt in created_microtopics:
                    result_text += f"{mt.number}. {mt.name}\n"
                result_text += f"⚠️ Пропущено пустых строк: {skipped}"

        # Получаем обновленный список микротем
        microtopics = await MicrotopicRepository.get_by_subject(subject_id)

        await state.set_state(ManagerTopicStates.topics_list)
        await message.answer(
            text=result_text,
            reply_markup=await get_topics_list_kb(subject_name, microtopics)
        )

    except ValueError as e:
        # Ошибка при создании
        await message.answer(
            text=f"❌ {str(e)}\n\nПопробуйте еще раз:",
            reply_markup=get_home_kb()
        )

@router.callback_query(StateFilter(ManagerTopicStates.topics_list), TopicCallback.filter(F.action == TopicActions.DELETE_BY_NUMBER))
async def start_delete_by_number(callback: CallbackQuery, callback_data: TopicCallback, state: FSMContext):
    """Начинаем процесс удаления микротемы по номеру"""
    subject_id = int(callback_data.subject)

    # Получаем название предмета для отображения
    subject = await SubjectRepository.get_by_id(subject_id)
    if not subject:
        await callback.message.edit_text(
            text="❌ Предмет не найден!",
            reply_markup=get_manager_main_menu_kb()
        )
        return

    await state.set_state(ManagerTopicStates.delete_by_number)
    await state.update_data(subject_id=subject_id, subject_name=subject.name)

    await callback.message.edit_text(
        text=f"Предмет: {subject.name}\n\n"
             f"❌ Введите номер микротемы для удаления:",
        reply_markup=get_home_kb()
    )

@router.message(StateFilter(ManagerTopicStates.delete_by_number))
async def process_delete_number(message: Message, state: FSMContext):
    """Обрабатываем ввод номера микротемы для удаления"""
    data = await state.get_data()
    subject_id = data['subject_id']
    subject_name = data['subject_name']

    try:
        number = int(message.text.strip())

        if number < 1:
            await message.answer(
                text="❌ Номер микротемы должен быть больше 0. Попробуйте еще раз:",
                reply_markup=get_home_kb()
            )
            return

        # Удаляем микротему по номеру
        success, deleted_name = await MicrotopicRepository.delete_by_number(subject_id, number)

        if success:
            # Получаем обновленный список микротем
            microtopics = await MicrotopicRepository.get_by_subject(subject_id)

            await state.set_state(ManagerTopicStates.topics_list)
            await message.answer(
                text=f"✅ Микротема №{number} \"{deleted_name}\" удалена из предмета {subject_name}",
                reply_markup=await get_topics_list_kb(subject_name, microtopics)
            )
        else:
            await message.answer(
                text=f"❌ Микротема с номером {number} не найдена в предмете {subject_name}.\n"
                     f"Попробуйте другой номер:",
                reply_markup=get_home_kb()
            )

    except ValueError:
        await message.answer(
            text="❌ Введите корректный номер микротемы (число):",
            reply_markup=get_home_kb()
        )

@router.callback_query(StateFilter(ManagerTopicStates.topics_list), TopicCallback.filter(F.action == TopicActions.SHOW_LIST))
async def show_microtopics_list(callback: CallbackQuery, callback_data: TopicCallback, state: FSMContext):
    """Показываем список всех микротем предмета в текстовом виде"""
    subject_id = int(callback_data.subject)

    # Получаем предмет и его микротемы
    subject = await SubjectRepository.get_by_id(subject_id)
    if not subject:
        await callback.message.edit_text(
            text="❌ Предмет не найден!",
            reply_markup=get_manager_main_menu_kb()
        )
        return

    microtopics = await MicrotopicRepository.get_by_subject(subject_id)

    if not microtopics:
        text = f"📋 Микротемы по предмету {subject.name}:\n\n❌ Микротемы не найдены"
    else:
        text = f"📋 Микротемы по предмету {subject.name}:\n\n"
        for microtopic in microtopics:
            text += f"{microtopic.number}. {microtopic.name}\n"
        text += f"\nВсего микротем: {len(microtopics)}"

    await callback.message.edit_text(
        text=text,
        reply_markup=await get_topics_list_kb(subject.name, microtopics)
    )
