"""Authentication, Identity Management, Invitation, Task Assignment, and Tenant Secret Models.

This module defines strict Pydantic V2 models and DTOs for user identity, role-based
access control (RBAC), organization management, cryptographic session token exchange,
invitations, single-use workflow execution assignments, and tenant BYOK secrets.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from enum import StrEnum
from typing import Annotated, Any, Literal, Self

from pydantic import ConfigDict, EmailStr, Field, SecretStr, field_validator, model_validator

from backend_v2.exceptions import ErrorCodes
from backend_v2.models.core_base import (
    PrefixedUUID7,
    V2CoreBase,
    generate_uuid7_opaque_id,
)
from backend_v2.models.domain.execution import ExecutionAssignment as ExecutionAssignment
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.dtos.base import BaseDTO, BaseResponseDTO
from backend_v2.models.enums import (
    AssignmentResultVisibility,
    EmailDeliveryStatus,
    EntityPrefix,
    InvitationStatus,
    LaxAssignmentResultVisibility,
    LaxAssignmentStatus,
    LaxEmailDeliveryStatus,
    LaxInvitationStatus,
    LaxSecretScope,
    LaxSecretStorageMode,
    LaxSystemLocale,
    SecretStorageMode,
    SystemLocale,
)
from backend_v2.models.enums import (
    LaxSubscriptionStatus as LaxSubscriptionStatus,
)
from backend_v2.models.enums import (
    LaxUserRole as LaxUserRole,
)
from backend_v2.models.enums import (
    SubscriptionStatus as SubscriptionStatus,
)
from backend_v2.models.enums import (
    UserRole as UserRole,
)

logger = logging.getLogger(__name__)

SYSTEM_ROOT_USER_ID: str = "usr_0195f3a00000700a83fd6b3d77c748f4"

__all__ = [
    "SYSTEM_ROOT_USER_ID",
    "CliSessionStateDTO",
    "ExecutionAssignment",
    "ExecutionAssignmentBatchCreateDTO",
    "ExecutionAssignmentBatchResponseDTO",
    "ExecutionAssignmentCreateDTO",
    "ExecutionAssignmentDraftDTO",
    "ExecutionAssignmentOnboardingRequestDTO",
    "ExecutionAssignmentPreviewDTO",
    "ExecutionAssignmentRecipientDTO",
    "ExecutionAssignmentResponseDTO",
    "ExecutionAssignmentSubmitDTO",
    "ImpersonationRequest",
    "ImpersonationResponse",
    "Invitation",
    "InvitationAcceptRequestDTO",
    "InvitationBatchCreateDTO",
    "InvitationBatchResponseDTO",
    "InvitationCreateDTO",
    "InvitationResponseDTO",
    "LaxSubscriptionStatus",
    "LaxUserRole",
    "LogoutRequestDTO",
    "LogoutResponseDTO",
    "Organization",
    "OrganizationCreate",
    "OrganizationDeleteResponse",
    "OrganizationUpdateDTO",
    "ResolvedCredentialDTO",
    "SubscriptionStatus",
    "SystemOrganizations",
    "TenantSecretCreateDTO",
    "TenantSecretDTO",
    "TenantSecretResponseDTO",
    "TokenData",
    "TokenExchangeRequestDTO",
    "TokenExchangeResponseDTO",
    "TransactionalEmailBatchResultDTO",
    "TransactionalEmailItemDTO",
    "User",
    "UserAdminView",
    "UserBase",
    "UserCreate",
    "UserDeleteResponse",
    "UserRole",
    "UserUpdate",
]


class SystemOrganizations(StrEnum):
    """Canonical predefined system organization identifiers.

    Attributes:
        ROOT_SYSTEM: Canonical root system organization RFC 9562 UUIDv7 Opaque Stripe ID.
    """

    ROOT_SYSTEM = "org_0195f3a0000070008000000000000001"

    @classmethod
    def is_system(cls, org_id: str | None) -> bool:
        """Check whether an organization identifier belongs to the global system scope.

        Args:
            org_id: Organization identifier to evaluate, or None.

        Returns:
            True if the identifier represents a global system scope, False otherwise.
        """
        return not org_id or org_id in (cls.ROOT_SYSTEM.value, "SYSTEM")


# --- Base & Domain Models ---


class Organization(V2CoreBase):
    """Represents a tenant or customer organization.

    Attributes:
        id: Unique Organization Opaque Stripe ID (org_<hex32>).
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
        allowed_email_domains: Optional allowlist of lowercase email domains permitted for invitations and assignments.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    id: Annotated[
        PrefixedUUID7,
        Field(
            default_factory=lambda: generate_uuid7_opaque_id(EntityPrefix.ORG),
            description="Unique Organization ID (org_<hex32>)",
        ),
    ]
    slug: Annotated[str | None, Field(default=None, description="Legacy human-readable identifier")] = None
    name: Annotated[str, Field(description="Display Name")]
    created_at: Annotated[datetime | None, Field(default=None, description="ISO Timestamp")] = None
    is_active: Annotated[bool, Field(description="Subscription status")]
    tier: Annotated[str, Field(description="Service Tier")]
    contact_email: Annotated[str | None, Field(default=None, description="Admin Contact")] = None

    # Billing & SaaS Fields
    billing_id: Annotated[str | None, Field(default=None, description="External Billing ID (Stripe/etc)")] = None
    subscription_status: Annotated[LaxSubscriptionStatus, Field(description="Current billing status")]
    quota_limit: Annotated[float, Field(description="Monthly API call quota (USD)")]
    tpm_limit: Annotated[int, Field(ge=1000, description="Tokens Per Minute Limit")]
    rpm_limit: Annotated[int, Field(ge=1, description="Requests Per Minute Limit")]
    allowed_email_domains: Annotated[
        list[str],
        Field(
            default_factory=list,
            description="Optional allowlist of lowercase email domains permitted for organization invitations and task assignments",
        ),
    ]

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

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    email: Annotated[EmailStr, Field(description="User email address")]
    name: Annotated[str | None, Field(default=None, description="User display name")] = None
    role: Annotated[LaxUserRole, Field(description="Assigned permission role")]
    organization_id: Annotated[
        str | None, Field(default=None, description="ID of the organization this user belongs to")
    ] = None
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


