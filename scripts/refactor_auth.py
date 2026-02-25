import re

with open("backend/services/auth.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Imports
content = content.replace("from tinydb import Query", "")
content = content.replace("from backend.database.wrapper import AbstractDatabase, AbstractTable", "from backend.database.repository import AbstractWorkflowRepository")

# 2. OrganizationRepository
org_repo_old = """class OrganizationRepository:
    \"\"\"Repository for Organization data access.\"\"\"

    def __init__(self, db_client: AbstractDatabase):
        \"\"\"Initialize OrganizationRepository.\"\"\"
        self.table: AbstractTable = db_client.table("organizations")

    def get_by_id(self, org_id: str) -> Organization | None:
        \"\"\"Retrieves an organization by ID.

        Args:
            org_id (str): Organization ID.

        Returns:
            Optional[Organization]: The organization object.
        \"\"\"
        # TinyDB simulation for get
        result = self.table.get(lambda x: x.get("id") == org_id)
        if result:
            # Robustness: existing data might miss 'tier'
            if "tier" not in result:
                result["tier"] = "standard"
            return Organization(**result)
        return None

    def create(self, org: Organization) -> Organization:
        \"\"\"Persists a new organization.

        Args:
            org (Organization): The object to save.

        Returns:
            Organization: The saved object.
        \"\"\"
        self.table.insert(org.model_dump(mode="json"))
        return org

    def list_all(self) -> list[Organization]:
        \"\"\"List all organizations.\"\"\"
        results = []
        for o in self.table.all():
            if "tier" not in o:
                o["tier"] = "standard"
            results.append(Organization(**o))
        return results"""

org_repo_new = """class OrganizationRepository:
    \"\"\"Repository for Organization data access.\"\"\"

    def __init__(self, repo: AbstractWorkflowRepository):
        self.repo = repo

    async def get_by_id(self, org_id: str) -> Organization | None:
        data = await self.repo.get_organization(org_id)
        if data:
            if "tier" not in data:
                data["tier"] = "standard"
            return Organization(**data)
        return None

    async def create(self, org: Organization) -> Organization:
        await self.repo.create_organization(org.model_dump(mode="json"))
        return org

    async def list_all(self) -> list[Organization]:
        results = []
        for o in await self.repo.list_organizations():
            if "tier" not in o:
                o["tier"] = "standard"
            results.append(Organization(**o))
        return results"""
content = content.replace(org_repo_old, org_repo_new)

# 3. UserRepository
user_repo_old = """class UserRepository:
    \"\"\"Handles persistence of User metadata (roles, display names, hierarchy).

    Persists to the underlying database (TinyDB or Firestore).
    \"\"\"

    def __init__(self, db_client: AbstractDatabase):
        \"\"\"Initialize UserRepository.\"\"\"
        self.table: AbstractTable = db_client.table("users")

    def get_by_id(self, id: str) -> User | None:
        \"\"\"Retrieves user by ID.

        Args:
            id (str): User ID.

        Returns:
            Optional[User]: The user object.
        \"\"\"
        # TinyDB / Memory filter approach
        # FIX: Use explicit Query object for robustness
        UserQuery = Query()
        result = self.table.get(UserQuery.id == id)
        if result:
            return User(**result)
        return None

    def get_by_email(self, email: str) -> User | None:
        \"\"\"Retrieve user by email.\"\"\"
        # FIX: Use explicit Query object for robustness
        UserQuery = Query()
        result = self.table.get(UserQuery.email == email)
        if result:
            return User(**result)
        return None

    def create(self, user: User) -> User:
        \"\"\"Create new user sync in DB.

        Raises:
            AppException: If collision.
        \"\"\"
        # Enforce unique email/slug/uid if necessary here, but usually repo layer just writes.
        # Minimal collision check on ID:
        if self.get_by_id(user.id):
            raise AppException(f"User with ID {user.id} already exists.", 409)

        # TinyDB expects str/dict
        self.table.insert(user.model_dump(mode="json"))
        return user

    def update(self, id: str, updates: UserUpdate) -> User | None:
        \"\"\"Updates user in DB. Only applying fields that are set.

        Returns None if not found.
        \"\"\"
        user = self.get_by_id(id)
        if not user:
            return None

        update_data = updates.model_dump(exclude_unset=True)
        if not update_data:
            return user

        # Update in DB
        self.table.update(update_data, lambda x: x.get("id") == id)

        # Return updated
        return self.get_by_id(id)

    def list_all(self) -> list[User]:
        \"\"\"List all users.\"\"\"
        raw_users = self.table.all()
        return [User(**u) for u in raw_users]

    def delete(self, id: str) -> bool:
        \"\"\"Hard delete user from DB.\"\"\"
        # TinyDB remove
        ids = self.table.remove(Query().id == id)
        return len(ids) > 0

    def get_by_organization(self, org_id: str) -> list[User]:
        \"\"\"Retrieve all users associated with an organization ID.\"\"\"
        results = self.table.search(Query().organization_id == org_id)
        return [User(**u) for u in results]"""

user_repo_new = """class UserRepository:
    def __init__(self, repo: AbstractWorkflowRepository):
        self.repo = repo

    async def get_by_id(self, id: str) -> User | None:
        data = await self.repo.get_user(id)
        return User(**data) if data else None

    async def get_by_email(self, email: str) -> User | None:
        data = await self.repo.get_user_by_email(email)
        return User(**data) if data else None

    async def create(self, user: User) -> User:
        if await self.get_by_id(user.id):
            raise AppException(f"User with ID {user.id} already exists.", 409)
        await self.repo.create_user(user.model_dump(mode="json"))
        return user

    async def update(self, id: str, updates: UserUpdate) -> User | None:
        user = await self.get_by_id(id)
        if not user:
            return None
        update_data = updates.model_dump(exclude_unset=True)
        if update_data:
            await self.repo.update_user(id, update_data)
        return await self.get_by_id(id)

    async def list_all(self) -> list[User]:
        return [User(**u) for u in await self.repo.list_users()]

    async def delete(self, id: str) -> bool:
        return await self.repo.delete_user(id)

    async def get_by_organization(self, org_id: str) -> list[User]:
        return [User(**u) for u in await self.repo.list_users(org_id)]"""
content = content.replace(user_repo_old, user_repo_new)

# 4. AuthService init
content = content.replace("def __init__(self, db_client: AbstractDatabase, use_firebase: bool = False, audit_service: Any = None):", "def __init__(self, repo: AbstractWorkflowRepository, use_firebase: bool = False, audit_service: Any = None):")
content = content.replace("self.repo = UserRepository(db_client)", "self.repo = UserRepository(repo)")
content = content.replace("self.org_repo = OrganizationRepository(db_client)", "self.org_repo = OrganizationRepository(repo)")

# 5. AuthService verify_token => async
content = content.replace("def verify_token(self, token: str) -> TokenData:", "async def verify_token(self, token: str) -> TokenData:")
content = content.replace("user = self.repo.get_by_id(id)", "user = await self.repo.get_by_id(id)")

# 6. create_organization calls
content = content.replace("creator = self.repo.get_by_id(creator_id)", "creator = await self.repo.get_by_id(creator_id)")
content = content.replace("self.org_repo.create(new_org)", "await self.org_repo.create(new_org)")

# 7. _create_user_internal
content = content.replace("org_exists = self.org_repo.get_by_id(target_org_id)", "org_exists = await self.org_repo.get_by_id(target_org_id)")
content = content.replace("saved_user = self.repo.create(new_user)", "saved_user = await self.repo.create(new_user)")

# 8. _count_org_admins
content = content.replace("def _count_org_admins(self, org_id: str) -> int:", "async def _count_org_admins(self, org_id: str) -> int:")
content = content.replace("all_users = self.repo.list_all()", "all_users = await self.repo.list_all()")

# 9. get_users_by_organization
content = content.replace("await asyncio.to_thread(self.repo.get_by_organization, organization_id)", "await self.repo.get_by_organization(organization_id)")

# 10. delete_user calls
content = content.replace("initiator = await asyncio.to_thread(self.repo.get_by_id, initiator_id)", "initiator = await self.repo.get_by_id(initiator_id)")
content = content.replace("target = await asyncio.to_thread(self.repo.get_by_id, target_id)", "target = await self.repo.get_by_id(target_id)")
content = content.replace("admin_count = await asyncio.to_thread(self._count_org_admins, target.organization_id)", "admin_count = await self._count_org_admins(target.organization_id)")
content = content.replace("await asyncio.to_thread(self.repo.delete, target_id)", "await self.repo.delete(target_id)")

# 11. delete_organization
content = content.replace("all_users = await asyncio.to_thread(self.repo.list_all)", "all_users = await self.repo.list_all()")
content = content.replace("await asyncio.to_thread(self.repo.delete, user.id)", "await self.repo.delete(user.id)")

def_delete_org = """        def _delete_org() -> None:
            self.org_repo.table.remove(Query().id == target_org_id)

        await asyncio.to_thread(_delete_org)"""
new_delete_org = "        await self.repo.delete_organization(target_org_id)"
content = content.replace(def_delete_org, new_delete_org)

# 12. update_user
content = content.replace("initiator = self.repo.get_by_id(initiator_id)", "initiator = await self.repo.get_by_id(initiator_id)")
content = content.replace("target = self.repo.get_by_id(target_id)", "target = await self.repo.get_by_id(target_id)")
content = content.replace("admin_count = self._count_org_admins(target.organization_id)", "admin_count = await self._count_org_admins(target.organization_id)")
content = content.replace("updated_user = self.repo.update(target_id, updates)", "updated_user = await self.repo.update(target_id, updates)")

# 13. update_user_role
content = content.replace("count = await asyncio.to_thread(self._count_org_admins, target.organization_id)", "count = await self._count_org_admins(target.organization_id)")
content = content.replace("updated = self.repo.update(target_id, UserUpdate(role=new_role))", "updated = await self.repo.update(target_id, UserUpdate(role=new_role))")

# 14. ensure_root_user => async
content = content.replace('def ensure_root_user(self, email: str = "root@example.com") -> User:', 'async def ensure_root_user(self, email: str = "root@example.com") -> User:')
content = content.replace("if not self.org_repo.get_by_id(", "if not await self.org_repo.get_by_id(")
content = content.replace("self.org_repo.create(", "await self.org_repo.create(")
content = content.replace("root = self.repo.get_by_id(", "root = await self.repo.get_by_id(")
content = content.replace('self.repo.update(root.id, UserUpdate(organization_id="436d84de-c526-43b7-93ef-634912be0d2f"))', 'await self.repo.update(root.id, UserUpdate(organization_id="436d84de-c526-43b7-93ef-634912be0d2f"))')

with open("backend/services/auth.py", "w", encoding="utf-8") as f:
    f.write(content)
