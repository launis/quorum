"""Execution API Routers.

This module aggregates the execution, workflows, and reports routing logic, providing
a centralized APIRouter for all execution-related endpoints.
"""

from fastapi import APIRouter

from .executions import router as executions_router
from .reports import external_router as external_reports_router
from .reports import router as reports_router
from .workflows import router as workflows_router

__all__ = ["external_reports_router", "reports_router", "router"]

router = APIRouter(prefix="/execution")
router.include_router(executions_router)
router.include_router(workflows_router)
router.include_router(reports_router)

