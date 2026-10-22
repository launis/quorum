"""Protocol definitions for auth subpackage bounded context decoupling."""

from __future__ import annotations

from typing import Protocol

from backend_v2.models.auth import User, UserCreate


class UserCreatorProtocol(Protocol):
    """Protocol for decoupling organization-level user creation from UserService implementation."""

    async def __call__(
        self,
        creator_id: str,
        user_data: UserCreate,
        force_org_id: str | None = None,
    ) -> User:
        """Create a user within the specified organization."""
        ...
