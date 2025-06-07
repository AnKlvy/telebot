from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter

from admin.utils.common import (
    curators_db, teachers_db, courses_db, subjects_db, groups_db,
    get_courses_list_kb, get_subjects_list_kb, get_groups_list_kb, 
    get_people_list_kb, get_confirmation_kb, add_person, remove_person
)
from common.keyboards import get_home_kb

router = Router()

class AdminCuratorsStates(StatesGroup):
    # Состояния для добавления куратора
    enter_curator_name = State()
    enter_curator_telegram_id = State()
    select_curator_course = State()
    select_curator_subject = State()
    select_curator_group = State()
    confirm_add_curator = State()
    
    # Состояния для удаления куратора
    select_subject_for_curator_deletion = State()
    select_group_for_curator_deletion = State()
    select_curator_to_delete = State()
    confirm_delete_curator = State()

class AdminTeachersStates(StatesGroup):
    # Состояния для добавления преподавателя
    enter_teacher_name = State()
    enter_teacher_telegram_id = State()
    select_teacher_course = State()
    select_teacher_subject = State()
    select_teacher_group = State()
    confirm_add_teacher = State()
    
    # Состояния для удаления преподавателя
    select_subject_for_teacher_deletion = State()
    select_group_for_teacher_deletion = State()
    select_teacher_to_delete = State()
    confirm_delete_teacher = State()

