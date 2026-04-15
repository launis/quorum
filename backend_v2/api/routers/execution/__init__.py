"""Execution API Routers."""

from fastapi import APIRouter

from .executions import router as executions_router
from .scorecard import router as scorecard_router
from .workflows import router as workflows_router

router = APIRouter(prefix="/execution")
router.include_router(executions_router)
router.include_router(workflows_router)
router.include_router(scorecard_router)
