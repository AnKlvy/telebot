from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from common.keyboards import get_main_menu_back_button, get_universal_back_button, back_to_main_button
from typing import List, Any
from database import CourseRepository, SubjectRepository, LessonRepository, HomeworkRepository


def get_homework_management_kb() -> InlineKeyboardMarkup:
    """Клавиатура управления домашними заданиями"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить ДЗ", callback_data="manager_add_homework")],
        [InlineKeyboardButton(text="❌ Удалить ДЗ", callback_data="manager_delete_homework")],
        *get_main_menu_back_button()
    ])

async def get_courses_kb() -> InlineKeyboardMarkup:
    """Клавиатура выбора курса"""
    try:
        courses = await CourseRepository.get_all()
        buttons = []

        for course in courses:
            buttons.append([
                InlineKeyboardButton(
                    text=course.name,
                    callback_data=f"course_{course.id}"
                )
            ])

        buttons.extend(get_main_menu_back_button())
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    except Exception:
        # Fallback на хардкод данные в случае ошибки
        buttons = [
            [InlineKeyboardButton(text="Интенсив. География", callback_data="course_1")],
            [InlineKeyboardButton(text="Интенсив. Математика", callback_data="course_2")],
            *get_main_menu_back_button()
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)

async def get_subjects_kb(course_id: int = None) -> InlineKeyboardMarkup:
    """Клавиатура выбора предмета"""
    try:
        if course_id:
            # Получаем предметы для конкретного курса
            course = await CourseRepository.get_by_id(course_id)
            subjects = course.subjects if course else []
        else:
            # Получаем все предметы
            subjects = await SubjectRepository.get_all()

        buttons = []
        for subject in subjects:
            buttons.append([
                InlineKeyboardButton(
                    text=subject.name,
                    callback_data=f"subject_{subject.id}"
                )
            ])

        buttons.extend(get_main_menu_back_button())
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    except Exception:
        # Fallback на хардкод данные в случае ошибки
        buttons = [
            [InlineKeyboardButton(text="История Казахстана", callback_data="subject_1")],
            [InlineKeyboardButton(text="Математическая грамотность", callback_data="subject_2")],
            [InlineKeyboardButton(text="География", callback_data="subject_3")],
            [InlineKeyboardButton(text="Биология", callback_data="subject_4")],
            [InlineKeyboardButton(text="Химия", callback_data="subject_5")],
            [InlineKeyboardButton(text="Информатика", callback_data="subject_6")],
            *get_main_menu_back_button()
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)

async def get_lessons_kb(subject_id: int = None) -> InlineKeyboardMarkup:
    """Клавиатура выбора урока"""
    try:
        if subject_id:
            lessons = await LessonRepository.get_by_subject(subject_id)
        else:
            lessons = await LessonRepository.get_all()

        buttons = []
        for lesson in lessons:
            buttons.append([
                InlineKeyboardButton(
                    text=lesson.name,
                    callback_data=f"lesson_{lesson.id}"
                )
            ])

        buttons.append([
            InlineKeyboardButton(
                text="➕ Добавить новый урок",
                callback_data="add_new_lesson"
            )
        ])

        buttons.extend(get_main_menu_back_button())
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    except Exception:
        # Fallback на хардкод данные в случае ошибки
        buttons = [
            [InlineKeyboardButton(text="1. Алканы", callback_data="lesson_1")],
            [InlineKeyboardButton(text="2. Изомерия", callback_data="lesson_2")],
            [InlineKeyboardButton(text="3. Кислоты", callback_data="lesson_3")],
            [InlineKeyboardButton(text="➕ Добавить новый урок", callback_data="add_new_lesson")],
            *get_main_menu_back_button()
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_time_limit_kb() -> InlineKeyboardMarkup:
    """Клавиатура выбора времени на ответ"""
    time_options = [10, 20, 30, 60, 120, 180, 240, 300]
    
    buttons = []
    for time in time_options:
        text = f"{time} сек."
        if time >= 60:
            minutes = time // 60
            seconds = time % 60
            text = f"{minutes} мин."
            if seconds > 0:
                text += f" {seconds} сек."
        
        buttons.append([
            InlineKeyboardButton(
                text=text, 
                callback_data=f"time_{time}"
            )
        ])
    
    buttons.extend(get_main_menu_back_button())
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_correct_answer_kb(answer_options: List[str] = None) -> InlineKeyboardMarkup:
    """Клавиатура выбора правильного ответа"""
    buttons = []

    if answer_options:
        # Используем реальные варианты ответов
        letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
        for i, option in enumerate(answer_options):
            if i < len(letters):
                letter = letters[i]
                # Обрезаем длинный текст для отображения
                display_text = option[:30] + "..." if len(option) > 30 else option
                buttons.append([
                    InlineKeyboardButton(
                        text=f"{letter}. {display_text}",
                        callback_data=f"correct_{i}"
                    )
                ])
    else:
        # Fallback на стандартные варианты
        for i, letter in enumerate(["A", "B", "C", "D", "E"]):
            buttons.append([
                InlineKeyboardButton(
                    text=f"Вариант {letter}",
                    callback_data=f"correct_{i}"
                )
            ])

    buttons.extend(get_main_menu_back_button())
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_add_question_kb(question_count: int) -> InlineKeyboardMarkup:
    """Клавиатура для добавления вопросов"""
    buttons = [
        [
            InlineKeyboardButton(
                text="➕ Добавить ещё вопрос", 
                callback_data="add_more_question"
            )
        ],
        [
            InlineKeyboardButton(
                text=f"✅ Завершить ({question_count} вопросов)", 
                callback_data="finish_adding_questions"
            )
        ],
        *get_main_menu_back_button()
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_confirm_homework_kb() -> InlineKeyboardMarkup:
    """Клавиатура подтверждения создания ДЗ"""
    buttons = [
        [
            InlineKeyboardButton(
                text="✅ Подтвердить", 
                callback_data="confirm_homework"
            )
        ],
        # [
        #     InlineKeyboardButton(
        #         text="🔄 Изменить",
        #         callback_data="edit_homework"
        #     )
        # ],
        [
            InlineKeyboardButton(
                text="❌ Отменить", 
                callback_data="cancel_homework"
            )
        ],
        *get_main_menu_back_button()
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def get_homeworks_list_kb(lesson_id: int) -> InlineKeyboardMarkup:
    """Клавиатура со списком ДЗ для удаления"""
    try:
        homeworks = await HomeworkRepository.get_by_lesson(lesson_id)

        buttons = []
        for hw in homeworks:
            buttons.append([
                InlineKeyboardButton(
                    text=hw.name,
                    callback_data=f"delete_hw_{hw.id}"
                )
            ])

        if not homeworks:
            buttons.append([
                InlineKeyboardButton(
                    text="📝 Нет домашних заданий",
                    callback_data="no_homeworks"
                )
            ])

        buttons.extend(get_main_menu_back_button())
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    except Exception:
        # Fallback на хардкод данные в случае ошибки
        buttons = [
            [InlineKeyboardButton(text="Базовое ДЗ по алканам", callback_data="delete_hw_1")],
            [InlineKeyboardButton(text="Углубленное ДЗ по алканам", callback_data="delete_hw_2")],
            [InlineKeyboardButton(text="ДЗ на повторение", callback_data="delete_hw_3")],
            *get_main_menu_back_button()
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_photo_skip_kb() -> InlineKeyboardMarkup:
    """Клавиатура для пропуска добавления фото"""
    buttons = [
        [
            InlineKeyboardButton(
                text="⏩ Пропустить (без фото)",
                callback_data="skip_photo"
            )
        ],
        *get_main_menu_back_button()
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_photo_edit_kb() -> InlineKeyboardMarkup:
    """Клавиатура для редактирования фото"""
    buttons = [
        [
            InlineKeyboardButton(
                text="📷 Изменить фото",
                callback_data="edit_photo"
            )
        ],
        [
            InlineKeyboardButton(
                text="🗑 Удалить фото",
                callback_data="remove_photo"
            )
        ],
        [
            InlineKeyboardButton(
                text="➡️ Продолжить",
                callback_data="continue_without_edit"
            )
        ],
        *get_main_menu_back_button()
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_step_edit_kb(step: str, has_data: bool = True, is_bonus_test: bool = False) -> InlineKeyboardMarkup:
    """Универсальная клавиатура для редактирования на каждом шаге"""
    buttons = []

    # Определяем текст кнопок в зависимости от шага
    edit_texts = {
        "test_name": "✏️ Изменить название",
        "question_text": "✏️ Изменить текст вопроса",
        "photo": "📷 Изменить фото" if has_data else "📷 Добавить фото",
        "answer_options": "✏️ Изменить варианты ответов",
        "correct_answer": "✅ Изменить правильный ответ",
        "time_limit": "⏱ Изменить время",
        "topic": "🏷 Изменить микротему",
        "summary": "✏️ Редактировать"
    }

    continue_texts = {
        "test_name": "➡️ Добавить вопросы",
        "question_text": "📷 Добавить фото",
        "photo": "📝 Ввести варианты ответов" if is_bonus_test else "🏷 Выбрать микротему",
        "answer_options": "✅ Выбрать правильный ответ",
        "correct_answer": "⏱ Установить время",
        "time_limit": "💾 Сохранить вопрос",
        "topic": "📝 Ввести варианты ответов",
        "summary": "➡️ Продолжить"
    }

    edit_text = edit_texts.get(step, "✏️ Редактировать")
    continue_text = continue_texts.get(step, "➡️ Продолжить")

    if has_data or step == "photo":
        buttons.append([
            InlineKeyboardButton(
                text=edit_text,
                callback_data=f"edit_{step}"
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            text=continue_text,
            callback_data=f"continue_{step}"
        )
    ])

    buttons.append(back_to_main_button())
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_question_edit_kb(question_num: int) -> InlineKeyboardMarkup:
    """Клавиатура для редактирования вопроса"""
    buttons = [
        [
            InlineKeyboardButton(
                text="✏️ Изменить текст вопроса",
                callback_data=f"edit_question_text_{question_num}"
            )
        ],
        [
            InlineKeyboardButton(
                text="📷 Изменить фото",
                callback_data=f"edit_question_photo_{question_num}"
            )
        ],
        [
            InlineKeyboardButton(
                text="📝 Изменить варианты ответов",
                callback_data=f"edit_answer_options_{question_num}"
            )
        ],
        [
            InlineKeyboardButton(
                text="✅ Изменить правильный ответ",
                callback_data=f"edit_correct_answer_{question_num}"
            )
        ],
        [
            InlineKeyboardButton(
                text="⏱ Изменить время",
                callback_data=f"edit_time_limit_{question_num}"
            )
        ],
        [
            InlineKeyboardButton(
                text="🏷 Изменить микротему",
                callback_data=f"edit_topic_{question_num}"
            )
        ],
        [
            InlineKeyboardButton(
                text="🗑 Удалить вопрос",
                callback_data=f"delete_question_{question_num}"
            )
        ],
        [
            InlineKeyboardButton(
                text="➡️ Продолжить",
                callback_data="continue_editing"
            )
        ],
        *get_main_menu_back_button()
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)