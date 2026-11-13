"""Studio Task Brief Service."""

from __future__ import annotations

import logging

from backend_v2.database.interfaces import ITaskBriefRepository
from backend_v2.exceptions import ErrorCodes, ResourceNotFoundError
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.core_base import I18nText, generate_opaque_id
from backend_v2.models.domain.task_brief import TaskBrief
from backend_v2.models.enums import EntityPrefix
from backend_v2.services.studio.auth_validator import (
    enforce_modification_rights,
    enforce_tenant_isolation,
    is_resource_accessible,
    resolve_create_organization_id,
)

logger = logging.getLogger(__name__)

__all__ = ["StudioTaskBriefService"]


class StudioTaskBriefService:
    """Domain Service for managing reusable human-facing Task Briefs.

    Attributes:
        task_brief_repo: Repository interface for task brief persistence.
    """

    def __init__(
        self,
        task_brief_repo: ITaskBriefRepository,
    ) -> None:
        """Initialize the StudioTaskBriefService.

        Args:
            task_brief_repo: The task brief repository.
        """
        self.task_brief_repo = task_brief_repo

    async def _require_task_brief(self, initiator: TokenData, id: str, *, after_save: bool = False) -> TaskBrief:
        """Fetch a task brief by ID or raise ResourceNotFoundError.

        Args:
            initiator: The authenticated user requesting the resource.
            id: The canonical tbr_<32_hex> task brief identifier.
            after_save: Whether the lookup occurs during post-save roundtrip verification.

        Returns:
            The resolved TaskBrief domain instance.

        Raises:
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the task brief does not exist.
        """
        brief = await self.task_brief_repo.get_task_brief_by_id(id)
        if not brief:
            context_suffix = " after save" if after_save else ""
            logger.error(
                "[StudioTaskBriefService] %s: TaskBrief %s not found%s (Initiator: %s).",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                id,
                context_suffix,
                initiator.id,
                exc_info=True,
                extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value, "task_brief_id": id},
            )
            raise ResourceNotFoundError(resource_type="task_brief", resource_id=id)
        return brief

    async def list_task_briefs(self, initiator: TokenData) -> list[TaskBrief]:
        """List all TaskBrief records accessible to the authenticated user.

        Args:
            initiator: The authenticated user.

        Returns:
            List of accessible TaskBrief domain models.

        Raises:
            AppException (ErrorCodes.VALIDATION_FAILED): If persisted records fail schema validation.
        """
        briefs = await self.task_brief_repo.get_all_task_briefs()
        if initiator.role == UserRole.ROOT:
            return briefs
        return [b for b in briefs if is_resource_accessible(initiator, b.organization_id)]

    async def get_task_brief(self, initiator: TokenData, id: str) -> TaskBrief:
        """Retrieve a specific TaskBrief by ID with tenant isolation enforcement.

        Args:
            initiator: The authenticated user.
            id: The canonical tbr_<32_hex> task brief identifier.

        Returns:
            The resolved TaskBrief domain model.

        Raises:
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the task brief is missing.
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If tenant isolation is violated.
        """
        brief = await self._require_task_brief(initiator, id)
        enforce_tenant_isolation(initiator, brief.organization_id, "task_brief", brief.id)
        return brief

    async def _insert_validated_task_brief(self, initiator: TokenData, id: str, data: TaskBrief) -> TaskBrief:
        """Insert a newly drafted or cloned TaskBrief after RBAC verification.

        Args:
            initiator: The authenticated user creating the task brief.
            id: Server-issued canonical tbr_<32_hex> identifier.
            data: Newly constructed TaskBrief domain model payload.

        Returns:
            Persisted TaskBrief reloaded from the repository.

        Raises:
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If modification rights are violated.
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the task brief is missing after save.
        """
        enforce_modification_rights(initiator, data.organization_id)
        normalized = data
        if normalized.id != id:
            normalized = normalized.model_copy(update={"id": id})
        await self.task_brief_repo.create_task_brief(normalized)
        return await self._require_task_brief(initiator, id, after_save=True)

    async def save_task_brief(self, initiator: TokenData, id: str, data: TaskBrief) -> TaskBrief:
        """Update an existing TaskBrief in-place under its authoritative ID.

        Args:
            initiator: The authenticated user.
            id: The canonical tbr_<32_hex> task brief identifier.
            data: The TaskBrief domain model payload.

        Returns:
            The persisted TaskBrief domain model.

        Raises:
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the target task brief does not exist.
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If modification rights are violated.
        """
        existing = await self._require_task_brief(initiator, id)
        enforce_modification_rights(initiator, existing.organization_id)

        target_org: str = existing.organization_id
        if initiator.role == UserRole.ROOT:
            target_org = data.organization_id
            enforce_modification_rights(initiator, target_org)

        normalized = data.model_copy(update={"id": id, "organization_id": target_org})
        await self.task_brief_repo.create_task_brief(normalized)
        return await self._require_task_brief(initiator, id, after_save=True)

    async def delete_task_brief(self, initiator: TokenData, id: str) -> None:
        """Delete a TaskBrief by ID after enforcing RBAC and database referential integrity.

        Args:
            initiator: The authenticated user.
            id: The canonical tbr_<32_hex> task brief identifier.

        Raises:
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the task brief is missing.
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If modification rights are violated.
            AppException (ErrorCodes.DELETE_BLOCKED_BY_USAGE): If referenced by an assignment.
        """
        brief = await self._require_task_brief(initiator, id)
        enforce_modification_rights(initiator, brief.organization_id)
        await self.task_brief_repo.delete_task_brief(id)

    async def create_task_brief_draft(self, initiator: TokenData) -> TaskBrief:
        """Create a new TaskBrief draft with a fresh backend-issued tbr_<32_hex> UUIDv7 ID.

        Args:
            initiator: The authenticated user.

        Returns:
            The newly created TaskBrief draft.

        Raises:
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the draft cannot be reloaded after save.
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If modification rights are violated.
        """
        new_id = generate_opaque_id(EntityPrefix.TASK_BRIEF)
        target_org = resolve_create_organization_id(initiator)
        draft = TaskBrief(
            id=new_id,
            slug=new_id,
            organization_id=target_org,
            label=I18nText(translations={"en": "New Task Brief", "fi": "Uusi tehtävänanto"}),
            description=I18nText(translations={"en": "Draft task brief", "fi": "Tehtävänantoluonnos"}),
            instruction_text="Initial task brief instructions.",
            source_url=None,
        )
        return await self._insert_validated_task_brief(initiator, new_id, draft)

    async def clone_task_brief(self, initiator: TokenData, id: str) -> TaskBrief:
        """Clone an existing TaskBrief under a newly generated tbr_<32_hex> UUIDv7 ID.

        Args:
            initiator: The authenticated user.
            id: The canonical tbr_<32_hex> identifier of the source task brief.

        Returns:
            The newly cloned TaskBrief domain model.

        Raises:
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the source task brief is missing.
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If tenant access or modification rights are violated.
        """
        original = await self.get_task_brief(initiator, id)
        new_id = generate_opaque_id(EntityPrefix.TASK_BRIEF)
        if initiator.role == UserRole.ROOT:
            target_org = original.organization_id
        else:
            target_org = resolve_create_organization_id(initiator)
        cloned_label = original.label.with_copy_suffix()
        cloned_obj = original.model_copy(
            update={
                "id": new_id,
                "organization_id": target_org,
                "label": cloned_label,
            }
        )
        return await self._insert_validated_task_brief(initiator, new_id, cloned_obj)
