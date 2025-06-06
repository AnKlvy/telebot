from .main import router as main_router
from .homework import router as homework_router
from .progress import router as progress_router
from .shop import router as shop_router
from .test_report import router as test_report_router
from .trial_ent import router as trial_ent_router
from .curator_contact import router as curator_contact_router
from .account import router as account_router
from .homework_quiz import router as homework_quiz_router

router= main_router
router.include_router(homework_router)
router.include_router(progress_router)
router.include_router(shop_router)
router.include_router(test_report_router)
router.include_router(trial_ent_router)
router.include_router(curator_contact_router)
router.include_router(account_router)
router.include_router(homework_quiz_router)

__all__ = ["router"]
