from aiogram import Router
from .main import router as main_router
from .subjects import router as subjects_router
from .managers import router as managers_router
from .courses import router as courses_router
from .groups import router as groups_router
from .staff import router as staff_router
from .students import router as students_router
from .curators import router as curators_router
from .teachers import router as teachers_router

router = Router()
router.include_router(main_router)
router.include_router(subjects_router)
router.include_router(managers_router)
router.include_router(courses_router)
router.include_router(groups_router)
router.include_router(staff_router)
router.include_router(students_router)
router.include_router(curators_router)
router.include_router(teachers_router)

__all__ = ["router"]