class User(UserBase):
    """Full User model representing a persisted user record.

    Attributes:
        id: Unique User Opaque Stripe ID (usr_<hex32>).
        slug: Optional human-readable identifier.
        created_at: Account creation timestamp.
        created_by: Identifier of the creator user, if applicable.
        firebase_uid: External Firebase Auth UID when linked.
        deleted_at: GDPR soft-deletion UTC timestamp.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    id: Annotated[
        PrefixedUUID7,
        Field(
            default_factory=lambda: generate_uuid7_opaque_id(EntityPrefix.USER),
            description="Unique User ID (usr_<hex32>)",
        ),
    ]
    slug: Annotated[str | None, Field(default=None, description="Legacy human-readable identifier")] = None
    created_at: Annotated[datetime, Field(description="ISO 8601 Timestamp")]
    created_by: Annotated[str | None, Field(default=None, description="UID of the creator")] = None
    firebase_uid: Annotated[
        str | None,
        Field(default=None, min_length=1, max_length=128, description="External Firebase Auth UID"),
    ] = None
    deleted_at: Annotated[
        datetime | None,
        Field(default=None, description="GDPR soft-deletion timestamp"),
    ] = None

    @field_validator("created_at", "deleted_at", mode="before")
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


class UserAdminView(User):
    """Extended User model for administrative views with execution statistics and login metadata.

    Attributes:
        id: Unique User Opaque Stripe ID (usr_<hex32>).
        slug: Optional human-readable identifier.
        created_at: Account creation timestamp.
        created_by: Identifier of the creator user, if applicable.
        firebase_uid: External Firebase Auth UID when linked.
        deleted_at: GDPR soft-deletion UTC timestamp.
        last_login_at: Timestamp of most recent login, if available.
        execution_count: Total number of workflow executions run by the user.
    """

    model_config = ConfigDict(from_attributes=True, extra="forbid", frozen=True, strict=True)

    # Inherit all 13 persisted User fields (including firebase_uid and deleted_at) for unified client hydration.
    last_login_at: Annotated[datetime | None, Field(default=None, description="Timestamp of last login")] = None
    execution_count: Annotated[int, Field(default=0, description="Total number of executions run")] = 0

    @field_validator("last_login_at", mode="before")
    @classmethod
    def parse_last_login_at(cls, v: Any) -> Any:
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


# --- Creation & Update Models ---


class UserCreate(UserBase):
    """Payload for creating a new user account.

    Attributes:
        password: Optional initial password (minimum 6 characters).
        created_by: Optional identifier of the administrator creating the user.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    password: Annotated[str | None, Field(default=None, min_length=6, description="Initial password")] = None
    created_by: Annotated[str | None, Field(default=None, description="UID of the admin creating this user")] = None


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

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    name: Annotated[str, Field(description="Organization display name")]
    admin_email: Annotated[EmailStr, Field(description="Email for the initial admin user")]
    admin_password: Annotated[str, Field(description="Password for the initial admin user")]
    admin_name: Annotated[str, Field(description="Display name for the initial admin user")]
    tpm_limit: Annotated[int, Field(description="Tokens Per Minute Limit")]
    rpm_limit: Annotated[int, Field(description="Requests Per Minute Limit")]

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
        allowed_email_domains: Updated allowlist of lowercase email domains.
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
    allowed_email_domains: Annotated[
        list[str] | None,
        Field(
            default=None,
            description="Optional allowlist of lowercase email domains permitted for organization invitations and task assignments",
        ),
    ] = None


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

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    name: Annotated[str | None, Field(default=None, description="New display name")] = None
    role: Annotated[UserRole | None, Field(default=None, description="New role assignment")] = None
    is_active: Annotated[bool | None, Field(default=None, description="New active status")] = None
    password: Annotated[str | None, Field(default=None, description="New password (only for admin resets)")] = None
    language: Annotated[LaxSystemLocale | None, Field(default=None, description="Preferred UI language")] = None
    theme_mode: Annotated[
        Literal["system", "light", "dark"] | None, Field(default=None, description="Preferred Theme Mode")
    ] = None
    organization_id: Annotated[str | None, Field(default=None, description="New organization ID")] = None


# --- Auth & Session Token Exchange DTOs ---


