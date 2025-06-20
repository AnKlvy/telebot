"""
Тест логики бонусных тестов без запуска бота
"""
import asyncio
import sys
import os

# Добавляем корневую папку проекта в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import BonusTestRepository, BonusQuestionRepository, BonusAnswerOptionRepository


async def test_bonus_test_logic():
    """Тестируем логику получения данных для бонусного теста"""
    print("🧪 Тестирование логики бонусных тестов...")
    
    try:
        # Получаем первый бонусный тест
        tests = await BonusTestRepository.get_all()
        if not tests:
            print("❌ Бонусные тесты не найдены!")
            return
        
        test = tests[0]  # Берем первый тест
        print(f"🧪 Тестируем: {test.name} (ID: {test.id})")
        
        # Получаем вопросы теста
        question_repo = BonusQuestionRepository()
        questions = await question_repo.get_by_bonus_test(test.id)
        print(f"📝 Найдено вопросов: {len(questions)}")
        
        if not questions:
            print("❌ Вопросы не найдены!")
            return
        
        # Тестируем первый вопрос
        question = questions[0]
        print(f"❓ Тестируем вопрос: {question.text} (ID: {question.id})")
        
        # Получаем варианты ответов
        options = await BonusAnswerOptionRepository.get_by_bonus_question(question.id)
        print(f"🔤 Найдено вариантов ответов: {len(options)}")
        
        if not options:
            print("❌ Варианты ответов не найдены!")
            return
        
        # Проверяем варианты ответов
        correct_count = 0
        for i, option in enumerate(options, 1):
            status = "✅ ПРАВИЛЬНЫЙ" if option.is_correct else "❌ неправильный"
            print(f"   {i}. {option.text} ({status})")
            if option.is_correct:
                correct_count += 1
        
        if correct_count == 0:
            print("❌ Нет правильных ответов!")
        elif correct_count > 1:
            print(f"⚠️ Слишком много правильных ответов: {correct_count}")
        else:
            print("✅ Один правильный ответ найден")
        
        # Симулируем данные состояния как в боте
        test_state_data = {
            'bonus_test_id': test.id,
            'questions': [{
                'id': q.id,
                'text': q.text,
                'photo_path': q.photo_path,
                'time_limit': q.time_limit,
                'microtopic_number': None
            } for q in questions],
            'q_index': 0,
            'score': 0,
            'total_questions': len(questions)
        }
        
        print(f"\n📋 Симуляция данных состояния:")
        print(f"   bonus_test_id: {test_state_data.get('bonus_test_id')}")
        print(f"   questions count: {len(test_state_data.get('questions', []))}")
        print(f"   q_index: {test_state_data.get('q_index')}")
        
        # Симулируем логику из send_next_question
        is_bonus_test = test_state_data.get("bonus_test_id") is not None
        print(f"   is_bonus_test: {is_bonus_test}")
        
        if is_bonus_test:
            current_question = test_state_data['questions'][0]
            question_id = current_question['id']
            print(f"   Получаем варианты для вопроса ID: {question_id}")
            
            # Тестируем получение вариантов ответов
            answer_options = await BonusAnswerOptionRepository.get_by_bonus_question(question_id)
            print(f"   Получено вариантов: {len(answer_options)}")
            
            if answer_options:
                print("✅ Логика работает корректно!")
            else:
                print("❌ Варианты ответов не получены!")
        else:
            print("❌ Тест не определен как бонусный!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_bonus_test_logic())
