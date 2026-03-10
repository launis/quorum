from fastapi import APIRouter

from .prompt_blocks import router as prompt_blocks_router
from .system_configs import router as system_configs_router
from .steps import router as steps_router
from .workflows import router as workflows_router

router = APIRouter(prefix="/studio")

router.include_router(workflows_router)
router.include_router(prompt_blocks_router)
router.include_router(steps_router)
router.include_router(system_configs_router)
