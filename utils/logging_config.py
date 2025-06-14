"""
Конфигурация системы логирования
"""
import logging
import sys
import os
from datetime import datetime


def setup_logging():
    """Настройка логирования в файл и консоль"""
    # Создаем папку для логов если не существует
    os.makedirs("logs", exist_ok=True)
    
    # Формат логов
    log_format = "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Настраиваем корневой логгер
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Очищаем существующие обработчики
    logger.handlers.clear()
    
    # 1. Обработчик для консоли (цветной)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Добавляем цвета для разных уровней
    class ColoredFormatter(logging.Formatter):
        COLORS = {
            'DEBUG': '36m',    # Cyan
            'INFO': '32m',     # Green  
            'WARNING': '33m',  # Yellow
            'ERROR': '31m',    # Red
            'CRITICAL': '35m'  # Magenta
        }
        
        def format(self, record):
            record.color = self.COLORS.get(record.levelname, '37m')  # Default white
            return super().format(record)
    
    console_handler.setFormatter(ColoredFormatter(
        "%(asctime)s | \033[%(color)s%(levelname)-8s\033[0m | %(name)-20s | %(message)s",
        datefmt=date_format
    ))
    logger.addHandler(console_handler)
    
    # 2. Обработчик для файла (все логи)
    today = datetime.now().strftime("%Y-%m-%d")
    file_handler = logging.FileHandler(f"logs/bot_{today}.log", encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))
    logger.addHandler(file_handler)
    
    # 3. Обработчик для файла ошибок
    error_handler = logging.FileHandler(f"logs/errors_{today}.log", encoding='utf-8')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))
    logger.addHandler(error_handler)
    
    # Настраиваем фильтр для aiohttp.access логов
    class HealthCheckFilter(logging.Filter):
        """Фильтр для скрытия успешных health check запросов"""
        def filter(self, record):
            # Скрываем только успешные GET /health запросы (200 статус)
            if hasattr(record, 'getMessage'):
                message = record.getMessage()
                if '/health' in message and ' 200 ' in message and 'GET' in message:
                    return False
            return True

    # Применяем фильтр к aiohttp.access логгеру
    aiohttp_logger = logging.getLogger('aiohttp.access')
    aiohttp_logger.addFilter(HealthCheckFilter())

    # Логируем старт
    logging.info("🚀 Система логирования настроена")
    logging.info(f"📁 Логи сохраняются в: logs/bot_{today}.log")
    logging.info(f"📁 Ошибки сохраняются в: logs/errors_{today}.log")
    logging.info("🔇 Health check логи фильтруются (раз в 30 минут)")
