from typing import Dict, List, Any
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from common.keyboards import back_to_main_button
from database import CourseRepository, SubjectRepository, GroupRepository, UserRepository, StudentRepository, CuratorRepository, TeacherRepository, ManagerRepository



# groups_db удален - теперь используется база данных через GroupRepository

students_db = {}
curators_db = {}
teachers_db = {}
managers_db = {}

def get_entity_list_kb(items: List[Any], callback_prefix: str, id_field: str = "id", name_field: str = "name") -> InlineKeyboardMarkup:
    """
    Универсальная клавиатура для выбора из списка сущностей
    
    Args:
        items: Список элементов (может быть список строк или список словарей)
        callback_prefix: Префикс для callback_data
        id_field: Поле для ID (если элементы - словари)
        name_field: Поле для отображаемого имени (если элементы - словари)
    """
    buttons = []
    
    if not items:
        buttons.append([
            InlineKeyboardButton(text="📝 Список пуст", callback_data="empty_list")
        ])
    else:
        for item in items:
            if isinstance(item, dict):
                item_id = item.get(id_field)
                item_name = item.get(name_field)
                callback_data = f"{callback_prefix}_{item_id}"
            else:
                # Если элемент - строка
                item_name = str(item)
                callback_data = f"{callback_prefix}_{item}"
            
            buttons.append([
                InlineKeyboardButton(
                    text=item_name,
                    callback_data=callback_data
                )
            ])
    
    buttons.append(back_to_main_button())
    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def get_courses_list_kb(callback_prefix: str = "select_course") -> InlineKeyboardMarkup:
    """Клавиатура со списком курсов"""
    courses = await get_courses_list()
    courses_list = [{"id": course.id, "name": course.name} for course in courses]
    return get_entity_list_kb(courses_list, callback_prefix)

async def get_subjects_list_kb(callback_prefix: str = "select_subject", course_id: int = None) -> InlineKeyboardMarkup:
    """Клавиатура со списком предметов (опционально отфильтрованных по курсу)"""
    if course_id:
        # Получаем предметы конкретного курса
        subjects = await SubjectRepository.get_by_course(course_id)
    else:
        # Получаем все предметы
        subjects = await SubjectRepository.get_all()

    subjects_list = [{"id": subject.id, "name": subject.name} for subject in subjects]
    return get_entity_list_kb(subjects_list, callback_prefix)

async def get_groups_list_kb(callback_prefix: str = "select_group", subject_id: int = None) -> InlineKeyboardMarkup:
    """Клавиатура со списком групп (опционально отфильтрованных по предмету)"""
    if subject_id:
        groups = await GroupRepository.get_by_subject(subject_id)
    else:
        groups = await GroupRepository.get_all()

    groups_list = [{"id": group.id, "name": group.name} for group in groups]
    return get_entity_list_kb(groups_list, callback_prefix)

def get_people_list_kb(people_db: Dict, callback_prefix: str, subject: str = None, group: str = None) -> InlineKeyboardMarkup:
    """
    Универсальная клавиатура для списка людей (студенты, кураторы, преподаватели)
    с опциональной фильтрацией по предмету и группе
    """
    filtered_people = []
    
    for person_id, person_data in people_db.items():
        # Фильтрация по предмету
        if subject and person_data.get("subject") != subject:
            continue
        
        # Фильтрация по группе
        if group and person_data.get("group") != group:
            continue
        
        filtered_people.append({
            "id": person_id,
            "name": person_data.get("name", "Неизвестно")
        })
    
    return get_entity_list_kb(filtered_people, callback_prefix)

def get_managers_list_kb(callback_prefix: str = "select_manager") -> InlineKeyboardMarkup:
    """Клавиатура со списком менеджеров"""
    managers_list = [{"id": k, "name": v.get("name", "Неизвестно")} for k, v in managers_db.items()]
    return get_entity_list_kb(managers_list, callback_prefix)

