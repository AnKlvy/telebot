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
            # Для всех остальных ролей - убираем клавиатуру
            "manager": None,
            "curator": None,
            "teacher": None,
            "student": None,
            "new_user": None
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
        from aiogram.types import ReplyKeyboardRemove

        try:
            # Только админы получают клавиатуру с кнопками
            if role == "admin":
                keyboard = self._role_keyboards.get("admin")
                await message.answer("🔄 Роль обновлена", reply_markup=keyboard)
            else:
                # Для всех остальных ролей убираем клавиатуру
                await message.answer("🔄 Роль обновлена", reply_markup=ReplyKeyboardRemove())

            logging.info(f"✅ Клавиатура установлена для пользователя {message.from_user.id}, роль: {role}")
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
        if role == "admin":
            return self._role_keyboards.get("admin")
        else:
            from aiogram.types import ReplyKeyboardRemove
            return ReplyKeyboardRemove()

    def get_pending_keyboard(self):
        """Получить подготовленную клавиатуру"""
        return getattr(self, '_pending_keyboard', None)

    def should_update_keyboard(self, user_id: int, role: str) -> bool:
        """Проверить, нужно ли обновлять клавиатуру для пользователя"""
        if not hasattr(self, '_user_keyboards'):
            self._user_keyboards = {}

        current_role = self._user_keyboards.get(user_id)
        return current_role != role

    def get_reply_markup_for_role(self, role: str):
        """Получить reply_markup для роли (для использования в обработчиках)"""
        if role == "admin":
            return self._role_keyboards.get("admin")
        else:
            from aiogram.types import ReplyKeyboardRemove
            return ReplyKeyboardRemove()
    
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
