"""Authentication and Identity Management Models.

This module defines Pydantic models for user identity, role-based access control (RBAC),
organization management, and cryptographic token structures.
"""

from __future__ import annotations

import logging
from datetime import datetime
from enum import StrEnum
from typing import Annotated, Any, Literal

from pydantic import ConfigDict, EmailStr, Field, field_validator

from backend_v2.exceptions import ErrorCodes
from backend_v2.models.core_base import V2CoreBase, generate_opaque_id
from backend_v2.models.dtos.base import BaseDTO, BaseResponseDTO
from backend_v2.models.enums import EntityPrefix, LaxSystemLocale

logger = logging.getLogger(__name__)
__all__ = [
    "ImpersonationRequest",
    "ImpersonationResponse",
    "LaxSubscriptionStatus",
    "LaxUserRole",
    "LoginResponse",
    "Organization",
    "OrganizationCreate",
    "OrganizationDeleteResponse",
    "OrganizationUpdateDTO",
    "SubscriptionStatus",
    "SystemOrganizations",
    "TokenData",
    "TokenPayload",
    "User",
    "UserAdminView",
    "UserBase",
    "UserCreate",
    "UserDeleteResponse",
    "UserRole",
    "UserUpdate",
]

# --- Enums ---


class UserRole(StrEnum):
    """Enumeration of user permission roles within the system.

    Attributes:
        ROOT: System Owner / Platform Admin with unrestricted access.
        ADMIN: Organization Admin responsible for user management.
        MANAGER: Workflow/Process Lead managing execution flows.
        MEMBER: Standard User (Audit Runner).
        VIEWER: Read-Only Stakeholder.
    """

    ROOT = "ROOT"  # System Owner / Platform Admin
    ADMIN = "ADMIN"  # Organization Admin (User Management)
    MANAGER = "MANAGER"  # Workflow/Process Lead
    MEMBER = "MEMBER"  # Standard User (Audit Runner)
    VIEWER = "VIEWER"  # Read-Only Stakeholder


class SubscriptionStatus(StrEnum):
    """SaaS subscription lifecycle status enumeration.

    Attributes:
        ACTIVE: Subscription is active and in good standing.
        PAST_DUE: Subscription payment is past due.
        CANCELED: Subscription has been canceled.
        TRIAL: Organization is operating on a trial period.
    """

    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    TRIAL = "trial"


class SystemOrganizations(StrEnum):
    """Special predefined system organization identifiers.

    Attributes:
        ROOT_SYSTEM: Canonical root system organization identifier.
        LEGACY_SYSTEM: Legacy system scope marker retained for sentinel checks.
    """

    ROOT_SYSTEM = "org_system000000"
    LEGACY_SYSTEM = "SYSTEM"

    @classmethod
    def is_system(cls, org_id: str | None) -> bool:
        """Check whether an organization identifier belongs to the global system scope.

        Args:
            org_id: Organization identifier to evaluate, or None.

        Returns:
            True if the identifier represents a global system scope, False otherwise.
        """
        return org_id is None or org_id in (cls.ROOT_SYSTEM.value, cls.LEGACY_SYSTEM.value, "")


LaxUserRole = Annotated[UserRole, Field(strict=False)]
LaxSubscriptionStatus = Annotated[SubscriptionStatus, Field(strict=False)]

# --- Base Models ---


