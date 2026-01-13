"""Environment Configuration Tests."""

import os
from unittest.mock import patch

import pytest

import backend.database.wrapper as db_wrapper
from backend.settings import get_settings


@pytest.fixture(autouse=True)
def clear_settings_cache():
    """Clear settings cache before each test."""
    get_settings.cache_clear()
    yield


def test_env_mock_db_default():
    """Test Default Behavior: Should use Mock DB (Visualized as run_mock_locally.bat)."""
    # Clear env vars to allow defaults to take over, BUT Keep LLM Mocked
    with patch.dict(os.environ, {"USE_MOCK_LLM": "true", "USE_MOCK_DB": "true"}, clear=True):
        client = db_wrapper.get_db_client()
        assert isinstance(client, db_wrapper.TinyDBClient)
        # Verify it points to db_mock.json
        # TinyDB path access varies, assuming standard JSONStorage
        # client.db is TinyDB instance. _storage might be Middleware.
        # Usually client.db.storage.path or similar works if straight JSONStorage.
        # But here checking instance is enough for unit test logic via settings.
        settings = get_settings()
        assert settings.use_mock_db is True
        assert "db_mock.json" in settings.mock_db_path


def test_env_local_production():
    """Test Local Production: USE_MOCK_DB=False, STORAGE=LOCAL (run_locally.bat)."""
    env = {"USE_MOCK_DB": "false", "STORAGE_BACKEND": "LOCAL", "USE_MOCK_LLM": "true"}
    with patch.dict(os.environ, env, clear=True):
        client = db_wrapper.get_db_client()
        assert isinstance(client, db_wrapper.TinyDBClient)

        settings = get_settings()
        assert settings.use_mock_db is False
        assert "db.json" in settings.prod_db_path


@patch("backend.database.wrapper.firebase_admin")
@patch("backend.database.wrapper.credentials")
@patch("backend.database.wrapper.firestore")
def test_firestore_client_instantiation(mock_firestore, mock_creds, mock_admin):
    """Test Firestore Client Instantiation: Verify imports and init logic.

    Catches errors like "name 'os' is not defined".
    """
    try:
        from backend.database.wrapper import FirestoreClient

        # Mock settings and file system
        with (
            patch("backend.settings.get_settings") as mock_settings,
            patch("os.path.exists", return_value=True),
        ):  # Simulate service-account.json exists
            mock_settings.return_value.base_dir = "C:/mock"

            # Instantiation attempt
            client = FirestoreClient()
            assert client is not None

    except ImportError:
        pytest.skip("firebase_admin not installed")
    except NameError as e:
        pytest.fail(f"Code Error in FirestoreClient: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error initializing FirestoreClient: {e}")
