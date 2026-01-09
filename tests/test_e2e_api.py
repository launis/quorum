import importlib
import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


# Helper to reload backend dependencies to force DB switch between tests
# This is necessary because the App initializes the DB once at startup (Singleton).
def get_reloaded_client(env_vars):
    with patch.dict(os.environ, env_vars):
        # 1. Clear Pydantic Settings Cache
        from backend.settings import get_settings

        get_settings.cache_clear()

        # 2. Force Reload of critical modules
        # This ensures get_db_client() is re-evaluated with new settings
        import backend.database.wrapper
        import backend.dependencies
        import backend.main

        importlib.reload(backend.database.wrapper)
        importlib.reload(backend.dependencies)
        importlib.reload(backend.main)

        return TestClient(backend.main.app)


def test_e2e_api_mock_db():
    """E2E: Test basic API endpoints using the Local Mock Database.
    Target: Ensure default developer environment works.
    """
    print("\n[E2E] Starting Mock DB Test...")
    env = {"USE_MOCK_DB": "true"}

    try:
        client = get_reloaded_client(env)

        headers = {"Authorization": "Bearer mock-token:root_master"}

        # 1. Check Configuration Endpoint (Read)
        response = client.get("/config/components", headers=headers)
        assert response.status_code == 200, f"Failed to get components: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0, "Mock DB should have seed data components"

        # 2. Check Workflows Endpoint
        response = client.get("/db/workflows", headers=headers)
        assert response.status_code == 200

    except Exception as e:
        pytest.fail(f"Mock DB E2E Failed: {e}")


@pytest.mark.live
def test_e2e_api_firestore_db():
    """E2E: Test API endpoints using REAL Firestore connection.
    Target: Ensure cloud connectivity works through the API layer.

    Note: Requires GOOGLE_APPLICATION_CREDENTIALS or valid environment.
    """
    print("\n[E2E] Starting Firestore DB Test...")

    # Basic credential check
    # (The wrapper check inside the app is more robust, but we skip early if obvious)
    if not os.path.exists("service-account.json") and not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        pytest.skip("No service-account.json found for Firestore E2E")

    env = {"USE_MOCK_DB": "false", "STORAGE_BACKEND": "FIRESTORE"}

    try:
        client = get_reloaded_client(env)

        # 1. READ ONLY Operation (Safe)
        # Fetching components verifies connection without writing data
        headers = {"Authorization": "Bearer mock-token:root_master"}
        response = client.get("/config/components", headers=headers)

        if response.status_code == 500:
            # If server error, it might be the Auth error
            error_detail = response.json().get("detail", "")
            pytest.fail(f"Firestore Backend Crash: {error_detail}")

        assert response.status_code == 200, f"Firestore API responded with {response.status_code}"
        items = response.json()
        assert isinstance(items, list)
        # Even if empty, 200 OK means connection worked.

    except Exception as e:
        pytest.fail(f"Firestore E2E Exception: {e}")