def get_confirmation_kb(action: str, entity_type: str, entity_id: str = "") -> InlineKeyboardMarkup:
    """Универсальная клавиатура подтверждения действия"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"confirm_{action}_{entity_type}_{entity_id}")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data=f"cancel_{action}_{entity_type}")],
        back_to_main_button()
        ])

def get_tariff_selection_kb() -> InlineKeyboardMarkup:
    """Клавиатура выбора тарифа для ученика"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 Стандарт", callback_data="tariff_standard")],
        [InlineKeyboardButton(text="⭐ Премиум", callback_data="tariff_premium")],
        back_to_main_button()
    ])



# Функции для работы с данными через SQLAlchemy
async def add_course(name: str, subject_ids: List[int]) -> int:
    """Добавить новый курс с привязкой к существующим предметам по ID"""
    course = await CourseRepository.create(name)

    # Привязываем существующие предметы к курсу по ID
    for subject_id in subject_ids:
        await SubjectRepository.add_to_course(subject_id, course.id)

    return course.id

async def remove_course(course_id: int) -> bool:
    """Удалить курс (связи с предметами удалятся автоматически)"""
    try:
        # При Many-to-Many связи удаление курса автоматически удалит связи
        return await CourseRepository.delete(course_id)
    except Exception as e:
        print(f"Ошибка при удалении курса: {e}")
        return False

async def add_subject(name: str) -> bool:
    """Добавить новый предмет"""
    try:
        await SubjectRepository.create(name)
        return True
    except Exception:
        return False

async def remove_subject(subject_id: int) -> bool:
    """Удалить предмет"""
    return await SubjectRepository.delete(subject_id)

# Функции для получения данных
async def get_courses_list():
    """Получить список курсов"""
    return await CourseRepository.get_all()

async def get_subjects_list():
    """Получить список предметов"""
    return await SubjectRepository.get_all()

async def get_subject_by_id(subject_id: int):
    """Получить предмет по ID"""
    return await SubjectRepository.get_by_id(subject_id)

async def add_group(name: str, subject_id: int) -> bool:
    """Добавить новую группу"""
    try:
        await GroupRepository.create(name, subject_id)
        return True
    except ValueError:
        # Группа уже существует или предмет не найден
        return False

async def remove_group(group_id: int) -> bool:
    """Удалить группу"""
    return await GroupRepository.delete(group_id)

async def check_existing_user_for_role_assignment(telegram_id: int, target_role: str, current_user_telegram_id: int = None) -> dict:
    """
    Проверить существующего пользователя для назначения роли

    Args:
        telegram_id: Telegram ID проверяемого пользователя
        target_role: Целевая роль (student, curator, teacher, manager)
        current_user_telegram_id: Telegram ID текущего пользователя (админа)

    Returns:
        dict: {
            'exists': bool,
            'user': User|None,
            'can_assign': bool,
            'message': str
        }
    """
    from database import UserRepository

    print(f"🔍 DEBUG: check_existing_user_for_role_assignment вызвана")
    print(f"🔍 DEBUG: telegram_id={telegram_id}, target_role={target_role}, current_user_telegram_id={current_user_telegram_id}")

    existing_user = await UserRepository.get_by_telegram_id(telegram_id)

    if not existing_user:
        print(f"🔍 DEBUG: Пользователь не найден")
        return {
            'exists': False,
            'user': None,
            'can_assign': True,
            'message': ''
        }

    print(f"🔍 DEBUG: Найден пользователь: {existing_user.name}, роль: {existing_user.role}")

    # Если это админ добавляет себя
    is_admin_self_assignment = (
        current_user_telegram_id and
        telegram_id == current_user_telegram_id and
        existing_user.role == 'admin'
    )

    print(f"🔍 DEBUG: is_admin_self_assignment = {is_admin_self_assignment}")

    if is_admin_self_assignment:
        print(f"🔍 DEBUG: Разрешаем самоназначение админа")
        return {
            'exists': True,
            'user': existing_user,
            'can_assign': True,
            'message': f"✅ Вы можете добавить себя как {target_role}\n"
                      f"Текущая роль: {existing_user.role}\n"
                      f"Имя: {existing_user.name}"
        }

    # Обычная проверка для других случаев
    print(f"🔍 DEBUG: Блокируем добавление существующего пользователя")
    return {
        'exists': True,
        'user': existing_user,
        'can_assign': False,
        'message': f"❌ Пользователь с Telegram ID {telegram_id} уже существует!\n"
                  f"Имя: {existing_user.name}\n"
                  f"Роль: {existing_user.role}\n\n"
                  f"Введите другой Telegram ID:"
    }

