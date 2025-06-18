"""
Обновление баллов и уровней студентов
"""
from database import StudentRepository


async def update_all_student_points():
    """Обновление баллов и уровней всех студентов"""
    try:
        # Получаем всех студентов
        students = await StudentRepository.get_all()
        
        if not students:
            print("   ⚠️ Студенты не найдены")
            return
            
        updated_count = 0
        
        for student in students:
            try:
                # Получаем текущие данные студента
                current_student = await StudentRepository.get_by_id(student.id)
                if not current_student:
                    continue

                # Обновляем баллы и уровень на основе результатов ДЗ
                success = await StudentRepository.update_points_and_level(student.id)

                if success:
                    # Получаем обновленные данные
                    updated_student = await StudentRepository.get_by_id(student.id)
                    if updated_student:
                        print(f"   ✅ {updated_student.user.name}: {updated_student.points} баллов, уровень '{updated_student.level}'")
                        updated_count += 1
                    else:
                        print(f"   ❌ Не удалось получить обновленные данные для студента {student.user.name}")
                else:
                    print(f"   ❌ Ошибка обновления для студента {student.user.name}")

            except Exception as e:
                print(f"   ❌ Ошибка при обновлении студента {student.user.name}: {e}")
                
        print(f"🔄 Обновление завершено! Обновлено студентов: {updated_count}")
        
    except Exception as e:
        print(f"❌ Ошибка при обновлении баллов и уровней студентов: {e}")
