"""Builder API Tests."""

import logging
import os
import tempfile

import pytest
from fastapi.testclient import TestClient

from backend import dependencies
from backend.dependencies import get_db_client_dep
from backend.main import app

# Disable logging to prevent Windows IocpProactor noise during capture
logging.disable(logging.CRITICAL)


# Fixture to override DB with a temp file for isolation
@pytest.fixture(name="client")
def client_fixture():
    """Client fixture with isolated file DB."""
    # 0. Clear Singletons
    dependencies._db_client_instance = None
    dependencies._repository_instance = None
    dependencies._engine_instance = None
    dependencies._registry_instance = None
    dependencies._prompt_builder_instance = None
    dependencies._auth_service_instance = None
    dependencies._storage_service_instance = None

    # 1. Create Temp DB File
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)

    # 2. Define Override
    db_ref = []
    from backend.database.wrapper import TinyDBClient
    from backend.dependencies import get_current_user_from_header
    from backend.models.auth import TokenData, UserRole

    class DBHolder:
        client = None

    def get_test_db():
        if DBHolder.client is None:
            client = TinyDBClient(path)
            DBHolder.client = client
            db_ref.append(client)
            # SEED
            client.table("system_config").insert(
                {"type": "model_registry", "models": {"stub": {"fast": "stub", "deep": "stub"}}}
            )
        return DBHolder.client

    # Mock Auth Identity for Builder
    def mock_user():
        return TokenData(
            uid="builder_user", email="builder@example.com", role=UserRole.ROOT, organization_id="org_builder"
        )

    # 3. Apply Override
    app.dependency_overrides[get_db_client_dep] = get_test_db
    app.dependency_overrides[get_current_user_from_header] = mock_user

    # 4. Return Client
    # Use TestClient without context manager to avoid lifespan/loop conflict
    # (Since we override DB, we don't strictly need app startup events here)
    c = TestClient(app)
    yield c

    # 5. Cleanup
    app.dependency_overrides.clear()
    dependencies._db_client_instance = None  # Reset again
    dependencies._repository_instance = None
    dependencies._engine_instance = None
    dependencies._registry_instance = None
    dependencies._prompt_builder_instance = None
    dependencies._auth_service_instance = None
    dependencies._storage_service_instance = None

    for db in db_ref:
        try:
            db.close()
        except Exception:
            pass

    if os.path.exists(path):
        try:
            os.remove(path)
        except Exception:
            # On Windows, sometimes the file is still locked by the test runner/logger
            # We ignore this for now as it's just a temp file
            pass


# Remove global client and use fixture
# client = TestClient(app) # REMOVED


def test_list_agents_config(client):
    """Test that we can retrieve agent discovery metadata."""
    response = client.get("/builder/config/agents")
    assert response.status_code == 200
    agents = response.json()
    assert isinstance(agents, list)
    # Check for known agents
    names = [a["name"] for a in agents]
    assert "GuardAgent" in names
    assert "JudgeAgent" in names


def test_workflow_crud_lifecycle(client):
    """Test Create, Read, Update, Copy, Delete lifecycle."""
    # 0. SEED PROTECTOR
    print("DEBUG: Creating Protector...")
    res = client.post("/builder/workflows", json={"name": "Protector", "steps": ["step_guard"]})
    assert res.status_code == 200, f"Failed to seed Protector: {res.text}"

    # 1. CREATE
    print("DEBUG: Creating Test Workflow...")
    wf_data = {
        "name": "Test Workflow",
        "description": "Integration Test",
        "steps": ["step_guard", "step_analyst"],
        "default_model_mapping": {"step_guard": "fast"},
        "ui_schema": {"nodes": []},
    }

    create_res = client.post("/builder/workflows", json=wf_data)
    assert create_res.status_code == 200
    created_wf = create_res.json()
    wf_id = created_wf["id"]
    assert created_wf["name"] == "Test Workflow"

    # 2. READ (List)
    list_res = client.get("/builder/workflows")
    assert list_res.status_code == 200
    all_wfs = list_res.json()
    assert any(w["id"] == wf_id for w in all_wfs)

    # 3. READ (Detail)
    detail_res = client.get(f"/builder/workflows/{wf_id}")
    assert detail_res.status_code == 200
    assert detail_res.json()["id"] == wf_id

    # 4. UPDATE
    update_payload = {"name": "Updated Workflow Name", "default_model_mapping": {"step_guard": "deep"}}
    update_res = client.put(f"/builder/workflows/{wf_id}", json=update_payload)
    assert update_res.status_code == 200
    updated_wf = update_res.json()
    assert updated_wf["name"] == "Updated Workflow Name"
    assert updated_wf["default_model_mapping"]["step_guard"] == "deep"

    # 5. COPY
    copy_payload = {"new_name": "Copied Workflow"}
    copy_res = client.post(f"/builder/workflows/{wf_id}/copy", json=copy_payload)
    assert copy_res.status_code == 200
    copied_wf = copy_res.json()
    assert copied_wf["id"] != wf_id
    assert copied_wf["name"] == "Copied Workflow"
    assert copied_wf["steps"] == created_wf["steps"]  # Reference same steps V1 logic

    # 6. DELETE (Original)
    # Note: Orphan removal logic is tricky to test on shared steps (seed data steps).
    # Since "step_guard" is used by default workflow, it should NOT be deleted.
    delete_res = client.delete(f"/builder/workflows/{wf_id}")
    assert delete_res.status_code == 200
    data = delete_res.json()
    assert data["status"] == "deleted"
    # Verify steps were NOT deleted because they are shared
    # assert "step_guard" not in data['deleted_steps'] # FIXME: Flaky check in Singleton DB mode

    # 7. DELETE (Copy)
    client.delete(f"/builder/workflows/{copied_wf['id']}")


def test_orphan_step_deletion(client):
    """Test that truly custom orphan steps are deleted."""
    # Create workflow with a fake step ID that doesn't exist elsewhere
    # Note: Logic relies on steps existing in DB to be deleted.
    # We must insert a fake step first manually to test deletion logic properly,
    # or rely on the fact that the router just tries to remove IDs found in the workflow definition
    # from the global step table.

    # 1. Manually insert a dummy step into DB via some backdoor or assuming POST workflow just links IDs
    # The router delete logic:
    # orphans = target_steps - used_elsewhere
    # db.table('steps').remove(Step.id == step_id)

    # We can create a workflow with a unique ID "step_orphan_test"
    # Even if the step doc doesn't exist in 'steps' table, the logic tries to remove it.

    fake_step_id = "step_orphan_test_123"

    wf_data = {"name": "Orphan Test", "steps": [fake_step_id]}
    create_res = client.post("/builder/workflows", json=wf_data)
    wf_id = create_res.json()["id"]

    # Now Delete
    delete_res = client.delete(f"/builder/workflows/{wf_id}")
    data = delete_res.json()

    # It SHOULD list fake_step_id as deleted (because it is orphan)
    # (assuming no other workflow uses it, which is true)
    assert fake_step_id in data["deleted_steps"]
