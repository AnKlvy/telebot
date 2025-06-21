from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from common.utils import check_if_id_in_callback_data
from ..keyboards.shop import get_shop_menu_kb, get_exchange_points_kb, get_back_to_shop_kb, get_bonus_catalog_kb, get_my_bonuses_kb, get_purchase_confirmation_kb, get_item_purchase_confirmation_kb
from database import StudentRepository, ShopItemRepository, StudentPurchaseRepository, BonusTestRepository, StudentBonusTestRepository, BonusQuestionRepository, BonusAnswerOptionRepository
from common.navigation import log
from common.quiz_registrator import register_quiz_handlers, send_next_question, cleanup_test_messages
import logging
import asyncio

class ShopStates(StatesGroup):
    main = State()
    exchange = State()
    catalog = State()
    my_bonuses = State()
    purchase_confirmation = State()  # Для бонусных тестов
    item_purchase_confirmation = State()  # Для обычных товаров (бонусных заданий)
    bonus_test_confirmation = State()
    bonus_test_in_progress = State()

router = Router()

# Регистрируем общие quiz обработчики для бонусных тестов
register_quiz_handlers(
    router=router,
    test_state=ShopStates.bonus_test_in_progress,
    poll_answer_handler=None,  # Используем стандартный обработчик
    timeout_handler=None,      # Используем стандартный обработчик
    finish_handler=None        # Будем передавать в send_next_question
)

@router.callback_query(F.data == "shop")
async def show_shop_menu(callback: CallbackQuery, state: FSMContext):
    """Показать меню магазина"""
    await log("show_shop_menu", "student", state)

    # Получаем студента по telegram_id
    student = await StudentRepository.get_by_telegram_id(callback.from_user.id)
    if not student:
        await callback.message.edit_text(
            "❌ Профиль студента не найден. Обратитесь к администратору.",
            reply_markup=get_back_to_shop_kb()
        )
        return

    # Получаем баланс студента
    balance = await StudentRepository.get_balance(student.id)
    points = balance["points"]
    coins = balance["coins"]

    await callback.message.edit_text(
        "🎉 Добро пожаловать в магазин!\n"
        "Здесь ты можешь обменять баллы на монеты и потратить их на бонусы.\n"
        "💰 У тебя сейчас:\n"
        f"Баллы: {points}\n"
        f"Монеты: {coins}",
        reply_markup=get_shop_menu_kb()
    )
    await state.set_state(ShopStates.main)

@router.callback_query(ShopStates.main, F.data == "exchange_points")
async def show_exchange_options(callback: CallbackQuery, state: FSMContext):
    """Показать варианты обмена баллов на монеты"""
    await log("show_exchange_options", "student", state)

    # Получаем текущий баланс студента
    student = await StudentRepository.get_by_telegram_id(callback.from_user.id)
    if not student:
        await callback.message.edit_text(
            "❌ Профиль студента не найден.",
            reply_markup=get_back_to_shop_kb()
        )
        return

    balance = await StudentRepository.get_balance(student.id)
    points = balance["points"]

    await callback.message.edit_text(
        f"Выбери, сколько баллов хочешь обменять на монеты:\n"
        f"💰 Доступно баллов: {points}",
        reply_markup=await get_exchange_points_kb(points)
    )
    await state.set_state(ShopStates.exchange)

@router.callback_query(ShopStates.exchange, F.data.startswith("exchange_"))
async def process_exchange(callback: CallbackQuery, state: FSMContext):
    """Обработать обмен баллов на монеты"""
    await log("process_exchange", "student", state)

    exchange_amount = int(callback.data.replace("exchange_", ""))

    # Получаем студента
    student = await StudentRepository.get_by_telegram_id(callback.from_user.id)
    if not student:
        await callback.message.edit_text(
            "❌ Профиль студента не найден.",
            reply_markup=get_back_to_shop_kb()
        )
        return

    # Проверяем баланс и выполняем обмен
    success = await StudentRepository.exchange_points_to_coins(student.id, exchange_amount)

    if success:
        # Получаем новый баланс
        balance = await StudentRepository.get_balance(student.id)
        new_points = balance["points"]
        new_coins = balance["coins"]

        await callback.message.edit_text(
            "✅ Успешно!\n"
            f"Списано: {exchange_amount} баллов\n"
            f"Начислено: {exchange_amount} монет\n"
            f"💼 Новый баланс: {new_points} баллов | {new_coins} монет",
            reply_markup=get_back_to_shop_kb()
        )
    else:
        await callback.message.edit_text(
            "❌ Недостаточно баллов для обмена!",
            reply_markup=get_back_to_shop_kb()
        )

