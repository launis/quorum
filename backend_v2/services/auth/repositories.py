"""Repository wrappers for Organization and User identity persistence."""

from __future__ import annotations

import logging

from backend_v2.database.interfaces import IIdentityRepository
from backend_v2.exceptions import ConflictError, ErrorCodes
from backend_v2.models.auth import Organization, OrganizationUpdateDTO, User, UserUpdate

logger = logging.getLogger(__name__)

__all__ = [
    "OrganizationRepository",
    "UserRepository",
]


class OrganizationRepository:
    """Repository wrapper for Organization identity persistence operations.

    Attributes:
        repo: Underlying hexagonal identity repository protocol implementation.
    """

    def __init__(self, repo: IIdentityRepository) -> None:
        """Initialize the OrganizationRepository wrapper.

        Args:
            repo: Underlying hexagonal identity repository protocol implementation.
        """
        self.repo = repo

    async def get_by_id(self, org_id: str) -> Organization | None:
        """Fetch an organization by its canonical identifier.

        Args:
            org_id: Canonical Organization identifier (org_<hex32>).

        Returns:
            Validated Organization domain model if found, otherwise None.

        Raises:
            AppException: With ErrorCodes.STORAGE_ACCESS_FAILED or ErrorCodes.VALIDATION_FAILED
                if persistence lookup or model hydration fails.
        """
        return await self.repo.get_organization(org_id)

    async def create(self, org: Organization) -> Organization:
        """Create a new organization after verifying primary identifier uniqueness.

        Args:
            org: Validated Organization domain model to persist.

        Returns:
            Created Organization domain model.

        Raises:
            ConflictError: With ErrorCodes.CONFLICT_ERROR (409) if an organization with the
                same canonical ID already exists.
            AppException: With ErrorCodes.STORAGE_ACCESS_FAILED if persistence fails.
        """
        if await self.get_by_id(org.id) is not None:
            logger.error(
                "[OrganizationRepository] %s: Organization with ID %s already exists.",
                ErrorCodes.CONFLICT_ERROR.name,
                org.id,
                exc_info=True,
            )
            raise ConflictError(
                message=f"Organization with ID {org.id} already exists.",
                details={"error_code": ErrorCodes.CONFLICT_ERROR.value},
            )

        await self.repo.create_organization(org)
        return org

    async def update(self, org_id: str, updates: OrganizationUpdateDTO) -> bool:
        """Update an existing organization record in-place.

        Args:
            org_id: Canonical Organization identifier (org_<hex32>) to update.
            updates: Validated partial update payload.

        Returns:
            True if the organization existed and was updated, otherwise False.

        Raises:
            AppException: With ErrorCodes.STORAGE_ACCESS_FAILED if persistence fails.
        """
        return await self.repo.update_organization(org_id, updates)

    async def delete(self, org_id: str) -> bool:
        """Delete an organization record by its canonical identifier.

        Args:
            org_id: Canonical Organization identifier (org_<hex32>) to delete.

        Returns:
            True if the organization existed and was deleted, otherwise False.

        Raises:
            AppException: With ErrorCodes.STORAGE_ACCESS_FAILED if persistence fails.
        """
        return await self.repo.delete_organization(org_id)

    async def list_all(self) -> list[Organization]:
        """List all persisted organizations.

        Returns:
            List of validated Organization domain models.

        Raises:
            AppException: With ErrorCodes.STORAGE_ACCESS_FAILED or ErrorCodes.VALIDATION_FAILED
                if persistence query or model hydration fails.
        """
        return await self.repo.list_organizations()


