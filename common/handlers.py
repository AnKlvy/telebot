from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

router = Router()

# Импортируем словари переходов и обработчиков из файлов состояний
from student.states import STATE_TRANSITIONS as STUDENT_STATE_TRANSITIONS
from student.states import STATE_HANDLERS as STUDENT_STATE_HANDLERS
from curator.states import STATE_TRANSITIONS as CURATOR_STATE_TRANSITIONS
from curator.states import STATE_HANDLERS as CURATOR_STATE_HANDLERS

@router.callback_query(F.data == "back")
async def go_back(callback: CallbackQuery, state: FSMContext, user_role: str = None):
    current_state = await state.get_state()
    print(f"DEBUG: Нажата кнопка 'назад'. Текущее состояние: {current_state}, роль: {user_role}")

    # Выбираем нужный словарь переходов в зависимости от роли
    state_transitions = STUDENT_STATE_TRANSITIONS if user_role == "student" else CURATOR_STATE_TRANSITIONS
    state_handlers = STUDENT_STATE_HANDLERS if user_role == "student" else CURATOR_STATE_HANDLERS

    print(f"DEBUG: Используем словарь переходов для роли: {user_role}")

    # Если состояния нет или оно не в словаре переходов
    if not current_state or current_state not in state_transitions:
        print(f"DEBUG: Состояние {current_state} не найдено в словаре переходов")
        handler = state_handlers.get(None)
        if handler:
            print(f"DEBUG: Найден обработчик для None: {handler}")
            await callback.message.delete()
            await handler(callback.message)
            await state.clear()
        return
    
    # Получаем предыдущее состояние
    previous_state = state_transitions.get(current_state)
    print(f"DEBUG: Предыдущее состояние: {previous_state}")
    
    if previous_state is None:
        # Возвращаемся в главное меню
        print("DEBUG: Возвращаемся в главное меню")
        handler = state_handlers.get(None)
        if handler:
            print(f"DEBUG: Найден обработчик для None: {handler}")
            await callback.message.delete()
            await handler(callback.message)
            await state.clear()
    else:
        # Переходим в предыдущее состояние
        print(f"DEBUG: Переходим в предыдущее состояние: {previous_state}")
        await state.set_state(previous_state)
        handler = state_handlers.get(previous_state)
        if handler:
            print(f"DEBUG: Найден обработчик для {previous_state}: {handler}")
            await handler(callback, state)
        else:
            # Если обработчик не найден, возвращаемся в главное меню
            print(f"DEBUG: Обработчик для {previous_state} не найден, возвращаемся в главное меню")
            main_handler = state_handlers.get(None)
            if main_handler:
                print(f"DEBUG: Найден обработчик для None: {main_handler}")
                await callback.message.delete()
                await main_handler(callback.message)
                await state.clear()