"""
Инициализация данных магазина
"""
import asyncio
from database import init_database, ShopItemRepository


async def init_shop_items():
    """Проверка товаров магазина (теперь все товары создаются через админ-панель)"""
    print("Проверка товаров магазина...")

    # Проверяем, есть ли товары в базе
    existing_items = await ShopItemRepository.get_all_active()
    print(f"В магазине активных товаров: {len(existing_items)}")

    if existing_items:
        for item in existing_items:
            print(f"• {item.name} ({item.item_type}) - {item.price} монет")
    else:
        print("⚠️ В магазине нет активных товаров. Создайте их через админ-панель.")

    print("Проверка товаров завершена.")


async def main():
    """Основная функция инициализации"""
    await init_database()
    await init_shop_items()


if __name__ == "__main__":
    asyncio.run(main())
