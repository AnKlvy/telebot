"""
Создание контрольных тестов месяца
"""
from database import MonthTestRepository, SubjectRepository, CourseRepository


async def create_month_control_tests():
    """Создание контрольных тестов месяца для групп М-1, М-2 и PY-1"""
    try:
        print("📊 Создание контрольных тестов месяца...")
        
        # Получаем все входные тесты
        entry_tests = await MonthTestRepository.get_all()
        entry_tests = [t for t in entry_tests if t.test_type == 'entry']
        
        if not entry_tests:
            print("   ⚠️ Нет входных тестов для создания контрольных")
            return
        
        # Данные для контрольных тестов (на основе входных)
        control_tests_data = [
            # Математика - для групп М-1 и М-2
            {
                "entry_test_name": "Контрольный тест по алгебре",
                "control_test_name": "Контрольный тест по алгебре (Контроль)",
                "subject_name": "Математика"
            },
            {
                "entry_test_name": "Геометрия и фигуры", 
                "control_test_name": "Геометрия и фигуры (Контроль)",
                "subject_name": "Математика"
            },
            # Python - для группы PY-1
            {
                "entry_test_name": "Основы программирования",
                "control_test_name": "Основы программирования (Контроль)",
                "subject_name": "Python"
            }
        ]
        
        created_count = 0
        
        for test_data in control_tests_data:
            # Находим входной тест
            entry_test = None
            for test in entry_tests:
                if (test.name == test_data["entry_test_name"] and 
                    test.subject.name == test_data["subject_name"]):
                    entry_test = test
                    break
            
            if not entry_test:
                print(f"   ⚠️ Входной тест '{test_data['entry_test_name']}' не найден")
                continue
            
            # Проверяем, не существует ли уже контрольный тест
            existing_control = None
            all_tests = await MonthTestRepository.get_all()
            for test in all_tests:
                if (test.name == test_data["control_test_name"] and 
                    test.subject_id == entry_test.subject_id and
                    test.test_type == 'control'):
                    existing_control = test
                    break
            
            if existing_control:
                print(f"   ⚠️ Контрольный тест '{test_data['control_test_name']}' уже существует")
                continue
            
            # Создаем контрольный тест
            control_test = await MonthTestRepository.create(
                name=test_data["control_test_name"],
                course_id=entry_test.course_id,
                subject_id=entry_test.subject_id,
                test_type='control'
            )
            
            print(f"   ✅ Контрольный тест '{control_test.name}' создан для предмета '{test_data['subject_name']}'")
            created_count += 1
        
        print(f"📊 Создание контрольных тестов месяца завершено! Создано: {created_count}")
        
    except Exception as e:
        print(f"❌ Ошибка при создании контрольных тестов месяца: {e}")
        import traceback
        traceback.print_exc()


