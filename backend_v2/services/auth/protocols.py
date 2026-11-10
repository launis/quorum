"""Protocol definitions for auth subpackage bounded context decoupling."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from backend_v2.models.auth import User, UserCreate

__all__ = ["UserCreatorProtocol"]


@runtime_checkable
class UserCreatorProtocol(Protocol):
    """Protocol for decoupling organization-level user creation from UserService implementation."""

    async def __call__(
        self,
        creator_id: str,
        user_data: UserCreate,
        force_org_id: str | None = None,
    ) -> User:
        """Create a user within the specified organization.

        Args:
            creator_id: Canonical Opaque Stripe ID of the initiating user.
            user_data: Validated user creation payload.
            force_org_id: Optional canonical organization ID overriding standard tenant derivation.

        Returns:
            Persisted User domain model instance.

        Raises:
            AppException: With ErrorCodes.RESOURCE_NOT_FOUND if creator does not exist,
                ErrorCodes.VALIDATION_FAILED if target organization does not exist, or
                ErrorCodes.INTERNAL_SERVER_ERROR if upstream identity provisioning fails.
            PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if RBAC role hierarchy
                or multi-tenant isolation rules are violated.
        """
        ...
