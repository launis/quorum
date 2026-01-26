"""Builder API Package."""

from fastapi import APIRouter

from backend.api.routes.builder.fusion import router as fusion_router
from backend.api.routes.builder.library import router as library_router
from backend.api.routes.builder.playground import router as playground_router
from backend.api.routes.builder.steps import router as steps_router
from backend.api.routes.builder.workflows import router as workflows_router

router = APIRouter(prefix="/builder", tags=["Builder"])

# Include sub-routers
# We can mount them at root or namespaced if preferred.
# The original builder_router had /builder prefix.
# library: /schema, /config, /seed_data -> /builder/schema, ...
# workflows: /workflows -> /builder/workflows
# steps: /steps -> /builder/steps
# fusion: /validate, /compile -> /builder/validate

router.include_router(library_router)
router.include_router(workflows_router)
router.include_router(steps_router)
router.include_router(fusion_router)
router.include_router(playground_router)
