import logging
from typing import Any

from fastapi import APIRouter

from backend_v2.api.dependencies import CurrentUserDep, StudioServiceDep
from backend_v2.models.v2_core import PromptBlock

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/matrices", tags=["Admin Studio V2 - Matrices"])

@router.get("/", response_model=list[PromptBlock])
async def get_matrices(current_user: CurrentUserDep, studio_service: StudioServiceDep) -> list[PromptBlock]:
    """Retrieve all evaluation matrices securely via SSOT Service Layer."""
    return await studio_service.list_matrices(current_user)

@router.get("/{id}", response_model=PromptBlock)
async def get_matrix(id: str, current_user: CurrentUserDep, studio_service: StudioServiceDep) -> PromptBlock:
    """Retrieve a specific matrix securely via SSOT Service Layer."""
    return await studio_service.get_matrix(current_user, id)

@router.put("/{id}", response_model=PromptBlock)
async def save_matrix(id: str, data: PromptBlock, current_user: CurrentUserDep, studio_service: StudioServiceDep) -> PromptBlock:
    """Append or update a matrix securely via SSOT Service Layer."""
    return await studio_service.save_matrix(current_user, id, data)

@router.delete("/{id}")
async def delete_matrix(id: str, current_user: CurrentUserDep, studio_service: StudioServiceDep) -> dict[str, Any]:
    """Delete a matrix securely via SSOT Service Layer."""
    await studio_service.delete_matrix(current_user, id)
    return {"status": "success", "deleted_id": id}
