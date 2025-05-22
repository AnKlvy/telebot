from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from keyboards.curator_contact import get_curator_subjects_kb, get_back_to_curator_kb

router = Router()

class CuratorStates(StatesGroup):
    main = State()
    curator_info = State()

@router.callback_query(F.data == "curator")
async def show_curator_menu(callback: CallbackQuery, state: FSMContext):
    """Показать меню выбора предмета для связи с куратором"""
    await callback.message.edit_text(
        "Нужна помощь?\n"
        "Выбери предмет — я покажу, кто твой куратор и как с ним связаться:",
        reply_markup=get_curator_subjects_kb()
    )
    await state.set_state(CuratorStates.main)

@router.callback_query(CuratorStates.main, F.data.startswith("curator_"))
async def show_curator_info(callback: CallbackQuery, state: FSMContext):
    """Показать информацию о кураторе по выбранному предмету"""
    subject_id = callback.data.replace("curator_", "")
    
    # Определяем название предмета
    subject_names = {
        "chem": "Химия",
        "bio": "Биология",
        "kz": "История Казахстана",
        "mathlit": "Матемграмотность"
    }
    subject_name = subject_names.get(subject_id, "")
    
    # В реальном приложении здесь будет логика получения информации о кураторе из базы данных
    # Для примера используем фиксированные значения
    curator_info = {
        "chem": {
            "group": "Курс Интенсив – группа 1",
            "telegram": "@chem_curator01"
        },
        "bio": {
            "group": "Курс Интенсив – группа 2",
            "telegram": "@bio_curator02"
        },
        "kz": {
            "group": "Курс Интенсив – группа 3",
            "telegram": "@kz_curator03"
        },
        "mathlit": {
            "group": "Курс Интенсив – группа 4",
            "telegram": "@mathlit_curator04"
        }
    }
    
    curator = curator_info.get(subject_id, {})
    group = curator.get("group", "")
    telegram = curator.get("telegram", "")
    
    await callback.message.edit_text(
        f"Куратор по предмету {subject_name}:\n"
        f"Группа: {group}\n"
        f"📩 Telegram: {telegram}",
        reply_markup=get_back_to_curator_kb()
    )
    await state.set_state(CuratorStates.curator_info)

@router.callback_query(F.data == "back_to_curator")
async def back_to_curator_menu(callback: CallbackQuery, state: FSMContext):
    """Вернуться к выбору предмета куратора"""
    await show_curator_menu(callback, state)