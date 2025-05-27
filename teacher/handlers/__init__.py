from aiogram import Router
from .main import router as main_router
from .tests import router as tests_router
from .analytics import router as analytics_router
from .groups import router as groups_router

router = Router()
router.include_router(main_router)
router.include_router(tests_router)
router.include_router(analytics_router)
router.include_router(groups_router)

__all__ = ["router"]