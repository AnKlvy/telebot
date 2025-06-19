"""
Очистка магазина от статических бонусных тестов
"""
import asyncio
import sys
import os

# Добавляем корневую папку проекта в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import ShopItemRepository


async def remove_static_bonus_test():
    """Удалить статический товар 'Бонусный тест' из магазина"""
    print("Удаление статического товара 'Бонусный тест'...")
    
    try:
        # Получаем все товары
        items = await ShopItemRepository.get_all_active()
        
        # Ищем статический "Бонусный тест"
        bonus_test_item = None
        for item in items:
            if item.name == "Бонусный тест" and item.item_type == "bonus_test":
                bonus_test_item = item
                break
        
        if bonus_test_item:
            # Деактивируем товар
            success = await ShopItemRepository.deactivate(bonus_test_item.id)
            if success:
                print(f"   ✅ Статический товар 'Бонусный тест' (ID: {bonus_test_item.id}) деактивирован")
            else:
                print(f"   ❌ Не удалось деактивировать товар 'Бонусный тест'")
        else:
            print("   ⚠️ Статический товар 'Бонусный тест' не найден")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Ошибка при удалении статического товара: {e}")
        return False


async def main():
    """Основная функция очистки"""
    print("🧹 Очистка магазина от статических бонусных тестов...")
    
    success = await remove_static_bonus_test()
    
    if success:
        print("✅ Очистка завершена успешно!")
    else:
        print("❌ Очистка завершена с ошибками!")


if __name__ == "__main__":
    asyncio.run(main())
