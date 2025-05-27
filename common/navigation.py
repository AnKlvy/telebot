from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from typing import Dict

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
            # Возвращаемся в главное меню соответствующей роли
            print(f"DEBUG: Возвращаемся в главное меню для роли: {user_role}")
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
                # Проверяем количество параметров функции
                import inspect
                sig = inspect.signature(handler)
                param_count = len(sig.parameters)

                # Вызываем обработчик с нужным количеством аргументов
                if param_count == 2:  # callback, state
                    await handler(callback, state)
                elif param_count == 3:  # callback, state, role
                    await handler(callback, state, user_role)
                else:
                    print(f"DEBUG: Неподдерживаемое количество параметров в обработчике: {param_count}")
            else:
                # Если обработчик не найден, возвращаемся в главное меню
                print(f"DEBUG: Обработчик для {previous_state} не найден, возвращаемся в главное меню")
                main_handler = handlers.get(None)
                if main_handler:
                    await callback.message.delete()
                    await main_handler(callback.message)
                    await state.clear()
    
    async def handle_main_menu(self, callback: CallbackQuery, state: FSMContext, user_role: str):
        """Универсальный обработчик кнопки главного меню"""
        print(f"DEBUG: Обработка 'главное меню'. Роль: {user_role}")
        
        # Получаем обработчики для роли
        handlers = self.handlers_map.get(user_role, {})
        
        # Вызываем обработчик главного меню для соответствующей роли
        main_handler = handlers.get(None)
        if main_handler:
            if callback.message:
                await callback.message.delete()
            await main_handler(callback.message if hasattr(callback, 'message') else callback)
            await state.clear()

# Создаем глобальный экземпляр менеджера навигации
navigation_manager = NavigationManager()