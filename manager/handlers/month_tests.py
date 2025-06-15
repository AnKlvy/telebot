from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from manager.keyboards.month_tests import (
    get_month_tests_menu_kb,
    get_courses_for_tests_kb,
    get_subjects_for_tests_kb,
    get_microtopics_input_kb,
    get_confirm_test_creation_kb,
    get_tests_list_kb,
    get_confirm_delete_test_kb,
    get_delete_tests_list_kb
)
from manager.keyboards.main import get_manager_main_menu_kb
from common.keyboards import get_home_kb
from database.repositories.month_test_repository import MonthTestRepository
from database.repositories.month_test_microtopic_repository import MonthTestMicrotopicRepository
from database.repositories.course_repository import CourseRepository
from database.repositories.subject_repository import SubjectRepository
from database.repositories.microtopic_repository import MicrotopicRepository

router = Router()

class ManagerMonthTestsStates(StatesGroup):
    main = State()  # Главное меню тестов месяца
    select_course = State()  # Выбор курса
    select_subject = State()  # Выбор предмета
    enter_month_name = State()  # Ввод названия контрольного месяца
    enter_microtopics = State()  # Ввод номеров микротем
    confirm_creation = State()  # Подтверждение создания теста
    tests_list = State()  # Список созданных тестов
    confirm_deletion = State()  # Подтверждение удаления



@router.callback_query(F.data == "manager_month_tests")
async def show_month_tests_menu(callback: CallbackQuery, state: FSMContext):
    """Показываем главное меню тестов месяца"""
    await state.set_state(ManagerMonthTestsStates.main)
    await callback.message.edit_text(
        text="🧠 Управление входными и контрольными тестами месяца",
        reply_markup=get_month_tests_menu_kb()
    )

@router.callback_query(F.data == "create_month_test")
async def start_create_test(callback: CallbackQuery, state: FSMContext):
    """Начинаем создание нового теста"""
    await state.set_state(ManagerMonthTestsStates.select_course)
    await callback.message.edit_text(
        text="Выберите курс для создания теста:",
        reply_markup=await get_courses_for_tests_kb()
    )

@router.callback_query(StateFilter(ManagerMonthTestsStates.select_course), F.data.startswith("course_"))
async def select_course(callback: CallbackQuery, state: FSMContext):
    """Обрабатываем выбор курса"""
    course_id = int(callback.data.replace("course_", ""))
    course = await CourseRepository.get_by_id(course_id)

    if not course:
        await callback.message.edit_text(
            text="❌ Курс не найден",
            reply_markup=get_month_tests_menu_kb()
        )
        await state.set_state(ManagerMonthTestsStates.main)
        return

    await state.update_data(course_id=course_id, course_name=course.name)
    await state.set_state(ManagerMonthTestsStates.select_subject)

    await callback.message.edit_text(
        text=f"Курс: {course.name}\n\nВыберите предмет:",
        reply_markup=await get_subjects_for_tests_kb(course_id)
    )

@router.callback_query(StateFilter(ManagerMonthTestsStates.select_subject), F.data.startswith("subject_"))
async def select_subject(callback: CallbackQuery, state: FSMContext):
    """Обрабатываем выбор предмета"""
    subject_id = int(callback.data.replace("subject_", ""))
    subject = await SubjectRepository.get_by_id(subject_id)

    if not subject:
        await callback.message.edit_text(
            text="❌ Предмет не найден",
            reply_markup=get_month_tests_menu_kb()
        )
        await state.set_state(ManagerMonthTestsStates.main)
        return

    data = await state.get_data()
    course_name = data.get("course_name", "")

    await state.update_data(subject_id=subject_id, subject_name=subject.name)
    await state.set_state(ManagerMonthTestsStates.enter_month_name)

    await callback.message.edit_text(
        text=f"Курс: {course_name}\n"
             f"Предмет: {subject.name}\n\n"
             f"Введите название контрольного месяца:",
        reply_markup=get_home_kb()
    )

