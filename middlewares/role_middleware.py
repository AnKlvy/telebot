from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from database import get_user_role

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

        # Получаем роль пользователя из базы данных
        try:
            role = await get_user_role(user_id)
        except Exception as e:
            print(f"Ошибка получения роли пользователя: {e}")
            # Fallback: определяем роль по ID (для первоначальной настройки)
            # ВАЖНО: Замените 123456789 на свой реальный Telegram ID
            admin_ids = [123456789]  # Добавьте свой ID для первоначального доступа
            if user_id in admin_ids:
                role = "admin"
            else:
                role = "student"

        # Добавляем роль в данные события
        data["user_role"] = role

        # Продолжаем обработку события
        return await handler(event, data)