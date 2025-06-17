from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from common.keyboards import get_home_kb
from ..keyboards.main import get_curator_main_menu_kb
from ..keyboards.messages import (
    get_messages_menu_kb, get_groups_for_message_kb, 
    get_students_for_message_kb, get_confirm_message_kb
)

router = Router()

class MessageStates(StatesGroup):
    main = State()
    # Состояния для индивидуальных сообщений
    select_group_individual = State()
    select_student = State()
    enter_individual_message = State()
    confirm_individual_message = State()
    # Состояния для массовых сообщений
    select_group_mass = State()
    enter_mass_message = State()
    confirm_mass_message = State()

@router.callback_query(F.data == "curator_messages")
async def show_messages_menu(callback: CallbackQuery, state: FSMContext):
    """Показать меню сообщений"""
    await callback.message.edit_text(
        "Выберите тип сообщения:",
        reply_markup=get_messages_menu_kb()
    )
    await state.set_state(MessageStates.main)

# Обработчики для индивидуальных сообщений
@router.callback_query(MessageStates.main, F.data == "individual_message")
async def select_group_for_individual(callback: CallbackQuery, state: FSMContext):
    """Выбор группы для индивидуального сообщения"""
    await callback.message.edit_text(
        "Выберите группу ученика:",
        reply_markup=await get_groups_for_message_kb(callback.from_user.id)
    )
    await state.set_state(MessageStates.select_group_individual)

@router.callback_query(MessageStates.select_group_individual, F.data.startswith("msg_group_"))
async def select_student_for_message(callback: CallbackQuery, state: FSMContext):
    """Выбор ученика для индивидуального сообщения"""
    group_id = int(callback.data.replace("msg_group_", ""))
    await state.update_data(selected_group=group_id)

    await callback.message.edit_text(
        "Выберите ученика для отправки сообщения:",
        reply_markup=await get_students_for_message_kb(group_id)
    )
    await state.set_state(MessageStates.select_student)

@router.callback_query(MessageStates.select_student, F.data.startswith("msg_student_"))
async def enter_individual_message(callback: CallbackQuery, state: FSMContext):
    """Ввод текста индивидуального сообщения"""
    student_id = int(callback.data.replace("msg_student_", ""))

    try:
        from database import StudentRepository

        # Получаем реального студента из базы данных
        student = await StudentRepository.get_by_id(student_id)

        if not student:
            await callback.message.edit_text(
                "❌ Студент не найден",
                reply_markup=await get_groups_for_message_kb(callback.from_user.id)
            )
            return

        student_name = student.user.name
        await state.update_data(selected_student=student_id, student_name=student_name)

        await callback.message.edit_text(
            f"Введите текст сообщения для ученика {student_name}:",
            reply_markup=get_home_kb()
        )

    except Exception as e:
        print(f"❌ Ошибка при получении студента: {e}")
        await callback.message.edit_text(
            "❌ Ошибка при загрузке данных студента",
            reply_markup=await get_groups_for_message_kb(callback.from_user.id)
        )
        return
    await state.set_state(MessageStates.enter_individual_message)

@router.message(MessageStates.enter_individual_message)
async def confirm_individual_message(message: Message, state: FSMContext):
    """Подтверждение отправки индивидуального сообщения"""
    message_text = message.text
    user_data = await state.get_data()
    student_name = user_data.get("student_name", "Неизвестный ученик")

    await state.update_data(message_text=message_text)

    # Используем message.answer вместо callback.message.edit_text
    await message.answer(
        f"Проверьте сообщение для ученика {student_name}:\n\n"
        f"{message_text}",
        reply_markup=get_confirm_message_kb()
    )
    await state.set_state(MessageStates.confirm_individual_message)