def add_person(person_db: Dict, name: str, telegram_id: int, **kwargs) -> str:
    """Универсальная функция добавления человека"""
    person_id = str(telegram_id)
    person_db[person_id] = {
        "name": name,
        "telegram_id": telegram_id,
        **kwargs
    }
    return person_id

def remove_person(person_db: Dict, person_id: str) -> bool:
    """Универсальная функция удаления человека"""
    if person_id in person_db:
        del person_db[person_id]
        return True
    return False

# Функции для работы со студентами
async def add_student(name: str, telegram_id: int, tariff: str, course_ids: list = None, group_ids: list = None) -> bool:
    """Добавить нового студента или создать профиль студента для существующего пользователя"""
    try:
        # Проверяем, существует ли пользователь
        existing_user = await UserRepository.get_by_telegram_id(telegram_id)

        if existing_user:
            # Пользователь существует - используем его
            user = existing_user
            print(f"🔍 DEBUG: Используем существующего пользователя {user.name} (ID: {user.id})")
        else:
            # Создаем нового пользователя
            user = await UserRepository.create(
                telegram_id=telegram_id,
                name=name,
                role='student'
            )
            print(f"🔍 DEBUG: Создан новый пользователь {user.name} (ID: {user.id})")

        # Создаем профиль студента
        student = await StudentRepository.create(
            user_id=user.id,
            tariff=tariff
        )
        print(f"🔍 DEBUG: Создан профиль студента (ID: {student.id})")

        # Добавляем студента к курсам, если они указаны
        if course_ids:
            course_added = await StudentRepository.set_courses(student.id, course_ids)
            if course_added:
                print(f"🔍 DEBUG: Студент добавлен к курсам: {course_ids}")
            else:
                print(f"⚠️ DEBUG: Не удалось добавить студента к курсам: {course_ids}")

        # Добавляем студента к группам, если они указаны
        if group_ids:
            groups_added = await StudentRepository.set_groups(student.id, group_ids)
            if groups_added:
                print(f"🔍 DEBUG: Студент добавлен к группам: {group_ids}")
            else:
                print(f"⚠️ DEBUG: Не удалось добавить студента к группам: {group_ids}")

        return True
    except Exception as e:
        print(f"❌ DEBUG: Ошибка при добавлении студента: {e}")
        import traceback
        traceback.print_exc()
        return False

async def remove_student(student_id: int) -> bool:
    """Удалить студента"""
    # Получаем студента
    student = await StudentRepository.get_by_id(student_id)
    if not student:
        return False

    # Удаляем пользователя (студент удалится каскадно)
    from sqlalchemy import delete
    from database.models import User
    from database import get_db_session

    async with get_db_session() as session:
        result = await session.execute(delete(User).where(User.id == student.user_id))
        await session.commit()
        return result.rowcount > 0

async def get_students_list_kb(callback_prefix: str = "select_student", course_id: int = None, group_id: int = None) -> InlineKeyboardMarkup:
    """Клавиатура со списком студентов (опционально отфильтрованных по курсу и группе)"""
    students = await StudentRepository.get_by_course_and_group(course_id, group_id)
    students_list = [{"id": student.id, "name": student.user.name} for student in students]
    return get_entity_list_kb(students_list, callback_prefix)

