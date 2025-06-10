from typing import Dict, Callable, Any, Optional
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from admin.utils.common import (
    get_entity_list_kb, get_confirmation_kb,
    managers_db, add_subject, remove_subject, add_person, remove_person
)
from common.keyboards import get_home_kb


def generate_simple_entity_handlers(
    router: Router,
    entity_name: str,
    entity_name_accusative: str,
    callback_prefix: str,
    data_storage: Any,
    add_function: Callable,
    remove_function: Callable,
    states_class: Any,
    list_function: Optional[Callable] = None
):
    """
    Генератор обработчиков для простых сущностей (предметы, менеджеры)
    
    Args:
        router: Роутер для регистрации обработчиков
        entity_name: Название сущности (предмет, менеджер)
        entity_name_accusative: Название в винительном падеже
        callback_prefix: Префикс для callback_data
        data_storage: Хранилище данных
        add_function: Функция добавления
        remove_function: Функция удаления
        states_class: Класс состояний
        list_function: Функция получения списка (опционально)
    """
    
    # Обработчик начала добавления
    @router.callback_query(F.data == f"add_{callback_prefix}")
    async def start_add_entity(callback: CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            text=f"Введите название {entity_name_accusative}:",
            reply_markup=get_home_kb()
        )
        await state.set_state(getattr(states_class, f"enter_{callback_prefix}_name"))
    
    # Обработчик ввода названия
    @router.message(StateFilter(getattr(states_class, f"enter_{callback_prefix}_name")))
    async def process_entity_name(message: Message, state: FSMContext):
        entity_name_input = message.text.strip()
        
        await state.update_data(**{f"{callback_prefix}_name": entity_name_input})
        await state.set_state(getattr(states_class, f"confirm_add_{callback_prefix}"))
        
        await message.answer(
            text=f"📋 Подтверждение добавления:\n\n"
                 f"{entity_name.capitalize()}: {entity_name_input}",
            reply_markup=get_confirmation_kb("add", callback_prefix)
        )
    
    # Обработчик подтверждения добавления
    @router.callback_query(StateFilter(getattr(states_class, f"confirm_add_{callback_prefix}")), F.data.startswith(f"confirm_add_{callback_prefix}_"))
    async def confirm_add_entity(callback: CallbackQuery, state: FSMContext):
        data = await state.get_data()
        entity_name_input = data.get(f"{callback_prefix}_name")

        success = add_function(entity_name_input)

        if success:
            await callback.message.edit_text(
                text=f"✅ {entity_name.capitalize()} '{entity_name_input}' успешно добавлен!",
                reply_markup=get_home_kb()
            )
        else:
            await callback.message.edit_text(
                text=f"❌ {entity_name.capitalize()} '{entity_name_input}' уже существует!",
                reply_markup=get_home_kb()
            )

        await state.clear()
    
    # Обработчик начала удаления
    @router.callback_query(F.data == f"remove_{callback_prefix}")
    async def start_remove_entity(callback: CallbackQuery, state: FSMContext):
        if list_function:
            items_list = list_function()
        else:
            items_list = list(data_storage) if isinstance(data_storage, (list, dict)) else data_storage
        
        await callback.message.edit_text(
            text=f"Выберите {entity_name_accusative} для удаления:",
            reply_markup=get_entity_list_kb(items_list, f"delete_{callback_prefix}")
        )
        await state.set_state(getattr(states_class, f"select_{callback_prefix}_to_delete"))
    
    # Обработчик выбора для удаления
    @router.callback_query(F.data.startswith(f"delete_{callback_prefix}_"))
    async def select_entity_to_delete(callback: CallbackQuery, state: FSMContext):
        entity_id = callback.data.replace(f"delete_{callback_prefix}_", "")
        
        await state.update_data(**{f"{callback_prefix}_to_delete": entity_id})
        await state.set_state(getattr(states_class, f"confirm_delete_{callback_prefix}"))
        
        await callback.message.edit_text(
            text=f"🗑 Подтверждение удаления:\n\n"
                 f"{entity_name.capitalize()}: {entity_id}\n\n"
                 f"⚠️ Это действие нельзя отменить!",
            reply_markup=get_confirmation_kb("delete", callback_prefix, entity_id)
        )
    
    # Обработчик подтверждения удаления
    @router.callback_query(StateFilter(getattr(states_class, f"confirm_delete_{callback_prefix}")), F.data.startswith(f"confirm_delete_{callback_prefix}_"))
    async def confirm_delete_entity(callback: CallbackQuery, state: FSMContext):
        data = await state.get_data()
        entity_id = data.get(f"{callback_prefix}_to_delete")

        success = remove_function(entity_id)

        if success:
            await callback.message.edit_text(
                text=f"✅ {entity_name.capitalize()} '{entity_id}' успешно удален!",
                reply_markup=get_home_kb()
            )
        else:
            await callback.message.edit_text(
                text=f"❌ {entity_name.capitalize()} '{entity_id}' не найден!",
                reply_markup=get_home_kb()
            )

        await state.clear()
    
    # Обработчики отмены
    @router.callback_query(StateFilter(getattr(states_class, f"confirm_add_{callback_prefix}")), F.data.startswith(f"cancel_add_{callback_prefix}"))
    async def cancel_add_entity(callback: CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            text=f"❌ Добавление {entity_name_accusative} отменено",
            reply_markup=get_home_kb()
        )
        await state.clear()

    @router.callback_query(StateFilter(getattr(states_class, f"confirm_delete_{callback_prefix}")), F.data.startswith(f"cancel_delete_{callback_prefix}"))
    async def cancel_delete_entity(callback: CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            text=f"❌ Удаление {entity_name_accusative} отменено",
            reply_markup=get_home_kb()
        )
        await state.clear()

