from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from sqlalchemy.sql.expression import text

# Глобальный кэш ролей (общий для всех экземпляров middleware)
_global_role_cache = {}
_global_cache_updated = False
_database_available = None  # None = не проверено, True = доступна, False = недоступна

class RoleMiddleware(BaseMiddleware):
    """Middleware для определения роли пользователя"""

    def __init__(self):
        # Используем глобальный кэш
        pass

    async def _check_database_availability(self):
        """Проверить доступность базы данных"""
        global _database_available

        try:
            from database import get_db_session
            async with get_db_session() as session:
                # Простой запрос для проверки соединения
                await session.execute(text("SELECT 1"))
                _database_available = True
                return True
        except Exception as e:
            print(f"❌ База данных недоступна: {e}")
            _database_available = False
            return False

    async def _update_role_cache(self):
        """Обновить кэш ролей из базы данных"""
        global _global_role_cache, _global_cache_updated, _database_available

        # Проверяем доступность БД, если еще не проверяли
        if _database_available is None:
            if not await self._check_database_availability():
                return

        # Если БД недоступна, не пытаемся обновить кэш
        if _database_available is False:
            return

        try:
            from database import get_db_session, User
            from sqlalchemy import select

            async with get_db_session() as session:
                # Получаем всех пользователей
                result = await session.execute(select(User))
                all_users = result.scalars().all()

                # Группируем по ролям
                _global_role_cache = {
                    'admin': [],
                    'manager': [],
                    'curator': [],
                    'teacher': [],
                    'student': []
                }

                for user in all_users:
                    if user.role in _global_role_cache:
                        _global_role_cache[user.role].append(user.telegram_id)

                # Устанавливаем флаг только при успешном обновлении
                _global_cache_updated = True

                print(f"🔄 Кэш ролей обновлен:")
                for role, ids in _global_role_cache.items():
                    if ids:  # Показываем только непустые роли
                        print(f"  {role}: {ids}")

        except Exception as e:
            print(f"❌ Ошибка обновления кэша ролей: {e}")
            # Помечаем БД как недоступную
            _database_available = False
            # НЕ устанавливаем флаг при ошибке, чтобы попробовать снова позже
            # Инициализируем пустой кэш при ошибке
            _global_role_cache = {
                'admin': [],
                'manager': [],
                'curator': [],
                'teacher': [],
                'student': []
            }

    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        global _global_role_cache, _global_cache_updated, _database_available

        user_id = event.from_user.id

        # Обновляем кэш при первом запуске (только если БД доступна)
        if not _global_cache_updated and _database_available is not False:
            await self._update_role_cache()

        # Определяем роль по ID из кэша
        role = "student"  # По умолчанию

        # Если кэш пустой или БД недоступна, используем хардкод для админа
        if (_database_available is False or
            not _global_role_cache or
            all(not users for users in _global_role_cache.values())):
            # Хардкод для админа (замените на ваш ID)
            if user_id in [955518340, 5205775566]:  # Андрей Климов
                role = "admin"
            else:
                role = "student"
        else:
            # Ищем роль в кэше
            for role_name, user_ids in _global_role_cache.items():
                if user_id in user_ids:
                    role = role_name
                    break

        print(f"🔍 MIDDLEWARE: User ID: {user_id} -> Role: {role} (DB: {_database_available})")

        # Добавляем роль в данные события
        data["user_role"] = role
        data["user_id"] = user_id

        # Продолжаем обработку события
        return await handler(event, data)


async def force_update_role_cache():
    """Принудительно обновить кэш ролей (для использования при добавлении новых пользователей)"""
    global _global_role_cache, _global_cache_updated

    try:
        from database import get_db_session, User
        from sqlalchemy import select

        async with get_db_session() as session:
            # Получаем всех пользователей
            result = await session.execute(select(User))
            all_users = result.scalars().all()

            # Группируем по ролям
            _global_role_cache = {
                'admin': [],
                'manager': [],
                'curator': [],
                'teacher': [],
                'student': []
            }

            for user in all_users:
                if user.role in _global_role_cache:
                    _global_role_cache[user.role].append(user.telegram_id)

            print(f"🔄 Кэш ролей принудительно обновлен:")
            for role, ids in _global_role_cache.items():
                if ids:  # Показываем только непустые роли
                    print(f"  {role}: {ids}")

    except Exception as e:
        print(f"❌ Ошибка принудительного обновления кэша ролей: {e}")
        # Инициализируем пустой кэш при ошибке
        _global_role_cache = {
            'admin': [],
            'manager': [],
            'curator': [],
            'teacher': [],
            'student': []
        }