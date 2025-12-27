from fastapi import APIRouter

# DEPRECATED: This router's functionality has been consolidated into backend/api/execution_router.py
# This file is kept only to prevent import errors if legacy code references it.
# It should not be included in the main application.

router = APIRouter(tags=["Deprecated"])