async def get_groups_by_course_kb(callback_prefix: str = "select_group", course_id: int = None) -> InlineKeyboardMarkup:
    """Клавиатура со списком групп для курса"""
    if course_id:
        # Получаем предметы курса через репозиторий
        subjects = await SubjectRepository.get_by_course(course_id)

        # Получаем все группы для предметов этого курса
        all_groups = []
        for subject in subjects:
            subject_groups = await GroupRepository.get_by_subject(subject.id)
            all_groups.extend(subject_groups)

        groups_list = [{"id": group.id, "name": f"{group.name} ({group.subject.name})"} for group in all_groups]
    else:
        groups = await GroupRepository.get_all()
        groups_list = [{"id": group.id, "name": f"{group.name} ({group.subject.name})"} for group in groups]

    return get_entity_list_kb(groups_list, callback_prefix)

async def get_course_by_id(course_id: int):
    """Получить курс по ID"""
    return await CourseRepository.get_by_id(course_id)

async def get_group_by_id(group_id: int):
    """Получить группу по ID"""
    return await GroupRepository.get_by_id(group_id)

# Функции для работы с кураторами
async def add_curator(name: str, telegram_id: int, course_id: int, subject_id: int, group_ids: list) -> bool:
    """Добавить нового куратора или создать профиль куратора для существующего пользователя"""
    try:
        # Проверяем, существует ли пользователь
        existing_user = await UserRepository.get_by_telegram_id(telegram_id)

        if existing_user:
            # Пользователь существует - используем его
            user = existing_user
            print(f"🔍 DEBUG: Используем существующего пользователя {user.name} (ID: {user.id})")
        else:
            # Создаем нового пользователя
            user = await UserRepository.create(
                telegram_id=telegram_id,
                name=name,
                role='curator'
            )
            print(f"🔍 DEBUG: Создан новый пользователь {user.name} (ID: {user.id})")

        # Создаем профиль куратора
        curator = await CuratorRepository.create(
            user_id=user.id,
            course_id=course_id,
            subject_id=subject_id
        )
        print(f"🔍 DEBUG: Создан профиль куратора (ID: {curator.id})")

        # Добавляем куратора во все выбранные группы
        for group_id in group_ids:
            group_added = await CuratorRepository.add_curator_to_group(curator.id, group_id)
            if group_added:
                print(f"🔍 DEBUG: Куратор добавлен в группу (group_id: {group_id})")
            else:
                print(f"⚠️ DEBUG: Не удалось добавить куратора в группу (group_id: {group_id})")

        return True
    except Exception as e:
        print(f"❌ DEBUG: Ошибка при добавлении куратора: {e}")
        import traceback
        traceback.print_exc()
        return False

async def remove_curator(curator_id: int) -> bool:
    """Удалить куратора"""
    # Получаем куратора
    curator = await CuratorRepository.get_by_id(curator_id)
    if not curator:
        return False

    # Удаляем пользователя (куратор удалится каскадно)
    from sqlalchemy import delete
    from database.models import User
    from database import get_db_session

    async with get_db_session() as session:
        result = await session.execute(delete(User).where(User.id == curator.user_id))
        await session.commit()
        return result.rowcount > 0

async def get_curators_list_kb(callback_prefix: str = "select_curator", subject_id: int = None, group_id: int = None) -> InlineKeyboardMarkup:
    """Клавиатура со списком кураторов (опционально отфильтрованных по предмету и группе)"""
    curators = await CuratorRepository.get_by_subject_and_group(subject_id, group_id)
    curators_list = [{"id": curator.id, "name": curator.user.name} for curator in curators]
    return get_entity_list_kb(curators_list, callback_prefix)