def generate_person_entity_handlers(
    router: Router,
    entity_name: str,
    entity_name_accusative: str,
    callback_prefix: str,
    data_storage: Dict,
    states_class: Any,
    add_function: Callable = None,
    additional_fields: Dict[str, str] = None
):
    """
    Генератор обработчиков для людей (менеджеры, кураторы, преподаватели, ученики)
    
    Args:
        additional_fields: Дополнительные поля для ввода {"field_name": "Описание поля"}
    """
    
    # Обработчик начала добавления
    @router.callback_query(F.data == f"add_{callback_prefix}")
    async def start_add_person(callback: CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            text=f"Введите имя и фамилию {entity_name_accusative}:",
            reply_markup=get_home_kb()
        )
        await state.set_state(getattr(states_class, f"enter_{callback_prefix}_name"))
    
    # Обработчик ввода имени
    @router.message(StateFilter(getattr(states_class, f"enter_{callback_prefix}_name")))
    async def process_person_name(message: Message, state: FSMContext):
        person_name = message.text.strip()
        
        await state.update_data(**{f"{callback_prefix}_name": person_name})
        await state.set_state(getattr(states_class, f"enter_{callback_prefix}_telegram_id"))
        
        await message.answer(
            text=f"Введите Telegram ID {entity_name_accusative}:",
            reply_markup=get_home_kb()
        )
    
    # Обработчик ввода Telegram ID
    @router.message(StateFilter(getattr(states_class, f"enter_{callback_prefix}_telegram_id")))
    async def process_person_telegram_id(message: Message, state: FSMContext):
        try:
            telegram_id = int(message.text.strip())

            # Проверяем, существует ли уже пользователь с таким Telegram ID
            from database import UserRepository
            existing_user = await UserRepository.get_by_telegram_id(telegram_id)

            if existing_user:
                await message.answer(
                    text=f"❌ Пользователь с Telegram ID {telegram_id} уже существует!\n"
                         f"Имя: {existing_user.name}\n"
                         f"Роль: {existing_user.role}\n\n"
                         f"Введите другой Telegram ID:",
                    reply_markup=get_home_kb()
                )
                return

            await state.update_data(**{f"{callback_prefix}_telegram_id": telegram_id})

            # Если есть дополнительные поля, переходим к ним
            if additional_fields:
                first_field = list(additional_fields.keys())[0]
                await state.set_state(getattr(states_class, f"enter_{callback_prefix}_{first_field}"))
                await message.answer(
                    text=additional_fields[first_field],
                    reply_markup=get_home_kb()
                )
            else:
                # Переходим к подтверждению
                await show_person_confirmation(message, state, entity_name, callback_prefix, states_class)

        except ValueError:
            await message.answer(
                text="❌ Telegram ID должен быть числом. Попробуйте еще раз:",
                reply_markup=get_home_kb()
            )

    # Обработчик подтверждения добавления
    @router.callback_query(StateFilter(getattr(states_class, f"confirm_add_{callback_prefix}")), F.data.startswith(f"confirm_add_{callback_prefix}_"))
    async def confirm_add_person(callback: CallbackQuery, state: FSMContext):
        data = await state.get_data()
        person_name = data.get(f"{callback_prefix}_name")
        telegram_id = data.get(f"{callback_prefix}_telegram_id")

        # Собираем дополнительные поля
        additional_data = {}
        for key, value in data.items():
            if key.startswith(f"{callback_prefix}_") and key not in [f"{callback_prefix}_name", f"{callback_prefix}_telegram_id"]:
                field_name = key.replace(f"{callback_prefix}_", "")
                additional_data[field_name] = value

        # Добавляем человека
        if add_function:
            success = add_function(person_name, telegram_id, **additional_data)
        else:
            person_id = add_person(data_storage, person_name, telegram_id, **additional_data)
            success = True

        if success:
            await callback.message.edit_text(
                text=f"✅ {entity_name.capitalize()} '{person_name}' успешно добавлен!",
                reply_markup=get_home_kb()
            )
        else:
            await callback.message.edit_text(
                text=f"❌ {entity_name.capitalize()} '{person_name}' уже существует!",
                reply_markup=get_home_kb()
            )
        await state.clear()

    # Обработчик отмены
    @router.callback_query(StateFilter(getattr(states_class, f"confirm_add_{callback_prefix}")), F.data.startswith(f"cancel_add_{callback_prefix}"))
    async def cancel_add_person(callback: CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            text=f"❌ Добавление {entity_name_accusative} отменено",
            reply_markup=get_home_kb()
        )
        await state.clear()

async def show_person_confirmation(message: Message, state: FSMContext, entity_name: str, callback_prefix: str, states_class: Any):
    """Показать подтверждение для добавления человека"""
    data = await state.get_data()
    person_name = data.get(f"{callback_prefix}_name")
    telegram_id = data.get(f"{callback_prefix}_telegram_id")

    confirmation_text = f"📋 Подтверждение добавления:\n\n"
    confirmation_text += f"Имя: {person_name}\n"
    confirmation_text += f"Telegram ID: {telegram_id}\n"

    # Добавляем дополнительные поля если есть
    for key, value in data.items():
        if key.startswith(f"{callback_prefix}_") and key not in [f"{callback_prefix}_name", f"{callback_prefix}_telegram_id"]:
            field_name = key.replace(f"{callback_prefix}_", "").replace("_", " ").title()
            confirmation_text += f"{field_name}: {value}\n"

    await state.set_state(getattr(states_class, f"confirm_add_{callback_prefix}"))
    await message.answer(
        text=confirmation_text,
        reply_markup=get_confirmation_kb("add", callback_prefix)
    )
