"""Execution Routes Package."""

from fastapi import APIRouter

from backend.api.routes.execution.artifacts import router as artifacts_router
from backend.api.routes.execution.lifecycle import executions_router
from backend.api.routes.execution.lifecycle import router as lifecycle_router
from backend.api.routes.execution.monitor import router as monitor_router
from backend.api.routes.execution.views import router as views_router

router = APIRouter()

router.include_router(lifecycle_router)
router.include_router(executions_router)
router.include_router(monitor_router)
router.include_router(artifacts_router)
router.include_router(views_router)

