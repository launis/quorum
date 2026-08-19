"""Output Profile Service."""

import logging
import uuid
from typing import Any

from pydantic import ValidationError

from backend_v2.database.interfaces import IOutputProfileRepository
from backend_v2.exceptions import AppException, ErrorCodes, ResourceNotFoundError
from backend_v2.models.auth import SystemOrganizations, TokenData, UserRole
from backend_v2.models.domain.output_profile import OutputProfile
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
    ):
        """Initialize the service.

        Args:
            output_profile_repo: The output profile repository.
            workflow_service: The studio workflow service.
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
        all_data = await self.output_profile_repo.get_all_output_profiles()
        profiles = []
        for x in all_data:
            try:
                profiles.append(OutputProfile.model_validate(x, strict=False))
            except ValidationError as e:
                logger.error(
                    "[StudioService] %s: OutputProfile %s failed hydration. Error: %s",
                    ErrorCodes.STATE_INTEGRITY_ERROR.name,
                    x.get("id"),
                    str(e),
                )
                raise AppException(
                    message=f"Database integrity error: OutputProfile {x.get('id')} failed strict validation.",
                    status_code=500,
                    details={"error_code": ErrorCodes.STATE_INTEGRITY_ERROR},
                ) from e

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
        data = await self.output_profile_repo.get_output_profile_by_id(id)
        if not data:
            logger.error(
                "[StudioOutputProfileService] %s: Output Profile %s not found (Initiator: %s).",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                id,
                initiator.id,
            )
            raise ResourceNotFoundError(resource_type="output_profile", resource_id=id)

        profile = OutputProfile.model_validate(data, strict=False)
        enforce_tenant_isolation(initiator, profile.organization_id, "output_profile", profile.id)
        return profile

    async def save_output_profile(
        self, initiator: TokenData, id: str, data: dict[str, Any] | OutputProfile
    ) -> OutputProfile:
        """Save output profile.

        Args:
            initiator: The authenticated user.
            id: The output profile ID.
            data: The profile data or OutputProfile object.

        Returns:
            The saved OutputProfile.

        Raises:
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the resource is missing after save.
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If tenant access is violated.
            AppException (ErrorCodes.VALIDATION_FAILED): On validation errors.
        """
        if isinstance(data, dict):
            existing = await self.output_profile_repo.get_output_profile_by_id(id)
            if existing:
                merged = {**existing, **data}
                profile = OutputProfile.model_validate(merged)
            else:
                profile = OutputProfile.model_validate(data)
        else:
            profile = data

        enforce_modification_rights(initiator, profile.organization_id)

        workflow = await self.workflow_service.get_workflow(initiator, profile.workflow_id)
        all_steps = await self.workflow_service.list_steps(initiator)

        # Delegate permission calculation to the Domain Model
        allowed_blocks = workflow.get_allowed_layout_targets(all_steps)

        for layout in profile.layouts:
            for comp in layout.target_blocks:
                if comp != "*" and comp not in allowed_blocks:
                    msg = f"Target Component '{comp}' does not exist in the context of Workflow '{workflow.slug}'."
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

        dump = profile.model_dump(mode="json")
        if "id" not in dump:
            dump["id"] = id

        await self.output_profile_repo.create_output_profile(dump)

        saved = await self.output_profile_repo.get_output_profile_by_id(id)
        if not saved:
            logger.error(
                "[StudioOutputProfileService] %s: Output Profile %s not found after save (Initiator: %s).",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                id,
                initiator.id,
            )
            raise ResourceNotFoundError(resource_type="output_profile", resource_id=id)
        return OutputProfile.model_validate(saved, strict=False)

    async def delete_output_profile(self, initiator: TokenData, id: str) -> None:
        """Delete output profile.

        Args:
            initiator: The authenticated user.
            id: The output profile ID.

        Raises:
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the resource is missing.
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If tenant access is violated.
        """
        data = await self.output_profile_repo.get_output_profile_by_id(id)
        if not data:
            logger.error(
                "[StudioOutputProfileService] %s: Output Profile %s not found (Initiator: %s).",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                id,
                initiator.id,
            )
            raise ResourceNotFoundError(resource_type="output_profile", resource_id=id)

        enforce_modification_rights(initiator, data.get("organization_id"))
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
        new_id = f"opt_{uuid.uuid4().hex[:16]}"
        draft_dict: dict[str, Any] = {
            "id": new_id,
            "slug": new_id,
            "name": {"default_locale": "en", "translations": {"en": "New Profile", "fi": "Uusi profiili"}},
            "category_id": "report",
            "layouts": [
                {"layout_type": "default_pdf", "layout_config": {"columns": 1, "theme": "light"}, "blocks": []}
            ],
            "organization_id": (
                SystemOrganizations.ROOT_SYSTEM if initiator.role == UserRole.ROOT else initiator.organization_id
            ),
        }
        draft = OutputProfile.model_validate(draft_dict)
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
        data = await self.output_profile_repo.get_output_profile_by_id(id)
        if not data:
            logger.error(
                "[StudioOutputProfileService] %s: OutputProfile %s not found (Initiator: %s).",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                id,
                initiator.id,
            )
            raise ResourceNotFoundError(resource_type="output_profile", resource_id=id)

        profile = OutputProfile.model_validate(data, strict=False)
        enforce_tenant_isolation(initiator, profile.organization_id, "output_profile", profile.id)

        new_id = f"prof_{uuid.uuid4().hex}"

        cloned_data = profile.model_dump(mode="json")
        cloned_data["id"] = new_id

        if initiator.role != UserRole.ROOT:
            cloned_data["organization_id"] = initiator.organization_id

        if "name" in cloned_data and isinstance(cloned_data["name"], dict):
            default_locale = cloned_data["name"].get("default_locale", "en")
            translations = cloned_data["name"].get("translations", {})
            if default_locale in translations:
                translations[default_locale] = translations[default_locale] + " (Copy)"
                cloned_data["name"]["translations"] = translations
        elif "name" in cloned_data and isinstance(cloned_data["name"], str):
            cloned_data["name"] = cloned_data["name"] + " (Copy)"

        await self.output_profile_repo.create_output_profile(cloned_data)

        saved = await self.output_profile_repo.get_output_profile_by_id(new_id)
        if not saved:
            logger.error(
                "[StudioOutputProfileService] %s: OutputProfile %s not found after clone (Initiator: %s).",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                new_id,
                initiator.id,
            )
            raise ResourceNotFoundError(resource_type="output_profile", resource_id=new_id)

        return OutputProfile.model_validate(saved, strict=False)
