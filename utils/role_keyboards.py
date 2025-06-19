"""
Управление постоянными клавиатурами (ReplyKeyboardMarkup) в зависимости от роли пользователя
"""
import logging
from typing import Dict
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


class RoleKeyboardsManager:
    """Менеджер для установки постоянных клавиатур в зависимости от роли пользователя"""
    
    def __init__(self):
        # Убираем кэширование - клавиатура должна устанавливаться при каждом сообщении
        pass
        
        # Определяем клавиатуры для каждой роли
        self._role_keyboards = {
            "admin": ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="админ")],
                    [KeyboardButton(text="менеджер"), KeyboardButton(text="преподаватель")],
                    [KeyboardButton(text="куратор"), KeyboardButton(text="ученик")]
                ],
                resize_keyboard=True,
                persistent=True
            ),
            "manager": ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="менеджер")]
                ],
                resize_keyboard=True,
                persistent=True
            ),
            "curator": ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="куратор")]
                ],
                resize_keyboard=True,
                persistent=True
            ),
            "teacher": ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="преподаватель")]
                ],
                resize_keyboard=True,
                persistent=True
            ),
            "student": ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="ученик")]
                ],
                resize_keyboard=True,
                persistent=True
            ),
            "new_user": ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="старт")]
                ],
                resize_keyboard=True,
                persistent=True
            )
        }
    
    async def set_keyboard_for_user(self, message, role: str) -> bool:
        """
        Установить постоянную клавиатуру для конкретного пользователя в зависимости от его роли

        Args:
            message: Объект сообщения для отправки клавиатуры
            role: Роль пользователя

        Returns:
            bool: True если клавиатура была установлена
        """
        # Получаем клавиатуру для роли
        keyboard = self._role_keyboards.get(role, self._role_keyboards["new_user"])

        try:
            # Отправляем клавиатуру с минимальным сообщением
            await message.answer("🎛️", reply_markup=keyboard)
            return True

        except Exception as e:
            logging.error(f"❌ Ошибка установки клавиатуры для пользователя {message.from_user.id}: {e}")
            return False
    
    async def remove_keyboard_for_user(self, message) -> bool:
        """
        Удалить постоянную клавиатуру для конкретного пользователя
        
        Args:
            message: Объект сообщения для удаления клавиатуры
            
        Returns:
            bool: True если клавиатура была удалена успешно
        """
        user_id = message.from_user.id
        
        try:
            # Удаляем клавиатуру
            await message.answer(
                "🗑️ Клавиатура удалена",
                reply_markup=ReplyKeyboardRemove()
            )
            
            # Кэш не используется
            
            logging.info(f"✅ Клавиатура удалена для пользователя {user_id}")
            return True
            
        except Exception as e:
            logging.error(f"❌ Ошибка удаления клавиатуры для пользователя {user_id}: {e}")
            return False
    
    def get_keyboard_for_role(self, role: str) -> ReplyKeyboardMarkup:
        """
        Получить клавиатуру для роли
        
        Args:
            role: Роль пользователя
            
        Returns:
            ReplyKeyboardMarkup: Клавиатура для роли
        """
        return self._role_keyboards.get(role, self._role_keyboards["new_user"])
    
    def clear_cache(self):
        """Кэш не используется, но метод оставлен для совместимости"""
        logging.info("🗑️ Кэш клавиатур не используется")

    def get_cache_info(self) -> Dict[str, int]:
        """
        Кэш не используется, но метод оставлен для совместимости

        Returns:
            Dict[str, int]: Пустая статистика
        """
        return {}


# Глобальный экземпляр менеджера клавиатур
role_keyboards_manager = RoleKeyboardsManager()
