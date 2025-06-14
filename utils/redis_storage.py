"""
Redis Storage для aiogram FSM
"""
import json
import logging
from typing import Dict, Optional, Any

from aiogram.fsm.storage.base import BaseStorage, StorageKey, StateType
from .redis_manager import RedisManager

logger = logging.getLogger(__name__)


class RedisStorage(BaseStorage):
    """
    Redis хранилище для aiogram FSM состояний
    """
    
    def __init__(self, redis_manager: RedisManager):
        self.redis_manager = redis_manager
    
    def _make_key(self, key: StorageKey) -> str:
        """Создать ключ для Redis"""
        return f"fsm:{key.bot_id}:{key.chat_id}:{key.user_id}"
    
    def _make_data_key(self, key: StorageKey) -> str:
        """Создать ключ для данных FSM"""
        return f"fsm_data:{key.bot_id}:{key.chat_id}:{key.user_id}"
    
    async def set_state(self, key: StorageKey, state: StateType = None) -> None:
        """Установить состояние"""
        redis_key = self._make_key(key)
        
        if state is None:
            # Удаляем состояние
            if await self.redis_manager.is_connected():
                await self.redis_manager.redis.delete(redis_key)
        else:
            # Сохраняем состояние
            state_value = state.state if hasattr(state, 'state') else str(state)
            if await self.redis_manager.is_connected():
                await self.redis_manager.redis.setex(
                    redis_key, 
                    86400,  # 24 часа TTL
                    state_value
                )
    
    async def get_state(self, key: StorageKey) -> Optional[str]:
        """Получить состояние"""
        if not await self.redis_manager.is_connected():
            return None
            
        redis_key = self._make_key(key)
        try:
            state = await self.redis_manager.redis.get(redis_key)
            return state.decode('utf-8') if state else None
        except Exception as e:
            logger.error(f"Ошибка получения состояния {redis_key}: {e}")
            return None
    
    async def set_data(self, key: StorageKey, data: Dict[str, Any]) -> None:
        """Установить данные"""
        if not await self.redis_manager.is_connected():
            return
            
        redis_key = self._make_data_key(key)
        try:
            if data:
                serialized_data = json.dumps(data, ensure_ascii=False)
                await self.redis_manager.redis.setex(
                    redis_key,
                    86400,  # 24 часа TTL
                    serialized_data
                )
            else:
                await self.redis_manager.redis.delete(redis_key)
        except Exception as e:
            logger.error(f"Ошибка сохранения данных {redis_key}: {e}")
    
    async def get_data(self, key: StorageKey) -> Dict[str, Any]:
        """Получить данные"""
        if not await self.redis_manager.is_connected():
            return {}
            
        redis_key = self._make_data_key(key)
        try:
            data = await self.redis_manager.redis.get(redis_key)
            if data:
                return json.loads(data.decode('utf-8'))
            return {}
        except Exception as e:
            logger.error(f"Ошибка получения данных {redis_key}: {e}")
            return {}
    
    async def update_data(self, key: StorageKey, data: Dict[str, Any]) -> Dict[str, Any]:
        """Обновить данные"""
        current_data = await self.get_data(key)
        current_data.update(data)
        await self.set_data(key, current_data)
        return current_data
    
    async def close(self) -> None:
        """Закрыть соединение"""
        if self.redis_manager:
            await self.redis_manager.disconnect()
