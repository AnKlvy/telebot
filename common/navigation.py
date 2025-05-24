from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from typing import Dict, Callable, Any, Optional

from student.handlers.main import show_student_main_menu


class NavigationManager:
    """Менеджер навигации, не зависящий от конкретных ролей"""
    
    def __init__(self):
        self.transitions_map = {}  # Словарь переходов для разных ролей
        self.handlers_map = {}     # Словарь обработчиков для разных ролей
    
    def register_role(self, role: str, transitions: Dict, handlers: Dict):
        """Регистрация переходов и обработчиков для роли"""
        self.transitions_map[role] = transitions
        self.handlers_map[role] = handlers
    
    async def handle_back(self, callback: CallbackQuery, state: FSMContext, user_role: str):
        """Универсальный обработчик кнопки назад"""
        current_state = await state.get_state()
        print(f"DEBUG: Обработка 'назад'. Текущее состояние: {current_state}, роль: {user_role}")
        
        # Получаем переходы и обработчики для роли (или дефолтные)
        transitions = self.transitions_map.get(user_role, {})
        handlers = self.handlers_map.get(user_role, {})
        
        # Если состояния нет или оно не в словаре переходов
        if not current_state or current_state not in transitions:
            print(f"DEBUG: Состояние {current_state} не найдено в словаре переходов")
            handler = handlers.get(None)
            if handler:
                print(f"DEBUG: Найден обработчик для None: {handler}")
                await callback.message.delete()
                await handler(callback.message)
                await state.clear()
            return
        
        # Получаем предыдущее состояние
        previous_state = transitions.get(current_state)
        print(f"DEBUG: Предыдущее состояние: {previous_state}")
        
        if previous_state is None:
            # Возвращаемся в главное меню
            print("DEBUG: Возвращаемся в главное меню")
            handler = handlers.get(None)
            if handler:
                await callback.message.delete()
                await handler(callback.message)
                await state.clear()
        else:
            # Переходим в предыдущее состояние
            print(f"DEBUG: Переходим в предыдущее состояние: {previous_state}")
            await state.set_state(previous_state)
            handler = handlers.get(previous_state)
            if handler:
                await handler(callback, state)
            else:
                # Если обработчик не найден, возвращаемся в главное меню
                print(f"DEBUG: Обработчик для {previous_state} не найден, возвращаемся в главное меню")
                main_handler = handlers.get(None)
                if main_handler:
                    await callback.message.delete()
                    await main_handler(callback.message)
                    await state.clear()

# Создаем глобальный экземпляр менеджера навигации
navigation_manager = NavigationManager()

# Импортируем словари переходов и обработчиков
from student.states.states_homework import STATE_TRANSITIONS as STUDENT_TRANSITIONS, STATE_HANDLERS as STUDENT_HANDLERS
from curator.states.states_homework import STATE_TRANSITIONS as CURATOR_TRANSITIONS, STATE_HANDLERS as CURATOR_HANDLERS
from curator.states.states_analytics import STATE_TRANSITIONS as ANALYTICS_TRANSITIONS, STATE_HANDLERS as ANALYTICS_HANDLERS
from student.states.states_curator_contact import STATE_TRANSITIONS as CURATOR_CONTACT_TRANSITIONS, STATE_HANDLERS as CURATOR_CONTACT_HANDLERS
from student.states.states_progress import STATE_TRANSITIONS as PROGRESS_TRANSITIONS, STATE_HANDLERS as PROGRESS_HANDLERS
from student.states.states_shop import STATE_TRANSITIONS as SHOP_TRANSITIONS, STATE_HANDLERS as SHOP_HANDLERS
from student.states.states_test_report import STATE_TRANSITIONS as TEST_REPORT_TRANSITIONS, STATE_HANDLERS as TEST_REPORT_HANDLERS

# Регистрируем роли
def register_handlers():
    from curator.handlers.main import show_curator_main_menu

    # Объединяем словари переходов и обработчиков для куратора
    curator_transitions = {**CURATOR_TRANSITIONS, **ANALYTICS_TRANSITIONS}
    curator_handlers = {**CURATOR_HANDLERS, **ANALYTICS_HANDLERS}

    # Объединяем словари переходов и обработчиков для студента
    student_transitions = {**STUDENT_TRANSITIONS, **CURATOR_CONTACT_TRANSITIONS, **PROGRESS_TRANSITIONS, **SHOP_TRANSITIONS, **TEST_REPORT_TRANSITIONS}
    student_handlers = {**STUDENT_HANDLERS, **CURATOR_CONTACT_HANDLERS, **PROGRESS_HANDLERS, **SHOP_HANDLERS, **TEST_REPORT_HANDLERS}

    navigation_manager.register_role("student", student_transitions, {None: show_student_main_menu, **student_handlers})
    navigation_manager.register_role("curator", curator_transitions, {None: show_curator_main_menu, **curator_handlers})