from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext


async def check_if_id_in_callback_data(callback_starts_with: str, callback: CallbackQuery, state: FSMContext, id_type) -> str:
    """
    Проверяет, является ли callback.data ID или это кнопка "назад"
    
    Args:
        callback_starts_with: Префикс для поиска в callback_data
        callback: Объект CallbackQuery
        state: Контекст состояния FSM
        id_type: Тип ID для сохранения в состоянии
        
    Returns:
        str: ID из callback_data или состояния
    """
    # Проверяем, является ли callback.data ID группы или это кнопка "назад"
    if callback.data.startswith(callback_starts_with):
        id = callback.data.replace(callback_starts_with, "")
        print(f"{id_type}_id: ", id)
        await state.update_data(**{id_type: id})
    else:
        # Если это кнопка "назад" или другой callback, берем ID из состояния
        user_data = await state.get_data()
        id = user_data.get(id_type)
        print(f"Using saved {id_type}_id: ", id)
    return id
