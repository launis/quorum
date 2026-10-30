"""Execution API Routers.

This module aggregates the execution and reports routing logic, providing
a centralized APIRouter for execution-related endpoints.
"""

from fastapi import APIRouter

from .executions import router as executions_router
from .reports import router as reports_router

__all__ = ["reports_router", "router"]

router = APIRouter(prefix="/execution")
router.include_router(executions_router)