@router.callback_query(ShopStates.main, F.data == "bonus_catalog")
async def show_bonus_catalog(callback: CallbackQuery, state: FSMContext):
    """Показать каталог бонусов"""
    await log("show_bonus_catalog", "student", state)

    # Получаем студента и его баланс
    student = await StudentRepository.get_by_telegram_id(callback.from_user.id)
    if not student:
        await callback.message.edit_text(
            "❌ Профиль студента не найден.",
            reply_markup=get_back_to_shop_kb()
        )
        return

    balance = await StudentRepository.get_balance(student.id)
    coins = balance["coins"]

    # Получаем активные товары из магазина
    shop_items = await ShopItemRepository.get_all_active()

    # Получаем бонусные тесты из базы данных
    bonus_tests = await BonusTestRepository.get_all()

    # Отладочная информация
    logging.info(f"Найдено товаров в магазине: {len(shop_items)}")
    logging.info(f"Найдено бонусных тестов: {len(bonus_tests)}")

    for item in shop_items:
        logging.info(f"Товар: {item.name}, тип: {item.item_type}, активен: {item.is_active}")

    # Получаем уже купленные товары студента
    purchased_items = await StudentPurchaseRepository.get_student_purchases(student.id)
    purchased_item_ids = {purchase.item_id for purchase in purchased_items}

    # Получаем уже купленные бонусные тесты студента
    purchased_bonus_tests = await StudentBonusTestRepository.get_student_bonus_tests(student.id)
    purchased_bonus_test_ids = {purchase.bonus_test_id for purchase in purchased_bonus_tests}

    # Объединяем товары и бонусные тесты
    all_items = []

    # Добавляем обычные товары (кроме статического "Бонусный тест" и уже купленных)
    for item in shop_items:
        if item.item_type != "bonus_test" and item.id not in purchased_item_ids:
            all_items.append({
                'type': 'shop_item',
                'id': item.id,
                'name': item.name,
                'price': item.price,
                'item_type': item.item_type
            })
            logging.info(f"Добавлен товар в каталог: {item.name}")

    # Добавляем бонусные тесты как товары (только не купленные)
    for test in bonus_tests:
        if test.id not in purchased_bonus_test_ids:
            question_count = len(test.questions) if test.questions else 0
            all_items.append({
                'type': 'bonus_test',
                'id': test.id,
                'name': f"{test.name} ({question_count} вопр.)",
                'price': test.price,
                'item_type': 'bonus_test'
            })
            logging.info(f"Добавлен бонусный тест в каталог: {test.name}")

    logging.info(f"Всего товаров в каталоге: {len(all_items)}")

    if not all_items:
        await callback.message.edit_text(
            "🛒 Каталог бонусов\n"
            "В данный момент товары недоступны.",
            reply_markup=get_back_to_shop_kb()
        )
    else:
        await callback.message.edit_text(
            f"🛒 Каталог бонусов\n"
            f"💰 У тебя: {coins} монет\n\n"
            "Выбери товар для покупки:",
            reply_markup=await get_bonus_catalog_kb(all_items, coins)
        )
    await state.set_state(ShopStates.catalog)