@router.callback_query(MessageStates.confirm_individual_message, F.data == "send_message")
async def send_individual_message(callback: CallbackQuery, state: FSMContext):
    """Отправка индивидуального сообщения"""
    user_data = await state.get_data()
    student_id = user_data.get("selected_student")
    student_name = user_data.get("student_name", "Неизвестный ученик")
    message_text = user_data.get("message_text", "")

    # Получаем бота из контекста
    bot = callback.bot

    try:
        from database import StudentRepository

        # Получаем реального студента из базы данных
        student = await StudentRepository.get_by_id(student_id)

        if not student:
            await callback.message.edit_text(
                f"❌ Студент не найден в базе данных",
                reply_markup=get_messages_menu_kb()
            )
            await state.set_state(MessageStates.main)
            return

        # Получаем Telegram ID ученика
        telegram_id = student.user.telegram_id

        success = False
        error_message = ""

        if telegram_id:
            try:
                # Отправляем сообщение ученику
                await bot.send_message(
                    chat_id=telegram_id,
                    text=f"Сообщение от куратора:\n\n{message_text}"
                )
                success = True
            except Exception as e:
                print(f"Ошибка при отправке сообщения: {e}")
                # Проверяем тип ошибки
                error_str = str(e)
                if "Forbidden" in error_str or "bot was blocked" in error_str or "chat not found" in error_str:
                    error_message = f"❌ Ученик {student_name} никогда не писал боту.\n\nПопросите ученика написать боту любое сообщение (например, /start), а затем попробуйте снова."
                else:
                    error_message = f"❌ Не удалось отправить сообщение ученику {student_name}.\nОшибка: {error_str}"
        else:
            error_message = f"❌ У ученика {student_name} не указан Telegram ID."

        if success:
            await callback.message.edit_text(
                f"✅ Сообщение успешно отправлено ученику {student_name}!",
                reply_markup=get_messages_menu_kb()
            )
        else:
            await callback.message.edit_text(
                error_message,
                reply_markup=get_messages_menu_kb()
            )

    except Exception as e:
        print(f"❌ Ошибка при отправке сообщения: {e}")
        await callback.message.edit_text(
            f"❌ Ошибка при отправке сообщения ученику {student_name}",
            reply_markup=get_messages_menu_kb()
        )

    await state.set_state(MessageStates.main)

# Обработчики для массовой рассылки
@router.callback_query(MessageStates.main, F.data == "mass_message")
async def select_group_for_mass(callback: CallbackQuery, state: FSMContext):
    """Выбор группы для массовой рассылки"""
    await callback.message.edit_text(
        "Выберите группу для массовой рассылки:",
        reply_markup=await get_groups_for_message_kb(callback.from_user.id)
    )
    await state.set_state(MessageStates.select_group_mass)

@router.callback_query(MessageStates.select_group_mass, F.data.startswith("msg_group_"))
async def enter_mass_message(callback: CallbackQuery, state: FSMContext):
    """Ввод текста массовой рассылки"""
    group_id = int(callback.data.replace("msg_group_", ""))

    try:
        from database import GroupRepository

        # Получаем реальную группу из базы данных
        group = await GroupRepository.get_by_id(group_id)

        if not group:
            await callback.message.edit_text(
                "❌ Группа не найдена",
                reply_markup=await get_groups_for_message_kb(callback.from_user.id)
            )
            return

        group_name = f"{group.name}"
        if group.subject:
            group_name += f" ({group.subject.name})"

        await state.update_data(selected_group=group_id, group_name=group_name)

        await callback.message.edit_text(
            f"Введите текст сообщения для рассылки всем ученикам группы {group_name}:",
            reply_markup=get_home_kb()
        )

    except Exception as e:
        print(f"❌ Ошибка при получении группы: {e}")
        await callback.message.edit_text(
            "❌ Ошибка при загрузке данных группы",
            reply_markup=await get_groups_for_message_kb(callback.from_user.id)
        )
        return

    await state.set_state(MessageStates.enter_mass_message)

@router.message(MessageStates.enter_mass_message)
async def confirm_mass_message(message: Message, state: FSMContext):
    """Подтверждение отправки массовой рассылки"""
    message_text = message.text
    user_data = await state.get_data()
    group_name = user_data.get("group_name", "Неизвестная группа")
    
    await state.update_data(message_text=message_text)
    
    # Используем message.answer вместо callback.message.edit_text
    await message.answer(
        f"Проверьте сообщение для рассылки всем ученикам группы {group_name}:\n\n"
        f"{message_text}",
        reply_markup=get_confirm_message_kb()
    )
    await state.set_state(MessageStates.confirm_mass_message)

