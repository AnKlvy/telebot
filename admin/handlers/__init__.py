from aiogram import Router
from .main import router as main_router

router = Router()
router.include_router(main_router)

__all__ = ["router"]
