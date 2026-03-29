import logging
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, RootModel


class PromptBlockSimulationResponse(RootModel[dict[str, Any]]):
    pass

class PromptBlockDeleteResponse(BaseModel):
    status: str
    deleted_id: str

from backend_v2.api.dependencies import CurrentUserDep, StudioServiceDep
from backend_v2.models.v2_core import PromptBlock

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/prompt-blocks", tags=["Admin Studio V2 - Prompt Blocks"])


class PromptBlockSimulationRequest(BaseModel):
    block: PromptBlock
    mock_inputs: dict[str, Any] = {}


@router.post("/simulate", response_model=PromptBlockSimulationResponse)
async def simulate_prompt_block(
    data: PromptBlockSimulationRequest,
    current_user: CurrentUserDep,
    studio_service: StudioServiceDep,
) -> PromptBlockSimulationResponse:
    """Dry-run and validate a PromptBlock template rendering."""
    result = await studio_service.simulate_prompt_block(current_user, data.block, data.mock_inputs)
    return PromptBlockSimulationResponse(result)


@router.get("/", response_model=list[PromptBlock])
async def get_prompt_blocks(current_user: CurrentUserDep, studio_service: StudioServiceDep) -> list[PromptBlock]:
    """Retrieve all prompt blocks securely via SSOT Service Layer."""
    return await studio_service.list_prompt_blocks(current_user)


@router.get("/{id}", response_model=PromptBlock)
async def get_prompt_block(id: str, current_user: CurrentUserDep, studio_service: StudioServiceDep) -> PromptBlock:
    """Retrieve a specific prompt block by id securely via SSOT Service Layer."""
    return await studio_service.get_prompt_block(current_user, id)


@router.post("/{id}/clone", response_model=PromptBlock)
async def clone_prompt_block(
    id: str,
    current_user: CurrentUserDep,
    studio_service: StudioServiceDep,
) -> PromptBlock:
    """Deep clone a prompt block securely via SSOT Service Layer."""
    return await studio_service.clone_prompt_block(current_user, id)


@router.put("/{id}", response_model=PromptBlock)
async def save_prompt_block(
    id: str,
    data: PromptBlock,
    current_user: CurrentUserDep,
    studio_service: StudioServiceDep,
) -> PromptBlock:
    """Append or update a prompt block securely via SSOT Service Layer."""
    return await studio_service.save_prompt_block(current_user, id, data)


@router.delete("/{id}", response_model=PromptBlockDeleteResponse)
async def delete_prompt_block(
    id: str,
    current_user: CurrentUserDep,
    studio_service: StudioServiceDep,
    force_delete: bool = False,
) -> PromptBlockDeleteResponse:
    """Delete a prompt block securely via SSOT Service Layer."""
    try:
        await studio_service.delete_prompt_block(current_user, id, force_delete=force_delete)
        return PromptBlockDeleteResponse(status="success", deleted_id=id)
    except Exception as e:
        from backend_v2.exceptions import AppException, ErrorCodes
        if isinstance(e, AppException):
            raise
        logger.error(
            "[PromptBlocksRouter] %s: %s",
            ErrorCodes.INTERNAL_SERVER_ERROR.name,
            str(e),
            exc_info=True,
            extra={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value, "target_id": id, "error": str(e)},
        )
        raise AppException(
            message="Internal delete failure",
            status_code=500,
            details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
        ) from e
