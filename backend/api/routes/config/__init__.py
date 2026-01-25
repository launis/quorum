"""Configuration Routes Package."""

from fastapi import APIRouter

from backend.api.routes.config.components import router as components_router
from backend.api.routes.config.ontology import router as ontology_router
from backend.api.routes.config.schemas import router as schemas_router
from backend.api.routes.config.workflows import router as workflows_router

router = APIRouter()

router.include_router(components_router)
router.include_router(ontology_router)
router.include_router(workflows_router)
router.include_router(schemas_router)


