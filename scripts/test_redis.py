#!/usr/bin/env python3
"""
Скрипт для тестирования Redis подключения
"""
import asyncio
import sys
import os
from dotenv import load_dotenv

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Загружаем .env.dev для локального тестирования
load_dotenv('.env.dev')

# Переопределяем REDIS_HOST для локального тестирования
os.environ['REDIS_HOST'] = 'localhost'

from utils.redis_manager import RedisManager
from utils.config import REDIS_ENABLED, REDIS_HOST, REDIS_PORT


async def test_redis():
    """Тестирование Redis подключения"""
    print("🔍 Тестирование Redis подключения...")
    print(f"Redis включен: {REDIS_ENABLED}")
    print(f"Redis хост: {REDIS_HOST}:{REDIS_PORT}")
    
    if not REDIS_ENABLED:
        print("❌ Redis отключен в конфигурации")
        return False
    
    redis_manager = RedisManager()
    
    try:
        # Подключение
        await redis_manager.connect()
        
        if not redis_manager.connected:
            print("❌ Не удалось подключиться к Redis")
            return False
        
        print("✅ Подключение к Redis успешно")
        
        # Тест записи/чтения
        test_key = "test_key"
        test_value = "test_value"
        
        success = await redis_manager.set(test_key, test_value, ttl=60)
        if not success:
            print("❌ Ошибка записи в Redis")
            return False
        
        print("✅ Запись в Redis успешна")
        
        retrieved_value = await redis_manager.get(test_key)
        if retrieved_value != test_value:
            print(f"❌ Ошибка чтения из Redis. Ожидалось: {test_value}, получено: {retrieved_value}")
            return False
        
        print("✅ Чтение из Redis успешно")
        
        # Очистка тестовых данных
        await redis_manager.delete(test_key)
        print("✅ Очистка тестовых данных")
        
        # Тест FSM состояний
        user_id = 12345
        chat_id = 67890
        test_state = "TestState:test"
        test_data = {"key": "value", "number": 42}
        
        success = await redis_manager.set_fsm_state(user_id, chat_id, test_state, test_data)
        if not success:
            print("❌ Ошибка записи FSM состояния")
            return False
        
        print("✅ Запись FSM состояния успешна")
        
        state, data = await redis_manager.get_fsm_state(user_id, chat_id)
        if state != test_state or data != test_data:
            print(f"❌ Ошибка чтения FSM состояния")
            print(f"Состояние: ожидалось {test_state}, получено {state}")
            print(f"Данные: ожидалось {test_data}, получено {data}")
            return False
        
        print("✅ Чтение FSM состояния успешно")
        
        # Очистка FSM данных
        await redis_manager.clear_fsm_state(user_id, chat_id)
        print("✅ Очистка FSM данных")
        
        print("\n🎉 Все тесты Redis прошли успешно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании Redis: {e}")
        return False
    
    finally:
        await redis_manager.disconnect()


if __name__ == "__main__":
    result = asyncio.run(test_redis())
    sys.exit(0 if result else 1)
