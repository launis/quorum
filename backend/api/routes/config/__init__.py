from fastapi import APIRouter

from backend.api.routes.config import components, knowledge, workflows, steps, models, ontology

router = APIRouter()

router.include_router(components.router, prefix="/components", tags=["Components"])
router.include_router(workflows.router, prefix="/workflows", tags=["Workflows"])
router.include_router(knowledge.router, prefix="/knowledge", tags=["Knowledge"])
router.include_router(steps.router, prefix="/steps", tags=["Steps"])
router.include_router(models.router, prefix="/models", tags=["Models"])
router.include_router(ontology.router, prefix="/ontology", tags=["Ontology"])
