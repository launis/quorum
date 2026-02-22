from fastapi import APIRouter

from backend.api.routes.config import (
    agents,
    components,
    dimensions,
    knowledge,
    matrices,
    models,
    ontology,
    outputs,
    schemas,
    steps,
    workflows,
)

router = APIRouter()

router.include_router(components.router, prefix="/components", tags=["Components"])
router.include_router(matrices.router, prefix="/matrices")
router.include_router(dimensions.router, prefix="/dimensions")
router.include_router(agents.router, prefix="/agents")
router.include_router(outputs.router, prefix="/outputs")
router.include_router(workflows.router, prefix="/workflows", tags=["Workflows"])
router.include_router(knowledge.router, prefix="/knowledge", tags=["Knowledge"])
router.include_router(steps.router, prefix="/steps", tags=["Steps"])
router.include_router(models.router, prefix="/models", tags=["Models"])
router.include_router(ontology.router, prefix="/ontology", tags=["Ontology"])
router.include_router(schemas.router)
