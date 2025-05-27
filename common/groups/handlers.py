from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from .states import GroupStates
from .keyboards import get_groups_kb, get_students_kb, get_student_profile_kb

async def show_groups(callback: CallbackQuery, state: FSMContext, role: str):
    """
    Базовый обработчик для показа списка групп
    
    Args:
        callback: Объект CallbackQuery
        state: Контекст состояния FSM
        role: Роль пользователя (curator)
    """
    await callback.message.edit_text(
        "Выберите группу для просмотра:",
        reply_markup=get_groups_kb(role)
    )

async def show_group_students(callback: CallbackQuery, state: FSMContext, role: str):
    """
    Базовый обработчик для показа списка студентов группы
    
    Args:
        callback: Объект CallbackQuery
        state: Контекст состояния FSM
        role: Роль пользователя (curator, teacher)
    """
    group_id = callback.data.replace(f"{role}_group_", "")
    
    # Определяем название группы
    group_names = {
        "chem_premium": "Химия — Премиум",
        "bio_intensive": "Биология — Интенсив",
        "history_basic": "История — Базовый"
    }
    group_name = group_names.get(group_id, "Неизвестная группа")
    
    await state.update_data(selected_group=group_id, group_name=group_name)
    
    await callback.message.edit_text(
        f"Группа: {group_name}\n\n"
        "Выберите ученика для просмотра информации:",
        reply_markup=get_students_kb(role, group_id)
    )

async def show_student_profile(callback: CallbackQuery, state: FSMContext, role: str):
    """
    Базовый обработчик для показа профиля студента
    
    Args:
        callback: Объект CallbackQuery
        state: Контекст состояния FSM
        role: Роль пользователя (curator, teacher)
    """
    # Получаем ID студента из callback_data
    student_id = callback.data.replace(f"{role}_student_", "")
    
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
    await state.update_data(selected_student_id=student_id, student=student)
    
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
        reply_markup=get_student_profile_kb(role)
    )