@router.callback_query(ShopStates.main, F.data == "my_bonuses")
async def show_my_bonuses(callback: CallbackQuery, state: FSMContext):
    """Показать мои бонусы"""
    await log("show_my_bonuses", "student", state)

    # Получаем студента
    student = await StudentRepository.get_by_telegram_id(callback.from_user.id)
    if not student:
        await callback.message.edit_text(
            "❌ Профиль студента не найден.",
            reply_markup=get_back_to_shop_kb()
        )
        return

    # Получаем обычные покупки студента
    purchases = await StudentPurchaseRepository.get_student_purchases(student.id)

    # Получаем покупки бонусных тестов
    bonus_test_purchases = await StudentBonusTestRepository.get_student_bonus_tests(student.id)

    if not purchases and not bonus_test_purchases:
        await callback.message.edit_text(
            "📦 Мои покупки\n"
            "У тебя пока нет приобретенных бонусов.",
            reply_markup=get_back_to_shop_kb()
        )
    else:
        await callback.message.edit_text(
            "📦 Мои покупки\n"
            "Выбери бонус для использования:",
            reply_markup=await get_my_bonuses_kb(purchases, bonus_test_purchases)
        )
    await state.set_state(ShopStates.my_bonuses)

@router.callback_query(ShopStates.catalog, F.data.startswith("buy_item_"))
async def show_item_purchase_confirmation(callback: CallbackQuery, state: FSMContext):
    """Показать подтверждение покупки обычного товара (бонусного задания)"""
    await log("show_item_purchase_confirmation", "student", state)

    item_id = int(callback.data.replace("buy_item_", ""))

    # Получаем студента
    student = await StudentRepository.get_by_telegram_id(callback.from_user.id)
    if not student:
        await callback.message.edit_text(
            "❌ Профиль студента не найден.",
            reply_markup=get_back_to_shop_kb()
        )
        return

    # Получаем товар
    item = await ShopItemRepository.get_by_id(item_id)
    if not item or not item.is_active:
        await callback.message.edit_text(
            "❌ Товар не найден или недоступен.",
            reply_markup=get_back_to_shop_kb()
        )
        return

    # Проверяем баланс
    balance = await StudentRepository.get_balance(student.id)
    if balance["coins"] < item.price:
        await callback.message.edit_text(
            f"❌ Недостаточно монет!\n"
            f"Нужно: {item.price} монет\n"
            f"У тебя: {balance['coins']} монет",
            reply_markup=get_back_to_shop_kb()
        )
        return

    # Проверяем, не покупал ли студент уже этот товар
    existing_purchase = await StudentPurchaseRepository.has_purchased_item(student.id, item.id)
    if existing_purchase:
        await callback.message.edit_text(
            f"⚠️ Ты уже покупал это бонусное задание!\n"
            f"Проверь раздел 'Мои бонусы'.",
            reply_markup=get_back_to_shop_kb()
        )
        return

    # Показываем подтверждение покупки
    await callback.message.edit_text(
        f"💳 Подтверждение покупки\n\n"
        f"🎁 {item.name}\n"
        f"📝 {item.description[:100]}{'...' if len(item.description or '') > 100 else ''}\n"
        f"💰 Стоимость: {item.price} монет\n\n"
        f"💼 Твой баланс: {balance['coins']} монет\n"
        f"💸 После покупки останется: {balance['coins'] - item.price} монет\n\n"
        f"❓ Подтвердить покупку?",
        reply_markup=get_item_purchase_confirmation_kb(item_id)
    )

    # Сохраняем данные для подтверждения
    await state.update_data(
        item_to_purchase_id=item_id,
        item_to_purchase_name=item.name,
        item_to_purchase_price=item.price
    )
    await state.set_state(ShopStates.item_purchase_confirmation)

