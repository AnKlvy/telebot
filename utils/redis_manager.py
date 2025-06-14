"""
Redis менеджер для кэширования данных
"""
import json
import pickle
import logging
from typing import Any, Optional, Dict, List
from datetime import timedelta
import redis.asyncio as redis
from os import getenv
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Настройки Redis
REDIS_HOST = getenv("REDIS_HOST", "redis")
REDIS_PORT = int(getenv("REDIS_PORT", "6379"))
REDIS_DB = int(getenv("REDIS_DB", "0"))
REDIS_PASSWORD = getenv("REDIS_PASSWORD", None)

# TTL по умолчанию (в секундах)
DEFAULT_TTL = 3600  # 1 час
ROLE_CACHE_TTL = 1800  # 30 минут для ролей
KEYBOARD_CACHE_TTL = 600  # 10 минут для клавиатур
FSM_STATE_TTL = 86400  # 24 часа для состояний FSM

class RedisManager:
    """Менеджер для работы с Redis"""
    
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
        self.connected = False
    
    async def connect(self):
        """Подключение к Redis"""
        try:
            self.redis = redis.from_url(
                f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
                password=REDIS_PASSWORD,
                encoding="utf-8",
                decode_responses=False,  # Для работы с pickle
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # Проверяем соединение
            await self.redis.ping()
            self.connected = True
            logger.info("✅ Redis подключен успешно")
            
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к Redis: {e}")
            self.connected = False
            self.redis = None
    
    async def disconnect(self):
        """Отключение от Redis"""
        if self.redis:
            await self.redis.close()
            self.connected = False
            logger.info("🔌 Redis отключен")
    
    async def is_connected(self) -> bool:
        """Проверка соединения с Redis"""
        if not self.redis or not self.connected:
            return False
        
        try:
            await self.redis.ping()
            return True
        except Exception:
            self.connected = False
            return False
    
    # === МЕТОДЫ ДЛЯ КЭШИРОВАНИЯ FSM СОСТОЯНИЙ ===
    
    async def set_fsm_state(self, user_id: int, chat_id: int, state: str, data: Dict = None, ttl: int = FSM_STATE_TTL):
        """Сохранить состояние FSM"""
        if not await self.is_connected():
            return False
        
        try:
            state_key = f"fsm_state:{user_id}:{chat_id}"
            data_key = f"fsm_data:{user_id}:{chat_id}"
            
            await self.redis.setex(state_key, ttl, state)
            if data:
                await self.redis.setex(data_key, ttl, json.dumps(data))
            
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения FSM состояния {user_id}:{chat_id}: {e}")
            return False
    
    async def get_fsm_state(self, user_id: int, chat_id: int) -> tuple[Optional[str], Optional[Dict]]:
        """Получить состояние FSM"""
        if not await self.is_connected():
            return None, None
        
        try:
            state_key = f"fsm_state:{user_id}:{chat_id}"
            data_key = f"fsm_data:{user_id}:{chat_id}"
            
            state = await self.redis.get(state_key)
            data = await self.redis.get(data_key)
            
            state_str = state.decode('utf-8') if state else None
            data_dict = json.loads(data.decode('utf-8')) if data else None
            
            return state_str, data_dict
        except Exception as e:
            logger.error(f"❌ Ошибка получения FSM состояния {user_id}:{chat_id}: {e}")
            return None, None
    
    async def clear_fsm_state(self, user_id: int, chat_id: int):
        """Очистить состояние FSM"""
        if not await self.is_connected():
            return False
        
        try:
            state_key = f"fsm_state:{user_id}:{chat_id}"
            data_key = f"fsm_data:{user_id}:{chat_id}"
            
            await self.redis.delete(state_key, data_key)
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка очистки FSM состояния {user_id}:{chat_id}: {e}")
            return False
    
    # === ОБЩИЕ МЕТОДЫ ===
    
    async def set(self, key: str, value: str, ttl: int = DEFAULT_TTL):
        """Установить значение"""
        if not await self.is_connected():
            return False
        
        try:
            await self.redis.setex(key, ttl, value)
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка установки значения {key}: {e}")
            return False
    
    async def get(self, key: str) -> Optional[str]:
        """Получить значение"""
        if not await self.is_connected():
            return None
        
        try:
            value = await self.redis.get(key)
            return value.decode('utf-8') if value else None
        except Exception as e:
            logger.error(f"❌ Ошибка получения значения {key}: {e}")
            return None
    
    async def delete(self, *keys: str):
        """Удалить ключи"""
        if not await self.is_connected():
            return False
        
        try:
            await self.redis.delete(*keys)
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка удаления ключей {keys}: {e}")
            return False


# Глобальный экземпляр Redis менеджера
redis_manager = RedisManager()
