"""
Создание тестовых данных для контрольных тестов месяца
"""
import asyncio
from database import (
    MonthControlTestResultRepository, StudentRepository, MonthTestRepository, 
    QuestionRepository, HomeworkRepository, LessonRepository
)


async def create_month_control_test_results():
    """Создание тестовых результатов контрольных тестов месяца"""
    try:
        print("📊 Создание тестовых результатов контрольных тестов месяца...")
        
        # Проверяем, есть ли уже результаты
        existing_results = await MonthControlTestResultRepository.get_all()
        if existing_results:
            print("   ⚠️ Результаты контрольных тестов месяца уже существуют, пропускаем создание")
            return
        
        # Получаем студентов и тесты месяца
        students = await StudentRepository.get_all()
        month_tests = await MonthTestRepository.get_all()
        
        # Фильтруем только контрольные тесты
        control_tests = [mt for mt in month_tests if mt.test_type == 'control']
        
        if not students or not control_tests:
            print("   ⚠️ Студенты или контрольные тесты месяца не найдены, пропускаем создание результатов")
            return

        # Создаем тестовые результаты для студентов групп М-1 и PY-1
        # Результаты контрольных тестов должны показывать прогресс по сравнению с входными
        test_data = [
            # Группа М-1 (Математика) - улучшение результатов
            {
                "student_name": "Аружан Ахметова",  # Студент группы М-1
                "month_test_name": "Контрольный тест по алгебре",
                "test_type": "control",
                "correct_percentage": 92,  # Было 85% во входном → стало 92% (+7%)
            },
            {
                "student_name": "Аружан Ахметова",  # Студент группы М-1
                "month_test_name": "Геометрия и фигуры",
                "test_type": "control",
                "correct_percentage": 83,  # Было 72% во входном → стало 83% (+11%)
            },
            
            # Группа PY-1 (Python) - смешанные результаты
            {
                "student_name": "Муханбетжан Олжас",  # Студент группы PY-1
                "month_test_name": "Основы программирования",
                "test_type": "control",
                "correct_percentage": 94,  # Было 90% во входном → стало 94% (+4%)
            },
            
            # Дополнительные результаты для разнообразия
            {
                "student_name": "Бекзат Сериков",  # Студент группы PY-2
                "month_test_name": "Основы программирования",
                "test_type": "control", 
                "correct_percentage": 72,  # Было 65% во входном → стало 72% (+7%)
            },
            {
                "student_name": "Ерасыл Мухамедов",  # Студент группы М-2
                "month_test_name": "Контрольный тест по алгебре",
                "test_type": "control",
                "correct_percentage": 85,  # Было 78% во входном → стало 85% (+7%)
            },
            {
                "student_name": "Ерасыл Мухамедов",  # Студент группы М-2
                "month_test_name": "Геометрия и фигуры",
                "test_type": "control",
                "correct_percentage": 61,  # Было 55% во входном → стало 61% (+6%)
            }
        ]

        created_count = 0
        
        for data in test_data:
            # Находим студента
            student = None
            for s in students:
                if s.user.name == data["student_name"]:
                    student = s
                    break
            
            if not student:
                print(f"   ⚠️ Студент '{data['student_name']}' не найден")
                continue

            # Находим контрольный тест месяца
            month_test = None
            for mt in control_tests:
                if mt.name == data["month_test_name"] and mt.test_type == data["test_type"]:
                    month_test = mt
                    break
            
            if not month_test:
                print(f"   ⚠️ Контрольный тест месяца '{data['month_test_name']}' не найден")
                continue

            # Проверяем, не проходил ли уже студент этот тест
            if await MonthControlTestResultRepository.has_student_taken_test(student.id, month_test.id):
                print(f"   ⚠️ {student.user.name} уже проходил контрольный тест '{month_test.name}'")
                continue

            # Создаем демонстрационные результаты (без реальных вопросов)
            # В реальной системе здесь будут вопросы из ДЗ по микротемам теста
            total_questions = 9  # 3 микротемы * 3 вопроса
            target_correct = int(total_questions * data["correct_percentage"] / 100)
            
            question_results = []
            for i in range(total_questions):
                # Создаем демонстрационные результаты
                microtopic_number = (i // 3) + 1  # Микротемы 1, 2, 3
                is_correct = i < target_correct
                
                question_results.append({
                    'question_id': 1,  # Демонстрационный ID вопроса
                    'selected_answer_id': 1,  # Демонстрационный ID ответа
                    'is_correct': is_correct,
                    'time_spent': 25,  # Примерное время ответа
                    'microtopic_number': microtopic_number
                })

            # Создаем результат теста
            test_result = await MonthControlTestResultRepository.create_test_result(
                student_id=student.id,
                month_test_id=month_test.id,
                question_results=question_results
            )

            print(f"   ✅ Результат контрольного теста месяца создан: {student.user.name} - {month_test.name} ({test_result.score_percentage}%)")
            created_count += 1

        print(f"📊 Создание тестовых результатов контрольных тестов месяца завершено! Создано: {created_count}")

    except Exception as e:
        print(f"❌ Ошибка при создании тестовых результатов контрольных тестов месяца: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Главная функция для запуска создания тестовых данных"""
    await create_month_control_test_results()


if __name__ == "__main__":
    asyncio.run(main())
