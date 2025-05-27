from aiogram import Router
from .main import router as main_router
from .analytics import router as analytics_router

router = Router()
router.include_router(main_router)
router.include_router(analytics_router)

__all__ = ["router"]