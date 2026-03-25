"""System router for exposing backend registry and configuration."""

from fastapi import APIRouter

router = APIRouter(prefix="/system", tags=["System"])