# Функции для работы с преподавателями
async def add_teacher(name: str, telegram_id: int, course_id: int, subject_id: int, group_ids: list) -> bool:
    """Добавить нового преподавателя или создать профиль преподавателя для существующего пользователя"""
    try:
        # Проверяем, существует ли пользователь
        existing_user = await UserRepository.get_by_telegram_id(telegram_id)

        if existing_user:
            # Пользователь существует - используем его
            user = existing_user
            print(f"🔍 DEBUG: Используем существующего пользователя {user.name} (ID: {user.id})")
        else:
            # Создаем нового пользователя
            user = await UserRepository.create(
                telegram_id=telegram_id,
                name=name,
                role='teacher'
            )
            print(f"🔍 DEBUG: Создан новый пользователь {user.name} (ID: {user.id})")

        # Создаем профиль преподавателя
        teacher = await TeacherRepository.create(
            user_id=user.id,
            course_id=course_id,
            subject_id=subject_id
        )
        print(f"🔍 DEBUG: Создан профиль преподавателя (ID: {teacher.id})")

        # Добавляем преподавателя во все выбранные группы
        for group_id in group_ids:
            group_added = await TeacherRepository.add_teacher_to_group(teacher.id, group_id)
            if group_added:
                print(f"🔍 DEBUG: Преподаватель добавлен в группу (group_id: {group_id})")
            else:
                print(f"⚠️ DEBUG: Не удалось добавить преподавателя в группу (group_id: {group_id})")

        return True
    except Exception as e:
        print(f"❌ DEBUG: Ошибка при добавлении преподавателя: {e}")
        import traceback
        traceback.print_exc()
        return False

async def remove_teacher(teacher_id: int) -> bool:
    """Удалить преподавателя"""
    # Получаем преподавателя
    teacher = await TeacherRepository.get_by_id(teacher_id)
    if not teacher:
        return False

    # Удаляем пользователя (преподаватель удалится каскадно)
    from sqlalchemy import delete
    from database.models import User
    from database import get_db_session

    async with get_db_session() as session:
        result = await session.execute(delete(User).where(User.id == teacher.user_id))
        await session.commit()
        return result.rowcount > 0

async def get_teachers_list_kb(callback_prefix: str = "select_teacher", subject_id: int = None, group_id: int = None) -> InlineKeyboardMarkup:
    """Клавиатура со списком преподавателей (опционально отфильтрованных по предмету и группе)"""
    teachers = await TeacherRepository.get_by_subject_and_group(subject_id, group_id)
    teachers_list = [{"id": teacher.id, "name": teacher.user.name} for teacher in teachers]
    return get_entity_list_kb(teachers_list, callback_prefix)

# Функции для работы с менеджерами
async def add_manager(name: str, telegram_id: int) -> bool:
    """Добавить нового менеджера или создать профиль менеджера для существующего пользователя"""
    try:
        # Проверяем, существует ли пользователь
        existing_user = await UserRepository.get_by_telegram_id(telegram_id)

        if existing_user:
            # Пользователь существует - используем его
            user = existing_user
            print(f"🔍 DEBUG: Используем существующего пользователя {user.name} (ID: {user.id})")
        else:
            # Создаем нового пользователя
            user = await UserRepository.create(
                telegram_id=telegram_id,
                name=name,
                role='manager'
            )
            print(f"🔍 DEBUG: Создан новый пользователь {user.name} (ID: {user.id})")

        # Создаем профиль менеджера
        manager = await ManagerRepository.create(user_id=user.id)
        print(f"🔍 DEBUG: Создан профиль менеджера (ID: {manager.id})")
        return True
    except Exception as e:
        print(f"❌ DEBUG: Ошибка при добавлении менеджера: {e}")
        import traceback
        traceback.print_exc()
        return False

async def remove_manager(manager_id: int) -> bool:
    """Удалить менеджера"""
    # Получаем менеджера
    manager = await ManagerRepository.get_by_id(manager_id)
    if not manager:
        return False

    # Удаляем пользователя (менеджер удалится каскадно)
    from sqlalchemy import delete
    from database.models import User
    from database import get_db_session

    async with get_db_session() as session:
        result = await session.execute(delete(User).where(User.id == manager.user_id))
        await session.commit()
        return result.rowcount > 0

