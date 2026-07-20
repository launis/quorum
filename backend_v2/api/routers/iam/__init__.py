"""IAM API Routers."""

from fastapi import APIRouter

from .auth import router as auth_router
from .organizations import router as organizations_router
from .users import router as users_router

__all__ = ["router"]

router = APIRouter(prefix="/iam")

# Map /api/v2/iam/auth directly instead of moving the legacy auth endpoints under `/iam` prefix in auth_router.py
router.include_router(auth_router)
router.include_router(users_router)
router.include_router(organizations_router)
