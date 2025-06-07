
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
import logging

from common.keyboards import get_main_menu_back_button, get_home_kb
from common.manager_tests.register_handlers import register_test_handlers
from .main import show_manager_main_menu

from aiogram.fsm.state import State, StatesGroup

class BonusTestStates(StatesGroup):
    main = State()
    select_course = State()
    select_subject = State()
    select_lesson = State()
    enter_test_name = State()
    add_question = State()
    select_topic = State()
    enter_question_text = State()
    add_question_photo = State()
    enter_answer_options = State()
    select_correct_answer = State()
    set_time_limit = State()
    confirm_test = State()
    enter_price = State()
    delete_test = State()
    select_test_to_delete = State()
    request_topic = State()
    process_topic = State()
    process_photo = State()
    skip_photo = State()

# Настройка логгера
logger = logging.getLogger(__name__)

router = Router()

def get_bonus_test_management_kb() -> InlineKeyboardMarkup:
    """Клавиатура управления бонусными тестами"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить бонусный тест", callback_data="add_bonus_test")],
        [InlineKeyboardButton(text="🗑 Удалить бонусный тест", callback_data="delete_bonus_test")],
        *get_main_menu_back_button()
    ])

def get_price_kb() -> InlineKeyboardMarkup:
    """Клавиатура выбора цены в монетах"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="50 монет", callback_data="price_50")],
        [InlineKeyboardButton(text="100 монет", callback_data="price_100")],
        [InlineKeyboardButton(text="150 монет", callback_data="price_150")],
        [InlineKeyboardButton(text="200 монет", callback_data="price_200")],
        [InlineKeyboardButton(text="Ввести вручную", callback_data="price_custom")],
        *get_main_menu_back_button()
    ])

def get_confirm_bonus_test_kb() -> InlineKeyboardMarkup:
    """Клавиатура подтверждения создания бонусного теста"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Создать тест", callback_data="confirm_bonus_test")],
        [InlineKeyboardButton(text="✏️ Редактировать", callback_data="edit_bonus_test")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_bonus_test")]
    ])

@router.callback_query(F.data == "manager_bonus_test")
async def show_bonus_test_management(callback: CallbackQuery, state: FSMContext):
    """Показ меню управления бонусными тестами"""
    logger.info("Вызван обработчик show_bonus_test_management")

    await callback.message.edit_text(
        "🧪 Управление бонусными тестами\n\n"
        "Бонусные тесты появляются в магазине у учеников и покупаются за монеты.",
        reply_markup=get_bonus_test_management_kb()
    )
    await state.set_state(BonusTestStates.main)

@router.callback_query(BonusTestStates.main, F.data == "add_bonus_test")
async def start_add_bonus_test(callback: CallbackQuery, state: FSMContext):
    """Начало добавления бонусного теста - переход в общий модуль"""
    logger.info("Вызван обработчик start_add_bonus_test")
    
    # Сразу переходим к добавлению названия теста в общем модуле
    await callback.message.edit_text(
        "Введите название бонусного теста:",
        reply_markup=get_home_kb()
    )
    await state.set_state(BonusTestStates.enter_test_name)

# Регистрируем общие обработчики тестов
register_test_handlers(router, BonusTestStates, "bonus_test")

@router.callback_query(BonusTestStates.confirm_test, F.data == "confirm_test")
async def set_bonus_test_price(callback: CallbackQuery, state: FSMContext):
    """Переход к установке цены в монетах после сохранения в общем модуле"""
    logger.info("Вызван обработчик set_bonus_test_price")
    
    user_data = await state.get_data()
    test_name = user_data.get("test_name", "")
    questions = user_data.get("questions", [])
    time_limit = user_data.get("time_limit", 0)
    
    # Форматируем время
    time_text = f"{time_limit} сек."
    if time_limit >= 60:
        minutes = time_limit // 60
        seconds = time_limit % 60
        time_text = f"{minutes} мин."
        if seconds > 0:
            time_text += f" {seconds} сек."
    
    await callback.message.edit_text(
        f"🧪 Название теста: {test_name}\n"
        f"📋 Количество вопросов: {len(questions)}\n"
        f"⏱ Время на ответ: {time_text}\n\n"
        "Выберите цену в монетах для этого бонусного теста:",
        reply_markup=get_price_kb()
    )
    await state.set_state(BonusTestStates.enter_price)

@router.callback_query(BonusTestStates.enter_price, F.data.startswith("price_"))
async def process_price_selection(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора цены"""
    logger.info("Вызван обработчик process_price_selection")
    
    price_data = callback.data.replace("price_", "")
    
    if price_data == "custom":
        await callback.message.edit_text(
            "Введите цену в монетах (число):",
            reply_markup=get_home_kb()
        )
        return
    
    price = int(price_data)
    await state.update_data(price=price)
    await show_bonus_test_confirmation(callback, state)

@router.message(BonusTestStates.enter_price)
async def process_custom_price(message: Message, state: FSMContext):
    """Обработка ввода пользовательской цены"""
    logger.info("Вызван обработчик process_custom_price")
    
    try:
        price = int(message.text.strip())
        if price <= 0:
            await message.answer("Цена должна быть положительным числом. Попробуйте еще раз:")
            return
            
        await state.update_data(price=price)
        await show_bonus_test_confirmation(message, state)
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число:")

