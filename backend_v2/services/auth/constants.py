"""Authentication and Identity constants."""

from __future__ import annotations

# Secure Secret for Local Tokens (Impersonation)
# In production, this MUST be set via environment variable.
JWT_SECRET = "cognitive-quorum-internal-secret-change-me"
JWT_ALGORITHM = "HS256"

# Constants for System Root Entities
SYSTEM_ROOT_USER_ID = "usr_0195f3a0000070008000a3fd6b3d77c7"
LEGACY_SYSTEM_ROOT_USER_ID = "10fb2f60-5ee1-419f-a16c-b5cfdfc5f55b"
LEGACY_SYSTEM_ORG_ID = "436d84de-c526-43b7-93ef-634912be0d2f"
LEGACY_ROOT_MASTER_ID = "root_master"

__all__ = [
    "JWT_ALGORITHM",
    "JWT_SECRET",
    "LEGACY_ROOT_MASTER_ID",
    "LEGACY_SYSTEM_ORG_ID",
    "LEGACY_SYSTEM_ROOT_USER_ID",
    "SYSTEM_ROOT_USER_ID",
]
