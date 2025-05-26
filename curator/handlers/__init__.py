from .main import router as main_router
from .groups import router as groups_router
from .homeworks import router as homeworks_router
from .messages import router as messages_router
from .analytics import router as analytics_router
from .tests import router as tests_router

router = main_router
router.include_router(groups_router)
router.include_router(homeworks_router)
router.include_router(messages_router)
router.include_router(analytics_router)
router.include_router(tests_router)

__all__ = ["router"]