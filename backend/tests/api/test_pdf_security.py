from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import status

from backend.api.routes.execution.artifacts import _enforce_pdf_access
from backend.exceptions import AppException
from backend.models.auth import TokenData, UserRole
from pathlib import Path

# --- RBAC UNIT TESTS ---

def test_rbac_root_allow():
    user = TokenData(uid="root", role=UserRole.ROOT, organization_id="system")
    execution = {"user_id": "other", "organization_id": "other_org"}
    # Should not raise
    _enforce_pdf_access(user, execution)

def test_rbac_admin_deny():
    user = TokenData(uid="admin", role=UserRole.ADMIN, organization_id="org1")
    execution = {"user_id": "u1", "organization_id": "org1"}
    with pytest.raises(AppException) as exc:
        _enforce_pdf_access(user, execution)
    assert exc.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc.value.details["error_code"] == "ADMIN_DENIED"

def test_rbac_manager_own_org_allow():
    user = TokenData(uid="mgr", role=UserRole.MANAGER, organization_id="org1")
    execution = {"user_id": "u1", "organization_id": "org1"}
    _enforce_pdf_access(user, execution)

def test_rbac_manager_other_org_deny():
    user = TokenData(uid="mgr", role=UserRole.MANAGER, organization_id="org1")
    execution = {"user_id": "u2", "organization_id": "org2"}
    with pytest.raises(AppException) as exc:
        _enforce_pdf_access(user, execution)
    assert exc.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc.value.details["error_code"] == "ORG_MISMATCH"

def test_rbac_member_own_exec_allow():
    user = TokenData(uid="u1", role=UserRole.MEMBER, organization_id="org1")
    execution = {"user_id": "u1", "organization_id": "org1"}
    _enforce_pdf_access(user, execution)

def test_rbac_member_other_exec_deny():
    user = TokenData(uid="u1", role=UserRole.MEMBER, organization_id="org1")
    execution = {"user_id": "u2", "organization_id": "org1"}
    with pytest.raises(AppException) as exc:
        _enforce_pdf_access(user, execution)
    assert exc.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc.value.details["error_code"] == "OWNERSHIP_REQUIRED"


# --- INTEGRATION MOCK TESTS ---
# We verify the logic flow in download endpoint via patching

from backend.api.routes.execution.artifacts import download_execution_pdf


@pytest.mark.asyncio
async def test_download_endpoint_file_exists():
    mock_repo = AsyncMock()
    mock_repo.get_execution.return_value = {"id": "ex1", "user_id": "u1", "organization_id": "org1"}

    mock_user = TokenData(uid="u1", role=UserRole.MEMBER, organization_id="org1")

    # Mock Storage
    mock_storage = MagicMock()
    mock_storage.exists.return_value = True
    mock_storage.read.return_value = b"pdf_content" # Fallback if instance check fails

    # Simulate Local Storage behavior
    from backend.services.storage import LocalFileStorage
    mock_storage.__class__ = LocalFileStorage
    mock_storage.base_path = Path("/tmp")

    # Mock FileResponse to avoid os.stat failure
    with patch("backend.api.routes.execution.artifacts.FileResponse") as mock_file_response:
        mock_file_response.return_value.status_code = 200

        resp = await download_execution_pdf("ex1", mock_repo, mock_user, AsyncMock(), mock_storage)

        # Should return the mock
        assert resp.status_code == 200

@pytest.mark.asyncio
async def test_download_endpoint_queues_job():
    mock_repo = AsyncMock()
    mock_repo.get_execution.return_value = {"id": "ex1", "user_id": "u1", "organization_id": "org1"}
    mock_pool = AsyncMock()

    mock_user = TokenData(uid="u1", role=UserRole.MEMBER, organization_id="org1")

    # Mock Storage
    mock_storage = MagicMock()
    mock_storage.exists.return_value = False

    resp = await download_execution_pdf("ex1", mock_repo, mock_user, mock_pool, mock_storage)

    # Should be 202
    assert resp.status_code == 202
    mock_pool.enqueue_job.assert_called_with("generate_pdf_job", execution_id="ex1")