def generate_staff_handlers(
    router: Router,
    entity_name: str,
    entity_name_accusative: str,
    callback_prefix: str,
    data_storage: dict,
    states_class: StatesGroup
):
    """
    Универсальный генератор для кураторов и преподавателей
    """
    
    # === ДОБАВЛЕНИЕ ===
    
    @router.callback_query(F.data == f"add_{callback_prefix}")
    async def start_add_staff(callback: CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            text=f"Введите имя и фамилию {entity_name_accusative}:",
            reply_markup=get_home_kb()
        )
        await state.set_state(getattr(states_class, f"enter_{callback_prefix}_name"))
    
    @router.message(StateFilter(getattr(states_class, f"enter_{callback_prefix}_name")))
    async def process_staff_name(message: Message, state: FSMContext):
        staff_name = message.text.strip()
        await state.update_data(**{f"{callback_prefix}_name": staff_name})
        await state.set_state(getattr(states_class, f"enter_{callback_prefix}_telegram_id"))
        
        await message.answer(
            text=f"Введите Telegram ID {entity_name_accusative}:",
            reply_markup=get_home_kb()
        )
    
    @router.message(StateFilter(getattr(states_class, f"enter_{callback_prefix}_telegram_id")))
    async def process_staff_telegram_id(message: Message, state: FSMContext):
        try:
            telegram_id = int(message.text.strip())
            await state.update_data(**{f"{callback_prefix}_telegram_id": telegram_id})
            await state.set_state(getattr(states_class, f"select_{callback_prefix}_course"))
            
            await message.answer(
                text=f"Выберите курс для {entity_name_accusative}:",
                reply_markup=get_courses_list_kb(f"{callback_prefix}_course")
            )
        except ValueError:
            await message.answer(
                text="❌ Telegram ID должен быть числом. Попробуйте еще раз:",
                reply_markup=get_home_kb()
            )
    
    @router.callback_query(getattr(states_class, f"select_{callback_prefix}_course"), F.data.startswith(f"{callback_prefix}_course_"))
    async def select_staff_course(callback: CallbackQuery, state: FSMContext):
        course_id = int(callback.data.replace(f"{callback_prefix}_course_", ""))
        course = courses_db.get(course_id)
        
        if not course:
            await callback.message.edit_text(
                text="❌ Курс не найден!",
                reply_markup=get_home_kb()
            )
            return
        
        await state.update_data(**{f"{callback_prefix}_course": course["name"], f"{callback_prefix}_course_id": course_id})
        await state.set_state(getattr(states_class, f"select_{callback_prefix}_subject"))
        
        await callback.message.edit_text(
            text=f"Курс: {course['name']}\n\nВыберите предмет:",
            reply_markup=get_subjects_list_kb(f"{callback_prefix}_subject", course_id)
        )
    
    @router.callback_query(getattr(states_class, f"select_{callback_prefix}_subject"), F.data.startswith(f"{callback_prefix}_subject_"))
    async def select_staff_subject(callback: CallbackQuery, state: FSMContext):
        subject = callback.data.replace(f"{callback_prefix}_subject_", "")
        data = await state.get_data()
        course_name = data.get(f"{callback_prefix}_course", "")
        
        await state.update_data(**{f"{callback_prefix}_subject": subject})
        await state.set_state(getattr(states_class, f"select_{callback_prefix}_group"))
        
        await callback.message.edit_text(
            text=f"Курс: {course_name}\nПредмет: {subject}\n\nВыберите группу:",
            reply_markup=get_groups_list_kb(f"{callback_prefix}_group", subject)
        )
    
    @router.callback_query(getattr(states_class, f"select_{callback_prefix}_group"), F.data.startswith(f"{callback_prefix}_group_"))
    async def select_staff_group(callback: CallbackQuery, state: FSMContext):
        group = callback.data.replace(f"{callback_prefix}_group_", "")
        data = await state.get_data()
        
        staff_name = data.get(f"{callback_prefix}_name", "")
        telegram_id = data.get(f"{callback_prefix}_telegram_id", "")
        course_name = data.get(f"{callback_prefix}_course", "")
        subject = data.get(f"{callback_prefix}_subject", "")
        
        await state.update_data(**{f"{callback_prefix}_group": group})
        await state.set_state(getattr(states_class, f"confirm_add_{callback_prefix}"))
        
        await callback.message.edit_text(
            text=f"📋 Подтверждение добавления:\n\n"
                 f"Имя: {staff_name}\n"
                 f"Telegram ID: {telegram_id}\n"
                 f"Курс: {course_name}\n"
                 f"Предмет: {subject}\n"
                 f"Группа: {group}",
            reply_markup=get_confirmation_kb("add", callback_prefix)
        )
    
    @router.callback_query(getattr(states_class, f"confirm_add_{callback_prefix}"), F.data.startswith(f"confirm_add_{callback_prefix}"))
    async def confirm_add_staff(callback: CallbackQuery, state: FSMContext):
        data = await state.get_data()
        
        staff_name = data.get(f"{callback_prefix}_name", "")
        telegram_id = data.get(f"{callback_prefix}_telegram_id", "")
        course = data.get(f"{callback_prefix}_course", "")
        subject = data.get(f"{callback_prefix}_subject", "")
        group = data.get(f"{callback_prefix}_group", "")
        
        # Добавляем сотрудника
        staff_id = add_person(data_storage, staff_name, telegram_id, 
                             course=course, subject=subject, group=group)
        
        await callback.message.edit_text(
            text=f"✅ {entity_name.capitalize()} '{staff_name}' успешно добавлен!",
            reply_markup=get_home_kb()
        )
        await state.clear()
    
    # === УДАЛЕНИЕ ===
    
    @router.callback_query(F.data == f"remove_{callback_prefix}")
    async def start_remove_staff(callback: CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            text="Выберите предмет:",
            reply_markup=get_subjects_list_kb(f"{callback_prefix}_delete_subject")
        )
        await state.set_state(getattr(states_class, f"select_subject_for_{callback_prefix}_deletion"))
    
    @router.callback_query(getattr(states_class, f"select_subject_for_{callback_prefix}_deletion"), F.data.startswith(f"{callback_prefix}_delete_subject_"))
    async def select_subject_for_staff_deletion(callback: CallbackQuery, state: FSMContext):
        subject = callback.data.replace(f"{callback_prefix}_delete_subject_", "")
        
        await state.update_data(deletion_subject=subject)
        await state.set_state(getattr(states_class, f"select_group_for_{callback_prefix}_deletion"))
        
        await callback.message.edit_text(
            text=f"Предмет: {subject}\n\nВыберите группу:",
            reply_markup=get_groups_list_kb(f"{callback_prefix}_delete_group", subject)
        )
    
    @router.callback_query(getattr(states_class, f"select_group_for_{callback_prefix}_deletion"), F.data.startswith(f"{callback_prefix}_delete_group_"))
    async def select_group_for_staff_deletion(callback: CallbackQuery, state: FSMContext):
        group = callback.data.replace(f"{callback_prefix}_delete_group_", "")
        data = await state.get_data()
        subject = data.get("deletion_subject", "")
        
        await state.update_data(deletion_group=group)
        await state.set_state(getattr(states_class, f"select_{callback_prefix}_to_delete"))
        
        await callback.message.edit_text(
            text=f"Предмет: {subject}\nГруппа: {group}\n\nВыберите {entity_name_accusative} для удаления:",
            reply_markup=get_people_list_kb(data_storage, f"delete_{callback_prefix}", subject, group)
        )
    
    @router.callback_query(getattr(states_class, f"select_{callback_prefix}_to_delete"), F.data.startswith(f"delete_{callback_prefix}_"))
    async def select_staff_to_delete(callback: CallbackQuery, state: FSMContext):
        staff_id = callback.data.replace(f"delete_{callback_prefix}_", "")
        staff = data_storage.get(staff_id)
        
        if not staff:
            await callback.message.edit_text(
                text=f"❌ {entity_name.capitalize()} не найден!",
                reply_markup=get_home_kb()
            )
            return
        
        await state.update_data(**{f"{callback_prefix}_to_delete": staff_id})
        await state.set_state(getattr(states_class, f"confirm_delete_{callback_prefix}"))
        
        await callback.message.edit_text(
            text=f"🗑 Подтверждение удаления:\n\n"
                 f"Имя: {staff.get('name', 'Неизвестно')}\n"
                 f"Предмет: {staff.get('subject', 'Неизвестно')}\n"
                 f"Группа: {staff.get('group', 'Неизвестно')}\n\n"
                 f"⚠️ Это действие нельзя отменить!",
            reply_markup=get_confirmation_kb("delete", callback_prefix, staff_id)
        )
    
    @router.callback_query(getattr(states_class, f"confirm_delete_{callback_prefix}"), F.data.startswith(f"confirm_delete_{callback_prefix}"))
    async def confirm_delete_staff(callback: CallbackQuery, state: FSMContext):
        data = await state.get_data()
        staff_id = data.get(f"{callback_prefix}_to_delete", "")
        
        staff = data_storage.get(staff_id)
        staff_name = staff.get("name", "Неизвестно") if staff else "Неизвестно"
        
        success = remove_person(data_storage, staff_id)
        
        if success:
            await callback.message.edit_text(
                text=f"✅ {entity_name.capitalize()} '{staff_name}' успешно удален!",
                reply_markup=get_home_kb()
            )
        else:
            await callback.message.edit_text(
                text=f"❌ {entity_name.capitalize()} не найден!",
                reply_markup=get_home_kb()
            )
        
        await state.clear()
    
    # === ОТМЕНА ===
    
    @router.callback_query(F.data.startswith(f"cancel_add_{callback_prefix}") | F.data.startswith(f"cancel_delete_{callback_prefix}"))
    async def cancel_staff_action(callback: CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            text="❌ Действие отменено",
            reply_markup=get_home_kb()
        )
        await state.clear()

# Генерируем обработчики для кураторов
generate_staff_handlers(
    router=router,
    entity_name="куратор",
    entity_name_accusative="куратора",
    callback_prefix="curator",
    data_storage=curators_db,
    states_class=AdminCuratorsStates
)

# Генерируем обработчики для преподавателей
generate_staff_handlers(
    router=router,
    entity_name="преподаватель", 
    entity_name_accusative="преподавателя",
    callback_prefix="teacher",
    data_storage=teachers_db,
    states_class=AdminTeachersStates
)
