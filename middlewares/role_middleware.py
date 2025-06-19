from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from sqlalchemy.sql.expression import text
import asyncio
import time
import logging
from utils.redis_manager import RedisManager
from utils.config import REDIS_ENABLED
from utils.role_keyboards import role_keyboards_manager

# Глобальный кэш ролей (общий для всех экземпляров middleware)
_global_role_cache = {}
_global_cache_updated = False
_database_available = None  # None = не проверено, True = доступна, False = недоступна
_cache_lock = asyncio.Lock()  # Блокировка для безопасного обновления кэша
_last_cache_update = 0  # Время последнего обновления кэша
CACHE_TTL = 300
REDIS_CACHE_KEY = "user_roles_cache"

class RoleMiddleware(BaseMiddleware):
    """Middleware для определения роли пользователя с Redis кэшированием"""

    def __init__(self):
        # Используем глобальный кэш
        self.redis_manager = RedisManager() if REDIS_ENABLED else None

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

    async def _load_from_redis(self):
        """Загрузить кэш ролей из Redis"""
        global _global_role_cache, _global_cache_updated, _last_cache_update

        if not self.redis_manager or not self.redis_manager.connected:
            return False

        try:
            import json
            cached_data = await self.redis_manager.get(REDIS_CACHE_KEY)
            if cached_data:
                cache_info = json.loads(cached_data)
                _global_role_cache = cache_info['roles']
                _global_cache_updated = True
                _last_cache_update = cache_info['timestamp']
                logging.info(f"✅ Роли загружены из Redis кэша ({len(sum(_global_role_cache.values(), []))} пользователей)")
                return True
        except Exception as e:
            logging.error(f"❌ Ошибка загрузки из Redis: {e}")

        return False

    async def _save_to_redis(self, roles_cache: dict):
        """Сохранить кэш ролей в Redis"""
        if not self.redis_manager or not self.redis_manager.connected:
            return False

        try:
            import json
            cache_data = {
                'roles': roles_cache,
                'timestamp': time.time()
            }
            await self.redis_manager.set(REDIS_CACHE_KEY, json.dumps(cache_data), CACHE_TTL)
            return True
        except Exception as e:
            logging.error(f"❌ Ошибка сохранения в Redis: {e}")
            return False

    async def _update_role_cache(self):
        """Обновить кэш ролей из базы данных с Redis кэшированием"""
        global _global_role_cache, _global_cache_updated, _database_available, _last_cache_update

        current_time = time.time()

        # Сначала пробуем загрузить из Redis
        if await self._load_from_redis():
            # Проверяем, не устарел ли кэш
            if (current_time - _last_cache_update) < CACHE_TTL:
                return  # Кэш актуален

        # Используем блокировку для предотвращения одновременных обновлений
        async with _cache_lock:
            # Двойная проверка после получения блокировки
            if _global_cache_updated and (current_time - _last_cache_update) < CACHE_TTL:
                return

            # Проверяем доступность БД
            if _database_available is None:
                if not await self._check_database_availability():
                    return

            if _database_available is False:
                return

            try:
                from database import get_db_session, User
                from sqlalchemy import select

                async with get_db_session() as session:
                    # Оптимизированный запрос - только нужные поля
                    result = await session.execute(
                        select(User.telegram_id, User.role).where(User.role.in_([
                            'admin', 'manager', 'curator', 'teacher', 'student'
                        ]))
                    )
                    users_data = result.all()

                    # Группируем по ролям
                    new_cache = {
                        'admin': [],
                        'manager': [],
                        'curator': [],
                        'teacher': [],
                        'student': []
                    }

                    for telegram_id, role in users_data:
                        if role in new_cache:
                            new_cache[role].append(telegram_id)

                    # Атомарное обновление кэша
                    _global_role_cache = new_cache
                    _global_cache_updated = True
                    _last_cache_update = current_time

                    # Сохраняем в Redis
                    await self._save_to_redis(new_cache)

                    logging.info(f"🔄 Кэш ролей обновлен из БД ({len(users_data)} пользователей)")

            except Exception as e:
                logging.error(f"❌ Ошибка обновления кэша ролей: {e}")
                _database_available = False
                # Инициализируем пустой кэш при ошибке
                if not _global_role_cache:
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

        # Проверяем TTL и необходимость обновления кэша
        current_time = time.time()
        cache_expired = (current_time - _last_cache_update) >= CACHE_TTL

        # Если кэш не инициализирован или устарел, обновляем его синхронно
        if (not _global_cache_updated or cache_expired) and _database_available is not False:
            await self._update_role_cache()

        # Определяем роль по ID из кэша
        role = "new_user"  # По умолчанию для пользователей не из базы

        # Если кэш пустой или БД недоступна, все пользователи считаются новыми
        if (_database_available is False or
            not _global_role_cache or
            all(not users for users in _global_role_cache.values())):
            role = "new_user"
        else:
            # Быстрый поиск роли в кэше
            user_found = False
            for role_name, user_ids in _global_role_cache.items():
                if user_id in user_ids:
                    role = role_name
                    user_found = True
                    break

            # Если пользователь не найден в кэше, он не зарегистрирован
            if not user_found:
                role = "new_user"

        # Логирование для отладки
        logging.debug(f"MIDDLEWARE: User {user_id} -> Role: {role}")

        # Добавляем роль в данные события
        data["user_role"] = role
        data["user_id"] = user_id

        # Продолжаем обработку события
        return await handler(event, data)


