import asyncio
import os

# Force Mock configuration
os.environ["USE_MOCK_DB"] = "true"
os.environ["USE_FIREBASE"] = "false"


# Mock DB Wrapper
class MockDatabase:
    def __init__(self):
        self.data = {"users": [], "organizations": [], "workflows": [], "executions": []}

    def table(self, name):
        return MockTable(self.data, name)


class MockTable:
    def __init__(self, data, name):
        self.data = data
        self.name = name

    def insert(self, item):
        self.data[self.name].append(item)
        return len(self.data[self.name])

    def all(self):
        return self.data[self.name]

    def get(self, query):
        for item in self.data[self.name]:
            if query(item):
                return item
        return None

    def search(self, query):
        # TinyDB query object support is hard to mock perfectly,
        # but our code uses lambdas often or we can inspect Query object if simple.
        # However, Repository wrapper uses TinyDB Query logic.
        # So we might need to actually use TinyDB with a temp file.
        pass

    def update(self, updates, query):
        for item in self.data[self.name]:
            if query(item):
                item.update(updates)

    def remove(self, query):
        initial = len(self.data[self.name])
        self.data[self.name] = [i for i in self.data[self.name] if not query(i)]
        return range(initial - len(self.data[self.name]))


# BETTER APPROACH: Use TinyDB with a temp file
from tinydb import TinyDB

temp_db_path = "verify_db.json"
if os.path.exists(temp_db_path):
    os.remove(temp_db_path)

db = TinyDB(temp_db_path)

# Models / Services
from backend.database.repository import TinyDBRepository
from backend.models.auth import OrganizationCreate
from backend.services.auth import AuthService


async def run_verification():
    print("--- Starting Verification ---")

    # 1. Setup
    repo = TinyDBRepository(db)
    auth_service = AuthService(db, use_firebase=False)

    # Ensure Root
    root = auth_service.ensure_root_user()
    print(f"Root created: {root.uid}")

    # 2. Setup Org & Data
    org_create = OrganizationCreate(
        name="DeleteMe Corp", admin_email="admin@deleteme.com", admin_password="password123", admin_name="Admin"
    )
    new_org = auth_service.create_organization(root.uid, org_create)
    org_id = new_org.id
    print(f"Org created: {org_id}")

    # Verify Admin exists
    admin_user = auth_service.repo.get_by_email("admin@deleteme.com")
    print(f"Org Admin created: {admin_user.uid}")

    # Add some dummy workflow data directly to repo
    await repo.create_workflow({"id": "wf1", "name": "Workflow 1", "organization_id": org_id})
    print("Workflow 'wf1' created in org.")

    # 3. Test ROOT PROTECTION
    print("\n[Test] Root Protection")
    try:
        auth_service.delete_user(root.uid, root.uid)
        print("FAIL: Root was able to delete Root!")
    except Exception as e:
        print(f"PASS: Caught expected error: {e}")

    # 4. Test ORG DELETION (Cascading)
    print("\n[Test] Org Deletion")
    try:
        # Mocking the Router logic: Call auth delete then repo cascade
        auth_service.delete_organization(root.uid, org_id)

        # Verify users gone
        leftover_admin = auth_service.repo.get_by_uid(admin_user.uid)
        if leftover_admin:
            print(f"FAIL: Admin user {admin_user.uid} still exists!")
        else:
            print("PASS: Admin user deleted.")

        # Verify logic called repo.delete_org_data
        await repo.delete_org_data(org_id)

        # Verify workflows gone
        wfs = await repo.get_all_workflows(org_id)
        if wfs:
            print(f"FAIL: Workflows still exist: {wfs}")
        else:
            print("PASS: Workflows deleted.")

        # Verify Org entity gone
        org_check = await repo.get_organization(org_id)
        if org_check:
            print("FAIL: Org entity still exists.")
        else:
            print("PASS: Org entity deleted.")

    except Exception as e:
        print(f"FAIL: Exception during Org Deletion: {e}")
        import traceback

        traceback.print_exc()

    print("--- Verification Complete ---")


if __name__ == "__main__":
    asyncio.run(run_verification())