@router.message(StateFilter(ManagerMonthTestsStates.enter_month_name))
async def process_month_name(message: Message, state: FSMContext):
    """Обрабатываем ввод названия месяца"""
    month_name = message.text.strip()

    data = await state.get_data()
    course_name = data.get("course_name", "")
    subject_name = data.get("subject_name", "")

    await state.update_data(month_name=month_name)
    await state.set_state(ManagerMonthTestsStates.enter_microtopics)

    await message.answer(
        text=f"Курс: {course_name}\n"
             f"Предмет: {subject_name}\n"
             f"Месяц: {month_name}\n\n"
             f"Введите номера микротем через пробел (например: 1 3 4):",
        reply_markup=get_microtopics_input_kb()
    )

@router.message(StateFilter(ManagerMonthTestsStates.enter_microtopics))
async def process_microtopics(message: Message, state: FSMContext):
    """Обрабатываем ввод номеров микротем"""
    microtopics_input = message.text.strip()

    # Разбиваем по пробелам и убираем пустые элементы
    microtopic_numbers = [num.strip() for num in microtopics_input.split() if num.strip()]

    data = await state.get_data()
    course_name = data.get("course_name", "")
    subject_name = data.get("subject_name", "")
    subject_id = data.get("subject_id")
    month_name = data.get("month_name", "")

    # Проверяем что введены только числа и убираем дубликаты
    valid_numbers = []
    invalid_numbers = []

    for num_str in microtopic_numbers:
        try:
            num = int(num_str)
            if num > 0 and num not in valid_numbers:  # Проверяем положительность и избегаем дублирования
                valid_numbers.append(num)
            elif num <= 0:
                invalid_numbers.append(f"{num_str} (должно быть > 0)")
        except ValueError:
            invalid_numbers.append(num_str)

    if invalid_numbers:
        await message.answer(
            f"❌ Некорректные номера микротем: {', '.join(invalid_numbers)}\n"
            f"Введите только положительные числа через пробел:",
            reply_markup=get_microtopics_input_kb()
        )
        return

    if not valid_numbers:
        await message.answer(
            f"❌ Не введено ни одного номера микротемы.\n"
            f"Введите номера микротем через пробел:",
            reply_markup=get_microtopics_input_kb()
        )
        return

    # Проверяем существование микротем в базе данных
    try:
        existing_numbers = []
        non_existing_numbers = []

        for number in valid_numbers:
            exists = await MicrotopicRepository.exists_by_number(subject_id, number)
            if exists:
                existing_numbers.append(number)
            else:
                non_existing_numbers.append(number)

        if non_existing_numbers:
            # Получаем список существующих микротем для подсказки
            existing_microtopics = await MicrotopicRepository.get_by_subject(subject_id)
            if existing_microtopics:
                available_numbers = [str(mt.number) for mt in existing_microtopics]
                available_text = f"\n\nДоступные номера микротем: {', '.join(available_numbers)}"
            else:
                available_text = "\n\n❗ В данном предмете пока нет микротем. Сначала создайте микротемы."

            await message.answer(
                f"❌ Микротемы с номерами {', '.join(map(str, non_existing_numbers))} не существуют для предмета '{subject_name}'.{available_text}\n\n"
                f"Введите корректные номера микротем:",
                reply_markup=get_microtopics_input_kb()
            )
            return

        if not existing_numbers:
            await message.answer(
                f"❌ Ни одна из указанных микротем не найдена.\n"
                f"Введите корректные номера микротем:",
                reply_markup=get_microtopics_input_kb()
            )
            return

    except Exception as e:
        await message.answer(
            f"❌ Ошибка при проверке микротем: {str(e)}\n"
            f"Попробуйте еще раз:",
            reply_markup=get_microtopics_input_kb()
        )
        return

    # Формируем список номеров для подтверждения (используем только существующие)
    numbers_text = ", ".join([str(num) for num in sorted(existing_numbers)])

    await state.update_data(selected_microtopic_numbers=existing_numbers)
    await state.set_state(ManagerMonthTestsStates.confirm_creation)

    await message.answer(
        text=f"📋 Подтверждение создания теста:\n\n"
             f"Курс: {course_name}\n"
             f"Предмет: {subject_name}\n"
             f"Месяц: {month_name}\n\n"
             f"Номера микротем: {numbers_text}\n\n"
             f"Будет создана привязка для ОДНОГО теста с двумя типами:\n"
             f"• Входной тест месяца\n"
             f"• Контрольный тест месяца\n\n"
             f"При прохождении будут генерироваться случайные вопросы из ДЗ по указанным микротемам",
        reply_markup=get_confirm_test_creation_kb()
    )

