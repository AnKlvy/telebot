"""
Скрипт для покупки бонусного теста для тестирования
"""
import asyncio
import sys
import os

# Добавляем корневую папку проекта в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import StudentRepository, BonusTestRepository, StudentBonusTestRepository


async def buy_bonus_test_for_testing():
    """Купить бонусный тест для тестирования"""
    print("🛒 Покупка бонусного теста для тестирования...")

    try:
        # Сначала посмотрим всех студентов
        from database.repositories.student_repository import StudentRepository as StudentRepo
        students = await StudentRepo.get_all()
        print(f"👥 Найдено студентов: {len(students)}")
        for i, s in enumerate(students[:5], 1):  # Показываем первых 5
            user_name = s.user.name if s.user else "Неизвестно"
            telegram_id = s.user.telegram_id if s.user else "Неизвестно"
            print(f"   {i}. {user_name} (TG: {telegram_id})")

        # Ищем студента Андрея Климова (попробуем разные ID)
        student = None
        test_ids = [123456789, 987654321, 1234567890]

        for test_id in test_ids:
            student = await StudentRepository.get_by_telegram_id(test_id)
            if student:
                user_name = student.user.name if student.user else "Неизвестно"
                print(f"✅ Найден студент с ID {test_id}: {user_name}")
                break

        if not student and students:
            # Берем первого студента
            student = students[0]
            user_name = student.user.name if student.user else "Неизвестно"
            telegram_id = student.user.telegram_id if student.user else "Неизвестно"
            print(f"📝 Используем первого студента: {user_name} (TG: {telegram_id})")

        if not student:
            print("❌ Студенты не найдены!")
            return
        
        user_name = student.user.name if student.user else "Неизвестно"
        print(f"👤 Найден студент: {user_name}")
        
        # Получаем баланс студента
        balance = await StudentRepository.get_balance(student.id)
        print(f"💰 Текущий баланс: {balance['coins']} монет, {balance['points']} баллов")
        
        # Если мало монет, добавляем
        if balance['coins'] < 100:
            print("💰 Добавляем монеты для покупки...")
            await StudentRepository.add_coins(student.id, 200)
            new_balance = await StudentRepository.get_balance(student.id)
            print(f"💰 Новый баланс: {new_balance['coins']} монет")
        
        # Получаем бонусные тесты
        tests = await BonusTestRepository.get_all()
        if not tests:
            print("❌ Бонусные тесты не найдены!")
            return
        
        # Покупаем первый тест (математика)
        test = tests[0]  # Тест по математике
        print(f"🧪 Покупаем тест: {test.name} за {test.price} монет")
        
        # Проверяем, не покупал ли уже
        already_purchased = await StudentBonusTestRepository.has_purchased_test(student.id, test.id)
        if already_purchased:
            print("⚠️ Тест уже куплен!")
            
            # Показываем купленные тесты
            purchases = await StudentBonusTestRepository.get_student_bonus_tests(student.id)
            print(f"📦 Купленных тестов: {len(purchases)}")
            for i, purchase in enumerate(purchases, 1):
                print(f"   {i}. {purchase.bonus_test.name} - {purchase.price_paid} монет")
            return
        
        # Покупаем тест
        success = await StudentRepository.spend_coins(student.id, test.price)
        if success:
            # Создаем запись о покупке
            purchase = await StudentBonusTestRepository.create_purchase(student.id, test.id, test.price)
            print(f"✅ Тест куплен! ID покупки: {purchase.id}")
            
            # Показываем новый баланс
            final_balance = await StudentRepository.get_balance(student.id)
            print(f"💰 Итоговый баланс: {final_balance['coins']} монет")
        else:
            print("❌ Не удалось купить тест!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(buy_bonus_test_for_testing())
