"""
Привязка студентов к курсам
"""
from database import StudentRepository


async def assign_students_to_courses(created_subjects, course_ent, course_it):
    """Привязать студентов к курсам на основе их предметов"""
    if not course_ent or not course_it:
        print("⚠️ Курсы не найдены, пропускаем привязку студентов")
        return

    # Получаем всех студентов
    students = await StudentRepository.get_all()

    for student in students:
        if not student.groups:
            continue

        # Собираем все предметы из групп студента
        student_subjects = set()
        for group in student.groups:
            if group.subject:
                student_subjects.add(group.subject.name)

        course_ids = []

        # Определяем к каким курсам относятся предметы студента
        for subject_name in student_subjects:
            if subject_name in ["Математика", "Физика", "История Казахстана", "Химия", "Биология"]:
                if course_ent.id not in course_ids:
                    course_ids.append(course_ent.id)

            if subject_name in ["Python", "JavaScript", "Java", "Математика"]:
                if course_it.id not in course_ids:
                    course_ids.append(course_it.id)

        # Привязываем студента к курсам
        if course_ids:
            success = await StudentRepository.set_courses(student.id, course_ids)
            if success:
                course_names = []
                if course_ent.id in course_ids:
                    course_names.append("ЕНТ")
                if course_it.id in course_ids:
                    course_names.append("IT")
                print(f"✅ Студент '{student.user.name}' привязан к курсам: {', '.join(course_names)}")
            else:
                print(f"❌ Ошибка привязки студента '{student.user.name}' к курсам")
