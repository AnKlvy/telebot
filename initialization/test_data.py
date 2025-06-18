"""
Создание тестовых данных и результатов
"""
from database import (
    StudentRepository, HomeworkRepository, QuestionRepository, 
    HomeworkResultRepository, QuestionResultRepository, AnswerOptionRepository
)


async def add_test_homework_results():
    """Добавление тестовых результатов домашних заданий для демонстрации статистики"""
    try:
        # Проверяем, есть ли уже результаты
        existing_results = await HomeworkResultRepository.get_all()
        if existing_results:
            print("   ⚠️ Тестовые результаты уже существуют, пропускаем создание")
            return

        # Получаем всех студентов
        students = await StudentRepository.get_all()
        if not students:
            print("   ❌ Не найдены студенты для создания результатов")
            return

        # Получаем все домашние задания
        homeworks = await HomeworkRepository.get_all()
        if not homeworks:
            print("   ❌ Не найдены домашние задания для создания результатов")
            return

        # Получаем все вопросы с вариантами ответов
        question_repo = QuestionRepository()
        questions = await question_repo.get_all()
        if not questions:
            print("   ❌ Не найдены вопросы для создания результатов")
            return

        created_results_count = 0
        created_question_results_count = 0

        # Создаем результаты для каждого студента
        for student in students:
            print(f"📊 Создаем результаты для студента '{student.user.name}':")

            # Получаем ДЗ только по предметам групп студента
            if not student.groups:
                print(f"   ⚠️  У студента {student.user.name} нет групп")
                continue

            # Собираем все предметы из групп студента
            subject_ids = []
            subject_names = []
            for group in student.groups:
                if group.subject:
                    subject_ids.append(group.subject_id)
                    subject_names.append(group.subject.name)

            if not subject_ids:
                print(f"   ⚠️  У студента {student.user.name} нет предметов в группах")
                continue

            subject_homeworks = [hw for hw in homeworks if hw.subject_id in subject_ids]
            if not subject_homeworks:
                print(f"   ⚠️  Нет ДЗ по предметам {', '.join(subject_names)}")
                continue

            import random
            if student.user.telegram_id == 955518340:  # Андрей Климов
                print(f"   Создаем результаты для {student.user.name}")
                max_homeworks = len(subject_homeworks)
                num_homeworks = max_homeworks  # Выполняет ВСЕ ДЗ
                student_homeworks = subject_homeworks  # Все ДЗ
                is_excellent_student = True
            elif student.user.telegram_id == 333444555:  # Муханбетжан Олжас
                print(f"   Создаем отличные результаты для {student.user.name}")
                max_homeworks = len(subject_homeworks)
                num_homeworks = max_homeworks  # Выполняет ВСЕ ДЗ
                student_homeworks = subject_homeworks  # Все ДЗ
                is_excellent_student = True
            else:
                # Разное количество ДЗ для разных студентов (от 1 до всех доступных)
                max_homeworks = len(subject_homeworks)
                num_homeworks = random.randint(1, max_homeworks)  # От 1 до всех ДЗ
                student_homeworks = random.sample(subject_homeworks, num_homeworks)  # Случайные ДЗ
                is_excellent_student = False

            print(f"   📚 Выполняет {num_homeworks} из {max_homeworks} ДЗ по предметам {', '.join(subject_names)}")

            for homework in student_homeworks:
                try:
                    # Получаем вопросы для этого ДЗ
                    homework_questions = await question_repo.get_by_homework(homework.id)
                    if not homework_questions:
                        continue

                    # Симулируем разные уровни успеха
                    if is_excellent_student:
                        success_rate = random.choice([0.9, 0.95, 1.0, 1.0, 1.0])  # В основном 100%
                    else:
                        success_rate = random.choice([0.5, 0.7, 0.8, 0.9, 1.0])  # 50%, 70%, 80%, 90%, 100%

                    total_questions = len(homework_questions)
                    correct_answers = int(total_questions * success_rate)

                    # Баллы начисляются только при 100% результате
                    points_earned = total_questions * 3 if success_rate == 1.0 else 0
                    points_awarded = success_rate == 1.0

                    # Создаем результат ДЗ
                    homework_result = await HomeworkResultRepository.create(
                        student_id=student.id,
                        homework_id=homework.id,
                        total_questions=total_questions,
                        correct_answers=correct_answers,
                        points_earned=points_earned,
                        is_first_attempt=True,
                        points_awarded=points_awarded
                    )

                    created_results_count += 1

                    # Создаем результаты для каждого вопроса
                    question_results_data = []
                    correct_count = 0

                    for question in homework_questions:
                        # Получаем варианты ответов для вопроса
                        answer_options = await AnswerOptionRepository.get_by_question(question.id)
                        if not answer_options:
                            continue

                        # Определяем правильность ответа
                        is_correct = correct_count < correct_answers
                        if is_correct:
                            # Выбираем правильный ответ
                            selected_answer = next((opt for opt in answer_options if opt.is_correct), None)
                            correct_count += 1
                        else:
                            # Выбираем случайный неправильный ответ
                            wrong_answers = [opt for opt in answer_options if not opt.is_correct]
                            selected_answer = random.choice(wrong_answers) if wrong_answers else answer_options[0]

                        # Случайное время ответа
                        time_spent = random.randint(5, 25)

                        question_results_data.append({
                            'question_id': question.id,
                            'selected_answer_id': selected_answer.id if selected_answer else None,
                            'is_correct': is_correct,
                            'time_spent': time_spent,
                            'microtopic_number': question.microtopic_number
                        })

                    # Создаем результаты вопросов
                    if question_results_data:
                        await QuestionResultRepository.create_multiple(
                            homework_result.id,
                            question_results_data
                        )
                        created_question_results_count += len(question_results_data)

                    percentage = round((correct_answers / total_questions * 100), 1) if total_questions > 0 else 0
                    print(f"      ✅ ДЗ '{homework.name}': {correct_answers}/{total_questions} ({percentage}%) - {points_earned} баллов")

                except Exception as e:
                    print(f"      ❌ Ошибка при создании результата для ДЗ '{homework.name}': {e}")
                    continue

        print(f"📊 Создание тестовых результатов завершено!")
        print(f"   ✅ Создано результатов ДЗ: {created_results_count}")
        print(f"   ✅ Создано результатов вопросов: {created_question_results_count}")

    except Exception as e:
        print(f"❌ Ошибка при добавлении тестовых результатов ДЗ: {e}")


