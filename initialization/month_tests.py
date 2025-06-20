"""
Создание тестовых тестов месяца
"""
from database import MonthTestRepository, QuestionRepository, AnswerOptionRepository, MicrotopicRepository, MonthTestMicrotopicRepository


async def add_test_month_tests(created_subjects):
    """Добавление тестовых тестов месяца для демонстрации"""
    try:
        from database import CourseRepository

        # Проверяем, есть ли уже тесты месяца
        existing_tests = await MonthTestRepository.get_all()
        if existing_tests:
            print("   ⚠️ Тесты месяца уже существуют, пропускаем создание")
            return
        # Данные для тестов месяца
        month_tests_data = [
            {
                "subject": "Математика",
                "month": "Январь",
                "name": "Контрольный тест по алгебре",
                "description": "Тест по основам алгебры за январь"
            },
            {
                "subject": "Физика", 
                "month": "Январь",
                "name": "Механика и движение",
                "description": "Тест по механике за январь"
            },
            {
                "subject": "Python",
                "month": "Январь", 
                "name": "Основы программирования",
                "description": "Тест по основам Python за январь"
            },
            {
                "subject": "Математика",
                "month": "Февраль",
                "name": "Геометрия и фигуры",
                "description": "Тест по геометрии за февраль"
            },
            {
                "subject": "Химия",
                "month": "Февраль",
                "name": "Химические реакции",
                "description": "Тест по химическим реакциям за февраль"
            }
        ]

        created_count = 0
        
        for test_data in month_tests_data:
            subject_name = test_data["subject"]
            if subject_name not in created_subjects:
                print(f"   ⚠️ Предмет '{subject_name}' не найден")
                continue
                
            subject = created_subjects[subject_name]

            # Получаем курсы для предмета
            all_courses = await CourseRepository.get_all()
            course_id = None
            for course in all_courses:
                if any(s.id == subject.id for s in course.subjects):
                    course_id = course.id
                    break

            # Создаем тест месяца
            month_test = await MonthTestRepository.create(
                name=test_data["name"],
                course_id=course_id,
                subject_id=subject.id
            )

            # Получаем микротемы для предмета
            microtopics = await MicrotopicRepository.get_by_subject(subject.id)

            # Добавляем первые 3 микротемы к тесту (или все, если их меньше 3)
            microtopics_to_add = microtopics[:3] if len(microtopics) >= 3 else microtopics

            for microtopic in microtopics_to_add:
                await MonthTestMicrotopicRepository.create(
                    month_test_id=month_test.id,
                    microtopic_number=microtopic.number
                )

            microtopic_numbers = [mt.number for mt in microtopics_to_add]
            print(f"   ✅ Тест месяца '{month_test.name}' создан для предмета '{subject_name}' ({test_data['month']})")
            print(f"      Добавлены микротемы: {microtopic_numbers}")
            created_count += 1

        print(f"🗓️ Создание тестовых тестов месяца завершено! Создано: {created_count}")

    except Exception as e:
        print(f"❌ Ошибка при добавлении тестовых тестов месяца: {e}")