@router.callback_query(ShopStates.item_purchase_confirmation, F.data.startswith("confirm_purchase_item_"))
async def confirm_item_purchase(callback: CallbackQuery, state: FSMContext):
    """Подтвердить покупку обычного товара (бонусного задания)"""
    await log("confirm_item_purchase", "student", state)

    item_id = int(callback.data.replace("confirm_purchase_item_", ""))

    # Получаем данные из состояния
    data = await state.get_data()
    stored_item_id = data.get("item_to_purchase_id")
    item_name = data.get("item_to_purchase_name", "Неизвестный товар")
    item_price = data.get("item_to_purchase_price", 0)

    # Проверяем соответствие ID
    if stored_item_id != item_id:
        await callback.message.edit_text(
            "❌ Ошибка: несоответствие данных товара.",
            reply_markup=get_back_to_shop_kb()
        )
        return

    # Получаем студента
    student = await StudentRepository.get_by_telegram_id(callback.from_user.id)
    if not student:
        await callback.message.edit_text(
            "❌ Профиль студента не найден.",
            reply_markup=get_back_to_shop_kb()
        )
        return

    # Получаем товар
    item = await ShopItemRepository.get_by_id(item_id)
    if not item or not item.is_active:
        await callback.message.edit_text(
            "❌ Товар не найден или недоступен.",
            reply_markup=get_back_to_shop_kb()
        )
        return

    # Повторно проверяем баланс (на случай изменений)
    balance = await StudentRepository.get_balance(student.id)
    if balance["coins"] < item.price:
        await callback.message.edit_text(
            f"❌ Недостаточно монет!\n"
            f"Нужно: {item.price} монет\n"
            f"У тебя: {balance['coins']} монет",
            reply_markup=get_back_to_shop_kb()
        )
        return

    # Повторно проверяем, не покупал ли студент уже этот товар
    existing_purchase = await StudentPurchaseRepository.has_purchased_item(student.id, item.id)
    if existing_purchase:
        await callback.message.edit_text(
            f"⚠️ Ты уже покупал это бонусное задание!\n"
            f"Проверь раздел 'Мои бонусы'.",
            reply_markup=get_back_to_shop_kb()
        )
        return

    # Выполняем покупку
    success = await StudentRepository.spend_coins(student.id, item.price)
    if success:
        # Создаем запись о покупке
        await StudentPurchaseRepository.create_purchase(student.id, item.id, item.price)

        # Получаем новый баланс
        new_balance = await StudentRepository.get_balance(student.id)

        await callback.message.edit_text(
            f"✅ Покупка успешна!\n"
            f"Куплено: {item.name}\n"
            f"Потрачено: {item.price} монет\n"
            f"💰 Осталось монет: {new_balance['coins']}\n\n"
            f"🎯 Бонусное задание доступно в разделе 'Мои бонусы'",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🛒 Вернуться к каталогу", callback_data="bonus_catalog")],
                [InlineKeyboardButton(text="📦 Мои бонусы", callback_data="my_bonuses")],
                [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
            ])
        )
    else:
        await callback.message.edit_text(
            "❌ Ошибка при покупке. Попробуйте позже.",
            reply_markup=get_back_to_shop_kb()
        )

@router.callback_query(ShopStates.catalog, F.data.startswith("buy_bonus_"))
async def show_bonus_test_purchase_confirmation(callback: CallbackQuery, state: FSMContext):
    """Показать подтверждение покупки бонусного теста"""
    await log("show_bonus_test_purchase_confirmation", "student", state)

    test_id = int(callback.data.replace("buy_bonus_", ""))

    # Получаем студента
    student = await StudentRepository.get_by_telegram_id(callback.from_user.id)
    if not student:
        await callback.message.edit_text(
            "❌ Профиль студента не найден.",
            reply_markup=get_back_to_shop_kb()
        )
        return

    # Получаем бонусный тест
    bonus_test = await BonusTestRepository.get_by_id(test_id)
    if not bonus_test:
        await callback.message.edit_text(
            "❌ Бонусный тест не найден.",
            reply_markup=get_back_to_shop_kb()
        )
        return

    # Проверяем баланс
    balance = await StudentRepository.get_balance(student.id)
    if balance["coins"] < bonus_test.price:
        await callback.message.edit_text(
            f"❌ Недостаточно монет!\n"
            f"Нужно: {bonus_test.price} монет\n"
            f"У тебя: {balance['coins']} монет",
            reply_markup=get_back_to_shop_kb()
        )
        return

    # Проверяем, не покупал ли студент уже этот тест
    already_purchased = await StudentBonusTestRepository.has_purchased_test(student.id, bonus_test.id)
    if already_purchased:
        await callback.message.edit_text(
            f"⚠️ Ты уже покупал этот бонусный тест!\n"
            f"Проверь раздел 'Мои бонусы'.",
            reply_markup=get_back_to_shop_kb()
        )
        return

    # Показываем подтверждение покупки
    question_count = len(bonus_test.questions) if bonus_test.questions else 0

    await callback.message.edit_text(
        f"💳 Подтверждение покупки\n\n"
        f"🧪 {bonus_test.name}\n"
        f"📊 Количество вопросов: {question_count}\n"
        f"💰 Стоимость: {bonus_test.price} монет\n\n"
        f"💼 Твой баланс: {balance['coins']} монет\n"
        f"💸 После покупки останется: {balance['coins'] - bonus_test.price} монет\n\n"
        f"❓ Подтвердить покупку?",
        reply_markup=get_purchase_confirmation_kb(test_id)
    )

    # Сохраняем данные для подтверждения
    await state.update_data(
        test_to_purchase_id=test_id,
        test_to_purchase_name=bonus_test.name,
        test_to_purchase_price=bonus_test.price
    )
    await state.set_state(ShopStates.purchase_confirmation)

