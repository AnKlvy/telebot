from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from ..keyboards.shop import get_shop_menu_kb, get_exchange_points_kb, get_back_to_shop_kb, get_bonus_catalog_kb, get_my_bonuses_kb
from database import StudentRepository, ShopItemRepository, StudentPurchaseRepository, BonusTestRepository, StudentBonusTestRepository
from common.navigation import log

router = Router()

class ShopStates(StatesGroup):
    main = State()
    exchange = State()
    catalog = State()
    my_bonuses = State()

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

    # Объединяем товары и бонусные тесты
    all_items = []

    # Добавляем обычные товары (кроме статического "Бонусный тест")
    for item in shop_items:
        if item.item_type != "bonus_test":
            all_items.append({
                'type': 'shop_item',
                'id': item.id,
                'name': item.name,
                'price': item.price,
                'item_type': item.item_type
            })

    # Добавляем бонусные тесты как товары
    for test in bonus_tests:
        question_count = len(test.questions) if test.questions else 0
        all_items.append({
            'type': 'bonus_test',
            'id': test.id,
            'name': f"{test.name} ({question_count} вопр.)",
            'price': test.price,
            'item_type': 'bonus_test'
        })

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
async def process_shop_item_purchase(callback: CallbackQuery, state: FSMContext):
    """Обработать покупку обычного товара из магазина"""
    await log("process_shop_item_purchase", "student", state)

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
            f"💰 Осталось монет: {new_balance['coins']}",
            reply_markup=get_back_to_shop_kb()
        )
    else:
        await callback.message.edit_text(
            "❌ Ошибка при покупке. Попробуйте позже.",
            reply_markup=get_back_to_shop_kb()
        )

@router.callback_query(ShopStates.catalog, F.data.startswith("buy_bonus_"))
async def process_bonus_test_purchase(callback: CallbackQuery, state: FSMContext):
    """Обработать покупку бонусного теста"""
    await log("process_bonus_test_purchase", "student", state)

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
            reply_markup=get_back_to_shop_kb()
        )
    else:
        await callback.message.edit_text(
            "❌ Ошибка при покупке. Попробуйте позже.",
            reply_markup=get_back_to_shop_kb()
        )

@router.callback_query(F.data.startswith("no_coins_"))
async def handle_insufficient_coins(callback: CallbackQuery, state: FSMContext):
    """Обработать случай недостатка монет"""
    await callback.answer("❌ Недостаточно монет для покупки!", show_alert=True)

@router.callback_query(F.data == "no_points")
async def handle_no_points(callback: CallbackQuery, state: FSMContext):
    """Обработать случай отсутствия баллов"""
    await callback.answer("❌ Недостаточно баллов для обмена!", show_alert=True)

@router.callback_query(F.data.startswith("use_bonus_"))
async def use_bonus_item(callback: CallbackQuery, state: FSMContext):
    """Использовать бонусное задание (текстовое)"""
    await log("use_bonus_item", "student", state)

    purchase_id = int(callback.data.replace("use_bonus_", ""))

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

    # Показываем бонусное задание в зависимости от типа
    if purchase.item.item_type == "pdf":
        content = f"📘 {purchase.item.name}\n\n"
        content += f"📝 {purchase.item.description}\n\n"
        content += "📄 Содержание PDF:\n"
        content += "• Разбор типичных ошибок\n"
        content += "• Примеры правильных решений\n"
        content += "• Рекомендации по подготовке\n"
        content += "• Дополнительные материалы\n\n"
        content += "💡 Изучи материал внимательно для лучшей подготовки!"

    elif purchase.item.item_type == "money":
        content = f"💰 {purchase.item.name}\n\n"
        content += f"🎉 Поздравляем! Вы выиграли денежный приз!\n\n"
        content += f"💵 Сумма: 5000 тенге\n"
        content += f"📞 Для получения приза свяжитесь с администратором\n"
        content += f"📱 Telegram: @admin\n\n"
        content += f"✅ Ваш промокод: BONUS{purchase.id}"

    elif purchase.item.item_type == "other":
        content = f"🎁 {purchase.item.name}\n\n"
        content += f"👨‍🏫 {purchase.item.description}\n\n"
        content += f"📅 Для записи на консультацию:\n"
        content += f"• Выберите удобное время\n"
        content += f"• Подготовьте вопросы заранее\n"
        content += f"• Консультация проходит онлайн\n\n"
        content += f"📞 Свяжитесь с преподавателем: @teacher\n"
        content += f"🎫 Ваш код бронирования: CONS{purchase.id}"

    else:
        content = f"🎁 {purchase.item.name}\n\n{purchase.item.description}"

    # Отмечаем как использованный
    await StudentPurchaseRepository.mark_as_used(purchase.id)

    await callback.message.edit_text(
        content,
        reply_markup=get_back_to_shop_kb()
    )

@router.callback_query(F.data.startswith("use_bonus_test_"))
async def use_bonus_test(callback: CallbackQuery, state: FSMContext):
    """Использовать бонусный тест (пока заглушка)"""
    await log("use_bonus_test", "student", state)

    purchase_id = int(callback.data.replace("use_bonus_test_", ""))

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

    # Пока показываем информацию о тесте (позже будет запуск теста)
    question_count = len(purchase.bonus_test.questions) if purchase.bonus_test.questions else 0

    await callback.message.edit_text(
        f"🧪 {purchase.bonus_test.name}\n\n"
        f"📊 Количество вопросов: {question_count}\n"
        f"⏱️ Время на вопрос: 30 секунд\n"
        f"💰 Стоимость: {purchase.price_paid} монет\n\n"
        f"🚧 Запуск бонусного теста будет реализован позже.\n"
        f"Пока что тест доступен для просмотра.",
        reply_markup=get_back_to_shop_kb()
    )

@router.callback_query(F.data == "back_to_shop")
async def back_to_shop(callback: CallbackQuery, state: FSMContext):
    """Вернуться в меню магазина"""
    await show_shop_menu(callback, state)