class TokenData(V2CoreBase):
    """Structure for verified Quorum Local JWT token payload data.

    Attributes:
        id: Authenticated user identifier.
        role: Authenticated user permission role.
        organization_id: Associated organization identifier, if tenant-scoped.
        email: Authenticated user email address, if present in token claims.
        mfa_verified: Whether the session satisfied Multi-Factor Authentication.
        jti: RFC 7519 unique JWT identifier for O(1) session revocation.
        actor_id: RFC 8693 Actor ID when session is an administrative impersonation.
        iat: Token issued-at UTC epoch timestamp in seconds.
        exp: Token expiration UTC epoch timestamp in seconds.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    id: Annotated[str, Field(description="Authenticated user ID")]
    role: Annotated[LaxUserRole, Field(description="Authenticated user role")]
    organization_id: Annotated[str | None, Field(default=None, description="Organization ID")] = None
    email: Annotated[str | None, Field(default=None, description="User email address")] = None
    mfa_verified: Annotated[
        bool,
        Field(default=True, description="Whether the session satisfied Multi-Factor Authentication"),
    ] = True
    jti: Annotated[
        str | None,
        Field(default=None, min_length=1, description="RFC 7519 unique JWT identifier for O(1) session revocation"),
    ] = None
    actor_id: Annotated[
        PrefixedUUID7 | None,
        Field(default=None, description="RFC 8693 Actor ID when session is an administrative impersonation"),
    ] = None
    iat: Annotated[
        int | None,
        Field(default=None, ge=0, description="Token issued-at UTC epoch timestamp in seconds"),
    ] = None
    exp: Annotated[
        int | None,
        Field(default=None, ge=0, description="Token expiration UTC epoch timestamp in seconds"),
    ] = None

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


class TokenExchangeRequestDTO(BaseDTO):
    """Request payload for exchanging an external Firebase ID token or CLI service secret for a Quorum Local JWT.

    Attributes:
        firebase_token: External Firebase ID Token for interactive sessions.
        target_user_id: Target seeded user ID for headless CLI, E2E, or local development token exchange.
        service_auth_secret: Optional shared service secret for headless M2M token exchange.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    firebase_token: Annotated[
        str | None,
        Field(default=None, min_length=10, description="External Firebase ID Token for interactive sessions"),
    ] = None
    target_user_id: Annotated[
        PrefixedUUID7 | None,
        Field(
            default=None,
            description="Target seeded user ID for headless CLI, E2E, or local development token exchange",
        ),
    ] = None
    service_auth_secret: Annotated[
        SecretStr | None,
        Field(default=None, description="Optional shared service secret for headless M2M token exchange"),
    ] = None

    @model_validator(mode="after")
    def _validate_mutual_exclusivity(self) -> Self:
        """Enforce XOR mutual exclusivity between firebase_token and target_user_id.

        Returns:
            Validated TokenExchangeRequestDTO instance.

        Raises:
            ValueError: With logged ErrorCodes.VALIDATION_FAILED if neither or both fields are supplied.
        """
        if not ((self.firebase_token is not None) ^ (self.target_user_id is not None)):
            msg = "Exactly one of 'firebase_token' or 'target_user_id' must be provided."
            logger.error("[AuthModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise ValueError(msg)
        return self


class TokenExchangeResponseDTO(BaseResponseDTO):
    """Response model for a successful Quorum Local JWT session token exchange.

    Attributes:
        access_token: Signed Quorum Local JWT bearer token string.
        token_type: Authorization token scheme ('bearer').
        expires_in_seconds: Token lifetime in seconds.
        user: Authenticated user profile.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    access_token: Annotated[str, Field(min_length=10, description="Signed Quorum Local JWT access token")]
    token_type: Annotated[Literal["bearer"], Field(default="bearer", description="Token scheme")] = "bearer"
    expires_in_seconds: Annotated[int, Field(ge=60, description="Token lifetime in seconds")]
    user: Annotated[User, Field(description="Authenticated user profile")]


class LogoutRequestDTO(BaseDTO):
    """Request payload for revoking the current JWT session or all user sessions.

    Attributes:
        revoke_all_sessions: When True, revokes all active sessions for the user across all devices.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    revoke_all_sessions: Annotated[
        bool,
        Field(default=False, description="When True, revokes all active sessions for the user across all devices"),
    ] = False


class LogoutResponseDTO(BaseResponseDTO):
    """Response payload confirming session revocation.

    Attributes:
        status: Static logout confirmation indicator ('logged_out').
        revoked_jti: Revoked RFC 7519 token identifier.
        all_sessions_revoked: Whether all active sessions for the user were revoked.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    status: Annotated[Literal["logged_out"], Field(default="logged_out", description="Logout status")] = "logged_out"
    revoked_jti: Annotated[str, Field(min_length=1, description="Revoked RFC 7519 token identifier")]
    all_sessions_revoked: Annotated[
        bool,
        Field(default=False, description="Whether all active sessions for the user were revoked"),
    ] = False


class CliSessionStateDTO(BaseDTO):
    """Immutable state container for headless CLI and E2E test session tokens.

    Attributes:
        access_token: Active Quorum Local JWT access token.
        expires_at_monotonic: Monotonic clock expiration timestamp in seconds.
        user_id: Authenticated CLI user ID (usr_<hex32>).
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    access_token: Annotated[str, Field(min_length=10, description="Active Quorum Local JWT access token")]
    expires_at_monotonic: Annotated[float, Field(ge=0.0, description="Monotonic clock expiration timestamp")]
    user_id: Annotated[PrefixedUUID7, Field(description="Authenticated CLI user ID")]


class UserDeleteResponse(BaseResponseDTO):
    """Payload response for deleting a user account.

    Attributes:
        status: Deletion status indicator message.
        id: Identifier of the deleted user.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    status: Annotated[str, Field(description="Deletion status message")]
    id: Annotated[str, Field(description="ID of the deleted user")]


class ImpersonationRequest(BaseDTO):
    """Request payload for initiating administrative break-glass user impersonation.

    Attributes:
        target_id: Identifier of the target user to impersonate (usr_<hex32>).
        reason: Mandatory ticket or support justification for break-glass impersonation.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    target_id: Annotated[PrefixedUUID7, Field(description="ID of the user to impersonate")]
    reason: Annotated[
        str,
        Field(
            default="Administrative support session",
            min_length=5,
            max_length=500,
            description="Mandatory ticket or support justification for break-glass impersonation",
        ),
    ] = "Administrative support session"


class ImpersonationResponse(BaseResponseDTO):
    """Response containing the issued administrative impersonation token.

    Attributes:
        access_token: Signed JWT impersonation access token.
        token_type: Authorization token scheme (defaults to 'bearer').
        target_id: Identifier of the impersonated target user (usr_<hex32>).
        reason: Mandatory ticket or support justification recorded for the impersonation.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    access_token: Annotated[str, Field(description="Impersonation access token")]
    token_type: Annotated[str, Field(default="bearer", description="Token type scheme")] = "bearer"
    target_id: Annotated[
        PrefixedUUID7,
        Field(
            default=SYSTEM_ROOT_USER_ID,
            description="ID of the impersonated target user",
        ),
    ] = SYSTEM_ROOT_USER_ID
    reason: Annotated[
        str,
        Field(
            default="Administrative support session",
            min_length=5,
            max_length=500,
            description="Mandatory ticket or support justification for break-glass impersonation",
        ),
    ] = "Administrative support session"


class OrganizationDeleteResponse(BaseResponseDTO):
    """Payload response for deleting an organization.

    Attributes:
        status: Deletion status indicator message.
        deleted_id: Identifier of the deleted organization.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    status: Annotated[str, Field(description="Deletion status message")]
    deleted_id: Annotated[str, Field(description="ID of the deleted organization")]


# --- Invitations ---


class Invitation(V2CoreBase):
    """Persisted organization invitation record.

    Attributes:
        id: Canonical Invitation Opaque Stripe ID (inv_<hex32>).
        organization_id: Target Organization ID (org_<hex32>).
        email: Invited user email address.
        role: Permission role granted upon acceptance.
        token_hash: SHA-256 hex digest of the raw invitation token.
        status: Invitation lifecycle status.
        email_delivery_status: Transactional email delivery status.
        invited_by: Creator User ID (usr_<hex32>).
        expires_at: UTC expiration timestamp.
        created_at: UTC creation timestamp.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    id: Annotated[
        PrefixedUUID7,
        Field(
            default_factory=lambda: generate_uuid7_opaque_id(EntityPrefix.INVITATION),
            description="Canonical Invitation ID (inv_<hex32>)",
        ),
    ]
    organization_id: Annotated[PrefixedUUID7, Field(description="Target Organization ID (org_<hex32>)")]
    email: Annotated[EmailStr, Field(description="Invited user email address")]
    role: Annotated[LaxUserRole, Field(default=UserRole.MEMBER, description="Role granted upon acceptance")] = (
        UserRole.MEMBER
    )
    token_hash: Annotated[
        str,
        Field(min_length=64, max_length=64, description="SHA-256 hex digest of the raw invitation token"),
    ]
    status: Annotated[
        LaxInvitationStatus,
        Field(default=InvitationStatus.PENDING, description="Invitation lifecycle status"),
    ] = InvitationStatus.PENDING
    email_delivery_status: Annotated[
        LaxEmailDeliveryStatus,
        Field(default=EmailDeliveryStatus.PENDING, description="Transactional email delivery status"),
    ] = EmailDeliveryStatus.PENDING
    invited_by: Annotated[PrefixedUUID7, Field(description="Creator User ID (usr_<hex32>)")]
    expires_at: Annotated[datetime, Field(description="UTC expiration timestamp")]
    created_at: Annotated[
        datetime,
        Field(default_factory=lambda: datetime.now(timezone.utc), description="UTC creation timestamp"),
    ]

    @field_validator("expires_at", "created_at", mode="before")
    @classmethod
    def _parse_iso_datetime(cls, value: datetime | str) -> datetime:
        """Coerce ISO 8601 datetime strings into timezone-aware datetime instances.

        Args:
            value: Raw timestamp value (ISO string or datetime object).

        Returns:
            Parsed datetime instance.

        Raises:
            ValueError: If a string input is not a valid ISO 8601 timestamp.
        """
        if isinstance(value, str):
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        return value


class InvitationCreateDTO(BaseDTO):
    """Payload for inviting a user to an organization.

    Attributes:
        email: Recipient email address.
        role: Role to grant upon acceptance.
        expires_in_hours: Invitation validity window in hours.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    email: Annotated[EmailStr, Field(description="Recipient email address")]
    role: Annotated[LaxUserRole, Field(default=UserRole.MEMBER, description="Role granted upon acceptance")] = (
        UserRole.MEMBER
    )
    expires_in_hours: Annotated[
        int,
        Field(default=168, ge=1, le=720, description="Invitation validity window in hours"),
    ] = 168


class InvitationAcceptRequestDTO(BaseDTO):
    """Payload for accepting an organization invitation token.

    Attributes:
        raw_token: Raw single-use invitation token from the invitation link.
        firebase_token: Verified Firebase ID token of the accepting user.
        name: Optional display name for newly provisioned user profile.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    raw_token: Annotated[str, Field(min_length=16, description="Raw single-use invitation token")]
    firebase_token: Annotated[
        str | None,
        Field(default=None, min_length=10, description="Firebase ID token of the accepting user"),
    ] = None
    name: Annotated[str | None, Field(default=None, min_length=1, max_length=120, description="Display name")] = None


class InvitationResponseDTO(BaseResponseDTO):
    """API response DTO representing an organization invitation without exposing token_hash.

    Attributes:
        id: Canonical Invitation ID (inv_<hex32>).
        organization_id: Target Organization ID (org_<hex32>).
        email: Invited user email address.
        role: Role granted upon acceptance.
        status: Invitation lifecycle status.
        email_delivery_status: Transactional email delivery status.
        invited_by: Creator User ID (usr_<hex32>).
        expires_at: UTC expiration timestamp.
        created_at: UTC creation timestamp.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    id: Annotated[PrefixedUUID7, Field(description="Canonical Invitation ID (inv_<hex32>)")]
    organization_id: Annotated[PrefixedUUID7, Field(description="Target Organization ID (org_<hex32>)")]
    email: Annotated[EmailStr, Field(description="Invited user email address")]
    role: Annotated[LaxUserRole, Field(description="Role granted upon acceptance")]
    status: Annotated[LaxInvitationStatus, Field(description="Invitation lifecycle status")]
    email_delivery_status: Annotated[
        LaxEmailDeliveryStatus,
        Field(default=EmailDeliveryStatus.PENDING, description="Transactional email delivery status"),
    ] = EmailDeliveryStatus.PENDING
    invited_by: Annotated[PrefixedUUID7, Field(description="Creator User ID (usr_<hex32>)")]
    expires_at: Annotated[datetime, Field(description="UTC expiration timestamp")]
    created_at: Annotated[datetime, Field(description="UTC creation timestamp")]


class InvitationBatchCreateDTO(BaseDTO):
    """Payload for bulk-creating organization invitations (1 to 500 recipients).

    Attributes:
        recipients: Closed list of 1 to 500 invitation creation payloads.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    recipients: Annotated[
        list[InvitationCreateDTO],
        Field(min_length=1, max_length=500, description="Batch of 1 to 500 invitation recipients"),
    ]


class InvitationBatchResponseDTO(BaseResponseDTO):
    """Response payload for bulk-created organization invitations.

    Attributes:
        created_count: Total number of invitations created in the batch.
        invitations: Materialized invitation response DTOs.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    created_count: Annotated[int, Field(ge=0, description="Total number of invitations created")]
    invitations: Annotated[list[InvitationResponseDTO], Field(description="Created invitations")]


# --- Task Assignment & Transactional Email DTOs ---


class ExecutionAssignmentCreateDTO(BaseDTO):
    """Payload for creating a single-use workflow execution assignment.

    Attributes:
        assigned_email: Recipient email address.
        invited_role: Role granted upon auto-onboarding.
        workflow_id: Target Workflow ID (wf_<hex32>).
        output_profile_id: Optional Output Profile ID (prf_<hex32>).
        target_locale: Target execution locale.
        locked_inputs: Immutable manager-locked workflow inputs.
        assignee_input_keys: ExpectedInput keys unlocked for assignee completion.
        result_visibility: Post-submission result visibility policy.
        hard_deadline_at: Absolute UTC deadline timestamp.
        relative_duration_seconds: Optional countdown timer in seconds from activation.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    assigned_email: Annotated[EmailStr, Field(description="Recipient email address")]
    invited_role: Annotated[
        LaxUserRole,
        Field(default=UserRole.MEMBER, description="Role granted upon auto-onboarding"),
    ] = UserRole.MEMBER
    workflow_id: Annotated[PrefixedUUID7, Field(description="Target Workflow ID (wf_<hex32>)")]
    output_profile_id: Annotated[
        PrefixedUUID7 | None,
        Field(default=None, description="Optional Output Profile ID (prf_<hex32>)"),
    ] = None
    target_locale: Annotated[
        LaxSystemLocale,
        Field(default=SystemLocale.FI, description="Target execution locale"),
    ] = SystemLocale.FI
    locked_inputs: Annotated[
        WorkflowInputs,
        Field(default_factory=WorkflowInputs, description="Immutable manager-locked workflow inputs"),
    ]
    assignee_input_keys: Annotated[
        list[str],
        Field(default_factory=list, description="ExpectedInput keys unlocked for assignee completion"),
    ]
    result_visibility: Annotated[
        LaxAssignmentResultVisibility,
        Field(
            default=AssignmentResultVisibility.CONFIRMATION_ONLY,
            description="Post-submission result visibility policy",
        ),
    ] = AssignmentResultVisibility.CONFIRMATION_ONLY
    hard_deadline_at: Annotated[
        datetime,
        Field(strict=False, description="Absolute UTC deadline timestamp"),
    ]
    relative_duration_seconds: Annotated[
        int | None,
        Field(default=None, ge=60, description="Optional relative countdown timer in seconds from activation"),
    ] = None


class ExecutionAssignmentRecipientDTO(BaseDTO):
    """Individual recipient descriptor within a bulk task assignment batch.

    Attributes:
        email: Recipient email address.
        name: Optional recipient display name.
        target_locale: Optional per-recipient locale override.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    email: Annotated[EmailStr, Field(description="Recipient email address")]
    name: Annotated[
        str | None,
        Field(default=None, min_length=1, max_length=120, description="Optional recipient display name"),
    ] = None
    target_locale: Annotated[
        LaxSystemLocale | None,
        Field(default=None, description="Optional per-recipient locale override"),
    ] = None


class ExecutionAssignmentBatchCreateDTO(BaseDTO):
    """Payload for bulk-creating 1 to 500 single-use workflow execution assignments.

    Attributes:
        recipients: List of 1 to 500 task assignment recipients.
        invited_role: Role granted upon auto-onboarding.
        workflow_id: Shared target Workflow ID (wf_<hex32>).
        output_profile_id: Optional shared Output Profile ID (prf_<hex32>).
        target_locale: Default target execution locale.
        locked_inputs: Shared manager-locked workflow inputs.
        assignee_input_keys: Shared ExpectedInput keys unlocked for assignee completion.
        result_visibility: Shared post-submission result visibility policy.
        hard_deadline_at: Shared absolute UTC deadline timestamp.
        relative_duration_seconds: Optional shared countdown timer in seconds from activation.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    recipients: Annotated[
        list[ExecutionAssignmentRecipientDTO],
        Field(min_length=1, max_length=500, description="Batch of 1 to 500 task assignment recipients"),
    ]
    invited_role: Annotated[
        LaxUserRole,
        Field(default=UserRole.MEMBER, description="Role granted upon auto-onboarding"),
    ] = UserRole.MEMBER
    workflow_id: Annotated[PrefixedUUID7, Field(description="Target Workflow ID (wf_<hex32>)")]
    output_profile_id: Annotated[
        PrefixedUUID7 | None,
        Field(default=None, description="Optional Output Profile ID (prf_<hex32>)"),
    ] = None
    target_locale: Annotated[
        LaxSystemLocale,
        Field(default=SystemLocale.FI, description="Default target execution locale"),
    ] = SystemLocale.FI
    locked_inputs: Annotated[
        WorkflowInputs,
        Field(default_factory=WorkflowInputs, description="Shared manager-locked workflow inputs"),
    ]
    assignee_input_keys: Annotated[
        list[str],
        Field(default_factory=list, description="Shared ExpectedInput keys unlocked for assignee completion"),
    ]
    result_visibility: Annotated[
        LaxAssignmentResultVisibility,
        Field(
            default=AssignmentResultVisibility.CONFIRMATION_ONLY,
            description="Post-submission result visibility policy",
        ),
    ] = AssignmentResultVisibility.CONFIRMATION_ONLY
    hard_deadline_at: Annotated[
        datetime,
        Field(strict=False, description="Shared absolute UTC deadline timestamp"),
    ]
    relative_duration_seconds: Annotated[
        int | None,
        Field(default=None, ge=60, description="Optional relative countdown timer in seconds from activation"),
    ] = None


class ExecutionAssignmentResponseDTO(BaseResponseDTO):
    """API response DTO representing a task assignment without exposing token_hash.

    Attributes:
        id: Canonical Task Assignment ID (tsk_<hex32>).
        batch_id: Optional cohort batch ID (tsk_<hex32>).
        organization_id: Owning Organization ID (org_<hex32>).
        assigned_email: Recipient email address.
        assigned_user_id: Bound User ID once activated (usr_<hex32>).
        invited_role: Role granted upon auto-onboarding.
        workflow_id: Target Workflow ID (wf_<hex32>).
        output_profile_id: Optional Output Profile ID (prf_<hex32>).
        target_locale: Target execution locale.
        locked_inputs: Immutable manager-locked workflow inputs.
        assignee_input_keys: ExpectedInput keys unlocked for assignee completion.
        draft_inputs: Server-side auto-saved draft inputs.
        status: Lifecycle status of the task assignment.
        email_delivery_status: Transactional email delivery status.
        result_visibility: Post-submission result visibility policy.
        hard_deadline_at: Absolute UTC deadline timestamp.
        relative_duration_seconds: Optional countdown timer in seconds from activation.
        activated_at: UTC activation timestamp.
        submitted_at: UTC submission timestamp.
        execution_id: Triggered ExecutionRecord ID (exe_<hex32>).
        created_by: Creator User ID (usr_<hex32>).
        created_at: UTC creation timestamp.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    id: Annotated[PrefixedUUID7, Field(description="Canonical Task Assignment ID (tsk_<hex32>)")]
    batch_id: Annotated[PrefixedUUID7 | None, Field(default=None, description="Optional cohort batch ID")] = None
    organization_id: Annotated[PrefixedUUID7, Field(description="Owning Organization ID (org_<hex32>)")]
    assigned_email: Annotated[EmailStr, Field(description="Recipient email address")]
    assigned_user_id: Annotated[PrefixedUUID7 | None, Field(default=None, description="Bound User ID")] = None
    invited_role: Annotated[LaxUserRole, Field(description="Role granted upon auto-onboarding")]
    workflow_id: Annotated[PrefixedUUID7, Field(description="Target Workflow ID (wf_<hex32>)")]
    output_profile_id: Annotated[PrefixedUUID7 | None, Field(default=None, description="Output Profile ID")] = None
    target_locale: Annotated[LaxSystemLocale, Field(description="Target execution locale")]
    locked_inputs: Annotated[WorkflowInputs, Field(description="Immutable manager-locked workflow inputs")]
    assignee_input_keys: Annotated[list[str], Field(description="Unlocked ExpectedInput keys")]
    draft_inputs: Annotated[WorkflowInputs, Field(description="Server-side auto-saved draft inputs")]
    status: Annotated[LaxAssignmentStatus, Field(description="Lifecycle status")]
    email_delivery_status: Annotated[
        LaxEmailDeliveryStatus,
        Field(default=EmailDeliveryStatus.PENDING, description="Transactional email delivery status"),
    ] = EmailDeliveryStatus.PENDING
    result_visibility: Annotated[LaxAssignmentResultVisibility, Field(description="Result visibility policy")]
    hard_deadline_at: Annotated[
        datetime,
        Field(strict=False, description="Absolute UTC deadline timestamp"),
    ]
    relative_duration_seconds: Annotated[
        int | None, Field(default=None, description="Relative duration in seconds")
    ] = None
    activated_at: Annotated[datetime | None, Field(default=None, description="UTC activation timestamp")] = None
    submitted_at: Annotated[datetime | None, Field(default=None, description="UTC submission timestamp")] = None
    execution_id: Annotated[PrefixedUUID7 | None, Field(default=None, description="Triggered ExecutionRecord ID")] = (
        None
    )
    created_by: Annotated[PrefixedUUID7, Field(description="Creator User ID (usr_<hex32>)")]
    created_at: Annotated[datetime, Field(description="UTC creation timestamp")]


class ExecutionAssignmentBatchResponseDTO(BaseResponseDTO):
    """Response payload for bulk-created workflow execution assignments.

    Attributes:
        batch_id: Shared cohort batch identifier (tsk_<hex32>).
        created_count: Total number of task assignments created.
        assignments: Materialized task assignment response DTOs.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    batch_id: Annotated[PrefixedUUID7, Field(description="Shared cohort batch identifier (tsk_<hex32>)")]
    created_count: Annotated[int, Field(ge=0, description="Total number of task assignments created")]
    assignments: Annotated[list[ExecutionAssignmentResponseDTO], Field(description="Created task assignments")]


class TransactionalEmailItemDTO(BaseDTO):
    """Outbound transactional email payload item with SecretStr-protected action URL.

    Attributes:
        entity_id: Associated Invitation or ExecutionAssignment Opaque Stripe ID.
        recipient_email: Recipient email address.
        recipient_name: Optional recipient display name.
        locale: Localized email template language.
        subject: Rendered email subject line.
        html_body: Rendered HTML email body.
        action_url: SecretStr-wrapped action link containing the raw single-use token.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    entity_id: Annotated[PrefixedUUID7, Field(description="Associated Invitation or ExecutionAssignment ID")]
    recipient_email: Annotated[EmailStr, Field(description="Recipient email address")]
    recipient_name: Annotated[str | None, Field(default=None, description="Optional recipient display name")] = None
    locale: Annotated[LaxSystemLocale, Field(default=SystemLocale.FI, description="Email template locale")] = (
        SystemLocale.FI
    )
    subject: Annotated[str, Field(min_length=1, description="Rendered email subject line")]
    html_body: Annotated[str, Field(min_length=1, description="Rendered HTML email body")]
    action_url: Annotated[
        SecretStr,
        Field(description="SecretStr-wrapped action URL preventing cleartext token exposure in logs"),
    ]


class TransactionalEmailBatchResultDTO(BaseDTO):
    """Summary of a batch transactional email dispatch operation.

    Attributes:
        sent_count: Number of emails successfully dispatched.
        failed_count: Number of emails that failed delivery.
        delivery_statuses: Per-entity delivery status map keyed by PrefixedUUID7.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    sent_count: Annotated[int, Field(ge=0, description="Number of emails successfully dispatched")]
    failed_count: Annotated[int, Field(ge=0, description="Number of emails that failed delivery")]
    delivery_statuses: Annotated[
        dict[PrefixedUUID7, EmailDeliveryStatus],
        Field(default_factory=dict, description="Per-entity delivery status map"),
    ]


class ExecutionAssignmentPreviewDTO(BaseResponseDTO):
    """Public pre-activation preview of a single-use workflow execution assignment.

    Attributes:
        id: Canonical Task Assignment ID (tsk_<hex32>).
        organization_id: Owning Organization ID (org_<hex32>).
        organization_name: Display name of the issuing organization.
        assigned_email_masked: Masked recipient email hint (e.g. 'j***@example.com').
        workflow_id: Target Workflow ID (wf_<hex32>).
        target_locale: Target execution locale.
        status: Current assignment status.
        hard_deadline_at: Absolute UTC deadline timestamp.
        relative_duration_seconds: Optional countdown timer in seconds from activation.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    id: Annotated[PrefixedUUID7, Field(description="Canonical Task Assignment ID (tsk_<hex32>)")]
    organization_id: Annotated[PrefixedUUID7, Field(description="Owning Organization ID (org_<hex32>)")]
    organization_name: Annotated[str, Field(min_length=1, description="Issuing organization display name")]
    assigned_email_masked: Annotated[str, Field(min_length=3, description="Masked recipient email hint")]
    workflow_id: Annotated[PrefixedUUID7, Field(description="Target Workflow ID (wf_<hex32>)")]
    target_locale: Annotated[LaxSystemLocale, Field(description="Target execution locale")]
    status: Annotated[LaxAssignmentStatus, Field(description="Current assignment status")]
    hard_deadline_at: Annotated[
        datetime,
        Field(strict=False, description="Absolute UTC deadline timestamp"),
    ]
    relative_duration_seconds: Annotated[
        int | None, Field(default=None, description="Relative duration in seconds")
    ] = None


class ExecutionAssignmentOnboardingRequestDTO(BaseDTO):
    """Payload for activating a single-use task assignment and auto-onboarding the assignee.

    Attributes:
        firebase_token: Verified Firebase ID token of the authenticated assignee.
        name: Optional display name for newly created user account.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    firebase_token: Annotated[
        str | None,
        Field(default=None, min_length=10, description="Verified Firebase ID token of the assignee"),
    ] = None
    name: Annotated[str | None, Field(default=None, min_length=1, max_length=120, description="Display name")] = None


class ExecutionAssignmentDraftDTO(BaseDTO):
    """Payload for auto-saving assignee draft inputs prior to final submission.

    Attributes:
        draft_inputs: Partial or complete assignee workflow inputs.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    draft_inputs: Annotated[WorkflowInputs, Field(description="Assignee draft workflow inputs")]


class ExecutionAssignmentSubmitDTO(BaseDTO):
    """Payload for submitting a single-use workflow execution assignment.

    Attributes:
        submitted_inputs: Final assignee workflow inputs to merge with manager locked_inputs.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    submitted_inputs: Annotated[WorkflowInputs, Field(description="Final assignee workflow inputs")]


# --- Tenant Secrets (BYOK Envelope Encryption) ---


class TenantSecretDTO(V2CoreBase):
    """Persisted tenant-scoped BYOK secret envelope record.

    Attributes:
        id: Canonical Tenant Secret Opaque Stripe ID (sec_<hex32>).
        organization_id: Owning Organization ID (org_<hex32>).
        scope: Capability scope ('llm_provider' or 'mcp_gateway').
        target_identifier: Provider enum value or MCP Gateway ID (sys_<hex32>).
        storage_mode: Cryptographic storage mode ('envelope_kms' or 'cloud_secret_manager').
        secret_manager_version_uri: Optional Cloud Secret Manager version URI.
        encrypted_dek: KMS-wrapped AES-256 Data Encryption Key bytes.
        ciphertext: AES-256-GCM encrypted secret payload bytes.
        nonce: 12-byte AES-256-GCM initialization vector.
        kek_version: Cloud KMS or local KEK version identifier used to wrap encrypted_dek.
        masked_hint: Redacted display hint (e.g. '...9f2a').
        updated_by: User ID who last rotated the secret (usr_<hex32>).
        updated_at: UTC timestamp of the most recent rotation.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    id: Annotated[
        PrefixedUUID7,
        Field(
            default_factory=lambda: generate_uuid7_opaque_id(EntityPrefix.TENANT_SECRET),
            description="Canonical Tenant Secret ID (sec_<hex32>)",
        ),
    ]
    organization_id: Annotated[PrefixedUUID7, Field(description="Owning Organization ID (org_<hex32>)")]
    scope: Annotated[LaxSecretScope, Field(description="Capability scope ('llm_provider' or 'mcp_gateway')")]
    target_identifier: Annotated[str, Field(min_length=1, max_length=128, description="Target provider or gateway ID")]
    storage_mode: Annotated[
        LaxSecretStorageMode,
        Field(default=SecretStorageMode.ENVELOPE_KMS, description="Cryptographic storage backend mode"),
    ] = SecretStorageMode.ENVELOPE_KMS
    secret_manager_version_uri: Annotated[
        str | None,
        Field(default=None, description="Optional Cloud Secret Manager version URI"),
    ] = None
    encrypted_dek: Annotated[bytes | None, Field(default=None, description="KMS-wrapped AES-256 DEK bytes")] = None
    ciphertext: Annotated[bytes | None, Field(default=None, description="AES-256-GCM encrypted secret bytes")] = None
    nonce: Annotated[bytes | None, Field(default=None, description="12-byte AES-256-GCM nonce")] = None
    kek_version: Annotated[
        str,
        Field(
            min_length=1,
            max_length=128,
            description="Cloud KMS or local KEK version identifier used to wrap encrypted_dek",
        ),
    ]
    masked_hint: Annotated[str, Field(min_length=1, max_length=32, description="Redacted display hint")]
    updated_by: Annotated[
        PrefixedUUID7,
        Field(default=SYSTEM_ROOT_USER_ID, description="User ID who last updated the secret (usr_<hex32>)"),
    ] = SYSTEM_ROOT_USER_ID
    updated_at: Annotated[
        datetime,
        Field(default_factory=lambda: datetime.now(timezone.utc), description="UTC timestamp of last update"),
    ]

    @field_validator("updated_at", mode="before")
    @classmethod
    def _parse_iso_datetime(cls, value: datetime | str) -> datetime:
        """Coerce ISO 8601 datetime strings into timezone-aware datetime instances.

        Args:
            value: Raw timestamp value (ISO string or datetime object).

        Returns:
            Parsed datetime instance.

        Raises:
            ValueError: If a string input is not a valid ISO 8601 timestamp.
        """
        if isinstance(value, str):
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        return value


class TenantSecretCreateDTO(BaseDTO):
    """Ingress payload for provisioning or rotating a tenant-scoped BYOK secret.

    Attributes:
        scope: Capability scope ('llm_provider' or 'mcp_gateway').
        target_identifier: Target LLMProvider value or MCP Gateway ID.
        plaintext_secret: Raw secret value wrapped in SecretStr so it never leaks in logs.
        storage_mode: Cryptographic storage mode (ENVELOPE_KMS or CLOUD_SECRET_MANAGER).
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    scope: Annotated[LaxSecretScope, Field(description="Capability scope ('llm_provider' or 'mcp_gateway')")]
    target_identifier: Annotated[str, Field(min_length=1, max_length=128, description="Target provider or gateway ID")]
    plaintext_secret: Annotated[SecretStr, Field(description="Raw secret value to encrypt at rest")]
    # Require explicit storage_mode selection at ingress with zero default fallback.
    storage_mode: Annotated[
        LaxSecretStorageMode,
        Field(description="Cryptographic storage mode (ENVELOPE_KMS or CLOUD_SECRET_MANAGER)."),
    ]


class TenantSecretResponseDTO(BaseResponseDTO):
    """Zero-leakage API response DTO for tenant secret metadata.

    Attributes:
        id: Canonical Tenant Secret ID (sec_<hex32>).
        organization_id: Owning Organization ID (org_<hex32>).
        scope: Capability scope ('llm_provider' or 'mcp_gateway').
        target_identifier: Target provider or gateway identifier.
        storage_mode: Cryptographic storage backend mode.
        configured: Always True when a persisted secret record exists.
        masked_hint: Redacted display hint (e.g. '...9f2a').
        kek_version: Cloud KMS or local KEK version identifier.
        updated_at: UTC timestamp of the most recent rotation.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    id: Annotated[PrefixedUUID7, Field(description="Canonical Tenant Secret ID (sec_<hex32>)")]
    organization_id: Annotated[PrefixedUUID7, Field(description="Owning Organization ID (org_<hex32>)")]
    scope: Annotated[LaxSecretScope, Field(description="Capability scope")]
    target_identifier: Annotated[str, Field(min_length=1, max_length=128, description="Target provider or gateway ID")]
    storage_mode: Annotated[LaxSecretStorageMode, Field(description="Cryptographic storage backend mode")]
    configured: Annotated[bool, Field(default=True, description="Whether the secret is configured")] = True
    masked_hint: Annotated[str, Field(min_length=1, max_length=32, description="Redacted display hint")]
    kek_version: Annotated[str, Field(min_length=1, max_length=128, description="Active KEK version identifier")]
    updated_at: Annotated[datetime, Field(description="UTC timestamp of most recent rotation")]


class ResolvedCredentialDTO(BaseDTO):
    """Ephemeral in-memory decrypted credential envelope for JIT execution injection.

    Attributes:
        organization_id: Owning Organization ID (org_<hex32>) or SYSTEM_ROOT.
        scope: Capability scope ('llm_provider' or 'mcp_gateway').
        target_identifier: Target provider or gateway identifier.
        secret_value: Decrypted secret wrapped in SecretStr to prevent logging exposure.
        is_tenant_byok: True when resolved from tenant_secrets, False when resolved from system fallback.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    organization_id: Annotated[str, Field(min_length=1, description="Organization ID or system scope")]
    scope: Annotated[LaxSecretScope, Field(description="Capability scope")]
    target_identifier: Annotated[str, Field(min_length=1, max_length=128, description="Target provider or gateway ID")]
    secret_value: Annotated[SecretStr, Field(description="Decrypted secret value wrapped in SecretStr")]
    is_tenant_byok: Annotated[bool, Field(default=True, description="Whether resolved from tenant BYOK storage")] = True
