from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

class RoleMiddleware(BaseMiddleware):
    """Middleware для определения роли пользователя"""
    
    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        # Получаем user_id
        user_id = event.from_user.id
        print("My user_id:", user_id)
        # В реальном приложении здесь будет запрос к базе данных для определения роли
        # Для примера используем фиксированные значения
        curator_ids = [123456789]  # Список ID кураторов
        admin_ids = [987654321]    # Список ID администраторов
        teacher_ids = [555555555]  # Список ID преподавателей
        manager_ids = [777777777, user_id]  # Список ID менеджеров
        
        # Определяем роль пользователя
        if user_id in admin_ids:
            role = "admin"
        elif user_id in curator_ids:
            role = "curator"
        elif user_id in teacher_ids:
            role = "teacher"
        elif user_id in manager_ids:
            role = "manager"
        else:
            role = "student"
        
        # Добавляем роль в данные события
        data["user_role"] = role
        
        # Продолжаем обработку события
        return await handler(event, data)