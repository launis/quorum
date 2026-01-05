"""Authentication and Identity Management Models.

This module defines Pydantic models for user identity, role-based access control (RBAC),
organization management, and cryptographic token structures.
"""
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field

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


# --- Base Models ---


class Organization(BaseModel):
    """Represents a tenant or customer organization.

    Attributes:
        id (str): Unique Organization ID (e.g. 'nokia-v1').
        name (str): Display Name.
        created_at (Optional[str]): ISO Timestamp.
        is_active (bool): Subscription status.
        tier (str): Service Tier.
        contact_email (Optional[str]): Admin Contact.
    """

    id: Annotated[str, Field(description="Unique Organization ID (e.g. 'nokia-v1')")]
    name: Annotated[str, Field(description="Display Name")]
    created_at: Annotated[str | None, Field(description="ISO Timestamp")] = None
    is_active: Annotated[bool, Field(description="Subscription status")] = True
    tier: Annotated[str, Field(description="Service Tier")] = "standard"
    contact_email: Annotated[str | None, Field(description="Admin Contact")] = None


class UserBase(BaseModel):
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
    role: Annotated[UserRole, Field(description="Assigned permission role")] = UserRole.MEMBER
    organization_id: Annotated[str | None, Field(description="ID of the organization this user belongs to")] = None
    is_active: Annotated[bool, Field(description="Is the account active?")] = True

    model_config = ConfigDict(extra="ignore")


# --- Database / API Response Models ---


class User(UserBase):
    """Full User model representing a persisted user record.

    Attributes:
        uid (str): Unique ID (matches Firebase UID if used).
        created_at (str): ISO 8601 Timestamp.
        created_by (Optional[str]): UID of the creator.
    """

    uid: Annotated[str, Field(description="Unique ID (matches Firebase UID if used)")]
    created_at: Annotated[str, Field(description="ISO 8601 Timestamp")]
    created_by: Annotated[str | None, Field(description="UID of the creator")] = None


# --- Creation Models ---


class UserCreate(UserBase):
    """Payload for creating a new user.

    Attributes:
        password (Optional[str]): Initial password (min 6 chars).
        created_by (Optional[str]): UID of the admin creating this user.
    """

    password: Annotated[str | None, Field(min_length=6, description="Initial password")] = None
    created_by: Annotated[str | None, Field(description="UID of the admin creating this user")] = None


class OrganizationCreate(BaseModel):
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


class UserUpdate(BaseModel):
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


# --- Auth Fragments ---


class TokenData(BaseModel):
    """Structure for JWT token payload data.

    Attributes:
        uid (str): User ID.
        role (UserRole): User Role.
        organization_id (Optional[str]): Organization ID.
        email (Optional[str]): User email.
    """

    uid: str
    role: UserRole
    organization_id: str | None = None
    email: str | None = None
