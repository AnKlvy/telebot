"""
Создание тестовых данных для входных тестов месяца
"""
import asyncio
from database import (
    MonthEntryTestResultRepository, StudentRepository, MonthTestRepository, 
    QuestionRepository, HomeworkRepository, LessonRepository
)


async def create_test_month_entry_results():
    """Создание тестовых результатов входных тестов месяца"""
    try:
        print("📊 Создание тестовых результатов входных тестов месяца...")
        
        # Проверяем, есть ли уже результаты
        existing_results = await MonthEntryTestResultRepository.get_all()
        if existing_results:
            print("   ⚠️ Результаты входных тестов месяца уже существуют, пропускаем создание")
            return
        
        # Получаем студентов и тесты месяца
        students = await StudentRepository.get_all()
        month_tests = await MonthTestRepository.get_all()
        
        if not students or not month_tests:
            print("   ⚠️ Студенты или тесты месяца не найдены, пропускаем создание результатов")
            return

        # Создаем тестовые результаты для студентов групп М-1, М-2 и PY-1
        test_data = [
            # Группа М-1 (Математика)
            {
                "student_name": "Аружан Ахметова",  # Студент группы М-1
                "month_test_name": "Контрольный тест по алгебре",
                "correct_percentage": 85,  # 85% правильных ответов
            },
            {
                "student_name": "Аружан Ахметова",  # Студент группы М-1
                "month_test_name": "Геометрия и фигуры",
                "correct_percentage": 72,  # 72% правильных ответов
            },
            {
                "student_name": "Андрей Климов",  # Студент группы М-1
                "month_test_name": "Контрольный тест по алгебре",
                "correct_percentage": 92,  # 92% правильных ответов
            },
            {
                "student_name": "Андрей Климов",  # Студент группы М-1
                "month_test_name": "Геометрия и фигуры",
                "correct_percentage": 88,  # 88% правильных ответов
            },

            # Группа М-2 (Математика)
            {
                "student_name": "Муханбетжан Олжас",  # Студент группы М-2
                "month_test_name": "Контрольный тест по алгебре",
                "correct_percentage": 78,  # 78% правильных ответов
            },
            {
                "student_name": "Муханбетжан Олжас",  # Студент группы М-2
                "month_test_name": "Геометрия и фигуры",
                "correct_percentage": 65,  # 65% правильных ответов
            },
            {
                "student_name": "Ерасыл Мухамедов",  # Студент группы М-2
                "month_test_name": "Контрольный тест по алгебре",
                "correct_percentage": 55,  # 55% правильных ответов
            },
            {
                "student_name": "Ерасыл Мухамедов",  # Студент группы М-2
                "month_test_name": "Геометрия и фигуры",
                "correct_percentage": 42,  # 42% правильных ответов
            },

            # Группа PY-1 (Python)
            {
                "student_name": "Муханбетжан Олжас",  # Студент группы PY-1
                "month_test_name": "Основы программирования",
                "correct_percentage": 90,  # 90% правильных ответов
            },
            {
                "student_name": "Андрей Климов",  # Студент группы PY-1
                "month_test_name": "Основы программирования",
                "correct_percentage": 95,  # 95% правильных ответов
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

            # Находим тест месяца
            month_test = None
            for mt in month_tests:
                if mt.name == data["month_test_name"]:
                    month_test = mt
                    break
            
            if not month_test:
                print(f"   ⚠️ Тест месяца '{data['month_test_name']}' не найден")
                continue

            # Проверяем, не проходил ли уже студент этот тест
            if await MonthEntryTestResultRepository.has_student_taken_test(student.id, month_test.id):
                print(f"   ⚠️ {student.user.name} уже проходил тест '{month_test.name}'")
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
            test_result = await MonthEntryTestResultRepository.create_test_result(
                student_id=student.id,
                month_test_id=month_test.id,
                question_results=question_results
            )

            print(f"   ✅ Результат входного теста месяца создан: {student.user.name} - {month_test.name} ({test_result.score_percentage}%)")
            created_count += 1

        print(f"📊 Создание тестовых результатов входных тестов месяца завершено! Создано: {created_count}")

    except Exception as e:
        print(f"❌ Ошибка при создании тестовых результатов входных тестов месяца: {e}")


async def main():
    """Главная функция для запуска создания тестовых данных"""
    await create_test_month_entry_results()


if __name__ == "__main__":
    asyncio.run(main())
