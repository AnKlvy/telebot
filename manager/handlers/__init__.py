from aiogram import Router
from .main import router as main_router
from .analytics import router as analytics_router
from .homework import router as homework_router
from .topics import router as topics_router
router = Router()
router.include_router(main_router)
router.include_router(analytics_router)
router.include_router(homework_router)
router.include_router(topics_router)
__all__ = ["router"]