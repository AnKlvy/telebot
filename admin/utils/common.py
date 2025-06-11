from typing import Dict, List, Any
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from common.keyboards import back_to_main_button
from database import CourseRepository, SubjectRepository, GroupRepository, UserRepository, StudentRepository, CuratorRepository, TeacherRepository



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
async def add_student(name: str, telegram_id: int, group_id: int, tariff: str) -> bool:
    """Добавить нового студента"""
    try:
        # Сначала создаем пользователя
        user = await UserRepository.create(
            telegram_id=telegram_id,
            name=name,
            role='student'
        )

        # Затем создаем профиль студента
        await StudentRepository.create(
            user_id=user.id,
            group_id=group_id,
            tariff=tariff
        )
        return True
    except Exception:
        # Студент уже существует или другая ошибка
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
async def add_curator(name: str, telegram_id: int, course_id: int, subject_id: int, group_id: int) -> bool:
    """Добавить нового куратора"""
    try:
        # Сначала создаем пользователя
        user = await UserRepository.create(
            telegram_id=telegram_id,
            name=name,
            role='curator'
        )

        # Затем создаем профиль куратора
        await CuratorRepository.create(
            user_id=user.id,
            course_id=course_id,
            subject_id=subject_id,
            group_id=group_id
        )
        return True
    except Exception:
        # Куратор уже существует или другая ошибка
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
async def add_teacher(name: str, telegram_id: int, course_id: int, subject_id: int, group_id: int) -> bool:
    """Добавить нового преподавателя"""
    try:
        # Сначала создаем пользователя
        user = await UserRepository.create(
            telegram_id=telegram_id,
            name=name,
            role='teacher'
        )

        # Затем создаем профиль преподавателя
        await TeacherRepository.create(
            user_id=user.id,
            course_id=course_id,
            subject_id=subject_id,
            group_id=group_id
        )
        return True
    except Exception:
        # Преподаватель уже существует или другая ошибка
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