class UserRepository:
    """Repository wrapper for User identity persistence operations.

    Attributes:
        repo: Underlying hexagonal identity repository protocol implementation.
    """

    def __init__(self, repo: IIdentityRepository) -> None:
        """Initialize the UserRepository wrapper.

        Args:
            repo: Underlying hexagonal identity repository protocol implementation.
        """
        self.repo = repo

    async def get_by_id(self, id: str) -> User | None:
        """Fetch a user by their canonical identifier.

        Args:
            id: Canonical User identifier (usr_<hex32>).

        Returns:
            Validated User domain model if found, otherwise None.

        Raises:
            AppException: With ErrorCodes.STORAGE_ACCESS_FAILED or ErrorCodes.VALIDATION_FAILED
                if persistence lookup or model hydration fails.
        """
        return await self.repo.get_user(id)

    async def get_by_email(self, email: str) -> User | None:
        """Fetch a user by their email address.

        Args:
            email: Normalized user email address.

        Returns:
            Validated User domain model if found, otherwise None.

        Raises:
            AppException: With ErrorCodes.STORAGE_ACCESS_FAILED or ErrorCodes.VALIDATION_FAILED
                if persistence query or model hydration fails.
        """
        return await self.repo.get_user_by_email(email)

    async def get_by_firebase_uid(self, firebase_uid: str) -> User | None:
        """Fetch an active, non-deleted user by their external Firebase Auth UID.

        Args:
            firebase_uid: External Firebase Authentication UID.

        Returns:
            Matching User domain model if found and not soft-deleted, otherwise None.

        Raises:
            AppException: With ErrorCodes.STORAGE_ACCESS_FAILED or ErrorCodes.VALIDATION_FAILED
                if persistence query or model hydration fails.
        """
        users = await self.repo.list_users()
        for user in users:
            if user.firebase_uid == firebase_uid and user.deleted_at is None:
                return user
        return None

    async def create(self, user: User) -> User:
        """Create a new user after verifying primary identifier uniqueness.

        Args:
            user: Validated User domain model to persist.

        Returns:
            Created User domain model.

        Raises:
            ConflictError: With ErrorCodes.CONFLICT_ERROR (409) if a user with the same
                canonical ID already exists.
            AppException: With ErrorCodes.STORAGE_ACCESS_FAILED if persistence fails.
        """
        if await self.get_by_id(user.id) is not None:
            logger.error(
                "[UserRepository] %s: User with ID %s already exists.",
                ErrorCodes.CONFLICT_ERROR.name,
                user.id,
                exc_info=True,
            )
            raise ConflictError(
                message=f"User with ID {user.id} already exists.",
                details={"error_code": ErrorCodes.CONFLICT_ERROR.value},
            )

        await self.repo.create_user(user)
        return user

    async def update(self, id: str, updates: UserUpdate) -> User | None:
        """Update an existing user in-place and return the refreshed domain model.

        Args:
            id: Canonical User identifier (usr_<hex32>) to update.
            updates: Validated partial user update payload.

        Returns:
            Updated User domain model if found, otherwise None.

        Raises:
            AppException: With ErrorCodes.STORAGE_ACCESS_FAILED or ErrorCodes.VALIDATION_FAILED
                if persistence update or roundtrip hydration fails.
        """
        user = await self.get_by_id(id)
        if user is None:
            return None

        await self.repo.update_user(id, updates)
        return await self.get_by_id(id)

    async def list_all(self) -> list[User]:
        """List all persisted users across organizations.

        Returns:
            List of validated User domain models.

        Raises:
            AppException: With ErrorCodes.STORAGE_ACCESS_FAILED or ErrorCodes.VALIDATION_FAILED
                if persistence query or model hydration fails.
        """
        return await self.repo.list_users()

    async def delete(self, id: str) -> bool:
        """Delete a user record by their canonical identifier.

        Args:
            id: Canonical User identifier (usr_<hex32>) to delete.

        Returns:
            True if the user existed and was deleted, otherwise False.

        Raises:
            AppException: With ErrorCodes.STORAGE_ACCESS_FAILED if persistence fails.
        """
        return await self.repo.delete_user(id)

    async def get_by_organization(self, org_id: str) -> list[User]:
        """Fetch all users belonging to a specific organization.

        Args:
            org_id: Canonical Organization identifier (org_<hex32>).

        Returns:
            List of validated User domain models scoped to the organization.

        Raises:
            AppException: With ErrorCodes.STORAGE_ACCESS_FAILED or ErrorCodes.VALIDATION_FAILED
                if persistence query or model hydration fails.
        """
        return await self.repo.list_users(org_id)
