from aiogram import Router
from .main import router as main_router
from .analytics import router as analytics_router
from .homework import router as homework_router
from .topics import router as topics_router
from .lessons import router as lessons_router
from .bonus_test import router as bonus_test_router
from .bonus_tasks import router as bonus_tasks_router
from .month_tests import router as month_tests_router
router = Router()
router.include_router(main_router)
router.include_router(analytics_router)
router.include_router(homework_router)
router.include_router(topics_router)
router.include_router(lessons_router)
router.include_router(bonus_test_router)
router.include_router(bonus_tasks_router)
router.include_router(month_tests_router)
__all__ = ["router"]