from .homework import router as homework_router, show_main_menu
from .progress import router as progress_router
from .shop import router as shop_router
from .test_report import router as test_report_router
from .trial_ent import router as trial_ent_router
from .curator_contact import router as curator_router
from .account import router as account_router

router = homework_router
router.include_router(progress_router)
router.include_router(shop_router)
router.include_router(test_report_router)
router.include_router(trial_ent_router)
router.include_router(curator_router)
router.include_router(account_router)

__all__ = ["router", "show_main_menu"]
