from aiogram import Router
from .main import router as main_router
from .analytics import router as analytics_router
from .homework import router as homework_router

router = Router()
router.include_router(main_router)
router.include_router(analytics_router)
router.include_router(homework_router)

__all__ = ["router"]