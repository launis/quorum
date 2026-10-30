"""Admin Studio Prompt Blocks API Router.

Provides endpoints to manage prompt blocks configurations.
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Path, Query, status

from backend_v2.api.dependencies import (
    CurrentUserDep,
    StudioPromptBlockServiceDep,
    StudioSimulationServiceDep,
)
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import OPAQUE_STRIPE_ID_REGEX
from backend_v2.models.domain.prompt_blocks import PromptBlock
from backend_v2.models.dtos.studio import (
    PromptBlockDeleteResponse,
    PromptBlockResponseDTO,
    PromptBlockSimulationRequest,
    PromptBlockSimulationResponse,
)
from backend_v2.models.enums import PromptBlockCategory

logger = logging.getLogger(__name__)

__all__ = ["router"]

router = APIRouter(prefix="/prompt-blocks", tags=["Admin Studio V2 - Prompt Blocks"])


@router.post("/simulate", response_model=PromptBlockSimulationResponse)
async def simulate_prompt_block(
    data: PromptBlockSimulationRequest,
    current_user: CurrentUserDep,
    studio_simulation_service: StudioSimulationServiceDep,
) -> PromptBlockSimulationResponse:
    """Dry-run and validate a PromptBlock template rendering.

    Args:
        data: The simulation request containing the prompt block and mock inputs.
        current_user: The authenticated user making the request.
        studio_simulation_service: The studio simulation service dependency.

    Returns:
        The results of the simulation.

    Raises:
        AppException: With ErrorCodes.RESOURCE_NOT_FOUND if the target scale score is not found,
            or ErrorCodes.VALIDATION_FAILED if scales contain zero claims or assertions to simulate.
    """
    return await studio_simulation_service.simulate_prompt_block(current_user, data)


@router.get("/", response_model=list[PromptBlockResponseDTO])
async def get_prompt_blocks(
    current_user: CurrentUserDep, prompt_block_service: StudioPromptBlockServiceDep
) -> list[PromptBlock]:
    """Retrieve all PromptBlocks securely.

    Args:
        current_user: The authenticated user making the request.
        prompt_block_service: The prompt block service dependency.

    Returns:
        A list of all prompt blocks.

    Raises:
        AppException: With ErrorCodes.STATE_INTEGRITY_ERROR if fetching prompt blocks fails.
    """
    return await prompt_block_service.list_prompt_blocks(current_user)


@router.post("/", response_model=PromptBlockResponseDTO)
async def create_prompt_block(
    current_user: CurrentUserDep,
    prompt_block_service: StudioPromptBlockServiceDep,
    category_id: Annotated[
        PromptBlockCategory,
        Query(description="Prompt block category for the new draft (system_rule, matrix, etc.)."),
    ] = PromptBlockCategory.SYSTEM_RULE,
) -> PromptBlock:
    """Create a new PromptBlock draft securely via SSOT.

    Args:
        current_user: The authenticated user making the request.
        prompt_block_service: The prompt block service dependency.
        category_id: Category of the prompt block draft to mint.

    Returns:
        The newly created prompt block draft.

    Raises:
        ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if the created draft cannot be reloaded.
        PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if tenant modification rights are violated.
        AppException: With ErrorCodes.AGENT_EXECUTION_CRITICAL if prompt block atomization fails prior to save.
    """
    return await prompt_block_service.create_prompt_block_draft(current_user, category_id=category_id)


@router.get("/{id}", response_model=PromptBlockResponseDTO)
async def get_prompt_block(
    id: Annotated[str, Path(pattern=OPAQUE_STRIPE_ID_REGEX)],
    current_user: CurrentUserDep,
    prompt_block_service: StudioPromptBlockServiceDep,
) -> PromptBlock:
    """Retrieve a specific prompt block by id securely via SSOT Service Layer.

    Args:
        id: The unique identifier of the prompt block.
        current_user: The authenticated user making the request.
        prompt_block_service: The prompt block service dependency.

    Returns:
        The requested prompt block.

    Raises:
        ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if the prompt block is not found.
        PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if tenant access isolation is violated.
    """
    return await prompt_block_service.get_prompt_block(current_user, id)


@router.post("/{id}/clone", response_model=PromptBlockResponseDTO)
async def clone_prompt_block(
    id: Annotated[str, Path(pattern=OPAQUE_STRIPE_ID_REGEX)],
    current_user: CurrentUserDep,
    prompt_block_service: StudioPromptBlockServiceDep,
) -> PromptBlock:
    """Deep clone a prompt block securely via SSOT Service Layer.

    Args:
        id: The unique identifier of the prompt block to clone.
        current_user: The authenticated user making the request.
        prompt_block_service: The prompt block service dependency.

    Returns:
        The newly cloned prompt block.

    Raises:
        ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if the source prompt block is not found.
        PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if tenant access or modification rights are violated.
        AppException: With ErrorCodes.AGENT_EXECUTION_CRITICAL if atomization of the cloned block fails.
    """
    return await prompt_block_service.clone_prompt_block(current_user, id)


@router.put("/{id}", response_model=PromptBlockResponseDTO)
async def save_prompt_block(
    id: Annotated[str, Path(pattern=OPAQUE_STRIPE_ID_REGEX)],
    data: PromptBlock,
    current_user: CurrentUserDep,
    prompt_block_service: StudioPromptBlockServiceDep,
) -> PromptBlock:
    """Append or update a prompt block securely via SSOT Service Layer.

    Args:
        id: The unique identifier of the prompt block.
        data: The new configuration data for the prompt block.
        current_user: The authenticated user making the request.
        prompt_block_service: The prompt block service dependency.

    Returns:
        The updated prompt block.

    Raises:
        AppException: With ErrorCodes.ID_MISMATCH if path id does not match payload id.
        ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if the prompt block is not found after save.
        PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if tenant modification rights are violated.
        AppException: With ErrorCodes.AGENT_EXECUTION_CRITICAL if prompt block atomization fails prior to save.
    """
    if data.id != id:
        logger.error(
            "[PromptBlocksRouter] %s: Path id '%s' does not match payload id '%s' (Initiator: %s).",
            ErrorCodes.ID_MISMATCH.name,
            id,
            data.id,
            current_user.id,
            exc_info=True,
            extra={"error_code": ErrorCodes.ID_MISMATCH.value, "prompt_block_id": id},
        )
        raise AppException(
            message=f"Path id '{id}' does not match payload id '{data.id}'",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.ID_MISMATCH.value},
        )

    return await prompt_block_service.save_prompt_block(current_user, id, data)


@router.delete("/{id}", response_model=PromptBlockDeleteResponse)
async def delete_prompt_block(
    id: Annotated[str, Path(pattern=OPAQUE_STRIPE_ID_REGEX)],
    current_user: CurrentUserDep,
    prompt_block_service: StudioPromptBlockServiceDep,
    force_delete: bool = False,
) -> PromptBlockDeleteResponse:
    """Delete a prompt block securely via SSOT Service Layer.

    Args:
        id: The unique identifier of the prompt block to delete.
        current_user: The authenticated user making the request.
        prompt_block_service: The prompt block service dependency.
        force_delete: Whether to force delete the prompt block.

    Returns:
        A PromptBlockDeleteResponse confirming the deletion.

    Raises:
        ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if the prompt block is not found.
        PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if tenant modification rights are violated.
        AppException: With ErrorCodes.SYSTEM_PROTECTED_RESOURCE if deleting a protected prompt block fails.
    """
    await prompt_block_service.delete_prompt_block(current_user, id, force_delete=force_delete)
    return PromptBlockDeleteResponse(status="success", deleted_id=id)
