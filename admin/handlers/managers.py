from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter

from admin.utils.common import (
    get_managers_list_kb, get_confirmation_kb, add_manager, remove_manager
)
from common.keyboards import get_home_kb

router = Router()

class AdminManagersStates(StatesGroup):
    # Состояния для добавления менеджера
    enter_manager_name = State()
    enter_manager_telegram_id = State()
    confirm_add_manager = State()

    # Состояния для удаления менеджера
    select_manager_to_delete = State()
    confirm_delete_manager = State()

# === ДОБАВЛЕНИЕ МЕНЕДЖЕРА ===

@router.callback_query(F.data == "add_manager")
async def start_add_manager(callback: CallbackQuery, state: FSMContext):
    """Начать добавление менеджера"""
    await callback.message.edit_text(
        text="Введите имя и фамилию менеджера:",
        reply_markup=get_home_kb()
    )
    await state.set_state(AdminManagersStates.enter_manager_name)

@router.message(StateFilter(AdminManagersStates.enter_manager_name))
async def process_manager_name(message: Message, state: FSMContext):
    """Обработать ввод имени менеджера"""
    manager_name = message.text.strip()
    await state.update_data(manager_name=manager_name)
    await state.set_state(AdminManagersStates.enter_manager_telegram_id)

    await message.answer(
        text="Введите Telegram ID менеджера:",
        reply_markup=get_home_kb()
    )

@router.message(StateFilter(AdminManagersStates.enter_manager_telegram_id))
async def process_manager_telegram_id(message: Message, state: FSMContext):
    """Обработать ввод Telegram ID менеджера"""
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

        data = await state.get_data()
        manager_name = data.get("manager_name", "")

        await state.update_data(manager_telegram_id=telegram_id)
        await state.set_state(AdminManagersStates.confirm_add_manager)

        await message.answer(
            text=f"📋 Подтверждение добавления менеджера:\n\n"
                 f"Имя: {manager_name}\n"
                 f"Telegram ID: {telegram_id}",
            reply_markup=get_confirmation_kb("add", "manager")
        )
    except ValueError:
        await message.answer(
            text="❌ Telegram ID должен быть числом. Попробуйте еще раз:",
            reply_markup=get_home_kb()
        )

@router.callback_query(StateFilter(AdminManagersStates.confirm_add_manager), F.data.startswith("confirm_add_manager_"))
async def confirm_add_manager(callback: CallbackQuery, state: FSMContext):
    """Подтвердить добавление менеджера"""
    data = await state.get_data()

    manager_name = data.get("manager_name", "")
    telegram_id = data.get("manager_telegram_id", "")

    # Добавляем менеджера
    success = await add_manager(manager_name, telegram_id)

    if success:
        await callback.message.edit_text(
            text=f"✅ Менеджер '{manager_name}' успешно добавлен!",
            reply_markup=get_home_kb()
        )
    else:
        await callback.message.edit_text(
            text=f"❌ Ошибка при добавлении менеджера '{manager_name}'!\nВозможно, пользователь с таким Telegram ID уже существует.",
            reply_markup=get_home_kb()
        )

    await state.clear()

# === УДАЛЕНИЕ МЕНЕДЖЕРА ===

@router.callback_query(F.data == "remove_manager")
async def start_remove_manager(callback: CallbackQuery, state: FSMContext):
    """Начать удаление менеджера"""
    await callback.message.edit_text(
        text="Выберите менеджера для удаления:",
        reply_markup=await get_managers_list_kb("delete_manager")
    )
    await state.set_state(AdminManagersStates.select_manager_to_delete)

@router.callback_query(AdminManagersStates.select_manager_to_delete, F.data.startswith("delete_manager_"))
async def select_manager_to_delete(callback: CallbackQuery, state: FSMContext):
    """Выбрать менеджера для удаления"""
    manager_id = int(callback.data.replace("delete_manager_", ""))

    # Получаем информацию о менеджере
    from database import ManagerRepository
    manager = await ManagerRepository.get_by_id(manager_id)

    if not manager:
        await callback.message.edit_text(
            text="❌ Менеджер не найден!",
            reply_markup=get_home_kb()
        )
        return

    await state.update_data(manager_to_delete_id=manager_id)
    await state.set_state(AdminManagersStates.confirm_delete_manager)

    await callback.message.edit_text(
        text=f"🗑 Подтверждение удаления менеджера:\n\n"
             f"Имя: {manager.user.name}\n"
             f"Telegram ID: {manager.user.telegram_id}\n\n"
             f"⚠️ Это действие нельзя отменить!",
        reply_markup=get_confirmation_kb("delete", "manager", str(manager_id))
    )

@router.callback_query(StateFilter(AdminManagersStates.confirm_delete_manager), F.data.startswith("confirm_delete_manager_"))
async def confirm_delete_manager(callback: CallbackQuery, state: FSMContext):
    """Подтвердить удаление менеджера"""
    data = await state.get_data()
    manager_id = data.get("manager_to_delete_id")

    # Получаем имя менеджера перед удалением
    from database import ManagerRepository
    manager = await ManagerRepository.get_by_id(manager_id)
    manager_name = manager.user.name if manager else "Неизвестно"

    success = await remove_manager(manager_id)

    if success:
        await callback.message.edit_text(
            text=f"✅ Менеджер '{manager_name}' успешно удален!",
            reply_markup=get_home_kb()
        )
    else:
        await callback.message.edit_text(
            text="❌ Менеджер не найден!",
            reply_markup=get_home_kb()
        )

    await state.clear()

# === ОТМЕНА ДЕЙСТВИЙ ===

@router.callback_query(StateFilter(AdminManagersStates.confirm_add_manager), F.data.startswith("cancel_add_manager"))
async def cancel_add_manager(callback: CallbackQuery, state: FSMContext):
    """Отменить добавление менеджера"""
    await callback.message.edit_text(
        text="❌ Добавление менеджера отменено",
        reply_markup=get_home_kb()
    )
    await state.clear()

@router.callback_query(StateFilter(AdminManagersStates.confirm_delete_manager), F.data.startswith("cancel_delete_manager"))
async def cancel_delete_manager(callback: CallbackQuery, state: FSMContext):
    """Отменить удаление менеджера"""
    await callback.message.edit_text(
        text="❌ Удаление менеджера отменено",
        reply_markup=get_home_kb()
    )
    await state.clear()
