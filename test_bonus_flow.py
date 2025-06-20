"""
Тест полного потока бонусного теста
"""
import asyncio
import sys
import os

# Добавляем корневую папку проекта в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import (
    StudentRepository, BonusTestRepository, StudentBonusTestRepository,
    BonusQuestionRepository, BonusAnswerOptionRepository
)


async def test_full_bonus_flow():
    """Тестируем полный поток бонусного теста"""
    print("🔄 Тестирование полного потока бонусного теста...")
    
    try:
        # 1. Получаем студента с купленным тестом
        student = await StudentRepository.get_by_telegram_id(333444555)  # Муханбетжан Олжас
        if not student:
            print("❌ Студент не найден!")
            return
        
        print(f"👤 Студент: {student.user.name}")
        
        # 2. Получаем купленные бонусные тесты
        purchases = await StudentBonusTestRepository.get_student_bonus_tests(student.id)
        if not purchases:
            print("❌ Купленные тесты не найдены!")
            return
        
        print(f"📦 Купленных тестов: {len(purchases)}")
        
        # 3. Берем первый купленный тест
        purchase = purchases[0]
        bonus_test = purchase.bonus_test
        print(f"🧪 Тест: {bonus_test.name} (ID: {bonus_test.id})")
        
        # 4. Получаем вопросы теста
        question_repo = BonusQuestionRepository()
        questions = await question_repo.get_by_bonus_test(bonus_test.id)
        print(f"📝 Вопросов в тесте: {len(questions)}")
        
        if not questions:
            print("❌ Вопросы не найдены!")
            return
        
        # 5. Симулируем данные состояния как в боте
        test_state_data = {
            'student_id': student.id,
            'user_id': student.user.telegram_id,
            'bonus_test_id': bonus_test.id,  # Ключевое поле!
            'bonus_test_purchase_id': purchase.id,
            'bonus_test_name': bonus_test.name,
            'score': 0,
            'q_index': 0,
            'total_questions': len(questions),
            'question_results': [],
            'messages_to_delete': [],
            'questions': [{
                'id': q.id,
                'text': q.text,
                'photo_path': q.photo_path,
                'time_limit': q.time_limit,
                'microtopic_number': None  # У бонусных тестов нет микротем
            } for q in questions]
        }
        
        print(f"\n📋 Данные состояния:")
        print(f"   bonus_test_id: {test_state_data.get('bonus_test_id')}")
        print(f"   questions count: {len(test_state_data.get('questions', []))}")
        print(f"   q_index: {test_state_data.get('q_index')}")
        
        # 6. Симулируем логику send_next_question
        index = test_state_data.get("q_index", 0)
        questions_data = test_state_data.get("questions", [])
        
        if index >= len(questions_data):
            print("❌ Индекс вопроса больше количества вопросов!")
            return
        
        question_data = questions_data[index]
        question_id = question_data['id']
        
        print(f"\n🔍 Обработка вопроса {index + 1}:")
        print(f"   ID: {question_id}")
        print(f"   Текст: {question_data['text']}")
        print(f"   Время: {question_data['time_limit']} сек")
        
        # 7. Определяем тип теста
        is_bonus_test = test_state_data.get("bonus_test_id") is not None
        print(f"   is_bonus_test: {is_bonus_test}")
        
        if is_bonus_test:
            # 8. Получаем варианты ответов для бонусного теста
            answer_options = await BonusAnswerOptionRepository.get_by_bonus_question(question_id)
            print(f"   Получено вариантов ответов: {len(answer_options)}")
            
            if answer_options:
                print("   Варианты ответов:")
                for i, opt in enumerate(answer_options, 1):
                    status = "✅" if opt.is_correct else "❌"
                    print(f"      {i}. {opt.text} {status}")
                
                # 9. Проверяем правильный ответ
                correct_options = [opt for opt in answer_options if opt.is_correct]
                if len(correct_options) == 1:
                    print("✅ Один правильный ответ найден")
                elif len(correct_options) == 0:
                    print("❌ Правильный ответ не найден!")
                else:
                    print(f"⚠️ Слишком много правильных ответов: {len(correct_options)}")
                
                print("✅ Полный поток работает корректно!")
            else:
                print("❌ Варианты ответов не получены!")
        else:
            print("❌ Тест не определен как бонусный!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_full_bonus_flow())
