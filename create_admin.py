#!/usr/bin/env python3
"""
Скрипт для создания админа
"""
import asyncio
import sys
import os

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import UserRepository


async def create_admin():
    """Создать админа"""
    try:
        # Данные админа
        telegram_id = 955518340
        name = "Андрей Климов"
        role = "admin"
        
        # Проверяем, существует ли уже админ
        existing_admin = await UserRepository.get_by_telegram_id(telegram_id)
        
        if existing_admin:
            print(f"⚠️ Админ уже существует:")
            print(f"   ID: {existing_admin.id}")
            print(f"   Имя: {existing_admin.name}")
            print(f"   Telegram ID: {existing_admin.telegram_id}")
            print(f"   Роль: {existing_admin.role}")
            return existing_admin
        
        # Создаем нового админа
        admin_user = await UserRepository.create(
            telegram_id=telegram_id,
            name=name,
            role=role
        )
        
        print(f"✅ Админ успешно создан:")
        print(f"   ID: {admin_user.id}")
        print(f"   Имя: {admin_user.name}")
        print(f"   Telegram ID: {admin_user.telegram_id}")
        print(f"   Роль: {admin_user.role}")
        
        return admin_user
        
    except Exception as e:
        print(f"❌ Ошибка при создании админа: {e}")
        return None


async def main():
    """Главная функция"""
    print("🔧 Создание админа...")
    admin = await create_admin()
    
    if admin:
        print("\n🎉 Готово! Админ создан или уже существует.")
    else:
        print("\n💥 Не удалось создать админа.")


if __name__ == "__main__":
    asyncio.run(main())
