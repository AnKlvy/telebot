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

# Временное хранилище данных (потом заменить на БД)
courses_db = {
    1: "ЕНТ",
    2: "IT"
}

subjects_db = {
    1: ["Математика", "Физика", "Информатика", "История Казахстана", "Химия", "Биология"],
    2: ["Python", "JavaScript", "Java"]
}

created_tests = {}

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
        reply_markup=get_courses_for_tests_kb()
    )

@router.callback_query(ManagerMonthTestsStates.select_course, F.data.startswith("course_"))
async def select_course(callback: CallbackQuery, state: FSMContext):
    """Обрабатываем выбор курса"""
    course_id = int(callback.data.replace("course_", ""))
    course_name = courses_db.get(course_id, "Неизвестный курс")
    
    await state.update_data(course_id=course_id, course_name=course_name)
    await state.set_state(ManagerMonthTestsStates.select_subject)
    
    await callback.message.edit_text(
        text=f"Курс: {course_name}\nВыберите предмет:",
        reply_markup=get_subjects_for_tests_kb(course_id)
    )

@router.callback_query(ManagerMonthTestsStates.select_subject, F.data.startswith("subject_"))
async def select_subject(callback: CallbackQuery, state: FSMContext):
    """Обрабатываем выбор предмета"""
    subject_name = callback.data.replace("subject_", "")
    
    data = await state.get_data()
    course_name = data.get("course_name", "")
    
    await state.update_data(subject_name=subject_name)
    await state.set_state(ManagerMonthTestsStates.enter_month_name)
    
    await callback.message.edit_text(
        text=f"Курс: {course_name}\n"
             f"Предмет: {subject_name}\n\n"
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
    month_name = data.get("month_name", "")

    # Проверяем что введены только числа и убираем дубликаты
    valid_numbers = []
    invalid_numbers = []

    for num_str in microtopic_numbers:
        try:
            num = int(num_str)
            if num not in valid_numbers:  # Избегаем дублирования
                valid_numbers.append(num)
        except ValueError:
            invalid_numbers.append(num_str)

    if invalid_numbers:
        await message.answer(
            f"❌ Некорректные номера микротем: {', '.join(invalid_numbers)}\n"
            f"Введите только числа через пробел:",
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

    # Формируем список номеров для подтверждения
    numbers_text = ", ".join([str(num) for num in sorted(valid_numbers)])

    await state.update_data(selected_microtopic_numbers=valid_numbers)
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

@router.callback_query(F.data == "confirm_create_test")
async def confirm_create_test(callback: CallbackQuery, state: FSMContext):
    """Подтверждаем создание теста - привязываем микротемы к предмету"""
    data = await state.get_data()

    # Генерируем уникальный ID для теста
    import time
    test_id = f"test_{int(time.time())}"

    # Создаем запись о тесте (привязка микротем к предмету и курсу)
    test_data = {
        "id": test_id,
        "course_id": data.get("course_id"),
        "course_name": data.get("course_name"),
        "subject_name": data.get("subject_name"),
        "month_name": data.get("month_name"),
        "microtopic_numbers": data.get("selected_microtopic_numbers", []),
        "created_at": time.time()
    }

    # Сохраняем привязку в хранилище
    created_tests[test_id] = test_data

    numbers_text = ", ".join([str(num) for num in sorted(test_data["microtopic_numbers"])])

    await callback.message.edit_text(
        text=f"✅ Тест месяца успешно создан!\n\n"
             f"📋 Привязка создана:\n"
             f"Курс: {test_data['course_name']}\n"
             f"Предмет: {test_data['subject_name']}\n"
             f"Месяц: {test_data['month_name']}\n"
             f"Микротемы: {numbers_text}\n\n"
             f"Теперь студенты смогут проходить:\n"
             f"• Входной тест месяца\n"
             f"• Контрольный тест месяца\n\n"
             f"Вопросы будут генерироваться из ДЗ по этим микротемам",
        reply_markup=get_month_tests_menu_kb()
    )
    await state.set_state(ManagerMonthTestsStates.main)

@router.callback_query(F.data == "cancel_create_test")
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
    tests_list = list(created_tests.values())

    await state.set_state(ManagerMonthTestsStates.tests_list)

    if not tests_list:
        await callback.message.edit_text(
            text="📋 Список тестов месяца пуст\n\nСоздайте первый тест!",
            reply_markup=get_month_tests_menu_kb()
        )
    else:
        tests_text = f"📋 Созданные тесты месяца ({len(tests_list)}):\n\n"
        for i, test in enumerate(tests_list, 1):
            numbers_text = ", ".join([str(num) for num in sorted(test["microtopic_numbers"])])
            tests_text += f"{i}. {test['course_name']} - {test['subject_name']}\n"
            tests_text += f"   Месяц: {test['month_name']}\n"
            tests_text += f"   Микротемы: {numbers_text}\n\n"

        await callback.message.edit_text(
            text=tests_text,
            reply_markup=get_month_tests_menu_kb()
        )

@router.callback_query(F.data == "delete_month_test")
async def start_delete_test(callback: CallbackQuery, state: FSMContext):
    """Начинаем удаление теста"""
    tests_list = list(created_tests.values())

    await state.set_state(ManagerMonthTestsStates.confirm_deletion)

    if not tests_list:
        await callback.message.edit_text(
            text="🗑 Нет тестов для удаления",
            reply_markup=get_month_tests_menu_kb()
        )
    else:
        await callback.message.edit_text(
            text="🗑 Выберите тест для удаления:",
            reply_markup=get_delete_tests_list_kb(tests_list)
        )

@router.callback_query(F.data.startswith("delete_test_"))
async def confirm_delete_test(callback: CallbackQuery, state: FSMContext):
    """Подтверждение удаления теста"""
    test_id = callback.data.replace("delete_test_", "")
    test = created_tests.get(test_id)

    if not test:
        await callback.message.edit_text(
            text="❌ Тест не найден",
            reply_markup=get_month_tests_menu_kb()
        )
        return

    numbers_text = ", ".join([str(num) for num in sorted(test["microtopic_numbers"])])

    await callback.message.edit_text(
        text=f"🗑 Подтверждение удаления теста:\n\n"
             f"Курс: {test['course_name']}\n"
             f"Предмет: {test['subject_name']}\n"
             f"Месяц: {test['month_name']}\n"
             f"Микротемы: {numbers_text}\n\n"
             f"⚠️ Это действие нельзя отменить!",
        reply_markup=get_confirm_delete_test_kb(test_id)
    )

@router.callback_query(F.data.startswith("confirm_delete_"))
async def delete_test(callback: CallbackQuery, state: FSMContext):
    """Удаляем тест"""
    test_id = callback.data.replace("confirm_delete_", "")
    test = created_tests.get(test_id)

    if test:
        del created_tests[test_id]
        await callback.message.edit_text(
            text=f"✅ Тест '{test['course_name']} - {test['subject_name']} - {test['month_name']}' удален",
            reply_markup=get_month_tests_menu_kb()
        )
    else:
        await callback.message.edit_text(
            text="❌ Тест не найден",
            reply_markup=get_month_tests_menu_kb()
        )

    await state.set_state(ManagerMonthTestsStates.main)

@router.callback_query(F.data == "cancel_delete")
async def cancel_delete(callback: CallbackQuery, state: FSMContext):
    """Отменяем удаление"""
    await callback.message.edit_text(
        text="❌ Удаление отменено",
        reply_markup=get_month_tests_menu_kb()
    )
    await state.set_state(ManagerMonthTestsStates.main)
