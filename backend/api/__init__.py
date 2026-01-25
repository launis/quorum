"""API Package.

This package contains all FastAPI routers and endpoint definitions for the
Quorum backend application.
"""

from fastapi import APIRouter

from backend.api.routes.config import router as config_router
from backend.api.routes.execution import router as execution_router

api_router = APIRouter()

# Register modular routers
# Prefix handling:
# Config router handles /config internally, so we mount it under /v1?
# Checking config/__init__.py: router = APIRouter() -> include_router(ontology_router prefix="/config")
# So if we mount at /v1, it becomes /v1/config/ontology. Correct.

api_router.include_router(config_router, prefix="/v1")

# Execution router handles /execute, /executions internally.
# Checking execution/__init__.py: router = APIRouter() -> includes lifecycle (prefix="/v1/execute")
# So if we mount at root (or /api), it becomes /api/v1/execute.
# The original execution_router was mounted?
# Let's check main.py or just mount it directly.
# Typically api_router is included in main with prefix="/api".
# So `api_router.include_router(execution_router)` results in:
# /api/v1/execute
# /api/executions (monitor)
api_router.include_router(execution_router)
