"""
Главный файл инициализации данных
Разделен на модули для лучшей организации кода
"""
import asyncio
import sys
import os

# Добавляем корневую папку проекта в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from initialization.courses_subjects import create_courses_and_subjects
from initialization.groups_users import create_groups_and_users
from initialization.lessons_homework import create_lessons_and_homework
from initialization.test_data import add_test_homework_results, create_results_for_andrey, \
    add_javascript_homework_results
from initialization.admin_roles import add_admin_roles
from initialization.student_assignments import assign_students_to_courses
from initialization.month_tests import add_test_month_tests
from initialization.update_points import update_all_student_points
from initialization.course_entry_test_data import create_course_entry_test_results
from initialization.month_entry_test_data import create_month_entry_test_results

from initialization.trial_ent_data import init_trial_ent_data
from initialization.init_shop_data import init_shop_items


async def add_initial_data():
    """Основная функция инициализации всех данных"""
    print("🚀 Начинаем инициализацию данных...")

    try:
        # 0. Создание схемы базы данных
        print("\n🗄️ Создание схемы базы данных...")
        from database.database import init_database
        await init_database()
        print("   ✅ Схема базы данных создана")
        # 1. Создание курсов и предметов
        print("\n📚 Создание курсов и предметов...")
        created_subjects, course_ent, course_it = await create_courses_and_subjects()
        
        # 2. Создание групп и пользователей
        print("\n👥 Создание групп и пользователей...")
        await create_groups_and_users(created_subjects)
        
        # 3. Создание уроков и домашних заданий
        print("\n📝 Создание уроков и домашних заданий...")
        await create_lessons_and_homework(created_subjects, [course_ent, course_it])
        
        # 4. Добавление ролей админам (создаем профили студентов для админов)
        print("\n👑 Добавление ролей админам...")
        await add_admin_roles(created_subjects, course_ent, course_it)

        # 5. Добавление тестовых результатов ДЗ
        print("\n📊 Добавление тестовых результатов ДЗ...")
        await add_test_homework_results()

        print("\n🎯 Создание результатов для Андрея...")
        await create_results_for_andrey()

        # 6. Добавление результатов ДЗ по JavaScript
        print("\n📊 Добавление результатов ДЗ по JavaScript...")
        await add_javascript_homework_results()

        # 7. Привязка студентов к курсам
        print("\n🔗 Привязка студентов к курсам...")
        await assign_students_to_courses(created_subjects, course_ent, course_it)
        
        # 8. Добавление тестовых тестов месяца
        print("\n🗓️ Добавление тестовых тестов месяца...")
        await add_test_month_tests(created_subjects)

        # 9. Создание результатов входных тестов курса
        print("\n📊 Создание результатов входных тестов курса...")
        await create_course_entry_test_results()

        # 10. Создание результатов входных тестов месяца
        print("\n📊 Создание результатов входных тестов месяца...")
        await create_month_entry_test_results()



        # 11. Обновление баллов и уровней студентов
        print("\n🔄 Обновление баллов и уровней студентов...")
        await update_all_student_points()

        # 12. Инициализация товаров магазина
        print("\n🛒 Инициализация товаров магазина...")
        await init_shop_items()

        # 13. Инициализация данных пробного ЕНТ
        print("\n🎯 Инициализация данных пробного ЕНТ...")
        await init_trial_ent_data()

        print("\n✅ Инициализация данных завершена успешно!")
        
    except Exception as e:
        print(f"\n❌ Ошибка при инициализации данных: {e}")
        import traceback
        traceback.print_exc()




if __name__ == "__main__":
    asyncio.run(add_initial_data())
