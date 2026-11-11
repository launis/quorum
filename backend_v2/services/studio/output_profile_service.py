"""Output Profile Service."""

from __future__ import annotations

import logging

from backend_v2.database.interfaces import IOutputProfileRepository
from backend_v2.exceptions import AppException, ErrorCodes, ResourceNotFoundError
from backend_v2.models.auth import SystemOrganizations, TokenData, UserRole
from backend_v2.models.core_base import generate_opaque_id
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.enums import EntityPrefix, StepFilterScope
from backend_v2.services.factories.output_profile_factory import build_draft_output_profile
from backend_v2.services.studio.auth_validator import (
    enforce_modification_rights,
    enforce_tenant_isolation,
    is_resource_accessible,
)
from backend_v2.services.studio.workflow_service import StudioWorkflowService

logger = logging.getLogger(__name__)

__all__ = ["StudioOutputProfileService"]


class StudioOutputProfileService:
    """Domain Service for managing Output Profiles.

    Attributes:
        output_profile_repo: Repository interface for output profile persistence.
        workflow_service: Domain service for workflow and step resolution.
    """

    def __init__(
        self,
        output_profile_repo: IOutputProfileRepository,
        workflow_service: StudioWorkflowService,
    ) -> None:
        """Initialize service.

        Args:
            output_profile_repo: The output profile repository.
            workflow_service: The workflow service.
        """
        self.output_profile_repo = output_profile_repo
        self.workflow_service = workflow_service

    async def _require_output_profile(
        self, initiator: TokenData, id: str, *, after_save: bool = False
    ) -> OutputProfile:
        """Fetch an output profile by ID or raise ResourceNotFoundError.

        Args:
            initiator: The authenticated user.
            id: The output profile ID.
            after_save: Whether the lookup occurs during post-save roundtrip verification.

        Returns:
            The resolved OutputProfile domain model.

        Raises:
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the output profile does not exist.
        """
        profile = await self.output_profile_repo.get_output_profile_by_id(id)
        if not profile:
            context_suffix = " after save" if after_save else ""
            logger.error(
                "[StudioOutputProfileService] %s: Output Profile %s not found%s (Initiator: %s).",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                id,
                context_suffix,
                initiator.id,
                exc_info=True,
                extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value, "profile_id": id},
            )
            raise ResourceNotFoundError(resource_type="output_profile", resource_id=id)
        return profile

    def _validate_target_block(
        self,
        initiator: TokenData,
        profile_id: str,
        workflow_id: str,
        target_label: str,
        block_id: str | None,
        allowed_targets: set[str],
    ) -> None:
        """Validate that a referenced target block exists within the workflow's allowed target set.

        Args:
            initiator: The authenticated user.
            profile_id: The output profile ID being validated.
            workflow_id: The parent workflow ID.
            target_label: Human-readable descriptor of the target reference field.
            block_id: Candidate block or layout target identifier.
            allowed_targets: Authoritative set of valid target IDs for the workflow.

        Raises:
            AppException (ErrorCodes.VALIDATION_FAILED): If the block ID is not in allowed_targets.
        """
        if block_id is not None and block_id not in allowed_targets:
            msg = f"{target_label} '{block_id}' does not exist in the context of Workflow '{workflow_id}'."
            logger.error(
                "[StudioOutputProfileService] %s: %s (Initiator: %s, Profile: %s)",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                initiator.id,
                profile_id,
                exc_info=True,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value, "profile_id": profile_id},
            )
            raise AppException(message=msg, status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED})

    async def list_output_profiles(self, initiator: TokenData) -> list[OutputProfile]:
        """List output profiles.

        Args:
            initiator: The authenticated user.

        Returns:
            A list of OutputProfiles.

        Raises:
            AppException (ErrorCodes.STATE_INTEGRITY_ERROR): If an output profile fails strict validation.
        """
        profiles = await self.output_profile_repo.get_all_output_profiles()

        if initiator.role == UserRole.ROOT:
            return profiles

        return [p for p in profiles if is_resource_accessible(initiator, p.organization_id)]

    async def get_output_profile(self, initiator: TokenData, id: str) -> OutputProfile:
        """Get output profile.

        Args:
            initiator: The authenticated user.
            id: The output profile ID.

        Returns:
            The OutputProfile.

        Raises:
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the resource is missing.
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If tenant access is violated.
        """
        profile = await self._require_output_profile(initiator, id)
        enforce_tenant_isolation(initiator, profile.organization_id, "output_profile", profile.id)
        return profile

    async def _validate_and_persist_output_profile(
        self, initiator: TokenData, id: str, profile: OutputProfile
    ) -> OutputProfile:
        """Validate workflow layout targets for an OutputProfile, persist it, and reload by ID.

        Args:
            initiator: The authenticated user performing the write.
            id: Authoritative output profile identifier.
            profile: OutputProfile domain model to validate and persist.

        Returns:
            Reloaded OutputProfile persisted under id.

        Raises:
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If parent workflow or saved profile is missing.
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If parent workflow tenant access is violated.
            AppException (ErrorCodes.VALIDATION_FAILED): If referenced target blocks are invalid for the workflow.
        """
        workflow = await self.workflow_service.get_workflow(initiator, profile.workflow_id)
        all_steps = await self.workflow_service.list_steps(initiator, scope=StepFilterScope.ALL)

        # Delegate permission calculation to the Domain Model
        allowed_blocks = workflow.get_allowed_layout_targets(all_steps)
        allowed_prompt_blocks = workflow.get_allowed_prompt_block_targets(all_steps)

        for group in profile.matrix_synthesis_groups:
            for comp in group.target_blocks:
                self._validate_target_block(
                    initiator, profile.id, workflow.id, "Target Component", comp, allowed_blocks
                )

        # Validate variance_target_block and user_role_target_block against allowed_prompt_blocks
        self._validate_target_block(
            initiator,
            profile.id,
            workflow.id,
            "Variance Target Block",
            profile.variance_target_block,
            allowed_prompt_blocks,
        )
        self._validate_target_block(
            initiator,
            profile.id,
            workflow.id,
            "User Role Target Block",
            profile.user_role_target_block,
            allowed_prompt_blocks,
        )

        if profile.id != id:
            profile = profile.model_copy(update={"id": id})

        await self.output_profile_repo.create_output_profile(profile)
        return await self._require_output_profile(initiator, id, after_save=True)

    async def _insert_validated_output_profile(
        self, initiator: TokenData, id: str, data: OutputProfile
    ) -> OutputProfile:
        """Insert a newly drafted or cloned OutputProfile after RBAC and target validation.

        Args:
            initiator: The authenticated user creating the profile.
            id: Server-issued output profile identifier.
            data: Newly constructed OutputProfile domain model.

        Returns:
            Persisted OutputProfile reloaded from the repository.

        Raises:
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If modification rights are violated.
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If parent workflow or saved profile is missing.
            AppException (ErrorCodes.VALIDATION_FAILED): If target block validation fails.
        """
        enforce_modification_rights(initiator, data.organization_id)
        return await self._validate_and_persist_output_profile(initiator, id, data)

    async def save_output_profile(self, initiator: TokenData, id: str, data: OutputProfile) -> OutputProfile:
        """Update an existing OutputProfile in-place under its authoritative ID.

        Args:
            initiator: The authenticated user.
            id: The output profile ID.
            data: The OutputProfile domain model.

        Returns:
            The saved OutputProfile.

        Raises:
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the target profile or parent workflow is missing.
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If tenant modification rights are violated.
            AppException (ErrorCodes.VALIDATION_FAILED): On target block validation errors.
        """
        existing = await self._require_output_profile(initiator, id)
        enforce_modification_rights(initiator, existing.organization_id)

        target_org: str | None = existing.organization_id
        if initiator.role == UserRole.ROOT:
            target_org = data.organization_id
            enforce_modification_rights(initiator, target_org)

        normalized = data.model_copy(update={"id": id, "organization_id": target_org})
        return await self._validate_and_persist_output_profile(initiator, id, normalized)

    async def delete_output_profile(self, initiator: TokenData, id: str) -> None:
        """Delete output profile.

        Args:
            initiator: The authenticated user.
            id: The output profile ID.

        Raises:
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the resource is missing.
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If tenant access is violated.
            AppException (ErrorCodes.DELETE_BLOCKED_BY_USAGE): If output profile is configured as default on a workflow.
        """
        profile = await self._require_output_profile(initiator, id)
        enforce_modification_rights(initiator, profile.organization_id)

        workflows = await self.workflow_service.list_workflows(initiator)
        for wf in workflows:
            if wf.default_profile_id == id:
                logger.error(
                    "[StudioOutputProfileService] %s: Cannot delete output profile %s because it is default_profile_id on workflow %s.",
                    ErrorCodes.DELETE_BLOCKED_BY_USAGE.name,
                    id,
                    wf.id,
                    exc_info=True,
                    extra={
                        "error_code": ErrorCodes.DELETE_BLOCKED_BY_USAGE.value,
                        "profile_id": id,
                        "workflow_id": wf.id,
                    },
                )
                raise AppException(
                    message=f"Cannot delete output profile {id} because it is configured as default on workflow {wf.id}.",
                    status_code=400,
                    details={
                        "error_code": ErrorCodes.DELETE_BLOCKED_BY_USAGE.value,
                        "profile_id": id,
                        "workflow_id": wf.id,
                    },
                )

        await self.output_profile_repo.delete_output_profile(id)

    async def create_output_profile_draft(self, initiator: TokenData) -> OutputProfile:
        """Create output profile draft.

        Args:
            initiator: The authenticated user.

        Returns:
            The drafted OutputProfile.

        Raises:
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If no workflow exists or profile is missing after save.
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If tenant access is violated.
            AppException (ErrorCodes.VALIDATION_FAILED): If draft layout target validation fails.
        """
        workflows = await self.workflow_service.list_workflows(initiator)
        if not workflows:
            msg = (
                f"No workflows available to associate with new OutputProfile for organization "
                f"'{initiator.organization_id}'."
            )
            logger.error(
                "[StudioOutputProfileService] %s: %s",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                msg,
                exc_info=True,
                extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
            )
            raise ResourceNotFoundError(resource_type="workflow", resource_id="primary_default")
        target_wf = workflows[0]
        target_wf_id = target_wf.id
        all_steps = await self.workflow_service.list_steps(initiator, scope=StepFilterScope.ALL)
        prompt_blocks = target_wf.get_allowed_prompt_block_targets(all_steps)
        matrix_block = next(iter(prompt_blocks), None)

        new_id = generate_opaque_id(EntityPrefix.OUTPUT_PROFILE)
        target_org = SystemOrganizations.ROOT_SYSTEM if initiator.role == UserRole.ROOT else initiator.organization_id
        draft = build_draft_output_profile(
            profile_id=new_id,
            workflow_id=target_wf_id,
            organization_id=target_org,
            initial_target_block=matrix_block,
        )
        return await self._insert_validated_output_profile(initiator, new_id, draft)

    async def clone_output_profile(self, initiator: TokenData, id: str) -> OutputProfile:
        """Clone output profile.

        Args:
            initiator: The authenticated user.
            id: The output profile ID.

        Returns:
            The cloned OutputProfile.

        Raises:
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the resource is missing.
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If tenant access is violated.
            AppException (ErrorCodes.VALIDATION_FAILED): If cloned layout target validation fails.
        """
        profile = await self._require_output_profile(initiator, id)
        enforce_tenant_isolation(initiator, profile.organization_id, "output_profile", profile.id)

        new_id = generate_opaque_id(EntityPrefix.OUTPUT_PROFILE)
        target_org = profile.organization_id if initiator.role == UserRole.ROOT else initiator.organization_id
        cloned_name = profile.name.with_copy_suffix()

        cloned_obj = profile.model_copy(
            update={
                "id": new_id,
                "organization_id": target_org,
                "name": cloned_name,
            }
        )
        return await self._insert_validated_output_profile(initiator, new_id, cloned_obj)
