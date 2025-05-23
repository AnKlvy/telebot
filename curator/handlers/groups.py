from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from ..keyboards.groups import get_curator_groups_kb, get_group_students_kb, get_student_profile_kb
from ..keyboards.main import get_curator_main_menu_kb

router = Router()

class CuratorGroupStates(StatesGroup):
    select_group = State()
    select_student = State()
    student_profile = State()

@router.callback_query(F.data == "curator_my_group")
async def show_curator_groups(callback: CallbackQuery, state: FSMContext):
    """Показать список групп куратора"""
    await callback.message.edit_text(
        "Выберите группу для просмотра:",
        reply_markup=get_curator_groups_kb()
    )
    await state.set_state(CuratorGroupStates.select_group)

@router.callback_query(CuratorGroupStates.select_group, F.data.startswith("group_"))
async def show_group_students(callback: CallbackQuery, state: FSMContext):
    """Показать список учеников в выбранной группе"""
    group_id = callback.data.replace("group_", "")
    
    # Определяем название группы
    group_names = {
        "chem_premium": "Химия — Премиум",
        "bio_intensive": "Биология — Интенсив",
        "history_basic": "История — Базовый"
    }
    group_name = group_names.get(group_id, "Неизвестная группа")
    
    await state.update_data(current_group_id=group_id, current_group_name=group_name)
    
    await callback.message.edit_text(
        f"Группа: {group_name}\n\n"
        "Выберите ученика для просмотра информации:",
        reply_markup=get_group_students_kb(group_id)
    )
    await state.set_state(CuratorGroupStates.select_student)

@router.callback_query(CuratorGroupStates.select_student, F.data.startswith("student_"))
async def show_student_profile(callback: CallbackQuery, state: FSMContext):
    """Показать профиль выбранного ученика"""
    # Получаем ID студента из callback_data
    student_id = callback.data.replace("student_", "")
    
    # Хардкодим данные для каждого студента
    if student_id == "1":
        student = {
            "name": "Аружан Ахметова",
            "telegram": "@aruzhan_chem",
            "subject": "Химия",
            "points": 870,
            "level": "🧪 Практик",
            "homeworks_completed": 28,
            "last_homework_date": "14.05.2025",
            "completion_percentage": 30
        }
    elif student_id == "2":
        student = {
            "name": "Мадияр Сапаров",
            "telegram": "@madiyar_bio",
            "subject": "Биология",
            "points": 920,
            "level": "🔬 Исследователь",
            "homeworks_completed": 32,
            "last_homework_date": "15.05.2025",
            "completion_percentage": 35
        }
    elif student_id == "3":
        student = {
            "name": "Диана Ержанова",
            "telegram": "@diana_history",
            "subject": "История",
            "points": 750,
            "level": "📚 Теоретик",
            "homeworks_completed": 25,
            "last_homework_date": "12.05.2025",
            "completion_percentage": 28
        }
    else:
        student = {
            "name": "Неизвестный ученик",
            "telegram": "Не указан",
            "subject": "Не указан",
            "points": 0,
            "level": "Не определен",
            "homeworks_completed": 0,
            "last_homework_date": "Нет данных",
            "completion_percentage": 0
        }
    
    # Сохраняем данные в состоянии
    await state.update_data(current_student_id=student_id, current_student=student)
    
    # Формируем сообщение
    await callback.message.edit_text(
        f"👤 {student['name']}\n"
        f"📞 Telegram: {student['telegram']}\n"
        f"📚 Предмет: {student['subject']}\n"
        f"🎯 Баллы: {student['points']}\n"
        f"📈 Уровень: {student['level']}\n"
        f"📋 Выполнено ДЗ: {student['homeworks_completed']} (с учетом повторных)\n"
        f"🕓 Последнее выполненное ДЗ: {student['last_homework_date']}\n"
        f"🕓% выполнения ДЗ: {student['completion_percentage']}%",
        reply_markup=get_student_profile_kb()
    )
    await state.set_state(CuratorGroupStates.student_profile)

@router.callback_query(F.data == "back_to_curator_main")
async def back_to_main_menu(callback: CallbackQuery, state: FSMContext):
    """Вернуться в главное меню куратора"""
    await callback.message.edit_text(
        "Добро пожаловать в панель куратора!\n"
        "Выберите действие из меню ниже:",
        reply_markup=get_curator_main_menu_kb()
    )
    await state.clear()

@router.callback_query(F.data == "back_to_groups")
async def back_to_groups_list(callback: CallbackQuery, state: FSMContext):
    """Вернуться к списку групп"""
    await show_curator_groups(callback, state)

@router.callback_query(F.data == "back_to_students")
async def back_to_students_list(callback: CallbackQuery, state: FSMContext):
    """Вернуться к списку учеников"""
    user_data = await state.get_data()
    group_id = user_data.get("current_group_id")
    group_name = user_data.get("current_group_name", "Группа")
    
    await callback.message.edit_text(
        f"Группа: {group_name}\n\n"
        "Выберите ученика для просмотра информации:",
        reply_markup=get_group_students_kb(group_id)
    )
    await state.set_state(CuratorGroupStates.select_student)