@router.callback_query(StateFilter(ManagerMonthTestsStates.confirm_creation), F.data == "confirm_create_test")
async def confirm_create_test(callback: CallbackQuery, state: FSMContext):
    """Подтверждаем создание теста - привязываем микротемы к предмету"""
    try:
        data = await state.get_data()
        course_id = data.get("course_id")
        subject_id = data.get("subject_id")
        month_name = data.get("month_name")
        microtopic_numbers = data.get("selected_microtopic_numbers", [])

        # Создаем тест месяца в базе данных
        month_test = await MonthTestRepository.create(
            name=month_name,
            course_id=course_id,
            subject_id=subject_id
        )

        # Добавляем связи с микротемами
        for microtopic_number in microtopic_numbers:
            await MonthTestMicrotopicRepository.create(
                month_test_id=month_test.id,
                microtopic_number=microtopic_number
            )

        numbers_text = ", ".join([str(num) for num in sorted(microtopic_numbers)])

        await callback.message.edit_text(
            text=f"✅ Тест месяца успешно создан!\n\n"
                 f"📋 Привязка создана:\n"
                 f"Курс: {data.get('course_name')}\n"
                 f"Предмет: {data.get('subject_name')}\n"
                 f"Месяц: {month_name}\n"
                 f"Микротемы: {numbers_text}\n\n"
                 f"Теперь студенты смогут проходить:\n"
                 f"• Входной тест месяца\n"
                 f"• Контрольный тест месяца\n\n"
                 f"Вопросы будут генерироваться из ДЗ по этим микротемам",
            reply_markup=get_month_tests_menu_kb()
        )
        await state.set_state(ManagerMonthTestsStates.main)

    except Exception as e:
        await callback.message.edit_text(
            text=f"❌ Ошибка при создании теста: {str(e)}",
            reply_markup=get_month_tests_menu_kb()
        )
        await state.set_state(ManagerMonthTestsStates.main)

@router.callback_query(StateFilter(ManagerMonthTestsStates.confirm_creation), F.data == "cancel_create_test")
async def cancel_create_test(callback: CallbackQuery, state: FSMContext):
    """Отменяем создание теста"""
    await callback.message.edit_text(
        text="❌ Создание теста отменено",
        reply_markup=get_month_tests_menu_kb()
    )
    await state.set_state(ManagerMonthTestsStates.main)

@router.callback_query(F.data == "list_month_tests")
async def list_month_tests(callback: CallbackQuery, state: FSMContext):
    """Показываем список созданных тестов"""
    try:
        tests_list = await MonthTestRepository.get_all()
        await state.set_state(ManagerMonthTestsStates.tests_list)

        if not tests_list:
            await callback.message.edit_text(
                text="📋 Список тестов месяца пуст\n\nСоздайте первый тест!",
                reply_markup=get_month_tests_menu_kb()
            )
        else:
            tests_text = f"📋 Созданные тесты месяца ({len(tests_list)}):\n\n"
            for i, test in enumerate(tests_list, 1):
                # Получаем номера микротем для теста
                microtopic_numbers = [mt.microtopic_number for mt in test.microtopics]
                numbers_text = ", ".join([str(num) for num in sorted(microtopic_numbers)])

                tests_text += f"{i}. {test.course.name} - {test.subject.name}\n"
                tests_text += f"   Месяц: {test.name}\n"
                tests_text += f"   Микротемы: {numbers_text}\n\n"

            await callback.message.edit_text(
                text=tests_text,
                reply_markup=get_month_tests_menu_kb()
            )
    except Exception as e:
        await callback.message.edit_text(
            text=f"❌ Ошибка при получении списка тестов: {str(e)}",
            reply_markup=get_month_tests_menu_kb()
        )
        await state.set_state(ManagerMonthTestsStates.main)

