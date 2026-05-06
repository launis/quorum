"""Authentication and Identity Management Models.

This module defines Pydantic models for user identity, role-based access control (RBAC),
organization management, and cryptographic token structures.
"""

import logging
import uuid
from datetime import datetime
from enum import Enum
from typing import Annotated, Any, Literal

from pydantic import ConfigDict, EmailStr, Field, field_validator

from backend_v2.exceptions import ErrorCodes
from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.dtos.base import BaseDTO, BaseResponseDTO

logger = logging.getLogger(__name__)

# --- Enums ---


class UserRole(str, Enum):
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
    MEMBER = "MEMBER"  # Standard User (Audit Runner) - Was TESTER
    VIEWER = "VIEWER"  # Read-Only Stakeholder


class SubscriptionStatus(str, Enum):
    """SaaS Subscription Status."""

    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    TRIAL = "trial"


class SystemOrganizations(str, Enum):
    """Special predefined system organizations."""

    ROOT_SYSTEM = "org_system000000"


LaxUserRole = Annotated[UserRole, Field(strict=False)]
LaxSubscriptionStatus = Annotated[SubscriptionStatus, Field(strict=False)]

# --- Base Models ---


class Organization(V2CoreBase):
    """Represents a tenant or customer organization.

    Attributes:
        id (str): Unique Organization ID (e.g. 'nokia-v1').
        name (str): Display Name.
        created_at (Optional[str]): ISO Timestamp.
        is_active (bool): Subscription status.
        tier (str): Service Tier.
        contact_email (Optional[str]): Admin Contact.
        billing_id (Optional[str]): External Billing ID (Stripe/etc).
        subscription_status (SubscriptionStatus): Current billing status.
        quota_limit (int): Monthly API call quota.
    """

    id: Annotated[
        str,
        Field(
            default_factory=lambda: f"org_{uuid.uuid4().hex}",
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

    # Billing & SaaS Fields (Phase 4)
    billing_id: Annotated[str | None, Field(description="External Billing ID (Stripe/etc)")] = None
    subscription_status: Annotated[LaxSubscriptionStatus, Field(description="Current billing status")]
    quota_limit: Annotated[float, Field(ge=0.0, description="Monthly API call quota (USD)")]
    tpm_limit: Annotated[int, Field(ge=1000, description="Tokens Per Minute Limit")]
    rpm_limit: Annotated[int, Field(ge=1, description="Requests Per Minute Limit")]

    @field_validator("created_at", mode="before")
    @classmethod
    def parse_datetime(cls, v: Any) -> Any:
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v

    @field_validator("id", "name")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            msg = "Field cannot be empty or whitespace only."
            logger.error("[AuthModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise ValueError(msg)
        return v.strip()

    @field_validator("contact_email", "billing_id")
    @classmethod
    def validate_non_empty_optional(cls, v: str | None) -> str | None:
        if v is not None and (not v or not v.strip()):
            msg = "Field cannot be empty or whitespace only."
            logger.error("[AuthModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise ValueError(msg)
        return v.strip() if v else v


class UserBase(V2CoreBase):
    """Base Pydantic model for User data, distinguishing shared fields.

    Attributes:
        email (EmailStr): User email address.
        display_name (Optional[str]): User display name.
        role (UserRole): Assigned permission role.
        organization_id (Optional[str]): ID of the organization this user belongs to.
        is_active (bool): Is the account active?
    """

    email: Annotated[EmailStr, Field(description="User email address")]
    display_name: Annotated[str | None, Field(description="User display name")] = None
    role: Annotated[LaxUserRole, Field(description="Assigned permission role")]
    organization_id: Annotated[str | None, Field(description="ID of the organization this user belongs to")] = None
    is_active: Annotated[bool, Field(description="Is the account active?")]
    language: Annotated[Literal["fi", "en", "sv"], Field(description="Preferred UI language")]
    theme_mode: Annotated[Literal["system", "light", "dark"], Field(description="Preferred Theme Mode")]

    @field_validator("display_name", "organization_id")
    @classmethod
    def validate_non_empty_optional(cls, v: str | None) -> str | None:
        if v is not None and (not v or not v.strip()):
            msg = "Field cannot be empty or whitespace only."
            logger.error("[AuthModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise ValueError(msg)
        return v.strip() if v else v


# --- Database / API Response Models ---


class User(UserBase):
    """Full User model representing a persisted user record.

    Attributes:
        id (str): Unique ID (matches Firebase UID if used).
        slug (Optional[str]): Legacy human-readable identifier.
        created_at (str): ISO 8601 Timestamp.
        created_by (Optional[str]): UID of the creator.
    """

    id: Annotated[
        str,
        Field(
            default_factory=lambda: f"usr_{uuid.uuid4().hex}",
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
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v

    @field_validator("id")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            msg = "Field cannot be empty or whitespace only."
            logger.error("[AuthModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise ValueError(msg)
        return v.strip()

    @field_validator("created_by")
    @classmethod
    def validate_non_empty_optional(cls, v: str | None) -> str | None:
        if v is not None and (not v or not v.strip()):
            msg = "Field cannot be empty or whitespace only."
            logger.error("[AuthModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise ValueError(msg)
        return v.strip() if v else v


class UserAdminView(UserBase):
    """Extended User model for admin views with statistics and raw datetime objects.

    Attributes:
        id (str): Unique ID.
        slug (Optional[str]): Legacy human-readable identifier.
        created_at (datetime): Timestamp as datetime object.
        created_by (Optional[str]): UID of the creator.
        last_login_at (Optional[datetime]): Timestamp of last login.
        execution_count (int): Total number of executions/audits run.
    """

    id: str
    slug: str | None = None
    created_at: datetime
    created_by: str | None = None
    last_login_at: datetime | None = None
    execution_count: int = 0

    model_config = ConfigDict(from_attributes=True, extra="forbid", frozen=True, strict=True)


# --- Creation Models ---


class UserCreate(UserBase):
    """Payload for creating a new user.

    Attributes:
        password (Optional[str]): Initial password (min 6 chars).
        created_by (Optional[str]): UID of the admin creating this user.
    """

    password: Annotated[str | None, Field(min_length=6, description="Initial password")] = None
    created_by: Annotated[str | None, Field(description="UID of the admin creating this user")] = None


class OrganizationCreate(BaseDTO):
    """Payload for creating a new organization.

    Attributes:
        name (str): Organization display name.
        admin_email (EmailStr): Email for the initial admin user.
        admin_password (str): Password for the initial admin user.
        admin_name (str): Display name for the initial admin user.
    """

    name: str
    admin_email: EmailStr
    admin_password: str
    admin_name: str
    tpm_limit: int
    rpm_limit: int

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    @field_validator("name", "admin_password", "admin_name")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            msg = "Field cannot be empty or whitespace only."
            logger.error("[AuthModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise ValueError(msg)
        return v.strip()


class UserUpdate(BaseDTO):
    """Payload for updating an existing user.

    Attributes:
        display_name (Optional[str]): New display name.
        role (Optional[UserRole]): New role assignment.
        is_active (Optional[bool]): New active status.
        password (Optional[str]): New password (only for admin resets).
    """

    display_name: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None
    password: str | None = None  # Only for admin resets
    language: str | None = None
    theme_mode: str | None = None
    organization_id: str | None = None

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")


# --- Auth Fragments ---


class TokenData(V2CoreBase):
    """Structure for JWT token payload data.

    Attributes:
        id (str): User ID.
        role (UserRole): User Role.
        organization_id (Optional[str]): Organization ID.
        email (Optional[str]): User email.
    """

    id: str
    role: LaxUserRole
    organization_id: str | None = None
    email: str | None = None

    @field_validator("id")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            msg = "Field cannot be empty or whitespace only."
            logger.error("[AuthModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise ValueError(msg)
        return v.strip()

    @field_validator("organization_id", "email")
    @classmethod
    def validate_non_empty_optional(cls, v: str | None) -> str | None:
        if v is not None and (not v or not v.strip()):
            msg = "Field cannot be empty or whitespace only."
            logger.error("[AuthModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise ValueError(msg)
        return v.strip() if v else v


class UserDeleteResponse(BaseResponseDTO):
    """Payload response for deleting a user."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    status: str
    id: str


class TokenPayload(BaseDTO):
    """Payload for token verification."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    token: str


class LoginResponse(BaseResponseDTO):
    """Response model for successful login."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    user: User
    token_valid: bool
    debug_msg: str | None = None


class ImpersonationRequest(BaseDTO):
    """Request payload for impersonation."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    target_id: str


class ImpersonationResponse(BaseResponseDTO):
    """Response containing the impersonation token."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    access_token: str
    token_type: str = "bearer"


class OrganizationDeleteResponse(BaseResponseDTO):
    """Payload response for deleting an organization."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    status: str
    deleted_id: str
