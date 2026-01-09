import asyncio
import os

# Force Mock configuration
os.environ["USE_MOCK_DB"] = "true"
os.environ["USE_FIREBASE"] = "false"

# Use TinyDB with a temp file
from tinydb import TinyDB

temp_db_path = "verify_root_cap.json"
if os.path.exists(temp_db_path):
    os.remove(temp_db_path)

db = TinyDB(temp_db_path)

# Models / Services
from backend.models.auth import OrganizationCreate, UserCreate, UserRole
from backend.services.auth import AuthService


async def run_verification():
    print("--- Starting Root Capability Verification ---")

    # 1. Setup
    auth_service = AuthService(db, use_firebase=False)

    # Ensure Root
    root = auth_service.ensure_root_user()
    print(f"Primary Root: {root.uid} (Org: {root.organization_id})")

    # 2. Create Organizations
    org_nokia = auth_service.create_organization(
        root.uid,
        OrganizationCreate(
            name="Nokia", admin_email="admin@nokia.com", admin_password="password123", admin_name="Nokia Admin"
        ),
    )
    print(f"Org Created: {org_nokia.id}")

    # 3. Test: Root creates another ROOT (should force system)
    print("\n[Test 1] Root creates Secondary Root")
    try:
        new_root_data = UserCreate(
            email="root2@system.com",
            password="password123",
            role=UserRole.ROOT,
            organization_id="nokia",  # Trying to put root in nokia
        )
        new_root = auth_service.create_user(root.uid, new_root_data)

        if new_root.organization_id == "system":
            print("PASS: New Root forced to 'system'.")
        else:
            print(f"FAIL: New Root in '{new_root.organization_id}' (Expected 'system')")

    except Exception as e:
        print(f"FAIL: Exception: {e}")

    # 4. Test: Root creates Admin in Nokia (Cross-Org)
    print("\n[Test 2] Root creates Admin in Nokia")
    try:
        new_admin_data = UserCreate(
            email="manager@nokia.com", password="password123", role=UserRole.MANAGER, organization_id=org_nokia.id
        )
        new_manager = auth_service.create_user(root.uid, new_admin_data)

        if new_manager.organization_id == org_nokia.id:
            print(f"PASS: Manager created in '{org_nokia.id}'.")
        else:
            print(f"FAIL: Manager created in '{new_manager.organization_id}'")

    except Exception as e:
        print(f"FAIL: Exception: {e}")

    print("--- Verification Complete ---")


if __name__ == "__main__":
    asyncio.run(run_verification())
