"""
Создание тестовых данных для входных тестов курса
"""
from database import (
    CourseEntryTestResultRepository, StudentRepository, SubjectRepository
)


async def create_course_entry_test_results():
    """Создание тестовых результатов входных тестов курса"""
    try:
        print("📊 Создание тестовых результатов входных тестов курса...")
        
        # Проверяем, есть ли уже результаты
        existing_results = await CourseEntryTestResultRepository.get_all()
        if existing_results:
            print("   ⚠️ Результаты входных тестов курса уже существуют, пропускаем создание")
            return
        
        # Получаем студентов и предметы
        students = await StudentRepository.get_all()
        subjects = await SubjectRepository.get_all()
        
        if not students or not subjects:
            print("   ⚠️ Студенты или предметы не найдены, пропускаем создание результатов")
            return
        
        # Создаем тестовые результаты для некоторых студентов
        test_cases = [
            {
                "student_name": "Аружан Ахметова",
                "subject_name": "Математика",
                "correct_percentage": 80,  # 80% правильных ответов
            },
            {
                "student_name": "Ерасыл Мухамедов", 
                "subject_name": "Математика",
                "correct_percentage": 60,  # 60% правильных ответов
            },
            {
                "student_name": "Муханбетжан Олжас",
                "subject_name": "Python",
                "correct_percentage": 93,  # 93% правильных ответов
            },
            {
                "student_name": "Муханбетжан Олжас",
                "subject_name": "Математика", 
                "correct_percentage": 75,  # 75% правильных ответов
            },
            {
                "student_name": "Бекзат Сериков",
                "subject_name": "Python",
                "correct_percentage": 85,  # 85% правильных ответов
            }
        ]
        
        created_count = 0
        
        for test_case in test_cases:
            # Находим студента
            student = None
            for s in students:
                if s.user.name == test_case["student_name"]:
                    student = s
                    break
            
            if not student:
                print(f"   ⚠️ Студент '{test_case['student_name']}' не найден")
                continue
            
            # Находим предмет
            subject = None
            for subj in subjects:
                if subj.name == test_case["subject_name"]:
                    subject = subj
                    break
            
            if not subject:
                print(f"   ⚠️ Предмет '{test_case['subject_name']}' не найден")
                continue
            
            # Проверяем, есть ли уже результат для этого студента и предмета
            existing_result = await CourseEntryTestResultRepository.get_by_student_and_subject(
                student.id, subject.id
            )
            
            if existing_result:
                print(f"   ⚠️ Результат для {student.user.name} по {subject.name} уже существует")
                continue
            
            # Получаем вопросы для предмета (до 30 штук)
            questions = await CourseEntryTestResultRepository.get_random_questions_for_subject(
                subject.id, 30
            )
            
            if len(questions) == 0:
                print(f"   ⚠️ Нет вопросов для предмета '{subject.name}'")
                continue
            
            total_questions = len(questions)
            target_correct = int((test_case["correct_percentage"] / 100) * total_questions)
            
            # Создаем результаты ответов
            question_results = []
            
            for i, question in enumerate(questions):
                # Первые target_correct вопросов - правильные, остальные - неправильные
                is_correct = i < target_correct
                
                # Выбираем ответ
                correct_answer = None
                wrong_answer = None
                
                for answer in question.answer_options:
                    if answer.is_correct:
                        correct_answer = answer
                    else:
                        wrong_answer = answer
                
                selected_answer = correct_answer if is_correct else wrong_answer
                
                question_results.append({
                    'question_id': question.id,
                    'selected_answer_id': selected_answer.id if selected_answer else None,
                    'is_correct': is_correct,
                    'time_spent': 20 + i,  # Разное время ответа
                    'microtopic_number': question.microtopic_number
                })
            
            # Создаем результат теста
            try:
                test_result = await CourseEntryTestResultRepository.create_test_result(
                    student_id=student.id,
                    subject_id=subject.id,
                    question_results=question_results
                )
                
                print(f"   ✅ Результат входного теста создан для {student.user.name} по предмету {subject.name} ({test_result.score_percentage}%, {test_result.correct_answers}/{test_result.total_questions})")
                created_count += 1
                
            except Exception as e:
                print(f"   ❌ Ошибка при создании результата для {student.user.name}: {e}")
        
        print(f"📊 Создание тестовых результатов входных тестов курса завершено! Создано: {created_count}")
        
    except Exception as e:
        print(f"❌ Ошибка при создании тестовых результатов входных тестов курса: {e}")
