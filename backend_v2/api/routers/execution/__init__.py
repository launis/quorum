"""Execution API Routers.

This module aggregates the execution and workflows routing logic, providing
a centralized APIRouter for all execution-related endpoints.
"""

from fastapi import APIRouter

from .executions import router as executions_router
from .workflows import router as workflows_router

router = APIRouter(prefix="/execution")
router.include_router(executions_router)
router.include_router(workflows_router)
