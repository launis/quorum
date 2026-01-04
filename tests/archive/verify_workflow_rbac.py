
import asyncio
import os
import shutil
from typing import Dict, Any

# Force Mock configuration
os.environ["USE_MOCK_DB"] = "true"
os.environ["USE_FIREBASE"] = "false"

from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from backend.api import builder_router
from backend.dependencies import get_current_user_from_header, EngineDep
from backend.models.auth import User, UserRole
from backend.database.repository import TinyDBRepository
from tinydb import TinyDB

# Defines
SYS_ID = "system"
ORG_NOKIA = "nokia"
ORG_OTHER = "other"

# Mocks
class MockUser(User):
    def __init__(self, uid, role, org_id):
        super().__init__(
            uid=uid, email=f"{uid}@test.com", role=role, organization_id=org_id, created_at="2024-01-01"
        )

mock_root = MockUser("root", UserRole.ROOT, SYS_ID)
mock_admin = MockUser("admin", UserRole.ADMIN, ORG_NOKIA)
mock_manager = MockUser("manager", UserRole.MANAGER, ORG_NOKIA)
mock_other = MockUser("spy", UserRole.MANAGER, ORG_OTHER)

# Setup App for Testing
app = FastAPI()
app.include_router(builder_router.router)

# DB Setup
if os.path.exists("verify_rbac.json"):
    os.remove("verify_rbac.json")
# Mock Engine to avoid complex imports
class MockRegistry:
    def __init__(self):
        self.agents_map = {}

class MockEngine:
    def __init__(self, repo):
        self.repository = repo
        self.registry = MockRegistry()

if os.path.exists("verify_rbac.json"):
    os.remove("verify_rbac.json")
db = TinyDB("verify_rbac.json")
repo = TinyDBRepository(db)
engine = MockEngine(repo)

# Dependency Overrides
active_user = mock_root # Logic will swap this

def get_test_user():
    return active_user

def get_test_engine():
    return engine

app.dependency_overrides[get_current_user_from_header] = get_test_user

# Re-override purely to be safe if imports differ
from backend import dependencies
dependencies.get_current_user_from_header = get_test_user
dependencies.get_engine = get_test_engine
app.dependency_overrides[dependencies.get_engine] = get_test_engine

client = TestClient(app)

def run_test():
    print("--- Starting RBAC Verification ---")
    global active_user
    
    # 1. Admin Blocked from Creation
    print("\n[Test 1] ADMIN tries to create Workflow")
    active_user = mock_admin
    res = client.post("/builder/workflows", json={"name": "Admin Hack", "steps": []})
    if res.status_code == 403:
        print("PASS: Admin blocked (403).")
    else:
        print(f"FAIL: Admin got {res.status_code} {res.json()}")

    # 2. Manager Creates Local Workflow
    print("\n[Test 2] MANAGER creates Workflow")
    active_user = mock_manager
    res = client.post("/builder/workflows", json={"name": "Nokia Process", "steps": []})
    if res.status_code == 200:
        print("PASS: Manager created workflow.")
        wf_id = res.json()['id']
        wf_org = res.json()['organization_id']
        if wf_org == ORG_NOKIA:
            print("PASS: Org ID assigned correctly.")
    else:
        print(f"FAIL: Manager got {res.status_code}")
        wf_id = None

    # 3. Manager Tries to Create Public
    print("\n[Test 3] MANAGER tries to create Public Workflow")
    res = client.post("/builder/workflows", json={"name": "Public Hack", "is_public": True})
    if res.status_code == 403:
         print("PASS: Public creation blocked for Manager.")
    else:
         print(f"FAIL: Manager allowed public? {res.status_code}")

    # 4. Root Creates Public System Workflow
    print("\n[Test 4] ROOT creates Public System Workflow")
    active_user = mock_root
    res = client.post("/builder/workflows", json={"name": "Std System", "is_public": True})
    if res.status_code == 200:
        sys_wf = res.json()
        print("PASS: Root created public workflow.")
        if sys_wf['organization_id'] == "system" and sys_wf['is_public'] == True:
            print("PASS: Org=system, Public=True.")
    else:
        print(f"FAIL: Root failed {res.status_code}")

    # 5. Visibility Check (Listing)
    print("\n[Test 5] Manager List View")
    active_user = mock_manager
    res = client.get("/builder/workflows")
    items = res.json()
    ids = [i['id'] for i in items]
    print(f"Manager sees {len(items)} workflows: {ids}")
    # Should see Own (Test 2) + Public System (Test 4)
    if len(items) >= 2:
        print("PASS: Manager sees own + public system.")
    else:
         print("FAIL: Visibility issue.")
         
    # 6. Other Org Manager List View
    print("\n[Test 6] Other Manager List View")
    active_user = mock_other
    res = client.get("/builder/workflows")
    items = res.json()
    ids = [i['id'] for i in items]
    print(f"Other Manager sees {len(items)} workflows: {ids}")
    # Should see ONLY Public System (Test 4), NOT Nokia (Test 2)
    has_system = any(i['id'] == sys_wf['id'] for i in items)
    has_nokia = any(i['id'] == wf_id for i in items) if wf_id else False
    
    if has_system and not has_nokia:
        print("PASS: Isolation verified.")
    else:
        print(f"FAIL: Isolation breach. System={has_system}, Nokia={has_nokia}")

    # 7. Manager tries to Delete System Workflow
    print("\n[Test 7] Manager tries to delete System Workflow")
    active_user = mock_manager
    res = client.delete(f"/builder/workflows/{sys_wf['id']}")
    if res.status_code == 403:
        print("PASS: Deletion blocked.")
    else:
        print(f"FAIL: Manager deleted system wf? {res.status_code}")

    print("--- Verification Complete ---")

if __name__ == "__main__":
    run_test()
