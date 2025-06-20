"""
Скрипт для отладки бонусных тестов
"""
import asyncio
import sys
import os

# Добавляем корневую папку проекта в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import BonusTestRepository, BonusQuestionRepository, BonusAnswerOptionRepository


async def debug_bonus_tests():
    """Проверить данные бонусных тестов в базе"""
    print("🔍 Отладка бонусных тестов...")
    
    try:
        # Получаем все бонусные тесты
        tests = await BonusTestRepository.get_all()
        print(f"\n📊 Найдено бонусных тестов: {len(tests)}")
        
        if not tests:
            print("❌ Бонусные тесты не найдены в базе данных!")
            return
        
        for i, test in enumerate(tests, 1):
            print(f"\n{i}. 🧪 Тест: {test.name}")
            print(f"   💰 Цена: {test.price} монет")
            print(f"   📅 Создан: {test.created_at}")
            
            # Получаем вопросы теста
            question_repo = BonusQuestionRepository()
            questions = await question_repo.get_by_bonus_test(test.id)
            print(f"   📝 Вопросов: {len(questions)}")
            
            if not questions:
                print("   ❌ Вопросы не найдены!")
                continue
            
            for j, question in enumerate(questions, 1):
                print(f"\n   {j}. ❓ Вопрос ID {question.id}: {question.text}")
                print(f"      ⏱️ Время: {question.time_limit} секунд")
                print(f"      📷 Фото: {question.photo_path or 'Нет'}")
                
                # Получаем варианты ответов
                options = await BonusAnswerOptionRepository.get_by_bonus_question(question.id)
                print(f"      🔤 Вариантов ответов: {len(options)}")
                
                if not options:
                    print("      ❌ Варианты ответов не найдены!")
                    continue
                
                for k, option in enumerate(options, 1):
                    status = "✅ ПРАВИЛЬНЫЙ" if option.is_correct else "❌ неправильный"
                    print(f"         {k}. {option.text} ({status})")
        
        print(f"\n✅ Отладка завершена. Всего тестов: {len(tests)}")
        
    except Exception as e:
        print(f"❌ Ошибка при отладке: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(debug_bonus_tests())
