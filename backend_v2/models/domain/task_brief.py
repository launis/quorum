"""Domain model for reusable human-facing Task Briefs and case descriptions.

Defines the immutable TaskBrief entity stored in the dedicated task_briefs table
and referenced by ExecutionAssignment.task_brief_id.
"""

from __future__ import annotations

from typing import Annotated

from pydantic import ConfigDict, Field, StringConstraints, field_validator

from backend_v2.exceptions import AppException
from backend_v2.models.core_base import (
    OPAQUE_STRIPE_ID_REGEX,
    I18nText,
    PrefixedUUID7,
    V2CoreBase,
    parse_prefixed_uuid7,
)
from backend_v2.models.enums import EntityPrefix

__all__ = ["StrictStr", "TaskAssignmentBriefDTO", "TaskBrief"]

StrictStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class TaskAssignmentBriefDTO(V2CoreBase):
    """Frozen publication-time TaskBrief snapshot embedded in execution assignments and responses.

    Attributes:
        id: Canonical TaskBrief Opaque Stripe ID (tbr_<hex32>).
        label: Localized title of the task brief.
        instruction_text: Optional plain-text or markdown task instructions.
        source_url: Optional reference document or external resource URL.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    id: Annotated[PrefixedUUID7, Field(description="Canonical TaskBrief ID (tbr_<hex32>)")]
    label: Annotated[I18nText, Field(description="Localized title of the task brief")]
    instruction_text: Annotated[
        str | None,
        Field(default=None, description="Optional task brief instruction text"),
    ] = None
    source_url: Annotated[
        str | None,
        Field(default=None, description="Optional reference document or external resource URL"),
    ] = None

    @field_validator("id")
    @classmethod
    def _validate_snapshot_task_brief_id(cls, v: str) -> str:
        """Validate that the snapshot identifier uses the canonical tbr_ prefix and UUIDv7 format.

        Args:
            v: Candidate TaskBrief identifier string.

        Returns:
            Validated TaskBrief identifier string.

        Raises:
            ValueError: If the identifier prefix is not 'tbr' or UUIDv7 validation fails.
        """
        try:
            parse_prefixed_uuid7(v, EntityPrefix.TASK_BRIEF)
        except AppException as exc:
            raise ValueError(exc.message) from exc
        return v


class TaskBrief(V2CoreBase):
    """Immutable domain model for a reusable human-facing task brief and case description.

    Attributes:
        id: Canonical TaskBrief Opaque Stripe ID (tbr_<hex32>).
        slug: Human-readable routing helper identifier with zero data relation role.
        organization_id: Owning Organization Opaque Stripe ID (org_<hex32>).
        label: Localized title of the task brief.
        description: Localized summary description of the task brief.
        instruction_text: Detailed plain-text or markdown task instructions shown to assignees.
        source_url: Optional external reference document or resource URL.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    id: Annotated[
        str,
        Field(
            pattern=OPAQUE_STRIPE_ID_REGEX,
            description="Canonical TaskBrief Opaque Stripe ID (tbr_<hex32>).",
        ),
    ]
    slug: Annotated[
        StrictStr,
        Field(description="Human-readable routing helper field with zero data relation role."),
    ]
    organization_id: Annotated[
        str,
        Field(
            pattern=OPAQUE_STRIPE_ID_REGEX,
            description="Owning tenant organization ID (org_<hex32>).",
        ),
    ]
    label: Annotated[I18nText, Field(description="Localized title for the UI.")]
    description: Annotated[I18nText, Field(description="Localized summary description for the UI.")]
    instruction_text: Annotated[
        StrictStr,
        Field(description="Reusable human-facing task brief and case description text."),
    ]
    source_url: Annotated[
        StrictStr | None,
        Field(default=None, description="Optional reference document or external resource URL."),
    ] = None

    @field_validator("id")
    @classmethod
    def _validate_task_brief_id(cls, v: str) -> str:
        """Validate that the identifier uses the canonical tbr_ prefix and RFC 9562 UUIDv7 format.

        Args:
            v: Candidate TaskBrief identifier string.

        Returns:
            Validated TaskBrief identifier string.

        Raises:
            ValueError: If the identifier prefix is not 'tbr' or UUIDv7 validation fails.
        """
        try:
            parse_prefixed_uuid7(v, EntityPrefix.TASK_BRIEF)
        except AppException as exc:
            raise ValueError(exc.message) from exc
        return v

    @field_validator("organization_id")
    @classmethod
    def _validate_organization_id(cls, v: str) -> str:
        """Validate that organization_id uses the canonical org_ prefix and RFC 9562 UUIDv7 format.

        Args:
            v: Candidate organization identifier string.

        Returns:
            Validated organization identifier string.

        Raises:
            ValueError: If the identifier prefix is not 'org' or UUIDv7 validation fails.
        """
        try:
            parse_prefixed_uuid7(v, EntityPrefix.ORGANIZATION)
        except AppException as exc:
            raise ValueError(exc.message) from exc
        return v
