import logging
from typing import Any

from fastapi import APIRouter

from backend_v2.api.dependencies import CurrentUserDep, StudioServiceDep
from backend_v2.models.v2_core import PromptBlock

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/prompt-blocks", tags=["Admin Studio V2 - Prompt Blocks"])

@router.get("/", response_model=list[PromptBlock])
async def get_prompt_blocks(current_user: CurrentUserDep, studio_service: StudioServiceDep) -> list[PromptBlock]:
    """Retrieve all prompt blocks securely via SSOT Service Layer."""
    return await studio_service.list_prompt_blocks(current_user)

@router.get("/{id}", response_model=PromptBlock)
async def get_prompt_block(id: str, current_user: CurrentUserDep, studio_service: StudioServiceDep) -> PromptBlock:
    """Retrieve a specific prompt block securely via SSOT Service Layer."""
    return await studio_service.get_prompt_block(current_user, id)

@router.put("/{id}", response_model=PromptBlock)
async def save_prompt_block(id: str, data: PromptBlock, current_user: CurrentUserDep, studio_service: StudioServiceDep) -> PromptBlock:
    """Append or update a prompt block securely via SSOT Service Layer."""
    return await studio_service.save_prompt_block(current_user, id, data)

@router.delete("/{id}")
async def delete_prompt_block(id: str, current_user: CurrentUserDep, studio_service: StudioServiceDep, force_delete: bool = False) -> dict[str, Any]:
    """Delete a prompt block securely via SSOT Service Layer."""
    await studio_service.delete_prompt_block(current_user, id, force_delete=force_delete)
    return {"status": "success", "deleted_id": id}
