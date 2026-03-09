from fastapi import APIRouter

from .matrices import router as matrices_router
from .system_configs import router as system_configs_router
from .task_blueprints import router as task_blueprints_router
from .workflows import router as workflows_router

router = APIRouter(prefix="/studio")

router.include_router(workflows_router)
router.include_router(matrices_router)
router.include_router(task_blueprints_router)
router.include_router(system_configs_router)
