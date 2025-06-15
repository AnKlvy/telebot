"""
Middleware для мониторинга производительности бота
"""
import time
import asyncio
import logging
import json
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, Update
from utils.redis_manager import RedisManager
from utils.config import REDIS_ENABLED
from datetime import datetime, timedelta
import psutil
import os

logger = logging.getLogger(__name__)

class PerformanceMiddleware(BaseMiddleware):
    """Middleware для мониторинга производительности запросов"""
    
    def __init__(self):
        self.redis_manager = RedisManager() if REDIS_ENABLED else None
        self.request_times = []
        self.active_requests = 0
        self.max_concurrent_requests = 0
        
    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        start_time = time.time()
        self.active_requests += 1
        self.max_concurrent_requests = max(self.max_concurrent_requests, self.active_requests)
        
        user_id = event.from_user.id
        event_type = "message" if isinstance(event, Message) else "callback"
        
        try:
            # Выполняем обработчик
            result = await handler(event, data)
            
            # Измеряем время выполнения
            execution_time = time.time() - start_time
            self.request_times.append(execution_time)
            
            # Логируем медленные запросы (>1 секунды)
            if execution_time > 1.0:
                logger.warning(f"🐌 Медленный запрос: {execution_time:.2f}с | User: {user_id} | Type: {event_type}")
            
            # Сохраняем метрики в Redis
            await self._save_metrics(user_id, event_type, execution_time)
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"❌ Ошибка в запросе: {e} | Time: {execution_time:.2f}с | User: {user_id}")
            raise
        finally:
            self.active_requests -= 1
    
    async def _save_metrics(self, user_id: int, event_type: str, execution_time: float):
        """Сохранить метрики производительности в Redis"""
        if not self.redis_manager or not await self.redis_manager.is_connected():
            return
        
        try:
            timestamp = datetime.now().isoformat()
            metric_data = {
                'user_id': user_id,
                'event_type': event_type,
                'execution_time': execution_time,
                'timestamp': timestamp,
                'active_requests': self.active_requests,
                'memory_usage': psutil.Process().memory_info().rss / 1024 / 1024  # MB
            }
            
            # Сохраняем в Redis с TTL 1 час
            key = f"performance_metrics:{timestamp}"
            await self.redis_manager.set(key, json.dumps(metric_data), 3600)
            
            # Обновляем агрегированную статистику
            await self._update_aggregate_stats(execution_time)
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения метрик: {e}")
    
    async def _update_aggregate_stats(self, execution_time: float):
        """Обновить агрегированную статистику"""
        if not self.redis_manager or not await self.redis_manager.is_connected():
            return
        
        try:
            stats_key = "performance_stats"
            stats_data = await self.redis_manager.get(stats_key)
            
            if stats_data:
                stats = json.loads(stats_data)
            else:
                stats = {
                    'total_requests': 0,
                    'total_time': 0,
                    'min_time': float('inf'),
                    'max_time': 0,
                    'max_concurrent': 0
                }
            
            # Обновляем статистику
            stats['total_requests'] += 1
            stats['total_time'] += execution_time
            stats['min_time'] = min(stats['min_time'], execution_time)
            stats['max_time'] = max(stats['max_time'], execution_time)
            stats['max_concurrent'] = max(stats['max_concurrent'], self.max_concurrent_requests)
            stats['avg_time'] = stats['total_time'] / stats['total_requests']
            
            # Сохраняем обновленную статистику
            await self.redis_manager.set(stats_key, json.dumps(stats), 86400)  # 24 часа
            
        except Exception as e:
            logger.error(f"❌ Ошибка обновления агрегированной статистики: {e}")
    
    def get_current_stats(self) -> Dict[str, Any]:
        """Получить текущую статистику производительности"""
        if not self.request_times:
            return {}
        
        recent_times = self.request_times[-100:]  # Последние 100 запросов
        
        return {
            'active_requests': self.active_requests,
            'max_concurrent_requests': self.max_concurrent_requests,
            'avg_response_time': sum(recent_times) / len(recent_times),
            'min_response_time': min(recent_times),
            'max_response_time': max(recent_times),
            'total_requests': len(self.request_times),
            'memory_usage_mb': psutil.Process().memory_info().rss / 1024 / 1024,
            'cpu_percent': psutil.Process().cpu_percent()
        }


class DatabasePerformanceMonitor:
    """Монитор производительности базы данных"""
    
    def __init__(self):
        self.query_times = []
        self.redis_manager = RedisManager() if REDIS_ENABLED else None
    
    async def log_query(self, query: str, execution_time: float):
        """Логировать выполнение запроса к БД"""
        self.query_times.append(execution_time)
        
        if execution_time > 0.5:  # Медленные запросы >500ms
            logger.warning(f"🐌 Медленный SQL запрос: {execution_time:.3f}с | {query[:100]}...")
        
        # Сохраняем в Redis
        if self.redis_manager and await self.redis_manager.is_connected():
            try:
                metric_data = {
                    'query': query[:200],  # Первые 200 символов
                    'execution_time': execution_time,
                    'timestamp': datetime.now().isoformat()
                }
                key = f"db_metrics:{datetime.now().isoformat()}"
                await self.redis_manager.set(key, json.dumps(metric_data), 3600)
            except Exception as e:
                logger.error(f"❌ Ошибка сохранения метрик БД: {e}")


# Глобальный экземпляр монитора БД
db_monitor = DatabasePerformanceMonitor()
