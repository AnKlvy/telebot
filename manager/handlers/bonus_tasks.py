from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
import logging

from common.keyboards import get_main_menu_back_button, get_home_kb
from .main import show_manager_main_menu
from database import ShopItemRepository

from aiogram.fsm.state import State, StatesGroup

class BonusTaskStates(StatesGroup):
    main = State()
    enter_task_name = State()
    enter_task_description = State()
    enter_price = State()
    confirm_task = State()
    delete_task = State()
    select_task_to_delete = State()

# Настройка логгера
logger = logging.getLogger(__name__)

router = Router()

def get_bonus_task_management_kb() -> InlineKeyboardMarkup:
    """Клавиатура управления бонусными заданиями"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить бонусное задание", callback_data="add_bonus_task")],
        [InlineKeyboardButton(text="🗑 Удалить бонусное задание", callback_data="delete_bonus_task")],
        *get_main_menu_back_button()
    ])

def get_task_price_kb() -> InlineKeyboardMarkup:
    """Клавиатура выбора цены в монетах для задания"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="30 монет", callback_data="task_price_30")],
        [InlineKeyboardButton(text="50 монет", callback_data="task_price_50")],
        [InlineKeyboardButton(text="80 монет", callback_data="task_price_80")],
        [InlineKeyboardButton(text="100 монет", callback_data="task_price_100")],
        [InlineKeyboardButton(text="150 монет", callback_data="task_price_150")],
        [InlineKeyboardButton(text="Ввести вручную", callback_data="task_price_custom")],
        *get_main_menu_back_button()
    ])

