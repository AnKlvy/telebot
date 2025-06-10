import logging
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from typing import Dict

async def log(name, role, state):
    logging.info(f"ВЫЗОВ: {name} | РОЛЬ: {role} | СОСТОЯНИЕ: {await state.get_state()}")

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
        
        role_to_use = await get_role_to_use(state, user_role)
        
        # Получаем переходы и обработчики для роли (или дефолтные)
        transitions = self.transitions_map.get(role_to_use, {})
        handlers = self.handlers_map.get(role_to_use, {})
        
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
            print(f"DEBUG: Возвращаемся в главное меню для роли: {role_to_use}")
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
        await log("handle_main_menu", user_role, state)
        print(f"DEBUG: Обработка 'главное меню'. Роль: {user_role}")

        # Получаем текущее состояние
        current_state = await state.get_state()
        print(f"DEBUG: Текущее состояние: {current_state}")

        role_to_use = await get_role_to_use(state, user_role)

        print(f"DEBUG: Определенная роль: {role_to_use}")

        # Получаем обработчики для роли
        handlers = self.handlers_map.get(role_to_use, {})

        # Вызываем обработчик главного меню для соответствующей роли
        main_handler = handlers.get(None)
        if main_handler:
            print(f"DEBUG: Найден обработчик главного меню: {main_handler}")
            if callback.message:
                await callback.message.delete()
            await main_handler(callback.message if hasattr(callback, 'message') else callback)
            await state.clear()
        else:
            print(f"DEBUG: Обработчик главного меню не найден для роли: {role_to_use}")
            print(f"DEBUG: Доступные обработчики: {list(handlers.keys())}")

async def get_role_to_use(state: FSMContext, user_role: str) -> str:
    current_state = await state.get_state()
    # Определяем роль по состоянию
    detected_role = None

    print(f"DEBUG get_role_to_use: current_state = '{current_state}', user_role = '{user_role}'")

    # Проверяем состояние на принадлежность к определенной роли
    role_prefixes = {
        "student": ["StudentMain", "HomeworkStates", "ProgressStates", "ShopStates",
                    "TrialEntStates", "StudentTestsStates", "CuratorStates", "AccountStates"],
        "curator": ["CuratorMain", "CuratorGroupStates", "CuratorAnalyticsStates",
                    "CuratorHomeworkStates", "MessageStates", "CuratorTestsStatisticsStates"],
        "teacher": ["TeacherMain", "TeacherGroupStates", "TeacherAnalyticsStates",
                    "TeacherTestsStatisticsStates"],
        "manager": ["ManagerMain", "ManagerAnalyticsStates", "AddHomeworkStates",
                    "ManagerGroupStates", "ManagerTopicStates", "ManagerLessonStates", "BonusTaskStates", "ManagerMonthTestsStates"],
        "admin": ["AdminMain", "AdminSubjectsStates", "AdminCoursesStates", "AdminGroupsStates",
                  "AdminStudentsStates", "AdminCuratorsStates", "AdminTeachersStates", "AdminManagersStates"]
    }
    if current_state:
        # Проверяем принадлежность состояния к роли
        for role, prefixes in role_prefixes.items():
            for prefix in prefixes:
                if current_state.startswith(prefix):
                    print(f"DEBUG: Состояние '{current_state}' соответствует префиксу '{prefix}' для роли '{role}'")
                    detected_role = role
                    break
            if detected_role:
                break

        if not detected_role:
            print(f"DEBUG: Состояние '{current_state}' не соответствует ни одному префиксу")
            print(f"DEBUG: Доступные префиксы: {role_prefixes}")

    # Используем определенную роль, если она найдена, иначе используем переданную роль
    role_to_use = detected_role or user_role
    print(f"DEBUG get_role_to_use: detected_role = '{detected_role}', final role_to_use = '{role_to_use}'")
    return role_to_use

# Создаем глобальный экземпляр менеджера навигации
navigation_manager = NavigationManager()