async def show_bonus_test_confirmation(message_or_callback, state: FSMContext):
    """Показ подтверждения создания бонусного теста"""
    user_data = await state.get_data()
    test_name = user_data.get("test_name", "")
    questions = user_data.get("questions", [])
    time_limit = user_data.get("time_limit", 0)
    price = user_data.get("price", 0)
    
    # Форматируем время
    time_text = f"{time_limit} сек."
    if time_limit >= 60:
        minutes = time_limit // 60
        seconds = time_limit % 60
        time_text = f"{minutes} мин."
        if seconds > 0:
            time_text += f" {seconds} сек."
    
    confirmation_text = (
        f"🧪 Бонусный тест готов к созданию:\n\n"
        f"📝 Название: {test_name}\n"
        f"📋 Количество вопросов: {len(questions)}\n"
        f"⏱ Время на ответ: {time_text}\n"
        f"💰 Цена: {price} монет\n\n"
        "Подтвердите создание бонусного теста:"
    )
    
    if hasattr(message_or_callback, 'message'):
        await message_or_callback.message.edit_text(
            confirmation_text,
            reply_markup=get_confirm_bonus_test_kb()
        )
    else:
        await message_or_callback.answer(
            confirmation_text,
            reply_markup=get_confirm_bonus_test_kb()
        )

@router.callback_query(BonusTestStates.enter_price, F.data == "confirm_bonus_test")
async def save_bonus_test(callback: CallbackQuery, state: FSMContext):
    """Сохранение бонусного теста"""
    logger.info("Вызван обработчик save_bonus_test")
    
    user_data = await state.get_data()
    test_name = user_data.get("test_name", "")
    price = user_data.get("price", 0)
    
    # Здесь должен быть код для сохранения бонусного теста в базу данных
    # с пометкой что это бонусный тест для магазина
    
    await callback.message.edit_text(
        f"✅ Бонусный тест '{test_name}' успешно создан!\n"
        f"💰 Цена: {price} монет\n\n"
        "Тест появится в каталоге бонусов у учеников.",
        reply_markup=get_bonus_test_management_kb()
    )
    await state.set_state(BonusTestStates.main)

@router.callback_query(BonusTestStates.enter_price, F.data == "edit_bonus_test")
async def edit_bonus_test(callback: CallbackQuery, state: FSMContext):
    """Редактирование бонусного теста"""
    logger.info("Вызван обработчик edit_bonus_test")
    
    await callback.message.edit_text(
        "Выберите цену в монетах для этого бонусного теста:",
        reply_markup=get_price_kb()
    )

@router.callback_query(BonusTestStates.enter_price, F.data == "cancel_bonus_test")
async def cancel_bonus_test(callback: CallbackQuery, state: FSMContext):
    """Отмена создания бонусного теста"""
    logger.info("Вызван обработчик cancel_bonus_test")
    
    await callback.message.edit_text(
        "❌ Создание бонусного теста отменено.",
        reply_markup=get_bonus_test_management_kb()
    )
    await state.set_state(BonusTestStates.main)

# Обработчики для удаления бонусных тестов
@router.callback_query(BonusTestStates.main, F.data == "delete_bonus_test")
async def show_bonus_tests_to_delete(callback: CallbackQuery, state: FSMContext):
    """Показ списка бонусных тестов для удаления"""
    logger.info("Вызван обработчик show_bonus_tests_to_delete")
    
    # В реальном приложении здесь будет запрос к базе данных
    tests_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧪 Тест по алканам - 100 монет", callback_data="delete_bonus_1")],
        [InlineKeyboardButton(text="🧪 Тест по изомерии - 150 монет", callback_data="delete_bonus_2")],
        *get_main_menu_back_button()
    ])
    
    await callback.message.edit_text(
        "Выберите бонусный тест для удаления:",
        reply_markup=tests_kb
    )
    await state.set_state(BonusTestStates.select_test_to_delete)

@router.callback_query(BonusTestStates.select_test_to_delete, F.data.startswith("delete_bonus_"))
async def confirm_delete_bonus_test(callback: CallbackQuery, state: FSMContext):
    """Подтверждение удаления бонусного теста"""
    logger.info("Вызван обработчик confirm_delete_bonus_test")
    
    test_id = callback.data.replace("delete_bonus_", "")
    await state.update_data(test_id=test_id)
    
    # В реальном приложении здесь будет запрос к базе данных
    test_name = "Тест по алканам" if test_id == "1" else "Тест по изомерии"
    
    await callback.message.edit_text(
        f"Вы действительно хотите удалить бонусный тест '{test_name}'?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Да, удалить", callback_data="confirm_delete_bonus")],
            [InlineKeyboardButton(text="❌ Нет, отмена", callback_data="cancel_delete_bonus")]
        ])
    )

@router.callback_query(F.data == "confirm_delete_bonus")
async def delete_bonus_test(callback: CallbackQuery, state: FSMContext):
    """Удаление бонусного теста"""
    logger.info("Вызван обработчик delete_bonus_test")
    
    # Здесь должен быть код для удаления бонусного теста из базы данных
    
    await callback.message.edit_text(
        "✅ Бонусный тест успешно удален!",
        reply_markup=get_bonus_test_management_kb()
    )
    await state.set_state(BonusTestStates.main)

@router.callback_query(F.data == "cancel_delete_bonus")
async def cancel_delete_bonus_test(callback: CallbackQuery, state: FSMContext):
    """Отмена удаления бонусного теста"""
    logger.info("Вызван обработчик cancel_delete_bonus_test")
    
    await show_bonus_tests_to_delete(callback, state)