@router.callback_query(ShopStates.purchase_confirmation, F.data.startswith("confirm_purchase_bonus_"))
async def confirm_bonus_test_purchase(callback: CallbackQuery, state: FSMContext):
    """Подтвердить покупку бонусного теста"""
    await log("confirm_bonus_test_purchase", "student", state)

    test_id = int(callback.data.replace("confirm_purchase_bonus_", ""))

    # Получаем данные из состояния
    data = await state.get_data()
    stored_test_id = data.get("test_to_purchase_id")
    test_name = data.get("test_to_purchase_name", "Неизвестный тест")
    test_price = data.get("test_to_purchase_price", 0)

    # Проверяем соответствие ID
    if stored_test_id != test_id:
        await callback.message.edit_text(
            "❌ Ошибка: несоответствие данных теста.",
            reply_markup=get_back_to_shop_kb()
        )
        return

    # Получаем студента
    student = await StudentRepository.get_by_telegram_id(callback.from_user.id)
    if not student:
        await callback.message.edit_text(
            "❌ Профиль студента не найден.",
            reply_markup=get_back_to_shop_kb()
        )
        return

    # Получаем бонусный тест
    bonus_test = await BonusTestRepository.get_by_id(test_id)
    if not bonus_test:
        await callback.message.edit_text(
            "❌ Бонусный тест не найден.",
            reply_markup=get_back_to_shop_kb()
        )
        return

    # Повторно проверяем баланс (на случай изменений)
    balance = await StudentRepository.get_balance(student.id)
    if balance["coins"] < bonus_test.price:
        await callback.message.edit_text(
            f"❌ Недостаточно монет!\n"
            f"Нужно: {bonus_test.price} монет\n"
            f"У тебя: {balance['coins']} монет",
            reply_markup=get_back_to_shop_kb()
        )
        return

    # Повторно проверяем, не покупал ли студент уже этот тест
    already_purchased = await StudentBonusTestRepository.has_purchased_test(student.id, bonus_test.id)
    if already_purchased:
        await callback.message.edit_text(
            f"⚠️ Ты уже покупал этот бонусный тест!\n"
            f"Проверь раздел 'Мои бонусы'.",
            reply_markup=get_back_to_shop_kb()
        )
        return

    # Выполняем покупку
    success = await StudentRepository.spend_coins(student.id, bonus_test.price)
    if success:
        # Создаем запись о покупке бонусного теста
        await StudentBonusTestRepository.create_purchase(student.id, bonus_test.id, bonus_test.price)

        # Получаем новый баланс
        new_balance = await StudentRepository.get_balance(student.id)

        question_count = len(bonus_test.questions) if bonus_test.questions else 0

        await callback.message.edit_text(
            f"✅ Покупка успешна!\n"
            f"Куплено: {bonus_test.name}\n"
            f"Вопросов: {question_count}\n"
            f"Потрачено: {bonus_test.price} монет\n"
            f"💰 Осталось монет: {new_balance['coins']}\n\n"
            f"🎯 Бонусный тест доступен в разделе 'Мои бонусы'",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🛒 Вернуться к каталогу", callback_data="bonus_catalog")],
                [InlineKeyboardButton(text="📦 Мои бонусы", callback_data="my_bonuses")],
                [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
            ])
        )
    else:
        await callback.message.edit_text(
            "❌ Ошибка при покупке. Попробуйте позже.",
            reply_markup=get_back_to_shop_kb()
        )

