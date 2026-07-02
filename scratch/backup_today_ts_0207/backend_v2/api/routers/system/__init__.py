"""System API Routers."""

from fastapi import APIRouter

from .configs import router as configs_router
from .health import router as health_router
from .telemetry import router as telemetry_router

router = APIRouter(prefix="/system")
router.include_router(health_router)
router.include_router(telemetry_router)
router.include_router(configs_router)
