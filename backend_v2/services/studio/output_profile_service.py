"""Output Profile Service."""

from __future__ import annotations

import logging

from backend_v2.database.interfaces import IOutputProfileRepository
from backend_v2.exceptions import AppException, ErrorCodes, ResourceNotFoundError
from backend_v2.models.auth import SystemOrganizations, TokenData, UserRole
from backend_v2.models.core_base import generate_opaque_id
from backend_v2.models.enums import EntityPrefix
from backend_v2.models.v2_core import OutputProfile
from backend_v2.services.factories.output_profile_factory import build_draft_output_profile
from backend_v2.services.studio.auth_validator import (
    enforce_modification_rights,
    enforce_tenant_isolation,
)
from backend_v2.services.studio.workflow_service import StudioWorkflowService

logger = logging.getLogger(__name__)


class StudioOutputProfileService:
    """Domain Service for managing Output Profiles."""

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

        org_id = initiator.organization_id
        return [p for p in profiles if p.organization_id in [org_id, SystemOrganizations.ROOT_SYSTEM]]

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
        profile = await self.output_profile_repo.get_output_profile_by_id(id)
        if not profile:
            logger.error(
                "[StudioOutputProfileService] %s: Output Profile %s not found (Initiator: %s).",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                id,
                initiator.id,
            )
            raise ResourceNotFoundError(resource_type="output_profile", resource_id=id)

        enforce_tenant_isolation(initiator, profile.organization_id, "output_profile", profile.id)
        return profile

    async def save_output_profile(self, initiator: TokenData, id: str, data: OutputProfile) -> OutputProfile:
        """Save output profile.

        Args:
            initiator: The authenticated user.
            id: The output profile ID.
            data: The OutputProfile domain model.

        Returns:
            The saved OutputProfile.

        Raises:
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the resource is missing after save.
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If tenant access is violated.
            AppException (ErrorCodes.VALIDATION_FAILED): On validation errors.
        """
        profile = data
        enforce_modification_rights(initiator, profile.organization_id)

        workflow = await self.workflow_service.get_workflow(initiator, profile.workflow_id)
        all_steps = await self.workflow_service.list_steps(initiator)

        # Delegate permission calculation to the Domain Model
        allowed_blocks = workflow.get_allowed_layout_targets(all_steps)

        for group in profile.matrix_synthesis_groups:
            for comp in group.target_blocks:
                if comp not in allowed_blocks:
                    msg = f"Target Component '{comp}' does not exist in the context of Workflow '{workflow.id}'."
                    logger.error(
                        "[StudioOutputProfileService] %s: %s (Initiator: %s, Profile: %s)",
                        ErrorCodes.VALIDATION_FAILED.name,
                        msg,
                        initiator.id,
                        profile.id,
                    )
                    raise AppException(
                        message=msg, status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED}
                    )

        if profile.id != id:
            profile = profile.model_copy(update={"id": id})

        await self.output_profile_repo.create_output_profile(profile)

        saved = await self.output_profile_repo.get_output_profile_by_id(id)
        if not saved:
            logger.error(
                "[StudioOutputProfileService] %s: Output Profile %s not found after save (Initiator: %s).",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                id,
                initiator.id,
            )
            raise ResourceNotFoundError(resource_type="output_profile", resource_id=id)
        return saved

    async def delete_output_profile(self, initiator: TokenData, id: str) -> None:
        """Delete output profile.

        Args:
            initiator: The authenticated user.
            id: The output profile ID.

        Raises:
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the resource is missing.
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If tenant access is violated.
        """
        profile = await self.output_profile_repo.get_output_profile_by_id(id)
        if not profile:
            logger.error(
                "[StudioOutputProfileService] %s: Output Profile %s not found (Initiator: %s).",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                id,
                initiator.id,
            )
            raise ResourceNotFoundError(resource_type="output_profile", resource_id=id)

        enforce_modification_rights(initiator, profile.organization_id)
        await self.output_profile_repo.delete_output_profile(id)

    async def create_output_profile_draft(self, initiator: TokenData) -> OutputProfile:
        """Create output profile draft.

        Args:
            initiator: The authenticated user.

        Returns:
            The drafted OutputProfile.

        Raises:
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If tenant access is violated.
        """
        workflows = await self.workflow_service.list_workflows(initiator)
        if not workflows:
            msg = (
                f"No workflows available to associate with new OutputProfile for organization "
                f"'{initiator.organization_id}'."
            )
            logger.error("[StudioOutputProfileService] %s: %s", ErrorCodes.RESOURCE_NOT_FOUND.name, msg)
            raise ResourceNotFoundError(resource_type="workflow", resource_id="primary_default")
        target_wf = workflows[0]
        target_wf_id = target_wf.id
        all_steps = await self.workflow_service.list_steps(initiator)
        allowed_blocks = target_wf.get_allowed_layout_targets(all_steps)
        matrix_block = next((b for b in allowed_blocks if not b.startswith("glb_")), None)

        new_id = generate_opaque_id(EntityPrefix.OUTPUT_PROFILE)
        target_org = SystemOrganizations.ROOT_SYSTEM if initiator.role == UserRole.ROOT else initiator.organization_id
        draft = build_draft_output_profile(
            profile_id=new_id,
            workflow_id=target_wf_id,
            organization_id=target_org,
            initial_target_block=matrix_block,
        )
        return await self.save_output_profile(initiator, new_id, draft)

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
        """
        profile = await self.output_profile_repo.get_output_profile_by_id(id)
        if not profile:
            logger.error(
                "[StudioOutputProfileService] %s: OutputProfile %s not found (Initiator: %s).",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                id,
                initiator.id,
            )
            raise ResourceNotFoundError(resource_type="output_profile", resource_id=id)

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
        return await self.save_output_profile(initiator, new_id, cloned_obj)
