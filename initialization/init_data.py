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
from initialization.month_control_tests import create_month_control_tests, create_month_control_test_results
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

        # 11. Создание контрольных тестов месяца
        print("\n📊 Создание контрольных тестов месяца...")
        await create_month_control_tests()

        # 12. Создание результатов контрольных тестов месяца
        print("\n📊 Создание результатов контрольных тестов месяца...")
        await create_month_control_test_results()

        # 13. Установка связей между входными и контрольными тестами
        print("\n🔗 Установка связей между входными и контрольными тестами...")
        await link_entry_and_control_tests()

        # 14. Обновление баллов и уровней студентов
        print("\n🔄 Обновление баллов и уровней студентов...")
        await update_all_student_points()

        # 15. Инициализация товаров магазина
        print("\n🛒 Инициализация товаров магазина...")
        await init_shop_items()

        # 16. Инициализация данных пробного ЕНТ
        print("\n🎯 Инициализация данных пробного ЕНТ...")
        await init_trial_ent_data()

        print("\n✅ Инициализация данных завершена успешно!")
        
    except Exception as e:
        print(f"\n❌ Ошибка при инициализации данных: {e}")
        import traceback
        traceback.print_exc()


async def link_entry_and_control_tests():
    """Установка связей parent_test_id между входными и контрольными тестами"""
    try:
        print("🔗 Установка связей между входными и контрольными тестами...")

        from database import MonthTestRepository
        from database.database import get_db_session

        # Получаем все тесты
        all_tests = await MonthTestRepository.get_all()
        entry_tests = [t for t in all_tests if t.test_type == 'entry']
        control_tests = [t for t in all_tests if t.test_type == 'control']

        # Соответствие между входными и контрольными тестами
        test_mappings = [
            ('Контрольный тест по алгебре', 'Контрольный тест по алгебре (Контроль)'),
            ('Геометрия и фигуры', 'Геометрия и фигуры (Контроль)'),
            ('Основы программирования', 'Основы программирования (Контроль)')
        ]

        updated_count = 0

        async with get_db_session() as session:
            for entry_name, control_name in test_mappings:
                # Находим входной тест
                entry_test = next((t for t in entry_tests if t.name == entry_name), None)
                if not entry_test:
                    print(f"   ⚠️ Входной тест '{entry_name}' не найден")
                    continue

                # Находим контрольный тест
                control_test = next((t for t in control_tests if t.name == control_name), None)
                if not control_test:
                    print(f"   ⚠️ Контрольный тест '{control_name}' не найден")
                    continue

                # Проверяем, не установлена ли уже связь
                if control_test.parent_test_id == entry_test.id:
                    print(f"   ✅ Связь уже установлена: {control_name} -> {entry_name}")
                    continue

                # Обновляем parent_test_id
                control_test.parent_test_id = entry_test.id
                session.add(control_test)
                print(f"   ✅ Установлена связь: {control_name} -> {entry_name} (ID: {entry_test.id})")
                updated_count += 1

            await session.commit()

        print(f"🔗 Установка связей завершена! Обновлено: {updated_count}")

    except Exception as e:
        print(f"❌ Ошибка при установке связей между тестами: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(add_initial_data())