@router.callback_query(ShopStates.purchase_confirmation, F.data == "cancel_purchase")
async def cancel_bonus_test_purchase(callback: CallbackQuery, state: FSMContext):
    """Отменить покупку бонусного теста"""
    await log("cancel_bonus_test_purchase", "student", state)

    await callback.message.edit_text(
        "❌ Покупка отменена",
        reply_markup=get_back_to_shop_kb()
    )
    await state.set_state(ShopStates.main)

@router.callback_query(ShopStates.item_purchase_confirmation, F.data == "cancel_purchase")
async def cancel_item_purchase(callback: CallbackQuery, state: FSMContext):
    """Отменить покупку обычного товара"""
    await log("cancel_item_purchase", "student", state)

    await callback.message.edit_text(
        "❌ Покупка отменена",
        reply_markup=get_back_to_shop_kb()
    )
    await state.set_state(ShopStates.main)

@router.callback_query(F.data.startswith("no_coins_"))
async def handle_insufficient_coins(callback: CallbackQuery, state: FSMContext):
    """Обработать случай недостатка монет"""
    await callback.answer("❌ Недостаточно монет для покупки!", show_alert=True)

@router.callback_query(F.data == "no_points")
async def handle_no_points(callback: CallbackQuery, state: FSMContext):
    """Обработать случай отсутствия баллов"""
    await callback.answer("❌ Недостаточно баллов для обмена!", show_alert=True)

@router.callback_query(F.data.startswith("use_bonus_") & ~F.data.startswith("use_bonus_test_"))
async def use_bonus_item(callback: CallbackQuery, state: FSMContext):
    """Использовать бонусное задание (текстовое)"""
    await log("use_bonus_item", "student", state)

    # Проверяем, что это не бонусный тест
    if callback.data.startswith("use_bonus_test_"):
        return  # Пропускаем, это должен обработать другой обработчик

    try:
        # Простое извлечение ID из callback_data
        purchase_id = int(callback.data.replace("use_bonus_", ""))
    except (ValueError, TypeError) as e:
        logging.error(f"Ошибка парсинга callback_data для обычного товара: '{callback.data}', ошибка: {e}")
        await callback.message.edit_text(
            f"❌ Ошибка: неверный ID покупки.\nCallback data: {callback.data}",
            reply_markup=get_back_to_shop_kb()
        )
        return

    # Получаем покупку
    purchase = await StudentPurchaseRepository.get_purchase_by_id(purchase_id)
    if not purchase:
        await callback.message.edit_text(
            "❌ Покупка не найдена.",
            reply_markup=get_back_to_shop_kb()
        )
        return

    # Проверяем, что это покупка текущего пользователя
    student = await StudentRepository.get_by_telegram_id(callback.from_user.id)
    if not student or purchase.student_id != student.id:
        await callback.message.edit_text(
            "❌ Это не ваша покупка.",
            reply_markup=get_back_to_shop_kb()
        )
        return

    # Показываем реальный контент из базы данных
    content = f"🎁 {purchase.item.name}\n\n"

    # Добавляем описание если есть
    if purchase.item.description:
        content += f"📝 {purchase.item.description}\n\n"

    # Добавляем основной контент из базы данных
    if purchase.item.content:
        content += f"{purchase.item.content}\n\n"

    # Добавляем информацию о файле если есть
    if purchase.item.file_path:
        content += f"📎 Файл: {purchase.item.file_path}\n\n"

    # Добавляем контактную информацию если есть
    if purchase.item.contact_info:
        content += f"📞 Контакты:\n{purchase.item.contact_info}\n\n"

    # Добавляем уникальный код для отслеживания
    if purchase.item.item_type in ["money", "other"]:
        content += f"🎫 Ваш код: {purchase.item.item_type.upper()}{purchase.id}"

    # Отмечаем как использованный
    await StudentPurchaseRepository.mark_as_used(purchase.id)

    await callback.message.edit_text(
        content,
        reply_markup=get_back_to_shop_kb()
    )