async def create_results_for_andrey():
    """Создание отличных результатов для Андрея Климова"""
    try:
        # Находим Андрея Климова
        andrey = await StudentRepository.get_by_telegram_id(955518340)
        if not andrey:
            print("   ⚠️ Андрей Климов еще не создан как студент, пропускаем создание результатов")
            return

        # Проверяем, что он в правильной группе (Python)
        has_python_group = False
        if andrey.groups:
            for group in andrey.groups:
                if group.subject and group.subject.name == "Python":
                    has_python_group = True
                    break
        
        if not has_python_group:
            print(f"   🔄 Добавляем Андрея в группу Python...")
            # Находим группу PY-1
            from database import GroupRepository
            groups = await GroupRepository.get_all()
            python_group = next((g for g in groups if g.name == "PY-1"), None)
            if python_group:
                await StudentRepository.add_groups(andrey.id, [python_group.id])
                andrey = await StudentRepository.get_by_id(andrey.id)  # Обновляем данные
                print(f"   ✅ Андрей добавлен в группу {python_group.name}")
            else:
                print("   ❌ Группа PY-1 не найдена")
                return

        print(f"   👤 Создаем результаты для {andrey.user.name}")

        # Получаем все ДЗ по Python
        homeworks = await HomeworkRepository.get_all()
        # Находим ID предмета Python из групп Андрея
        python_subject_id = None
        for group in andrey.groups:
            if group.subject and group.subject.name == "Python":
                python_subject_id = group.subject.id
                break
        
        if not python_subject_id:
            print("   ❌ Не найден предмет Python в группах Андрея")
            return
            
        python_homeworks = [hw for hw in homeworks if hw.subject_id == python_subject_id]

        if not python_homeworks:
            print("   ❌ Нет ДЗ по Python")
            return

        question_repo = QuestionRepository()
        created_results = 0

        # Проверяем, есть ли уже результаты для Андрея
        existing_results = await HomeworkResultRepository.get_by_student(andrey.id)
        if existing_results:
            print(f"   ⚠️ У Андрея уже есть {len(existing_results)} результатов, пропускаем создание")
            return

        for homework in python_homeworks:

            # Получаем вопросы для этого ДЗ
            homework_questions = await question_repo.get_by_homework(homework.id)
            if not homework_questions:
                continue

            total_questions = len(homework_questions)
            correct_answers = total_questions  # 100% результат
            points_earned = total_questions * 3  # Максимальные баллы

            # Создаем результат ДЗ
            homework_result = await HomeworkResultRepository.create(
                student_id=andrey.id,
                homework_id=homework.id,
                total_questions=total_questions,
                correct_answers=correct_answers,
                points_earned=points_earned,
                is_first_attempt=True,
                points_awarded=True
            )

            # Создаем результаты для каждого вопроса
            question_results_data = []

            for question in homework_questions:
                # Получаем варианты ответов для вопроса
                answer_options = await AnswerOptionRepository.get_by_question(question.id)
                if not answer_options:
                    continue

                # Выбираем правильный ответ
                correct_answer = next((opt for opt in answer_options if opt.is_correct), None)

                # Быстрое время ответа (как у опытного разработчика)
                import random
                time_spent = random.randint(5, 15)  # 5-15 секунд

                question_results_data.append({
                    'question_id': question.id,
                    'selected_answer_id': correct_answer.id if correct_answer else None,
                    'is_correct': True,
                    'time_spent': time_spent,
                    'microtopic_number': question.microtopic_number
                })

            # Создаем результаты вопросов
            if question_results_data:
                await QuestionResultRepository.create_multiple(
                    homework_result.id,
                    question_results_data
                )

            print(f"   ✅ ДЗ '{homework.name}': {correct_answers}/{total_questions} (100%) - {points_earned} баллов")
            created_results += 1

        # Обновляем баллы и уровень
        await StudentRepository.update_points_and_level(andrey.id)

        # Получаем финальные данные
        final_andrey = await StudentRepository.get_by_id(andrey.id)
        if final_andrey:
            print(f"   🎉 Итого создано результатов: {created_results}")
            print(f"   💎 Финальные баллы: {final_andrey.points}")
            print(f"   🏆 Финальный уровень: {final_andrey.level}")

    except Exception as e:
        print(f"   ❌ Ошибка при создании результатов для Андрея: {e}")
