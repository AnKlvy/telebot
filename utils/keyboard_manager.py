"""
Менеджер клавиатур для разных ролей пользователей
"""
import logging
from typing import Dict, Optional
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, Message
from aiogram import Bot


class KeyboardManager:
    """Простой менеджер клавиатур для ролей"""
    
    def __init__(self):
        # Клавиатура только для админов
        self.admin_keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="админ")],
                [KeyboardButton(text="менеджер"), KeyboardButton(text="преподаватель")],
                [KeyboardButton(text="куратор"), KeyboardButton(text="ученик")]
            ],
            resize_keyboard=True,
            persistent=True
        )
        
        # Для всех остальных - убираем клавиатуру
        self.remove_keyboard = ReplyKeyboardRemove()
        
        # Кэш установленных клавиатур для пользователей
        self._user_keyboards: Dict[int, str] = {}
    
    async def set_keyboard_for_role(self, bot: Bot, user_id: int, role: str) -> bool:
        """
        Установить клавиатуру для пользователя в зависимости от роли
        
        Args:
            bot: Экземпляр бота
            user_id: Telegram ID пользователя
            role: Роль пользователя
            
        Returns:
            bool: True если клавиатура была установлена
        """
        try:
            # Проверяем, нужно ли обновлять клавиатуру
            current_role = self._user_keyboards.get(user_id)
            if current_role == role:
                logging.debug(f"Клавиатура для пользователя {user_id} уже установлена для роли {role}")
                return True
            
            if role == "admin":
                # Админы получают клавиатуру с кнопками
                await bot.send_message(
                    chat_id=user_id,
                    text="🔑 Добро пожаловать, админ! Клавиатура активирована.",
                    reply_markup=self.admin_keyboard
                )
                logging.info(f"✅ Клавиатура админа установлена для пользователя {user_id}")
            else:
                # Просто обновить клавиатуру через set_chat_menu_button
                from aiogram.types import MenuButtonDefault
                await bot.set_chat_menu_button(
                    chat_id=user_id,
                    menu_button=MenuButtonDefault()
                )
                logging.info(f"✅ Клавиатура убрана для пользователя {user_id} (роль: {role})")
            
            # Запоминаем установленную роль
            self._user_keyboards[user_id] = role
            return True
            
        except Exception as e:
            logging.error(f"❌ Ошибка установки клавиатуры для пользователя {user_id}: {e}")
            return False
    
    async def force_update_keyboard(self, bot: Bot, user_id: int, role: str) -> bool:
        """
        Принудительно обновить клавиатуру (игнорируя кэш)
        
        Args:
            bot: Экземпляр бота
            user_id: Telegram ID пользователя
            role: Роль пользователя
            
        Returns:
            bool: True если клавиатура была обновлена
        """
        # Сбрасываем кэш для этого пользователя
        if user_id in self._user_keyboards:
            del self._user_keyboards[user_id]
        
        # Устанавливаем клавиатуру
        return await self.set_keyboard_for_role(bot, user_id, role)
    
    def get_keyboard_for_role(self, role: str):
        """
        Получить клавиатуру для роли (для использования в reply_markup)
        
        Args:
            role: Роль пользователя
            
        Returns:
            ReplyKeyboardMarkup или ReplyKeyboardRemove
        """
        if role == "admin":
            return self.admin_keyboard
        else:
            return self.remove_keyboard
    
    def clear_cache(self):
        """Очистить кэш клавиатур"""
        self._user_keyboards.clear()
        logging.info("🗑️ Кэш клавиатур очищен")
    
    def get_cache_info(self) -> Dict[str, int]:
        """
        Получить информацию о кэше
        
        Returns:
            Dict с информацией о кэше
        """
        return {
            "total_users": len(self._user_keyboards),
            "admin_users": len([r for r in self._user_keyboards.values() if r == "admin"]),
            "other_users": len([r for r in self._user_keyboards.values() if r != "admin"])
        }


# Глобальный экземпляр менеджера
keyboard_manager = KeyboardManager()


async def update_user_keyboard_after_role_change(user_id: int, new_role: str):
    """
    Обновить клавиатуру пользователя после изменения роли в базе данных
    
    Args:
        user_id: Telegram ID пользователя
        new_role: Новая роль пользователя
    """
    try:
        from aiogram import Bot
        from utils.config import TOKEN
        
        bot = Bot(token=TOKEN)
        success = await keyboard_manager.force_update_keyboard(bot, user_id, new_role)
        await bot.session.close()
        
        if success:
            logging.info(f"✅ Клавиатура обновлена для пользователя {user_id} с новой ролью '{new_role}'")
        else:
            logging.error(f"❌ Не удалось обновить клавиатуру для пользователя {user_id}")
            
    except Exception as e:
        logging.error(f"❌ Ошибка обновления клавиатуры для пользователя {user_id}: {e}")