@router.callback_query(F.data.startswith("use_bonus_test_"))
async def use_bonus_test(callback: CallbackQuery, state: FSMContext):
    """Использовать бонусный тест"""
    await log("use_bonus_test", "student", state)

    try:
        purchase_id = int(callback.data.replace("use_bonus_test_", ""))
    except (ValueError, TypeError) as e:
        logging.error(f"Ошибка парсинга callback_data для бонусного теста: '{callback.data}', ошибка: {e}")
        await callback.message.edit_text(
            f"❌ Ошибка: неверный ID покупки бонусного теста.\nCallback data: {callback.data}",
            reply_markup=get_back_to_shop_kb()
        )
        return

    # Получаем покупку бонусного теста
    purchase = await StudentBonusTestRepository.get_purchase_by_id(purchase_id)
    if not purchase:
        await callback.message.edit_text(
            "❌ Покупка не найдена.",
            reply_markup=get_back_to_shop_kb()
        )
        return

    # Проверяем, что это покупка текущего пользователя
    student = await StudentRepository.get_by_telegram_id(callback.from_user.id)
    if not student or purchase.student_id != student.id:
        await callback.message.edit_text(
            "❌ Это не ваша покупка.",
            reply_markup=get_back_to_shop_kb()
        )
        return

    # Получаем вопросы теста
    bonus_test = purchase.bonus_test
    questions = await BonusQuestionRepository().get_by_bonus_test(bonus_test.id)

    if not questions:
        await callback.message.edit_text(
            f"❌ В тесте '{bonus_test.name}' нет вопросов.",
            reply_markup=get_back_to_shop_kb()
        )
        return

    question_count = len(questions)

    # Показываем информацию о тесте с кнопкой запуска
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Начать тест", callback_data=f"start_bonus_test_{purchase_id}")],
        [InlineKeyboardButton(text="🔙 Назад к бонусам", callback_data="my_bonuses")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
    ])

    # Определяем диапазон времени для вопросов
    time_limits = [q.time_limit for q in questions]
    min_time = min(time_limits)
    max_time = max(time_limits)

    if min_time == max_time:
        time_info = f"⏱️ Время на вопрос: {min_time} секунд"
    else:
        time_info = f"⏱️ Время на вопрос: {min_time}-{max_time} секунд"

    await callback.message.edit_text(
        f"🧪 {bonus_test.name}\n\n"
        f"📊 Количество вопросов: {question_count}\n"
        f"{time_info}\n"
        f"💰 Стоимость: {purchase.price_paid} монет\n\n"
        f"🎯 Это бонусный тест для дополнительной практики.\n"
        f"Результаты не сохраняются, можно проходить сколько угодно раз!",
        reply_markup=keyboard
    )

    # Сохраняем данные для запуска теста
    await state.update_data(
        bonus_test_purchase_id=purchase_id,
        bonus_test_id=bonus_test.id,
        bonus_test_name=bonus_test.name
    )
    await state.set_state(ShopStates.bonus_test_confirmation)

