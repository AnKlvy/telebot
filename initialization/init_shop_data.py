"""
Инициализация данных магазина
"""
import asyncio
from database import (
    init_database, ShopItemRepository, BonusTestRepository,
    BonusQuestionRepository, BonusAnswerOptionRepository,
    StudentRepository, StudentBonusTestRepository
)


async def init_shop_items():
    """Создание товаров магазина и бонусных тестов"""
    print("Инициализация товаров магазина...")

    # Проверяем, есть ли товары в базе
    existing_items = await ShopItemRepository.get_all_active()

    if not existing_items:
        print("Создаем товары магазина...")

        # Создаем обычные товары
        pdf_item = await ShopItemRepository.create(
            name='PDF материалы по математике',
            description='Дополнительные материалы для подготовки к ЕНТ',
            price=50,
            item_type='pdf'
        )
        await ShopItemRepository.update_content(
            pdf_item.id,
            content='📄 Содержание материалов:\n• Разбор типичных ошибок\n• Примеры правильных решений\n• Рекомендации по подготовке\n• Дополнительные материалы\n\n💡 Изучи материал внимательно для лучшей подготовки!',
            file_path='https://example.com/math_materials.pdf'
        )
        print(f"   ✅ Создан товар: {pdf_item.name}")

        money_item = await ShopItemRepository.create(
            name='Денежный приз 5000 тенге',
            description='Денежный приз за отличную учебу',
            price=200,
            item_type='money'
        )
        await ShopItemRepository.update_content(
            money_item.id,
            content='🎉 Поздравляем! Вы выиграли денежный приз!\n\n💵 Сумма: 5000 тенге\n📞 Для получения приза свяжитесь с администратором',
            contact_info='Telegram: @admin_edubot\nТелефон: +7 777 123 45 67\nEmail: admin@schoolpro.kz'
        )
        print(f"   ✅ Создан товар: {money_item.name}")

        consultation_item = await ShopItemRepository.create(
            name='Консультация с преподавателем',
            description='Индивидуальная консультация по предмету',
            price=100,
            item_type='other'
        )
        await ShopItemRepository.update_content(
            consultation_item.id,
            content='👨‍🏫 Индивидуальная консультация с опытным преподавателем\n\n📅 Условия консультации:\n• Выберите удобное время\n• Подготовьте вопросы заранее\n• Консультация проходит онлайн\n• Длительность: 60 минут',
            contact_info='Telegram: @teacher_math\nТелефон: +7 777 987 65 43\nEmail: teacher@schoolpro.kz\n\nДля записи напишите в Telegram с указанием кода покупки'
        )
        print(f"   ✅ Создан товар: {consultation_item.name}")
    else:
        print(f"В магазине уже есть {len(existing_items)} товаров")

    # Создаем бонусные тесты
    await init_bonus_tests()

    # Создаем покупки для Андрея Климова
    await init_andrey_purchases()

    print("Инициализация товаров завершена.")