class Organization(V2CoreBase):
    """Represents a tenant or customer organization.

    Attributes:
        id: Unique Organization Opaque Stripe ID.
        slug: Optional human-readable identifier.
        name: Organization display name.
        created_at: Creation timestamp.
        is_active: Whether the organization subscription is active.
        tier: Service tier designation.
        contact_email: Administrative contact email address.
        billing_id: External billing provider identifier.
        subscription_status: Current SaaS billing status.
        quota_limit: Monthly API call quota in USD.
        tpm_limit: Tokens per minute rate limit.
        rpm_limit: Requests per minute rate limit.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    id: Annotated[
        str,
        Field(
            default_factory=lambda: generate_opaque_id(EntityPrefix.ORGANIZATION),
            pattern=r"^([a-z]{2,5})_[a-zA-Z0-9]{8,}$",
            description="Unique Organization ID (e.g. 'org_1234abcd')",
        ),
    ]
    slug: Annotated[str | None, Field(description="Legacy human-readable identifier")] = None
    name: Annotated[str, Field(description="Display Name")]
    created_at: Annotated[datetime | None, Field(description="ISO Timestamp")] = None
    is_active: Annotated[bool, Field(description="Subscription status")]
    tier: Annotated[str, Field(description="Service Tier")]
    contact_email: Annotated[str | None, Field(description="Admin Contact")] = None

    # Billing & SaaS Fields
    billing_id: Annotated[str | None, Field(description="External Billing ID (Stripe/etc)")] = None
    subscription_status: Annotated[LaxSubscriptionStatus, Field(description="Current billing status")]
    quota_limit: Annotated[float, Field(description="Monthly API call quota (USD)")]
    tpm_limit: Annotated[int, Field(ge=1000, description="Tokens Per Minute Limit")]
    rpm_limit: Annotated[int, Field(ge=1, description="Requests Per Minute Limit")]

    @field_validator("created_at", mode="before")
    @classmethod
    def parse_datetime(cls, v: Any) -> Any:
        """Coerces ISO 8601 datetime strings into datetime instances before strict validation.

        Args:
            v: Raw timestamp value (ISO string, datetime object, or None).

        Returns:
            Parsed datetime instance or original value for downstream validation.

        Raises:
            ValueError: If a string input is not a valid ISO 8601 timestamp.
        """
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v

    @field_validator("quota_limit")
    @classmethod
    def validate_quota_limit(cls, v: float) -> float:
        """Validates that the monthly quota limit is non-negative.

        Args:
            v: Input quota limit in USD.

        Returns:
            Validated non-negative quota limit.

        Raises:
            ValueError: With logged ErrorCodes.VALIDATION_FAILED if limit is negative.
        """
        if v < 0.0:
            msg = "Quota limit cannot be negative."
            logger.error("[AuthModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise ValueError(msg)
        return v

    @field_validator("id", "name")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        """Validates that a mandatory string field is not empty or whitespace-only.

        Args:
            v: Input string value.

        Returns:
            Stripped non-empty string.

        Raises:
            ValueError: With logged ErrorCodes.VALIDATION_FAILED if string is empty or whitespace-only.
        """
        if not v or not v.strip():
            msg = "Field cannot be empty or whitespace only."
            logger.error("[AuthModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise ValueError(msg)
        return v.strip()

    @field_validator("contact_email", "billing_id")
    @classmethod
    def validate_non_empty_optional(cls, v: str | None) -> str | None:
        """Validates that an optional string field is not empty or whitespace-only when provided.

        Args:
            v: Input optional string value.

        Returns:
            Stripped non-empty string, or None.

        Raises:
            ValueError: With logged ErrorCodes.VALIDATION_FAILED if provided string is empty or whitespace-only.
        """
        if v is not None and (not v or not v.strip()):
            msg = "Field cannot be empty or whitespace only."
            logger.error("[AuthModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise ValueError(msg)
        return v.strip() if v else v


class UserBase(V2CoreBase):
    """Base Pydantic model for User data containing shared identity and preference fields.

    Attributes:
        email: User email address.
        name: Optional user display name.
        role: Assigned permission role.
        organization_id: Identifier of the organization this user belongs to.
        is_active: Whether the user account is active.
        language: Preferred UI system locale.
        theme_mode: Preferred UI theme mode ('system', 'light', or 'dark').
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    email: Annotated[EmailStr, Field(description="User email address")]
    name: Annotated[str | None, Field(description="User display name")] = None
    role: Annotated[LaxUserRole, Field(description="Assigned permission role")]
    organization_id: Annotated[str | None, Field(description="ID of the organization this user belongs to")] = None
    is_active: Annotated[bool, Field(description="Is the account active?")]
    language: Annotated[LaxSystemLocale, Field(description="Preferred UI language")]
    theme_mode: Annotated[Literal["system", "light", "dark"], Field(description="Preferred Theme Mode")]

    @field_validator("name", "organization_id")
    @classmethod
    def validate_non_empty_optional(cls, v: str | None) -> str | None:
        """Validates that an optional string field is not empty or whitespace-only when provided.

        Args:
            v: Input optional string value.

        Returns:
            Stripped non-empty string, or None.

        Raises:
            ValueError: With logged ErrorCodes.VALIDATION_FAILED if provided string is empty or whitespace-only.
        """
        if v is not None and (not v or not v.strip()):
            msg = "Field cannot be empty or whitespace only."
            logger.error("[AuthModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise ValueError(msg)
        return v.strip() if v else v


# --- Database / API Response Models ---


class User(UserBase):
    """Full User model representing a persisted user record.

    Attributes:
        id: Unique User Opaque Stripe ID.
        slug: Optional human-readable identifier.
        created_at: Account creation timestamp.
        created_by: Identifier of the creator user, if applicable.
    """

    id: Annotated[
        str,
        Field(
            default_factory=lambda: generate_opaque_id(EntityPrefix.USER),
            pattern=r"^([a-z]{2,5})_[a-zA-Z0-9]{8,}$",
            description="Unique ID (matches Firebase UID if used)",
        ),
    ]
    slug: Annotated[str | None, Field(description="Legacy human-readable identifier")] = None
    created_at: Annotated[datetime, Field(description="ISO 8601 Timestamp")]
    created_by: Annotated[str | None, Field(description="UID of the creator")] = None

    @field_validator("created_at", mode="before")
    @classmethod
    def parse_datetime(cls, v: Any) -> Any:
        """Coerces ISO 8601 datetime strings into datetime instances before strict validation.

        Args:
            v: Raw timestamp value (ISO string or datetime object).

        Returns:
            Parsed datetime instance or original value for downstream validation.

        Raises:
            ValueError: If a string input is not a valid ISO 8601 timestamp.
        """
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v

    @field_validator("id")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        """Validates that the user identifier is not empty or whitespace-only.

        Args:
            v: Input identifier string.

        Returns:
            Stripped non-empty identifier string.

        Raises:
            ValueError: With logged ErrorCodes.VALIDATION_FAILED if string is empty or whitespace-only.
        """
        if not v or not v.strip():
            msg = "Field cannot be empty or whitespace only."
            logger.error("[AuthModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise ValueError(msg)
        return v.strip()

    @field_validator("created_by")
    @classmethod
    def validate_created_by_optional(cls, v: str | None) -> str | None:
        """Validates that the optional creator identifier is not empty when provided.

        Args:
            v: Input creator identifier string or None.

        Returns:
            Stripped creator identifier string, or None.

        Raises:
            ValueError: With logged ErrorCodes.VALIDATION_FAILED if provided string is empty or whitespace-only.
        """
        if v is not None and (not v or not v.strip()):
            msg = "Field cannot be empty or whitespace only."
            logger.error("[AuthModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise ValueError(msg)
        return v.strip() if v else v


class UserAdminView(UserBase):
    """Extended User model for administrative views with execution statistics and login metadata.

    Attributes:
        id: Unique User Opaque Stripe ID.
        slug: Optional human-readable identifier.
        created_at: Account creation timestamp.
        created_by: Identifier of the creator user, if applicable.
        last_login_at: Timestamp of most recent login, if available.
        execution_count: Total number of workflow executions run by the user.
    """

    id: Annotated[str, Field(description="Unique user identifier")]
    slug: Annotated[str | None, Field(default=None, description="Legacy human-readable identifier")] = None
    created_at: Annotated[datetime, Field(description="Account creation timestamp")]
    created_by: Annotated[str | None, Field(default=None, description="UID of the creator")] = None
    last_login_at: Annotated[datetime | None, Field(default=None, description="Timestamp of last login")] = None
    execution_count: Annotated[int, Field(default=0, description="Total number of executions run")] = 0

    model_config = ConfigDict(from_attributes=True, extra="forbid", frozen=True, strict=True)


# --- Creation Models ---


class UserCreate(UserBase):
    """Payload for creating a new user account.

    Attributes:
        password: Optional initial password (minimum 6 characters).
        created_by: Optional identifier of the administrator creating the user.
    """

    password: Annotated[str | None, Field(min_length=6, description="Initial password")] = None
    created_by: Annotated[str | None, Field(description="UID of the admin creating this user")] = None


class OrganizationCreate(BaseDTO):
    """Payload for provisioning a new tenant organization and its initial administrator.

    Attributes:
        name: Organization display name.
        admin_email: Email address for the initial administrator user.
        admin_password: Password for the initial administrator user.
        admin_name: Display name for the initial administrator user.
        tpm_limit: Tokens per minute limit allocated to the organization.
        rpm_limit: Requests per minute limit allocated to the organization.
    """

    name: Annotated[str, Field(description="Organization display name")]
    admin_email: Annotated[EmailStr, Field(description="Email for the initial admin user")]
    admin_password: Annotated[str, Field(description="Password for the initial admin user")]
    admin_name: Annotated[str, Field(description="Display name for the initial admin user")]
    tpm_limit: Annotated[int, Field(description="Tokens Per Minute Limit")]
    rpm_limit: Annotated[int, Field(description="Requests Per Minute Limit")]

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    @field_validator("name", "admin_password", "admin_name")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        """Validates that mandatory creation strings are not empty or whitespace-only.

        Args:
            v: Input string value.

        Returns:
            Stripped non-empty string.

        Raises:
            ValueError: With logged ErrorCodes.VALIDATION_FAILED if string is empty or whitespace-only.
        """
        if not v or not v.strip():
            msg = "Field cannot be empty or whitespace only."
            logger.error("[AuthModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise ValueError(msg)
        return v.strip()


class OrganizationUpdateDTO(BaseDTO):
    """Payload for updating an existing organization.

    Attributes:
        name: Updated organization display name.
        tier: Updated service tier designation.
        is_active: Updated active status flag.
        contact_email: Updated administrative contact email.
        billing_id: Updated external billing identifier.
        subscription_status: Updated SaaS subscription status.
        quota_limit: Updated monthly API quota limit in USD.
        tpm_limit: Updated tokens per minute limit.
        rpm_limit: Updated requests per minute limit.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    name: Annotated[str | None, Field(default=None, description="Updated display name")] = None
    tier: Annotated[str | None, Field(default=None, description="Updated service tier")] = None
    is_active: Annotated[bool | None, Field(default=None, description="Updated active status")] = None
    contact_email: Annotated[str | None, Field(default=None, description="Updated contact email")] = None
    billing_id: Annotated[str | None, Field(default=None, description="Updated billing ID")] = None
    subscription_status: Annotated[
        LaxSubscriptionStatus | None, Field(default=None, description="Updated subscription status")
    ] = None
    quota_limit: Annotated[
        float | None, Field(default=None, ge=0.0, description="Updated monthly quota limit (USD)")
    ] = None
    tpm_limit: Annotated[int | None, Field(default=None, ge=1000, description="Updated TPM limit")] = None
    rpm_limit: Annotated[int | None, Field(default=None, ge=1, description="Updated RPM limit")] = None


class UserUpdate(BaseDTO):
    """Payload for updating an existing user account.

    Attributes:
        name: Updated user display name.
        role: Updated role assignment.
        is_active: Updated account active status.
        password: Updated password for administrative resets.
        language: Updated preferred UI locale.
        theme_mode: Updated preferred UI theme mode.
        organization_id: Updated organization assignment identifier.
    """

    name: Annotated[str | None, Field(default=None, description="New display name")] = None
    role: Annotated[UserRole | None, Field(default=None, description="New role assignment")] = None
    is_active: Annotated[bool | None, Field(default=None, description="New active status")] = None
    password: Annotated[str | None, Field(default=None, description="New password (only for admin resets)")] = None
    language: Annotated[LaxSystemLocale | None, Field(default=None, description="Preferred UI language")] = None
    theme_mode: Annotated[
        Literal["system", "light", "dark"] | None, Field(default=None, description="Preferred Theme Mode")
    ] = None
    organization_id: Annotated[str | None, Field(default=None, description="New organization ID")] = None

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")


# --- Auth Fragments ---


class TokenData(V2CoreBase):
    """Structure for verified JWT token payload data.

    Attributes:
        id: Authenticated user identifier.
        role: Authenticated user permission role.
        organization_id: Associated organization identifier, if tenant-scoped.
        email: Authenticated user email address, if present in token claims.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    id: Annotated[str, Field(description="Authenticated user ID")]
    role: Annotated[LaxUserRole, Field(description="Authenticated user role")]
    organization_id: Annotated[str | None, Field(default=None, description="Organization ID")] = None
    email: Annotated[str | None, Field(default=None, description="User email address")] = None

    @field_validator("id")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        """Validates that the token user identifier is not empty or whitespace-only.

        Args:
            v: Input identifier string.

        Returns:
            Stripped non-empty identifier string.

        Raises:
            ValueError: With logged ErrorCodes.VALIDATION_FAILED if string is empty or whitespace-only.
        """
        if not v or not v.strip():
            msg = "Field cannot be empty or whitespace only."
            logger.error("[AuthModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise ValueError(msg)
        return v.strip()

    @field_validator("organization_id", "email")
    @classmethod
    def validate_non_empty_optional(cls, v: str | None) -> str | None:
        """Validates that optional token claim strings are not empty when provided.

        Args:
            v: Input optional string value.

        Returns:
            Stripped non-empty string, or None.

        Raises:
            ValueError: With logged ErrorCodes.VALIDATION_FAILED if provided string is empty or whitespace-only.
        """
        if v is not None and (not v or not v.strip()):
            msg = "Field cannot be empty or whitespace only."
            logger.error("[AuthModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise ValueError(msg)
        return v.strip() if v else v


class UserDeleteResponse(BaseResponseDTO):
    """Payload response for deleting a user account.

    Attributes:
        status: Deletion status indicator message.
        id: Identifier of the deleted user.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    status: Annotated[str, Field(description="Deletion status message")]
    id: Annotated[str, Field(description="ID of the deleted user")]


class TokenPayload(BaseDTO):
    """Request payload for cryptographic token verification.

    Attributes:
        token: Raw JWT bearer token string.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    token: Annotated[str, Field(description="JWT token string")]


class LoginResponse(BaseResponseDTO):
    """Response model for a successful authentication session handshake.

    Attributes:
        user: Authenticated user domain object.
        token_valid: Whether the verified token is valid.
        debug_msg: Optional diagnostic message.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    user: Annotated[User, Field(description="Authenticated user object")]
    token_valid: Annotated[bool, Field(description="Whether the token is valid")]
    debug_msg: Annotated[str | None, Field(default=None, description="Optional debug message")] = None


class ImpersonationRequest(BaseDTO):
    """Request payload for initiating administrative user impersonation.

    Attributes:
        target_id: Identifier of the target user to impersonate.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    target_id: Annotated[str, Field(description="ID of the user to impersonate")]


class ImpersonationResponse(BaseResponseDTO):
    """Response containing the issued administrative impersonation token.

    Attributes:
        access_token: Signed JWT impersonation access token.
        token_type: Authorization token scheme (defaults to 'bearer').
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    access_token: Annotated[str, Field(description="Impersonation access token")]
    token_type: Annotated[str, Field(default="bearer", description="Token type scheme")] = "bearer"


class OrganizationDeleteResponse(BaseResponseDTO):
    """Payload response for deleting an organization.

    Attributes:
        status: Deletion status indicator message.
        deleted_id: Identifier of the deleted organization.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    status: Annotated[str, Field(description="Deletion status message")]
    deleted_id: Annotated[str, Field(description="ID of the deleted organization")]