@router.callback_query(ShopStates.bonus_test_confirmation, F.data.startswith("start_bonus_test_"))
async def start_bonus_test(callback: CallbackQuery, state: FSMContext):
    """Начать прохождение бонусного теста"""
    await log("start_bonus_test", "student", state)

    purchase_id = int(callback.data.replace("start_bonus_test_", ""))

    # Получаем данные из состояния
    data = await state.get_data()
    bonus_test_id = data.get("bonus_test_id")

    if not bonus_test_id:
        await callback.answer("❌ Ошибка: данные теста не найдены", show_alert=True)
        return

    # Получаем вопросы теста
    questions = await BonusQuestionRepository().get_by_bonus_test(bonus_test_id)

    if not questions:
        await callback.answer("❌ В тесте нет вопросов", show_alert=True)
        return

    # Получаем ID студента
    student = await StudentRepository.get_by_telegram_id(callback.from_user.id)
    if not student:
        await callback.answer("❌ Студент не найден", show_alert=True)
        return

    # Инициализируем состояние теста
    test_data = {
        'student_id': student.id,
        'user_id': callback.from_user.id,
        'bonus_test_id': bonus_test_id,  # Важно: сохраняем ID бонусного теста
        'score': 0,
        'q_index': 0,
        'total_questions': len(questions),
        'question_results': [],
        'messages_to_delete': [],  # Список сообщений для удаления после теста
        'questions': [{
            'id': q.id,
            'text': q.text,
            'photo_path': q.photo_path,
            'time_limit': q.time_limit,
            'microtopic_number': None  # У бонусных тестов нет микротем
        } for q in questions]
    }

    await state.update_data(**test_data)
    await state.set_state(ShopStates.bonus_test_in_progress)
    await callback.answer()
    await send_next_question(callback.message.chat.id, state, callback.bot, finish_bonus_test)


async def finish_bonus_test(chat_id, state: FSMContext, bot: Bot):
    """Завершение бонусного теста (без сохранения результатов)"""
    await log("finish_bonus_test", "student", state)

    data = await state.get_data()
    score = data.get("score", 0)
    total_questions = data.get("total_questions", 0)
    bonus_test_name = data.get("bonus_test_name", "Бонусный тест")

    # Формируем сообщение с результатами
    percentage = round((score / total_questions) * 100, 1) if total_questions > 0 else 0

    if score == total_questions:
        result_emoji = "🎉"
        result_text = "Отлично! Все ответы правильные!"
    elif percentage >= 80:
        result_emoji = "👏"
        result_text = "Хорошо! Почти все правильно!"
    elif percentage >= 60:
        result_emoji = "👍"
        result_text = "Неплохо! Есть над чем поработать"
    else:
        result_emoji = "📚"
        result_text = "Стоит повторить материал"

    message = (
        f"{result_emoji} Бонусный тест завершен!\n\n"
        f"🧪 {bonus_test_name}\n"
        f"📊 Результат: {score}/{total_questions} ({percentage}%)\n"
        f"{result_text}\n\n"
        f"💡 Можешь пройти тест еще раз для закрепления!"
    )

    # Кнопки для дальнейших действий
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Пройти еще раз", callback_data=f"use_bonus_test_{data.get('bonus_test_purchase_id')}")],
        [InlineKeyboardButton(text="📦 Мои бонусы", callback_data="my_bonuses")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
    ])

    await bot.send_message(chat_id, message, reply_markup=keyboard)

    # Удаляем все сообщения теста после небольшой задержки
    await asyncio.sleep(1)
    await cleanup_test_messages(chat_id, data, bot)

    # Возвращаемся в состояние магазина
    await state.set_state(ShopStates.my_bonuses)


@router.callback_query(ShopStates.purchase_confirmation, F.data == "bonus_catalog")
async def back_to_catalog_from_confirmation(callback: CallbackQuery, state: FSMContext):
    """Вернуться к каталогу из подтверждения покупки"""
    await show_bonus_catalog(callback, state)

@router.callback_query(ShopStates.item_purchase_confirmation, F.data == "bonus_catalog")
async def back_to_catalog_from_item_confirmation(callback: CallbackQuery, state: FSMContext):
    """Вернуться к каталогу из подтверждения покупки товара"""
    await show_bonus_catalog(callback, state)

@router.callback_query(F.data == "my_bonuses")
async def handle_my_bonuses_callback(callback: CallbackQuery, state: FSMContext):
    """Обработчик для кнопки 'Мои бонусы'"""
    await show_my_bonuses(callback, state)


@router.callback_query(F.data == "back_to_shop")
async def back_to_shop(callback: CallbackQuery, state: FSMContext):
    """Вернуться в меню магазина"""
    await show_shop_menu(callback, state)

@router.callback_query(F.data == "bonus_catalog")
async def back_to_catalog_universal(callback: CallbackQuery, state: FSMContext):
    """Универсальный обработчик возврата к каталогу"""
    await show_bonus_catalog(callback, state)