async def init_bonus_tests():
    """Создание бонусных тестов"""
    print("Создание бонусных тестов...")

    # Проверяем, есть ли бонусные тесты
    existing_tests = await BonusTestRepository.get_all()

    if not existing_tests:
        # Создаем бонусный тест по математике
        math_test = await BonusTestRepository.create(
            name='Тест по математике',
            price=75
        )
        print(f"   ✅ Создан бонусный тест: {math_test.name}")

        # Создаем вопросы для теста
        question_repo = BonusQuestionRepository()

        # Вопрос 1 (легкий - больше времени)
        question1 = await question_repo.create(
            bonus_test_id=math_test.id,
            text='Сколько будет 2 + 2?',
            time_limit=20
        )

        options1 = [
            {'text': '3', 'is_correct': False},
            {'text': '4', 'is_correct': True},
            {'text': '5', 'is_correct': False},
            {'text': '6', 'is_correct': False}
        ]
        await BonusAnswerOptionRepository.create_multiple(question1.id, options1)
        print(f"   ✅ Создан вопрос: {question1.text} (20 сек)")

        # Вопрос 2 (средний)
        question2 = await question_repo.create(
            bonus_test_id=math_test.id,
            text='Чему равен квадрат числа 5?',
            time_limit=35
        )

        options2 = [
            {'text': '10', 'is_correct': False},
            {'text': '15', 'is_correct': False},
            {'text': '25', 'is_correct': True},
            {'text': '30', 'is_correct': False}
        ]
        await BonusAnswerOptionRepository.create_multiple(question2.id, options2)
        print(f"   ✅ Создан вопрос: {question2.text} (35 сек)")

        # Вопрос 3 (сложный - больше времени)
        question3 = await question_repo.create(
            bonus_test_id=math_test.id,
            text='Решите уравнение: x + 7 = 12',
            time_limit=50
        )

        options3 = [
            {'text': 'x = 3', 'is_correct': False},
            {'text': 'x = 4', 'is_correct': False},
            {'text': 'x = 5', 'is_correct': True},
            {'text': 'x = 6', 'is_correct': False}
        ]
        await BonusAnswerOptionRepository.create_multiple(question3.id, options3)
        print(f"   ✅ Создан вопрос: {question3.text}")

        # Создаем бонусный тест по физике
        physics_test = await BonusTestRepository.create(
            name='Тест по физике',
            price=80
        )
        print(f"   ✅ Создан бонусный тест: {physics_test.name}")

        # Вопрос по физике 1
        physics_question1 = await question_repo.create(
            bonus_test_id=physics_test.id,
            text='Какая единица измерения силы в системе СИ?',
            time_limit=25
        )

        physics_options1 = [
            {'text': 'Джоуль', 'is_correct': False},
            {'text': 'Ньютон', 'is_correct': True},
            {'text': 'Ватт', 'is_correct': False},
            {'text': 'Паскаль', 'is_correct': False}
        ]
        await BonusAnswerOptionRepository.create_multiple(physics_question1.id, physics_options1)
        print(f"   ✅ Создан вопрос: {physics_question1.text} (25 сек)")

        # Вопрос по физике 2
        physics_question2 = await question_repo.create(
            bonus_test_id=physics_test.id,
            text='Чему равна скорость света в вакууме?',
            time_limit=40
        )

        physics_options2 = [
            {'text': '300 000 км/с', 'is_correct': True},
            {'text': '150 000 км/с', 'is_correct': False},
            {'text': '500 000 км/с', 'is_correct': False},
            {'text': '200 000 км/с', 'is_correct': False}
        ]
        await BonusAnswerOptionRepository.create_multiple(physics_question2.id, physics_options2)
        print(f"   ✅ Создан вопрос: {physics_question2.text}")

    else:
        print(f"Бонусные тесты уже существуют: {len(existing_tests)} шт.")

        # Добавляем недостающие вопросы к существующим тестам
        await add_missing_questions_to_existing_tests()