def get_confirm_bonus_task_kb() -> InlineKeyboardMarkup:
    """Клавиатура подтверждения создания бонусного задания"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Создать задание", callback_data="confirm_bonus_task")],
        [InlineKeyboardButton(text="✏️ Редактировать", callback_data="edit_bonus_task")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_bonus_task")],
        *get_main_menu_back_button()
    ])

# Импортируем состояния менеджера
from manager.handlers.main import ManagerMainStates

# Добавляем обработчик с фильтром состояния менеджера
@router.callback_query(F.data == "manager_bonus_tasks")
async def manager_bonus_tasks_handler(callback: CallbackQuery, state: FSMContext):
    """Обработчик бонусных заданий из главного меню менеджера"""
    print(f"🔍 DEBUG: Получен callback с data: {callback.data}")
    logger.info(f"🔍 DEBUG: Получен callback с data: {callback.data}")

    # Проверяем текущее состояние
    current_state = await state.get_state()
    print(f"🔍 DEBUG: Текущее состояние: {current_state}")
    logger.info(f"🔍 DEBUG: Текущее состояние: {current_state}")

    await show_bonus_task_management(callback, state)

# Добавляем универсальный обработчик без фильтра состояния (на случай если состояние не установлено)
@router.callback_query(F.data == "manager_bonus_tasks")
async def debug_bonus_tasks_handler(callback: CallbackQuery, state: FSMContext):
    """Отладочный обработчик для проверки работы"""
    print(f"🔍 DEBUG UNIVERSAL: Получен callback с data: {callback.data}")
    logger.info(f"🔍 DEBUG UNIVERSAL: Получен callback с data: {callback.data}")

    # Проверяем текущее состояние
    current_state = await state.get_state()
    print(f"🔍 DEBUG UNIVERSAL: Текущее состояние: {current_state}")
    logger.info(f"🔍 DEBUG UNIVERSAL: Текущее состояние: {current_state}")
    await show_bonus_task_management(callback, state)

async def show_bonus_task_management(callback: CallbackQuery, state: FSMContext):
    """Показ меню управления бонусными заданиями"""
    logger.info("🎯 ВЫЗВАН ОБРАБОТЧИК show_bonus_task_management")
    print("🎯 ВЫЗВАН ОБРАБОТЧИК show_bonus_task_management")  # Дополнительное логирование

    try:
        # Сначала отвечаем на callback, чтобы убрать "часики"
        await callback.answer()

        await callback.message.edit_text(
            "📝 Управление бонусными заданиями\n\n"
            "Бонусные задания появляются в каталоге бонусов у учеников и покупаются за монеты.\n"
            "Вы можете дать название заданию и написать любой текст, который будет видеть ученик.",
            reply_markup=get_bonus_task_management_kb()
        )
        await state.set_state(BonusTaskStates.main)
        logger.info("✅ Обработчик show_bonus_task_management выполнен успешно")
        print("✅ Обработчик show_bonus_task_management выполнен успешно")
    except Exception as e:
        logger.error(f"❌ Ошибка в show_bonus_task_management: {e}")
        print(f"❌ Ошибка в show_bonus_task_management: {e}")
        await callback.answer("Произошла ошибка. Попробуйте еще раз.")

@router.callback_query(BonusTaskStates.main, F.data == "add_bonus_task")
async def start_add_bonus_task(callback: CallbackQuery, state: FSMContext):
    """Начало добавления бонусного задания"""
    logger.info("Вызван обработчик start_add_bonus_task")
    
    await callback.message.edit_text(
        "📝 Создание бонусного задания\n\n"
        "Введите название бонусного задания:",
        reply_markup=get_home_kb()
    )
    await state.set_state(BonusTaskStates.enter_task_name)

@router.message(BonusTaskStates.enter_task_name)
async def process_task_name(message: Message, state: FSMContext):
    """Обработка названия задания"""
    logger.info("Вызван обработчик process_task_name")
    
    task_name = message.text.strip()
    
    if not task_name:
        await message.answer("Название не может быть пустым. Пожалуйста, введите название задания:")
        return
    
    await state.update_data(task_name=task_name)
    
    await message.answer(
        f"📝 Название: {task_name}\n\n"
        "Теперь введите описание задания (любой текст, который будет видеть ученик):",
        reply_markup=get_home_kb()
    )
    await state.set_state(BonusTaskStates.enter_task_description)

@router.message(BonusTaskStates.enter_task_description)
async def process_task_description(message: Message, state: FSMContext):
    """Обработка описания задания"""
    logger.info("Вызван обработчик process_task_description")
    
    task_description = message.text.strip()
    
    if not task_description:
        await message.answer("Описание не может быть пустым. Пожалуйста, введите описание задания:")
        return
    
    await state.update_data(task_description=task_description)
    
    user_data = await state.get_data()
    task_name = user_data.get("task_name", "")
    
    await message.answer(
        f"📝 Название: {task_name}\n"
        f"📄 Описание: {task_description[:100]}{'...' if len(task_description) > 100 else ''}\n\n"
        "Выберите цену в монетах для этого бонусного задания:",
        reply_markup=get_task_price_kb()
    )
    await state.set_state(BonusTaskStates.enter_price)

@router.callback_query(BonusTaskStates.enter_price, F.data.startswith("task_price_"))
async def process_price_selection(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора цены"""
    logger.info("Вызван обработчик process_price_selection")
    
    price_data = callback.data.replace("task_price_", "")
    
    if price_data == "custom":
        await callback.message.edit_text(
            "Введите цену в монетах (число):",
            reply_markup=get_home_kb()
        )
        return
    
    price = int(price_data)
    await state.update_data(price=price)
    await show_bonus_task_confirmation(callback, state)

@router.message(BonusTaskStates.enter_price)
async def process_custom_price(message: Message, state: FSMContext):
    """Обработка ввода пользовательской цены"""
    logger.info("Вызван обработчик process_custom_price")
    
    try:
        price = int(message.text.strip())
        if price <= 0:
            await message.answer("Цена должна быть положительным числом. Попробуйте еще раз:")
            return
            
        await state.update_data(price=price)
        await show_bonus_task_confirmation(message, state)
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число:")

