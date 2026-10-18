"""Repository layer for Organization and User entities."""

from __future__ import annotations

from backend_v2.database.interfaces import IIdentityRepository
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.auth import Organization, User, UserUpdate

__all__ = [
    "OrganizationRepository",
    "UserRepository",
]


class OrganizationRepository:
    """Repository for Organization data access."""

    def __init__(self, repo: IIdentityRepository) -> None:
        """Initializes the Organization repository wrapper.

        Args:
            repo: The underlying identity repository interface.
        """
        self.repo = repo

    async def get_by_id(self, org_id: str) -> Organization | None:
        """Fetches an organization by its ID.

        Args:
            org_id: The ID of the organization to fetch.

        Returns:
            The Organization object if found, else None.
        """
        return await self.repo.get_organization(org_id)

    async def create(self, org: Organization) -> Organization:
        """Creates a new organization in the database.

        Args:
            org: The Organization object to create.

        Returns:
            The created Organization object.
        """
        await self.repo.create_organization(org)
        return org

    async def list_all(self) -> list[Organization]:
        """Lists all organizations.

        Returns:
            A list of all Organization objects.
        """
        return await self.repo.list_organizations()


class UserRepository:
    """Repository for User data access."""

    def __init__(self, repo: IIdentityRepository) -> None:
        """Initializes the User repository wrapper.

        Args:
            repo: The underlying identity repository interface.
        """
        self.repo = repo

    async def get_by_id(self, id: str) -> User | None:
        """Fetches a user by their ID.

        Args:
            id: The ID of the user to fetch.

        Returns:
            The User object if found, else None.
        """
        return await self.repo.get_user(id)

    async def get_by_email(self, email: str) -> User | None:
        """Fetches a user by their email address.

        Args:
            email: The email address of the user.

        Returns:
            The User object if found, else None.
        """
        return await self.repo.get_user_by_email(email)

    async def create(self, user: User) -> User:
        """Creates a new user in the database.

        Args:
            user: The User object to create.

        Returns:
            The created User object.

        Raises:
            AppException: If a user with the same ID already exists.
        """
        if await self.get_by_id(user.id):
            raise AppException(
                message=f"User with ID {user.id} already exists.",
                status_code=409,
                details={"error_code": ErrorCodes.CONFLICT_ERROR.value},
            )

        await self.repo.create_user(user)
        return user

    async def update(self, id: str, updates: UserUpdate) -> User | None:
        """Updates an existing user.

        Args:
            id: The ID of the user to update.
            updates: The update payload.

        Returns:
            The updated User object if successful, else None.
        """
        user = await self.get_by_id(id)

        if not user:
            return None

        await self.repo.update_user(id, updates)
        return await self.get_by_id(id)

    async def list_all(self) -> list[User]:
        """Lists all users.

        Returns:
            A list of all User objects.
        """
        return await self.repo.list_users()

    async def delete(self, id: str) -> bool:
        """Deletes a user by their ID.

        Args:
            id: The ID of the user to delete.

        Returns:
            True if deletion was successful, False otherwise.
        """
        return await self.repo.delete_user(id)

    async def get_by_organization(self, org_id: str) -> list[User]:
        """Fetches all users belonging to a specific organization.

        Args:
            org_id: The ID of the organization.

        Returns:
            A list of User objects.
        """
        return await self.repo.list_users(org_id)