async def add_missing_questions_to_existing_tests():
    """Добавляем недостающие вопросы к существующим тестам"""
    print("Проверка и добавление недостающих вопросов...")

    # Получаем все тесты
    tests = await BonusTestRepository.get_all()
    question_repo = BonusQuestionRepository()

    for test in tests:
        current_questions = len(test.questions) if test.questions else 0

        if test.name == 'Тест по математике' and current_questions < 3:
            print(f"   Добавляем вопросы к тесту '{test.name}' (текущих: {current_questions})")

            if current_questions < 2:
                # Добавляем второй вопрос
                question2 = await question_repo.create(
                    bonus_test_id=test.id,
                    text='Чему равен квадрат числа 5?',
                    time_limit=35
                )
                options2 = [
                    {'text': '10', 'is_correct': False},
                    {'text': '15', 'is_correct': False},
                    {'text': '25', 'is_correct': True},
                    {'text': '30', 'is_correct': False}
                ]
                await BonusAnswerOptionRepository.create_multiple(question2.id, options2)
                print(f"   ✅ Добавлен вопрос: {question2.text} (35 сек)")

            if current_questions < 3:
                # Добавляем третий вопрос
                question3 = await question_repo.create(
                    bonus_test_id=test.id,
                    text='Решите уравнение: x + 7 = 12',
                    time_limit=50
                )
                options3 = [
                    {'text': 'x = 3', 'is_correct': False},
                    {'text': 'x = 4', 'is_correct': False},
                    {'text': 'x = 5', 'is_correct': True},
                    {'text': 'x = 6', 'is_correct': False}
                ]
                await BonusAnswerOptionRepository.create_multiple(question3.id, options3)
                print(f"   ✅ Добавлен вопрос: {question3.text}")

    # Создаем дополнительные тесты, если их мало
    if len(tests) < 2:
        print("   Создаем дополнительный тест по физике...")
        physics_test = await BonusTestRepository.create(
            name='Тест по физике',
            price=80
        )

        # Вопрос по физике 1
        physics_question1 = await question_repo.create(
            bonus_test_id=physics_test.id,
            text='Какая единица измерения силы в системе СИ?',
            time_limit=30
        )
        physics_options1 = [
            {'text': 'Джоуль', 'is_correct': False},
            {'text': 'Ньютон', 'is_correct': True},
            {'text': 'Ватт', 'is_correct': False},
            {'text': 'Паскаль', 'is_correct': False}
        ]
        await BonusAnswerOptionRepository.create_multiple(physics_question1.id, physics_options1)
        print(f"   ✅ Создан тест и вопрос: {physics_question1.text}")

        # Вопрос по физике 2
        physics_question2 = await question_repo.create(
            bonus_test_id=physics_test.id,
            text='Чему равна скорость света в вакууме?',
            time_limit=30
        )
        physics_options2 = [
            {'text': '300 000 км/с', 'is_correct': True},
            {'text': '150 000 км/с', 'is_correct': False},
            {'text': '500 000 км/с', 'is_correct': False},
            {'text': '200 000 км/с', 'is_correct': False}
        ]
        await BonusAnswerOptionRepository.create_multiple(physics_question2.id, physics_options2)
        print(f"   ✅ Добавлен вопрос: {physics_question2.text}")


async def init_andrey_purchases():
    """Создание покупок для Андрея Климова"""
    print("Создание покупок для Андрея Климова...")

    # Получаем Андрея Климова
    andrey_user = await StudentRepository.get_by_telegram_id(955518340)
    if not andrey_user:
        print("   ⚠️ Андрей Климов не найден в базе данных")
        return

    print(f"   ✅ Найден студент: {andrey_user.user.name} (ID: {andrey_user.id})")

    # Добавляем монеты Андрею
    await StudentRepository.add_coins(andrey_user.id, 1000)
    balance = await StudentRepository.get_balance(andrey_user.id)
    print(f"   ✅ Баланс Андрея: {balance['coins']} монет")

    # Покупаем бонусные тесты
    bonus_tests = await BonusTestRepository.get_all()

    for test in bonus_tests:
        # Проверяем, не покупал ли уже этот тест
        already_purchased = await StudentBonusTestRepository.has_purchased_test(andrey_user.id, test.id)

        if not already_purchased:
            # Покупаем тест
            success = await StudentRepository.spend_coins(andrey_user.id, test.price)
            if success:
                purchase = await StudentBonusTestRepository.create_purchase(andrey_user.id, test.id, test.price)
                print(f"   ✅ Куплен бонусный тест: {test.name} (ID покупки: {purchase.id})")
            else:
                print(f"   ❌ Не удалось купить тест: {test.name}")
        else:
            print(f"   ⚠️ Тест уже куплен: {test.name}")

    # Проверяем финальный баланс
    final_balance = await StudentRepository.get_balance(andrey_user.id)
    print(f"   ✅ Финальный баланс Андрея: {final_balance['coins']} монет")


async def main():
    """Основная функция инициализации"""
    await init_database()
    await init_shop_items()


if __name__ == "__main__":
    asyncio.run(main())
