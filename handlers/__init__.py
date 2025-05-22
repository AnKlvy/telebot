from .homework import router as homework_router, show_main_menu
from .progress import router as progress_router
from .shop import router as shop_router
from .test_report import router as test_report_router

router = homework_router
router.include_router(progress_router)
router.include_router(shop_router)
router.include_router(test_report_router)

__all__ = ["router", "show_main_menu"]
