from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from ..keyboards.curator_contact import get_curator_subjects_kb, get_back_to_curator_kb
from database import StudentRepository, CuratorRepository, SubjectRepository
from common.navigation import log

router = Router()

class CuratorStates(StatesGroup):
    main = State()
    curator_info = State()

@router.callback_query(F.data == "curator")
async def show_curator_menu(callback: CallbackQuery, state: FSMContext):
    """Показать меню выбора предмета для связи с куратором"""
    await log("show_curator_menu", "student", state)

    # Получаем студента по telegram_id
    student = await StudentRepository.get_by_telegram_id(callback.from_user.id)
    if not student:
        await callback.message.edit_text(
            "❌ Профиль студента не найден. Обратитесь к администратору.",
            reply_markup=get_back_to_curator_kb()
        )
        return

    # Получаем предметы студента, по которым есть кураторы
    subjects_with_curators = []

    # Проходим по всем группам студента
    for group in student.groups:
        if group.subject:
            # Проверяем, есть ли кураторы по этому предмету для данного студента
            curators = await CuratorRepository.get_curators_for_student_subject(student.id, group.subject.id)
            if curators and group.subject not in subjects_with_curators:
                subjects_with_curators.append(group.subject)

    if not subjects_with_curators:
        await callback.message.edit_text(
            "❌ По вашим предметам кураторы не назначены. Обратитесь к администратору.",
            reply_markup=get_back_to_curator_kb()
        )
        return

    await callback.message.edit_text(
        "📞 Связь с куратором\n\n"
        "Нужна помощь?\n"
        "Выбери предмет — я покажу, кто твой куратор и как с ним связаться:",
        reply_markup=await get_curator_subjects_kb(subjects_with_curators)
    )
    await state.set_state(CuratorStates.main)

@router.callback_query(CuratorStates.main, F.data.startswith("curator_"))
async def show_curator_info(callback: CallbackQuery, state: FSMContext):
    """Показать информацию о кураторе по выбранному предмету"""
    await log("show_curator_info", "student", state)

    subject_id = int(callback.data.replace("curator_", ""))

    # Получаем студента
    student = await StudentRepository.get_by_telegram_id(callback.from_user.id)
    if not student:
        await callback.message.edit_text(
            "❌ Профиль студента не найден.",
            reply_markup=get_back_to_curator_kb()
        )
        return

    # Получаем предмет
    subject = await SubjectRepository.get_by_id(subject_id)
    if not subject:
        await callback.message.edit_text(
            "❌ Предмет не найден.",
            reply_markup=get_back_to_curator_kb()
        )
        return

    # Получаем кураторов для студента по данному предмету
    curators = await CuratorRepository.get_curators_for_student_subject(student.id, subject_id)

    if not curators:
        await callback.message.edit_text(
            f"❌ Кураторы по предмету {subject.name} не назначены.\n"
            f"Обратитесь к администратору.",
            reply_markup=get_back_to_curator_kb()
        )
        return

    # Получаем группы студента по данному предмету для отображения
    student_groups_for_subject = [group for group in student.groups if group.subject_id == subject_id]

    # Формируем сообщение с информацией о кураторах
    if len(curators) == 1:
        curator = curators[0]

        # Создаем ссылку на Telegram чат куратора
        telegram_info = f"tg://user?id={curator.user.telegram_id}" if curator.user else "Не указан"

        # Находим группы куратора, которые пересекаются с группами студента
        curator_groups_for_student = []
        curator_group_ids = [g.id for g in curator.groups]
        for group in student_groups_for_subject:
            if group.id in curator_group_ids:
                curator_groups_for_student.append(group)

        groups_text = ", ".join([group.name for group in curator_groups_for_student]) if curator_groups_for_student else "Не указана"

        message_text = (
            f"📞 Куратор по предмету {subject.name}:\n\n"
            f"👤 {curator.user.name}\n"
            f"📚 Группа: {groups_text}\n"
            f"📩 Написать куратору: [Открыть чат]({telegram_info})"
        )
    else:
        message_text = f"📞 Кураторы по предмету {subject.name}:\n\n"
        for i, curator in enumerate(curators, 1):
            # Создаем ссылку на Telegram чат куратора
            telegram_info = f"tg://user?id={curator.user.telegram_id}" if curator.user else "Не указан"

            # Находим группы куратора, которые пересекаются с группами студента
            curator_groups_for_student = []
            curator_group_ids = [g.id for g in curator.groups]
            for group in student_groups_for_subject:
                if group.id in curator_group_ids:
                    curator_groups_for_student.append(group)

            groups_text = ", ".join([group.name for group in curator_groups_for_student]) if curator_groups_for_student else "Не указана"

            message_text += (
                f"{i}. 👤 {curator.user.name}\n"
                f"   📚 Группа: {groups_text}\n"
                f"   📩 Написать: [Открыть чат]({telegram_info})\n\n"
            )

    await callback.message.edit_text(
        message_text,
        reply_markup=get_back_to_curator_kb(),
        parse_mode="Markdown"
    )
    await state.set_state(CuratorStates.curator_info)