@router.callback_query(F.data == "delete_month_test")
async def start_delete_test(callback: CallbackQuery, state: FSMContext):
    """Начинаем удаление теста"""
    try:
        tests_list = await MonthTestRepository.get_all()

        if not tests_list:
            await callback.message.edit_text(
                text="🗑 Нет тестов для удаления",
                reply_markup=get_month_tests_menu_kb()
            )
            await state.set_state(ManagerMonthTestsStates.main)
        else:
            await state.set_state(ManagerMonthTestsStates.confirm_deletion)
            await callback.message.edit_text(
                text="🗑 Выберите тест для удаления:",
                reply_markup=await get_delete_tests_list_kb(tests_list)
            )
    except Exception as e:
        await callback.message.edit_text(
            text=f"❌ Ошибка при получении списка тестов: {str(e)}",
            reply_markup=get_month_tests_menu_kb()
        )
        await state.set_state(ManagerMonthTestsStates.main)

@router.callback_query(StateFilter(ManagerMonthTestsStates.confirm_deletion), F.data.startswith("delete_test_"))
async def confirm_delete_test(callback: CallbackQuery, state: FSMContext):
    """Подтверждение удаления теста"""
    try:
        test_id = int(callback.data.replace("delete_test_", ""))
        test = await MonthTestRepository.get_by_id(test_id)

        if not test:
            await callback.message.edit_text(
                text="❌ Тест не найден",
                reply_markup=get_month_tests_menu_kb()
            )
            await state.set_state(ManagerMonthTestsStates.main)
            return

        # Получаем номера микротем для теста
        microtopic_numbers = [mt.microtopic_number for mt in test.microtopics]
        numbers_text = ", ".join([str(num) for num in sorted(microtopic_numbers)])

        await callback.message.edit_text(
            text=f"🗑 Подтверждение удаления теста:\n\n"
                 f"Курс: {test.course.name}\n"
                 f"Предмет: {test.subject.name}\n"
                 f"Месяц: {test.name}\n"
                 f"Микротемы: {numbers_text}\n\n"
                 f"⚠️ Это действие нельзя отменить!",
            reply_markup=get_confirm_delete_test_kb(test_id)
        )
    except Exception as e:
        await callback.message.edit_text(
            text=f"❌ Ошибка при получении теста: {str(e)}",
            reply_markup=get_month_tests_menu_kb()
        )
        await state.set_state(ManagerMonthTestsStates.main)

@router.callback_query(StateFilter(ManagerMonthTestsStates.confirm_deletion), F.data.startswith("confirm_delete_"))
async def delete_test(callback: CallbackQuery, state: FSMContext):
    """Удаляем тест"""
    try:
        test_id = int(callback.data.replace("confirm_delete_", ""))
        test = await MonthTestRepository.get_by_id(test_id)

        if test:
            await MonthTestRepository.delete(test_id)
            await callback.message.edit_text(
                text=f"✅ Тест '{test.course.name} - {test.subject.name} - {test.name}' удален",
                reply_markup=get_month_tests_menu_kb()
            )
        else:
            await callback.message.edit_text(
                text="❌ Тест не найден",
                reply_markup=get_month_tests_menu_kb()
            )
    except Exception as e:
        await callback.message.edit_text(
            text=f"❌ Ошибка при удалении теста: {str(e)}",
            reply_markup=get_month_tests_menu_kb()
        )

    await state.set_state(ManagerMonthTestsStates.main)

@router.callback_query(StateFilter(ManagerMonthTestsStates.confirm_deletion), F.data == "cancel_delete")
async def cancel_delete(callback: CallbackQuery, state: FSMContext):
    """Отменяем удаление"""
    await callback.message.edit_text(
        text="❌ Удаление отменено",
        reply_markup=get_month_tests_menu_kb()
    )
    await state.set_state(ManagerMonthTestsStates.main)
