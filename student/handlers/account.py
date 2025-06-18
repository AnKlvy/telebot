from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from ..keyboards.account import get_account_kb

router = Router()

class AccountStates(StatesGroup):
    main = State()

@router.callback_query(F.data == "account")
async def show_account_info(callback: CallbackQuery, state: FSMContext):
    """Показать информацию об аккаунте пользователя"""
    from database import StudentRepository, SubjectRepository

    try:
        # Получаем студента из базы данных
        student = await StudentRepository.get_by_telegram_id(callback.from_user.id)

        if not student:
            await callback.message.edit_text(
                "❌ Информация об аккаунте не найдена.\nВозможно, вы не зарегистрированы в системе.",
                reply_markup=get_account_kb()
            )
            await state.set_state(AccountStates.main)
            return

        # Получаем курсы студента
        from database import CourseRepository
        courses = await CourseRepository.get_by_user_id(callback.from_user.id)
        course_names = [course.name for course in courses] if courses else ["Не назначен"]

        # Получаем предметы студента
        subjects = await SubjectRepository.get_by_user_id(callback.from_user.id)
        subject_names = [subject.name for subject in subjects] if subjects else ["Не назначены"]

        # Формируем информацию о группах
        if student.groups:
            group_names = [f"{group.name} ({group.subject.name})" for group in student.groups]
            group_info = ", ".join(group_names)
        else:
            group_info = "Не назначены"

        # Формируем дату создания
        start_date = student.created_at.strftime("%d.%m.%Y") if student.created_at else "Неизвестно"

        courses_str = ", ".join(course_names)
        subjects_str = ", ".join(subject_names)
        tariff_str = student.tariff.capitalize() if student.tariff else "Не указан"

        await callback.message.edit_text(
            "❓ Аккаунт\n"
            f"📚 Курсы: {courses_str}\n"
            f"📋 Группы: {group_info}\n"
            f"💼 Тариф: {tariff_str}\n"
            f"📆 На курсе с: {start_date}\n"
            f"🧪 Предметы: {subjects_str}\n"
            f"🏆 Баллы: {student.points}\n"
            f"⭐ Уровень: {student.level}",
            reply_markup=get_account_kb()
        )

    except Exception as e:
        print(f"Ошибка при получении информации об аккаунте: {e}")
        await callback.message.edit_text(
            "❌ Ошибка при загрузке информации об аккаунте.",
            reply_markup=get_account_kb()
        )

    await state.set_state(AccountStates.main)