@router.callback_query(MessageStates.confirm_mass_message, F.data == "send_message")
async def send_mass_message(callback: CallbackQuery, state: FSMContext):
    """Отправка массовой рассылки"""
    user_data = await state.get_data()
    group_id = user_data.get("selected_group")
    group_name = user_data.get("group_name", "Неизвестная группа")
    message_text = user_data.get("message_text", "")

    # Получаем бота из контекста
    bot = callback.bot

    try:
        from database import StudentRepository

        # Получаем реальных студентов группы из базы данных
        students = await StudentRepository.get_by_group(group_id)

        if not students:
            await callback.message.edit_text(
                f"❌ В группе {group_name} нет студентов",
                reply_markup=get_messages_menu_kb()
            )
            await state.set_state(MessageStates.main)
            return

        # Счетчики для статистики
        sent_count = 0
        failed_count = 0

        # Отправляем сообщение каждому ученику группы
        blocked_students = []
        no_id_students = []

        for student in students:
            telegram_id = student.user.telegram_id
            if telegram_id:
                try:
                    # Отправляем сообщение ученику
                    await bot.send_message(
                        chat_id=telegram_id,
                        text=f"Сообщение от куратора для группы {group_name}:\n\n{message_text}"
                    )
                    sent_count += 1
                except Exception as e:
                    error_str = str(e)
                    print(f"Ошибка при отправке сообщения ученику {student.user.name}: {e}")
                    if "Forbidden" in error_str or "bot was blocked" in error_str or "chat not found" in error_str:
                        blocked_students.append(student.user.name)
                    failed_count += 1
            else:
                print(f"У студента {student.user.name} нет Telegram ID")
                no_id_students.append(student.user.name)
                failed_count += 1

        # Формируем отчет об отправке
        if sent_count > 0:
            status_text = f"✅ Сообщение успешно отправлено {sent_count} ученикам группы {group_name}!"

            if blocked_students:
                status_text += f"\n\n⚠️ Не получили сообщение ({len(blocked_students)} чел.):\n"
                for name in blocked_students:
                    status_text += f"• {name} (никогда не писал боту)\n"
                status_text += "\nПопросите этих учеников написать боту /start"

            if no_id_students:
                status_text += f"\n\n❌ Нет Telegram ID ({len(no_id_students)} чел.):\n"
                for name in no_id_students:
                    status_text += f"• {name}\n"
        else:
            status_text = f"❌ Не удалось отправить сообщение ни одному ученику группы {group_name}."

            if blocked_students:
                status_text += f"\n\nПричина: все ученики никогда не писали боту.\nПопросите учеников написать боту /start"
            elif no_id_students:
                status_text += f"\n\nПричина: у всех учеников отсутствует Telegram ID."

        await callback.message.edit_text(
            status_text,
            reply_markup=get_messages_menu_kb()
        )

    except Exception as e:
        print(f"❌ Ошибка при массовой рассылке: {e}")
        await callback.message.edit_text(
            f"❌ Ошибка при отправке сообщений группе {group_name}",
            reply_markup=get_messages_menu_kb()
        )

    await state.set_state(MessageStates.main)

# Обработчики для отмены и навигации
@router.callback_query(F.data == "cancel_message")
async def cancel_message(callback: CallbackQuery, state: FSMContext):
    """Отмена отправки сообщения"""
    current_state = await state.get_state()
    
    if current_state == MessageStates.confirm_individual_message.state:
        await callback.message.edit_text(
            "❌ Отправка индивидуального сообщения отменена.",
            reply_markup=get_messages_menu_kb()
        )
    elif current_state == MessageStates.confirm_mass_message.state:
        await callback.message.edit_text(
            "❌ Отправка массовой рассылки отменена.",
            reply_markup=get_messages_menu_kb()
        )
    else:
        await callback.message.edit_text(
            "❌ Операция отменена.",
            reply_markup=get_messages_menu_kb()
        )
    
    await state.set_state(MessageStates.main)

@router.callback_query(F.data == "back_to_groups_message")
async def back_to_groups_message(callback: CallbackQuery, state: FSMContext):
    """Вернуться к выбору группы"""
    await select_group_for_individual(callback, state)

@router.callback_query(F.data == "back_to_messages_menu")
async def back_to_messages_menu(callback: CallbackQuery, state: FSMContext):
    """Вернуться в меню сообщений"""
    await show_messages_menu(callback, state)

