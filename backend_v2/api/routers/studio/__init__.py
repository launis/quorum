"""Studio API Routes."""

from fastapi import APIRouter

from .mcp_gateways import router as mcp_gateways_router
from .model_registry import router as model_registry_router
from .prompt_blocks import router as prompt_blocks_router
from .steps import router as steps_router
from .system_configs import router as system_configs_router
from .workflows import router as workflows_router

router = APIRouter(prefix="/studio")

router.include_router(workflows_router)
router.include_router(prompt_blocks_router)
router.include_router(steps_router)
router.include_router(system_configs_router)
router.include_router(model_registry_router)
router.include_router(mcp_gateways_router)