async def show_bonus_task_confirmation(message_or_callback, state: FSMContext):
    """Показ подтверждения создания бонусного задания"""
    user_data = await state.get_data()
    task_name = user_data.get("task_name", "")
    task_description = user_data.get("task_description", "")
    price = user_data.get("price", 0)
    
    # Обрезаем описание для предварительного просмотра
    preview_description = task_description[:200] + "..." if len(task_description) > 200 else task_description
    
    confirmation_text = (
        f"📝 Бонусное задание готово к созданию:\n\n"
        f"📌 Название: {task_name}\n"
        f"📄 Описание: {preview_description}\n"
        f"💰 Цена: {price} монет\n\n"
        "Подтвердите создание бонусного задания:"
    )
    
    if hasattr(message_or_callback, 'message'):
        await message_or_callback.message.edit_text(
            confirmation_text,
            reply_markup=get_confirm_bonus_task_kb()
        )
    else:
        await message_or_callback.answer(
            confirmation_text,
            reply_markup=get_confirm_bonus_task_kb()
        )
    
    await state.set_state(BonusTaskStates.confirm_task)

@router.callback_query(BonusTaskStates.confirm_task, F.data == "confirm_bonus_task")
async def save_bonus_task(callback: CallbackQuery, state: FSMContext):
    """Сохранение бонусного задания"""
    logger.info("Вызван обработчик save_bonus_task")

    user_data = await state.get_data()
    task_name = user_data.get("task_name", "")
    task_description = user_data.get("task_description", "")
    price = user_data.get("price", 0)

    try:
        # Создаем бонусное задание в базе данных как товар магазина
        shop_item = await ShopItemRepository.create_bonus_task(
            name=task_name,
            description=task_description,
            price=price
        )

        await callback.message.edit_text(
            f"✅ Бонусное задание '{task_name}' успешно создано!\n"
            f"💰 Цена: {price} монет\n\n"
            "Задание появится в каталоге бонусов у учеников.",
            reply_markup=get_bonus_task_management_kb()
        )
        logger.info(f"Создано бонусное задание: {task_name} (ID: {shop_item.id})")

    except Exception as e:
        logger.error(f"Ошибка при создании бонусного задания: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка при создании бонусного задания.\n"
            "Попробуйте еще раз.",
            reply_markup=get_bonus_task_management_kb()
        )

    await state.set_state(BonusTaskStates.main)

@router.callback_query(BonusTaskStates.confirm_task, F.data == "edit_bonus_task")
async def edit_bonus_task(callback: CallbackQuery, state: FSMContext):
    """Редактирование бонусного задания - возврат к выбору цены"""
    logger.info("Вызван обработчик edit_bonus_task")
    
    await callback.message.edit_text(
        "Выберите цену в монетах для этого бонусного задания:",
        reply_markup=get_task_price_kb()
    )
    await state.set_state(BonusTaskStates.enter_price)

@router.callback_query(BonusTaskStates.confirm_task, F.data == "cancel_bonus_task")
async def cancel_bonus_task(callback: CallbackQuery, state: FSMContext):
    """Отмена создания бонусного задания"""
    logger.info("Вызван обработчик cancel_bonus_task")

    await callback.message.edit_text(
        "❌ Создание бонусного задания отменено.",
        reply_markup=get_bonus_task_management_kb()
    )
    await state.set_state(BonusTaskStates.main)

