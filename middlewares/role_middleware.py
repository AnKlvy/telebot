from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

class RoleMiddleware(BaseMiddleware):
    """Middleware для определения роли пользователя"""

    def __init__(self):
        # Кэш для списков пользователей по ролям
        self._role_cache = {}
        self._cache_updated = False

    async def _update_role_cache(self):
        """Обновить кэш ролей из базы данных"""
        try:
            from database import get_db_session, User
            from sqlalchemy import select

            async with get_db_session() as session:
                # Получаем всех пользователей
                result = await session.execute(select(User))
                all_users = result.scalars().all()

                # Группируем по ролям
                self._role_cache = {
                    'admin': [],
                    'manager': [],
                    'curator': [],
                    'teacher': [],
                    'student': []
                }

                for user in all_users:
                    if user.role in self._role_cache:
                        self._role_cache[user.role].append(user.telegram_id)

                self._cache_updated = True
                print(f"🔄 Кэш ролей обновлен:")
                for role, ids in self._role_cache.items():
                    if ids:  # Показываем только непустые роли
                        print(f"  {role}: {ids}")

        except Exception as e:
            print(f"❌ Ошибка обновления кэша ролей: {e}")

    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id

        # Обновляем кэш при первом запуске
        if not self._cache_updated:
            await self._update_role_cache()

        # Определяем роль по ID из кэша
        role = "student"  # По умолчанию

        for role_name, user_ids in self._role_cache.items():
            if user_id in user_ids:
                role = role_name
                break

        print(f"User ID: {user_id} -> Role: {role}")

        # Добавляем роль в данные события
        data["user_role"] = role
        data["user_id"] = user_id

        # Продолжаем обработку события
        return await handler(event, data)