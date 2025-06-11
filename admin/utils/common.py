from typing import Dict, List, Any
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from common.keyboards import back_to_main_button
from database import CourseRepository, SubjectRepository



groups_db = {
    "Математика": ["МАТ-1", "МАТ-2", "МАТ-3"],
    "Физика": ["ФИЗ-1", "ФИЗ-2"],
    "Python": ["PY-1", "PY-2", "PY-3"]
}

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

def get_groups_list_kb(callback_prefix: str = "select_group", subject: str = None) -> InlineKeyboardMarkup:
    """Клавиатура со списком групп (опционально отфильтрованных по предмету)"""
    if subject and subject in groups_db:
        groups_list = groups_db[subject]
    else:
        # Показываем все группы
        groups_list = []
        for subject_groups in groups_db.values():
            groups_list.extend(subject_groups)
    
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

def add_group(name: str, subject: str) -> bool:
    """Добавить новую группу"""
    if subject not in groups_db:
        groups_db[subject] = []
    
    if name not in groups_db[subject]:
        groups_db[subject].append(name)
        return True
    return False

def remove_group(name: str, subject: str) -> bool:
    """Удалить группу"""
    if subject in groups_db and name in groups_db[subject]:
        groups_db[subject].remove(name)
        return True
    return False

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
