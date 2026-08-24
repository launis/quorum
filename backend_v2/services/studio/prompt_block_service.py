"""Prompt Block Service."""

import logging
import uuid
from typing import Any

from pydantic import ValidationError

from backend_v2.database.interfaces import IPromptBlockRepository, ISystemRepository
from backend_v2.exceptions import AppException, ErrorCodes, ResourceNotFoundError
from backend_v2.models.auth import SystemOrganizations, TokenData, UserRole
from backend_v2.models.domain.prompt_blocks import (
    PromptBlock,
    PromptBlockAdapter,
)
from backend_v2.models.enums import BlockDataType, PromptBlockCategory
from backend_v2.services.orchestrator.atomizer import PromptAtomizer
from backend_v2.services.studio.auth_validator import (
    enforce_modification_rights,
    enforce_tenant_isolation,
)

logger = logging.getLogger(__name__)


class StudioPromptBlockService:
    """Domain Service for managing Prompt Blocks."""

    def __init__(
        self,
        prompt_block_repo: IPromptBlockRepository,
        system_repo: ISystemRepository,
    ):
        """Initialize the service.

        Args:
            prompt_block_repo: The prompt block repository.
            system_repo: The system repository.
        """
        self.prompt_block_repo = prompt_block_repo
        self.system_repo = system_repo

    async def list_prompt_blocks(self, initiator: TokenData) -> list[PromptBlock]:
        """List prompt blocks.

        Args:
            initiator: The authenticated user.

        Returns:
            A list of PromptBlocks.

        Raises:
            AppException (ErrorCodes.STATE_INTEGRITY_ERROR): On core errors.
        """
        all_data = await self.prompt_block_repo.get_all_prompt_blocks()

        blocks: list[PromptBlock] = []
        for x in all_data:
            try:
                blocks.append(PromptBlockAdapter.validate_python(x, strict=False))
            except ValidationError as e:
                logger.error(
                    "[StudioPromptBlockService] %s: PromptBlock %s failed hydration. DB is corrupt. Error: %s",
                    ErrorCodes.STATE_INTEGRITY_ERROR.name,
                    x.get("id"),
                    str(e),
                )
                raise AppException(
                    message=f"Database integrity error: PromptBlock {x.get('id')} failed strict validation.",
                    status_code=500,
                    details={"error_code": ErrorCodes.STATE_INTEGRITY_ERROR},
                ) from e

        if initiator.role == UserRole.ROOT:
            return blocks

        org_id = initiator.organization_id
        return [x for x in blocks if x.organization_id in [org_id, SystemOrganizations.ROOT_SYSTEM]]

    async def get_prompt_block(self, initiator: TokenData, id: str) -> PromptBlock:
        """Get prompt block.

        Args:
            initiator: The authenticated user.
            id: The prompt block ID.

        Returns:
            The PromptBlock.

        Raises:
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the resource is missing.
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If tenant access is violated.
        """
        data = await self.prompt_block_repo.get_prompt_block_by_id(id)
        if not data:
            logger.error(
                "[StudioPromptBlockService] %s: PromptBlock %s not found (Initiator: %s).",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                id,
                initiator.id,
            )
            raise ResourceNotFoundError(resource_type="prompt_block", resource_id=id)

        block = PromptBlockAdapter.validate_python(data, strict=False)
        enforce_tenant_isolation(initiator, block.organization_id, "prompt_block", block.id)
        return block

    async def save_prompt_block(self, initiator: TokenData, id: str, data: PromptBlock) -> PromptBlock:
        """Save prompt block.

        Args:
            initiator: The authenticated user.
            id: The prompt block ID.
            data: The PromptBlock data.

        Returns:
            The saved PromptBlock.

        Raises:
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the resource is missing.
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If tenant access is violated.
            AppException (ErrorCodes.AGENT_EXECUTION_CRITICAL): On core errors.
        """
        org_id = data.organization_id
        enforce_modification_rights(initiator, org_id)

        try:
            data = await PromptAtomizer.atomize_prompt_block(data, repository=self.system_repo)
        except Exception as e:
            logger.error(
                "[StudioPromptBlockService] %s: Atomization failed prior to save (Initiator: %s, Block: %s): %s",
                ErrorCodes.AGENT_EXECUTION_CRITICAL.name,
                initiator.id,
                id,
                e,
            )
            raise AppException(
                message=f"Atomization failed: {e}",
                status_code=500,
                details={"error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL},
            ) from e

        dump = data.model_dump(mode="json")
        if "id" not in dump:
            dump["id"] = id
        await self.prompt_block_repo.create_prompt_block(dump)

        saved = await self.prompt_block_repo.get_prompt_block_by_id(id)
        if not saved:
            logger.error(
                "[StudioPromptBlockService] %s: PromptBlock %s not found after save (Initiator: %s).",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                id,
                initiator.id,
            )
            raise ResourceNotFoundError(resource_type="prompt_block", resource_id=id)
        return PromptBlockAdapter.validate_python(saved, strict=False)

    async def delete_prompt_block(self, initiator: TokenData, id: str, force_delete: bool = False) -> None:
        """Delete prompt block.

        Args:
            initiator: The authenticated user.
            id: The prompt block ID.
            force_delete: Force deletion flag.

        Raises:
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the resource is missing.
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If tenant access is violated.
        """
        data = await self.prompt_block_repo.get_prompt_block_by_id(id)
        if not data:
            logger.error(
                "[StudioPromptBlockService] %s: PromptBlock %s not found (Initiator: %s).",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                id,
                initiator.id,
            )
            raise ResourceNotFoundError(resource_type="prompt_block", resource_id=id)

        block = PromptBlockAdapter.validate_python(data, strict=False)
        enforce_modification_rights(initiator, block.organization_id)
        await self.prompt_block_repo.delete_prompt_block(id, force_delete=force_delete)

    async def create_prompt_block_draft(self, initiator: TokenData) -> PromptBlock:
        """Create prompt block draft.

        Args:
            initiator: The authenticated user.

        Returns:
            The drafted PromptBlock.

        Raises:
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If tenant access is violated.
        """
        new_id = f"blk_{uuid.uuid4().hex[:16]}"

        draft_dict: dict[str, Any] = {
            "id": new_id,
            "slug": new_id,
            "label": {"default_locale": "en", "translations": {"en": "New Block", "fi": "Uusi lohko"}},
            "description": {"default_locale": "en", "translations": {"en": "Draft block", "fi": "Luonnos"}},
            "ai_description": "Initial AI logic draft.",
            "category_id": PromptBlockCategory.SYSTEM_RULE.value,
            "type": BlockDataType.INSTRUCTION.value,
            "output_extensions": [],
            "organization_id": (
                SystemOrganizations.ROOT_SYSTEM if initiator.role == UserRole.ROOT else initiator.organization_id
            ),
        }
        draft = PromptBlockAdapter.validate_python(draft_dict, strict=False)
        return await self.save_prompt_block(initiator, new_id, draft)

    async def clone_prompt_block(self, initiator: TokenData, id: str) -> PromptBlock:
        """Clone prompt block.

        Args:
            initiator: The authenticated user.
            id: The prompt block ID to clone.

        Returns:
            The cloned PromptBlock.

        Raises:
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the resource is missing.
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If tenant access is violated.
        """
        data = await self.prompt_block_repo.get_prompt_block_by_id(id)
        if not data:
            logger.error(
                "[StudioPromptBlockService] %s: PromptBlock %s not found (Initiator: %s).",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                id,
                initiator.id,
            )
            raise ResourceNotFoundError(resource_type="prompt_block", resource_id=id)

        block = PromptBlockAdapter.validate_python(data, strict=False)
        enforce_tenant_isolation(initiator, block.organization_id, "prompt_block", block.id)

        new_id = f"blk_{uuid.uuid4().hex[:16]}"

        cloned_data = block.model_dump(mode="json")
        cloned_data["id"] = new_id

        if initiator.role != UserRole.ROOT:
            cloned_data["organization_id"] = initiator.organization_id

        if "label" in cloned_data and isinstance(cloned_data["label"], dict):
            for locale, text in cloned_data["label"].get("translations", {}).items():
                cloned_data["label"]["translations"][locale] = text + " (Copy)"
        elif "label" in cloned_data:
            cloned_data["label"] = str(cloned_data["label"]) + " (Copy)"

        cloned_obj = PromptBlockAdapter.validate_python(cloned_data, strict=False)
        return await self.save_prompt_block(initiator, new_id, cloned_obj)
