#!/usr/bin/env python3
"""
Тестовый скрипт для проверки добавления куратора администратором
"""
import asyncio
import sys
import os
from unittest.mock import AsyncMock, MagicMock

# Добавляем путь к корневой папке проекта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import init_database
from admin.handlers.curators import process_curator_telegram_id
from admin.utils.common import check_existing_user_for_role_assignment
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, User


async def test_curator_handler():
    """Тестирование обработчика добавления куратора"""
    print("🧪 Тестирование обработчика добавления куратора")
    print("=" * 50)
    
    # Инициализируем базу данных
    await init_database()
    
    # Создаем мок объекты
    mock_user = User(
        id=955518340,  # Ваш Telegram ID (админ)
        is_bot=False,
        first_name="Андрей",
        username="admin_user"
    )
    
    mock_message = MagicMock(spec=Message)
    mock_message.text = "955518340"  # Ваш Telegram ID
    mock_message.from_user = mock_user
    mock_message.answer = AsyncMock()
    
    mock_state = AsyncMock(spec=FSMContext)
    mock_state.update_data = AsyncMock()
    mock_state.set_state = AsyncMock()
    
    print(f"🔍 Тестируем с Telegram ID: {mock_message.text}")
    print(f"🔍 От пользователя: {mock_user.id}")
    
    try:
        # Вызываем обработчик
        await process_curator_telegram_id(mock_message, mock_state)
        
        # Проверяем, что было вызвано
        print(f"✅ Обработчик выполнен успешно")
        print(f"📞 message.answer вызван {mock_message.answer.call_count} раз(а)")
        
        if mock_message.answer.call_count > 0:
            for i, call in enumerate(mock_message.answer.call_args_list):
                args, kwargs = call
                print(f"📞 Вызов {i+1}: {kwargs.get('text', args[0] if args else 'Нет текста')}")
        
    except Exception as e:
        print(f"❌ Ошибка при выполнении обработчика: {e}")
        import traceback
        traceback.print_exc()


async def test_check_function_directly():
    """Прямое тестирование функции проверки"""
    print("\n🧪 Прямое тестирование функции check_existing_user_for_role_assignment")
    print("=" * 70)
    
    await init_database()
    
    # Тест 1: Админ добавляет себя
    result = await check_existing_user_for_role_assignment(
        telegram_id=955518340,
        target_role='curator', 
        current_user_telegram_id=955518340
    )
    
    print(f"🔍 Тест 1 - Админ добавляет себя:")
    print(f"   exists: {result['exists']}")
    print(f"   can_assign: {result['can_assign']}")
    print(f"   message: {result['message']}")


if __name__ == "__main__":
    asyncio.run(test_check_function_directly())
    asyncio.run(test_curator_handler())
