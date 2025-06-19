"""
Создание тестовых данных для входных тестов месяца
"""
from database import (
    MonthEntryTestResultRepository, StudentRepository, MonthTestRepository, 
    QuestionRepository, HomeworkRepository, LessonRepository
)


async def create_month_entry_test_results():
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

        # Создаем тестовые результаты для студентов групп М-1 и PY-1
        test_data = [
            # Группа М-1 (Математика) - тест "Контрольный тест по алгебре"
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

            # Группа PY-1 (Python) - тест "Основы программирования"
            {
                "student_name": "Муханбетжан Олжас",  # Студент группы PY-1
                "month_test_name": "Основы программирования",
                "correct_percentage": 90,  # 90% правильных ответов
            },

            # Дополнительные результаты для разнообразия
            {
                "student_name": "Бекзат Сериков",  # Студент группы PY-2
                "month_test_name": "Основы программирования",
                "correct_percentage": 65,  # 65% правильных ответов
            },
            {
                "student_name": "Ерасыл Мухамедов",  # Студент группы М-2
                "month_test_name": "Контрольный тест по алгебре",
                "correct_percentage": 78,  # 78% правильных ответов
            },
            {
                "student_name": "Ерасыл Мухамедов",  # Студент группы М-2
                "month_test_name": "Геометрия и фигуры",
                "correct_percentage": 55,  # 55% правильных ответов
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

            # Получаем случайные вопросы для теста
            questions_data = await MonthEntryTestResultRepository.get_random_questions_for_month_test(month_test.id)
            
            if not questions_data:
                print(f"   ⚠️ Нет вопросов для теста месяца '{month_test.name}'")
                continue

            # Создаем результаты ответов на вопросы
            question_results = []
            total_questions = len(questions_data)
            target_correct = int(total_questions * data["correct_percentage"] / 100)
            
            for i, q_data in enumerate(questions_data):
                question = q_data['question']
                microtopic_number = q_data['microtopic_number']
                
                # Определяем правильность ответа (первые target_correct будут правильными)
                is_correct = i < target_correct
                
                # Выбираем случайный ответ
                if question.answer_options:
                    if is_correct:
                        # Ищем правильный ответ
                        correct_answer = next((ao for ao in question.answer_options if ao.is_correct), None)
                        selected_answer_id = correct_answer.id if correct_answer else question.answer_options[0].id
                    else:
                        # Ищем неправильный ответ
                        wrong_answers = [ao for ao in question.answer_options if not ao.is_correct]
                        selected_answer_id = wrong_answers[0].id if wrong_answers else question.answer_options[0].id
                else:
                    selected_answer_id = None

                question_results.append({
                    'question_id': question.id,
                    'selected_answer_id': selected_answer_id,
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
        import traceback
        traceback.print_exc()
