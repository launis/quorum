from enum import Enum
from typing import Optional, List, Annotated
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from datetime import datetime

# --- Enums ---

class UserRole(str, Enum):
    ROOT = "ROOT"       # System Owner / Platform Admin
    ADMIN = "ADMIN"     # Organization Admin (User Management)
    MANAGER = "MANAGER" # Workflow/Process Lead
    MEMBER = "MEMBER"   # Standard User (Audit Runner) - Was TESTER
    VIEWER = "VIEWER"   # Read-Only Stakeholder

# --- Base Models ---

class Organization(BaseModel):
    id: Annotated[str, Field(description="Unique Organization ID (e.g. 'nokia-v1')")]
    name: Annotated[str, Field(description="Display Name")]
    created_at: Annotated[Optional[str], Field(description="ISO Timestamp")] = None
    is_active: Annotated[bool, Field(description="Subscription status")] = True
    tier: Annotated[str, Field(description="Service Tier")] = "standard"
    contact_email: Annotated[Optional[str], Field(description="Admin Contact")] = None

class UserBase(BaseModel):
    email: Annotated[EmailStr, Field(description="User email address")]
    display_name: Annotated[Optional[str], Field(description="User display name")] = None
    role: Annotated[UserRole, Field(description="Assigned permission role")] = UserRole.MEMBER
    organization_id: Annotated[Optional[str], Field(description="ID of the organization this user belongs to")] = None
    is_active: Annotated[bool, Field(description="Is the account active?")] = True
    
    model_config = ConfigDict(extra='ignore')

# --- Database / API Response Models ---

class User(UserBase):
    uid: Annotated[str, Field(description="Unique ID (matches Firebase UID if used)")]
    created_at: Annotated[str, Field(description="ISO 8601 Timestamp")]
    created_by: Annotated[Optional[str], Field(description="UID of the creator")] = None

# --- Creation Models ---

class UserCreate(UserBase):
    """
    Payload for creating a new user. 
    organization_id is optional: if missing, inherits from creator.
    """
    password: Annotated[Optional[str], Field(min_length=6, description="Initial password")] = None
    created_by: Annotated[Optional[str], Field(description="UID of the admin creating this user")] = None

class OrganizationCreate(BaseModel):
    name: str
    admin_email: EmailStr
    admin_password: str
    admin_name: str

class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None # Only for admin resets

# --- Auth Fragments ---

class TokenData(BaseModel):
    uid: str
    role: UserRole
    organization_id: Optional[str] = None
    email: Optional[str] = None
