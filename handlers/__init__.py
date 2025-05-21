from .homework import router as homework_router, show_main_menu
from .progress import router as progress_router

router = homework_router
router.include_router(progress_router)

__all__ = ["router", "show_main_menu"]
