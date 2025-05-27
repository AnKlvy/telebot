from aiogram import Router
from .handlers import router as handlers_router
from .menu import show_tests_menu
from .states import TestsStates

# Создаем новый роутер с низким приоритетом
router = Router(name="tests_router")
router.include_router(handlers_router)

__all__ = ["router", "show_tests_menu", "TestsStates"]