async def force_update_role_cache():
    """Принудительно обновить кэш ролей (для использования при добавлении новых пользователей)"""
    global _global_role_cache, _global_cache_updated, _last_cache_update

    try:
        from database import get_db_session, User
        from sqlalchemy import select

        # Создаем временный экземпляр для доступа к Redis методам
        temp_middleware = RoleMiddleware()

        async with get_db_session() as session:
            # Оптимизированный запрос - только нужные поля
            result = await session.execute(
                select(User.telegram_id, User.role).where(User.role.in_([
                    'admin', 'manager', 'curator', 'teacher', 'student'
                ]))
            )
            users_data = result.all()

            # Группируем по ролям
            new_cache = {
                'admin': [],
                'manager': [],
                'curator': [],
                'teacher': [],
                'student': []
            }

            for telegram_id, role in users_data:
                if role in new_cache:
                    new_cache[role].append(telegram_id)

            # Атомарное обновление кэша
            _global_role_cache = new_cache
            _global_cache_updated = True
            _last_cache_update = time.time()

            # Сохраняем в Redis
            await temp_middleware._save_to_redis(new_cache)

            logging.info(f"🔄 Кэш ролей принудительно обновлен ({len(users_data)} пользователей)")

    except Exception as e:
        logging.error(f"❌ Ошибка принудительного обновления кэша ролей: {e}")
        # Инициализируем пустой кэш при ошибке
        _global_role_cache = {
            'admin': [],
            'manager': [],
            'curator': [],
            'teacher': [],
            'student': []
        }

async def clear_role_cache():
    """Очистить кэш ролей (и в Redis тоже)"""
    global _global_role_cache, _global_cache_updated

    _global_role_cache = {}
    _global_cache_updated = False

    # Очищаем Redis
    if REDIS_ENABLED:
        try:
            redis_manager = RedisManager()
            if redis_manager.connected:
                await redis_manager.delete(REDIS_CACHE_KEY)
                logging.info("🗑️ Кэш ролей очищен из Redis")
        except Exception as e:
            logging.error(f"❌ Ошибка очистки Redis кэша: {e}")

    # Также очищаем кэш клавиатур
    role_keyboards_manager.clear_cache()


async def update_user_keyboard(message, new_role: str):
    """
    Обновить клавиатуру для пользователя при изменении его роли

    Args:
        message: Объект сообщения
        new_role: Новая роль пользователя
    """
    try:
        await role_keyboards_manager.set_keyboard_for_user(message, new_role)
        logging.info(f"✅ Клавиатура обновлена для пользователя {message.from_user.id} с новой ролью '{new_role}'")
    except Exception as e:
        logging.error(f"❌ Ошибка обновления клавиатуры для пользователя {message.from_user.id}: {e}")


async def update_user_menu(bot, telegram_id: int, new_role: str):
    """
    Обновить меню пользователя через бота

    Args:
        bot: Экземпляр бота
        telegram_id: Telegram ID пользователя
        new_role: Новая роль пользователя
    """
    try:
        # Создаем фиктивное сообщение для обновления клавиатуры
        from aiogram.types import User, Chat, Message

        # Отправляем сообщение пользователю с обновленной клавиатурой
        from aiogram.types import ReplyKeyboardRemove

        if new_role == "admin":
            keyboard = role_keyboards_manager.get_keyboard_for_role("admin")
            await bot.send_message(
                chat_id=telegram_id,
                text="🔄 Ваша роль обновлена до админа. Клавиатура активирована.",
                reply_markup=keyboard
            )
        else:
            await bot.send_message(
                chat_id=telegram_id,
                text="🔄 Ваша роль обновлена. Клавиатура убрана.",
                reply_markup=ReplyKeyboardRemove()
            )

        logging.info(f"✅ Меню обновлено для пользователя {telegram_id} с ролью '{new_role}'")
    except Exception as e:
        logging.error(f"❌ Ошибка обновления меню для пользователя {telegram_id}: {e}")