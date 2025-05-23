from .main import router as main_router
from .groups import router as groups_router

router = main_router
router.include_router(groups_router)

__all__ = ["router"]