async def get_managers_list_kb(callback_prefix: str = "select_manager") -> InlineKeyboardMarkup:
    """Клавиатура со списком менеджеров"""
    managers = await ManagerRepository.get_all()
    managers_list = [{"id": manager.id, "name": manager.user.name} for manager in managers]
    return get_entity_list_kb(managers_list, callback_prefix)

# Функции для множественного выбора групп
async def get_groups_selection_kb(selected_group_ids: list, subject_id: int):
    """Клавиатура для выбора групп с возможностью множественного выбора"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    from common.keyboards import back_to_main_button

    buttons = []

    # Получаем все группы предмета из базы данных
    groups = await GroupRepository.get_by_subject(subject_id)

    for group in groups:
        if group.id in selected_group_ids:
            # Группа уже выбрана
            buttons.append([
                InlineKeyboardButton(
                    text=f"✅ {group.name}",
                    callback_data=f"unselect_group_{group.id}"
                )
            ])
        else:
            # Группа не выбрана
            buttons.append([
                InlineKeyboardButton(
                    text=f"⬜ {group.name}",
                    callback_data=f"select_group_{group.id}"
                )
            ])

    # Кнопки управления
    if selected_group_ids:
        buttons.append([
            InlineKeyboardButton(text="✅ Готово", callback_data="finish_group_selection")
        ])

    buttons.extend([
        back_to_main_button()
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Функции для множественного выбора курсов
async def get_courses_selection_kb(selected_course_ids: list):
    """Клавиатура для выбора курсов с возможностью множественного выбора"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    from common.keyboards import back_to_main_button

    buttons = []

    # Получаем все курсы из базы данных
    courses = await CourseRepository.get_all()

    for course in courses:
        if course.id in selected_course_ids:
            # Курс уже выбран
            buttons.append([
                InlineKeyboardButton(
                    text=f"✅ {course.name}",
                    callback_data=f"unselect_course_{course.id}"
                )
            ])
        else:
            # Курс не выбран
            buttons.append([
                InlineKeyboardButton(
                    text=f"⬜ {course.name}",
                    callback_data=f"select_course_{course.id}"
                )
            ])

    # Кнопки управления
    if selected_course_ids:
        buttons.append([
            InlineKeyboardButton(text="✅ Готово", callback_data="finish_course_selection")
        ])

    buttons.extend([
        back_to_main_button()
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Функции для множественного выбора групп студентов
async def get_student_groups_selection_kb(selected_group_ids: list, course_ids: list = None):
    """Клавиатура для выбора групп студента с возможностью множественного выбора"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    from common.keyboards import back_to_main_button

    buttons = []

    # Получаем группы из базы данных
    from database import GroupRepository, SubjectRepository
    if course_ids:
        # Получаем группы, связанные с выбранными курсами через предметы
        groups = []
        for course_id in course_ids:
            # Получаем предметы курса
            subjects = await SubjectRepository.get_by_course(course_id)
            # Получаем группы для каждого предмета
            for subject in subjects:
                subject_groups = await GroupRepository.get_by_subject(subject.id)
                groups.extend(subject_groups)
        # Убираем дубликаты
        unique_groups = {group.id: group for group in groups}.values()
        groups = list(unique_groups)
    else:
        # Получаем все группы
        groups = await GroupRepository.get_all()

    for group in groups:
        group_name = f"{group.name} ({group.subject.name})" if group.subject else group.name
        if group.id in selected_group_ids:
            # Группа уже выбрана
            buttons.append([
                InlineKeyboardButton(
                    text=f"✅ {group_name}",
                    callback_data=f"unselect_student_group_{group.id}"
                )
            ])
        else:
            # Группа не выбрана
            buttons.append([
                InlineKeyboardButton(
                    text=f"⬜ {group_name}",
                    callback_data=f"select_student_group_{group.id}"
                )
            ])

    # Кнопки управления
    if selected_group_ids:
        buttons.append([
            InlineKeyboardButton(text="✅ Готово", callback_data="finish_student_group_selection")
        ])

    buttons.extend([
        back_to_main_button()
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)