async def create_month_control_test_results():
    """Создание тестовых результатов контрольных тестов месяца"""
    try:
        print("📊 Создание результатов контрольных тестов месяца...")
        
        from database import MonthEntryTestResultRepository, StudentRepository
        
        # Проверяем, есть ли уже результаты контрольных тестов
        all_tests = await MonthTestRepository.get_all()
        control_tests = [t for t in all_tests if t.test_type == 'control']
        
        if not control_tests:
            print("   ⚠️ Нет контрольных тестов для создания результатов")
            return
        
        # Получаем студентов
        students = await StudentRepository.get_all()
        
        # Тестовые данные для контрольных тестов (показываем прогресс)
        control_test_data = [
            # Группа М-1 (Математика) - показываем улучшение
            {
                "student_name": "Аружан Ахметова",
                "control_test_name": "Контрольный тест по алгебре (Контроль)",
                "correct_percentage": 90,  # Улучшение с 77% до 90%
            },
            {
                "student_name": "Аружан Ахметова",
                "control_test_name": "Геометрия и фигуры (Контроль)",
                "correct_percentage": 78,  # Улучшение с 66% до 78%
            },
            {
                "student_name": "Андрей Климов",
                "control_test_name": "Контрольный тест по алгебре (Контроль)",
                "correct_percentage": 95,  # Улучшение с 88% до 95%
            },
            {
                "student_name": "Андрей Климов",
                "control_test_name": "Геометрия и фигуры (Контроль)",
                "correct_percentage": 85,  # Улучшение с 77% до 85%
            },
            
            # Группа М-2 (Математика) - смешанные результаты
            {
                "student_name": "Муханбетжан Олжас",
                "control_test_name": "Контрольный тест по алгебре (Контроль)",
                "correct_percentage": 82,  # Улучшение с 77% до 82%
            },
            {
                "student_name": "Муханбетжан Олжас",
                "control_test_name": "Геометрия и фигуры (Контроль)",
                "correct_percentage": 50,  # Ухудшение с 55% до 50%
            },
            {
                "student_name": "Ерасыл Мухамедов",
                "control_test_name": "Контрольный тест по алгебре (Контроль)",
                "correct_percentage": 60,  # Улучшение с 44% до 60%
            },
            {
                "student_name": "Ерасыл Мухамедов",
                "control_test_name": "Геометрия и фигуры (Контроль)",
                "correct_percentage": 30,  # Ухудшение с 33% до 30%
            },
            
            # Группа PY-1 (Python) - хорошие результаты
            {
                "student_name": "Муханбетжан Олжас",
                "control_test_name": "Основы программирования (Контроль)",
                "correct_percentage": 92,  # Улучшение с 88% до 92%
            },
            {
                "student_name": "Андрей Климов",
                "control_test_name": "Основы программирования (Контроль)",
                "correct_percentage": 97,  # Улучшение с 88% до 97%
            }
        ]
        
        created_count = 0
        
        for data in control_test_data:
            # Находим студента
            student = None
            for s in students:
                if s.user.name == data["student_name"]:
                    student = s
                    break
            
            if not student:
                print(f"   ⚠️ Студент '{data['student_name']}' не найден")
                continue
            
            # Находим контрольный тест
            control_test = None
            for test in control_tests:
                if test.name == data["control_test_name"]:
                    control_test = test
                    break
            
            if not control_test:
                print(f"   ⚠️ Контрольный тест '{data['control_test_name']}' не найден")
                continue
            
            # Проверяем, не проходил ли уже студент этот тест
            if await MonthEntryTestResultRepository.has_student_taken_test(student.id, control_test.id):
                print(f"   ⚠️ {student.user.name} уже проходил контрольный тест '{control_test.name}'")
                continue
            
            # Создаем демонстрационные результаты
            total_questions = 9  # 3 микротемы * 3 вопроса
            target_correct = int(total_questions * data["correct_percentage"] / 100)
            
            question_results = []
            for i in range(total_questions):
                microtopic_number = (i // 3) + 1  # Микротемы 1, 2, 3
                is_correct = i < target_correct
                
                question_results.append({
                    'question_id': 1,  # Демонстрационный ID вопроса
                    'selected_answer_id': 1,  # Демонстрационный ID ответа
                    'is_correct': is_correct,
                    'time_spent': 25,  # Примерное время ответа
                    'microtopic_number': microtopic_number
                })
            
            # Создаем результат контрольного теста
            test_result = await MonthEntryTestResultRepository.create_test_result(
                student_id=student.id,
                month_test_id=control_test.id,
                question_results=question_results
            )
            
            print(f"   ✅ Результат контрольного теста создан: {student.user.name} - {control_test.name} ({test_result.score_percentage}%)")
            created_count += 1
        
        print(f"📊 Создание результатов контрольных тестов месяца завершено! Создано: {created_count}")
        
    except Exception as e:
        print(f"❌ Ошибка при создании результатов контрольных тестов месяца: {e}")
        import traceback
        traceback.print_exc()