# Обработчики для удаления бонусных заданий
@router.callback_query(BonusTaskStates.main, F.data == "delete_bonus_task")
async def show_bonus_tasks_to_delete(callback: CallbackQuery, state: FSMContext):
    """Показ списка бонусных заданий для удаления"""
    logger.info("Вызван обработчик show_bonus_tasks_to_delete")

    try:
        # Получаем все бонусные задания из базы данных
        bonus_tasks = await ShopItemRepository.get_by_type("bonus_task")

        if not bonus_tasks:
            await callback.message.edit_text(
                "📝 Бонусных заданий пока нет.\n\n"
                "Создайте первое бонусное задание!",
                reply_markup=get_bonus_task_management_kb()
            )
            await state.set_state(BonusTaskStates.main)
            return

        # Создаем клавиатуру с бонусными заданиями
        buttons = []
        for task in bonus_tasks:
            button_text = f"📝 {task.name} - {task.price} монет"
            buttons.append([InlineKeyboardButton(
                text=button_text,
                callback_data=f"delete_task_{task.id}"
            )])

        buttons.extend(get_main_menu_back_button())
        tasks_kb = InlineKeyboardMarkup(inline_keyboard=buttons)

        await callback.message.edit_text(
            "Выберите бонусное задание для удаления:",
            reply_markup=tasks_kb
        )
        await state.set_state(BonusTaskStates.select_task_to_delete)

    except Exception as e:
        logger.error(f"Ошибка при получении списка бонусных заданий: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка при загрузке списка заданий.",
            reply_markup=get_bonus_task_management_kb()
        )
        await state.set_state(BonusTaskStates.main)

@router.callback_query(BonusTaskStates.select_task_to_delete, F.data.startswith("delete_task_"))
async def confirm_delete_bonus_task(callback: CallbackQuery, state: FSMContext):
    """Подтверждение удаления бонусного задания"""
    logger.info("Вызван обработчик confirm_delete_bonus_task")

    task_id = int(callback.data.replace("delete_task_", ""))
    await state.update_data(task_id=task_id)

    try:
        # Получаем информацию о задании из базы данных
        task = await ShopItemRepository.get_by_id(task_id)

        if not task:
            await callback.message.edit_text(
                "❌ Бонусное задание не найдено.",
                reply_markup=get_bonus_task_management_kb()
            )
            await state.set_state(BonusTaskStates.main)
            return

        await callback.message.edit_text(
            f"Вы действительно хотите удалить бонусное задание '{task.name}'?\n\n"
            "⚠️ Это действие нельзя отменить!",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Да, удалить", callback_data="confirm_delete_task")],
                [InlineKeyboardButton(text="❌ Нет, отмена", callback_data="cancel_delete_task")]
            ])
        )

    except Exception as e:
        logger.error(f"Ошибка при получении информации о задании: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка при загрузке информации о задании.",
            reply_markup=get_bonus_task_management_kb()
        )
        await state.set_state(BonusTaskStates.main)

@router.callback_query(F.data == "confirm_delete_task")
async def delete_bonus_task(callback: CallbackQuery, state: FSMContext):
    """Удаление бонусного задания"""
    logger.info("Вызван обработчик delete_bonus_task")

    user_data = await state.get_data()
    task_id = user_data.get("task_id")

    if not task_id:
        await callback.message.edit_text(
            "❌ Ошибка: не найден ID задания для удаления.",
            reply_markup=get_bonus_task_management_kb()
        )
        await state.set_state(BonusTaskStates.main)
        return

    try:
        # Деактивируем бонусное задание в базе данных
        success = await ShopItemRepository.deactivate(task_id)

        if success:
            await callback.message.edit_text(
                "✅ Бонусное задание успешно удалено!\n\n"
                "Задание больше не будет отображаться в каталоге бонусов у учеников.",
                reply_markup=get_bonus_task_management_kb()
            )
            logger.info(f"Удалено бонусное задание с ID: {task_id}")
        else:
            await callback.message.edit_text(
                "❌ Не удалось удалить бонусное задание.\n"
                "Возможно, оно уже было удалено.",
                reply_markup=get_bonus_task_management_kb()
            )

    except Exception as e:
        logger.error(f"Ошибка при удалении бонусного задания: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка при удалении задания.",
            reply_markup=get_bonus_task_management_kb()
        )

    await state.set_state(BonusTaskStates.main)

@router.callback_query(F.data == "cancel_delete_task")
async def cancel_delete_bonus_task(callback: CallbackQuery, state: FSMContext):
    """Отмена удаления бонусного задания"""
    logger.info("Вызван обработчик cancel_delete_bonus_task")

    await show_bonus_tasks_to_delete(callback, state)
