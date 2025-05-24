from .main import get_curator_main_menu_kb
from .groups import get_curator_groups_kb, get_group_students_kb, get_student_profile_kb
from common.keyboards import get_courses_kb, get_subjects_kb, get_lessons_kb, get_main_menu_back_button
from .homeworks import get_homework_menu_kb, get_groups_kb, get_students_by_homework_kb

__all__ = [
    "get_curator_main_menu_kb", 
    "get_curator_groups_kb", 
    "get_group_students_kb", 
    "get_student_profile_kb",
    "get_courses_kb",
    "get_subjects_kb",
    "get_lessons_kb",
    "get_homework_menu_kb",
    "get_groups_kb",
    "get_students_by_homework_kb",
    "*get_main_menu_back_button"
]