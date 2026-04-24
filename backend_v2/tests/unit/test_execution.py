from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.services.execution import ExecutionService


@pytest.fixture
def mock_repo() -> MagicMock:
    repo = MagicMock()
    repo.get_all_executions = AsyncMock(return_value=[])
    repo.get_execution = AsyncMock()
    repo.delete_execution = AsyncMock(return_value=True)
    repo.driver = MagicMock()
    repo.driver.get = AsyncMock()
    return repo


@pytest.fixture
def mock_executor() -> MagicMock:
    return MagicMock()


@pytest.fixture
def execution_service(mock_repo: MagicMock, mock_executor: MagicMock) -> ExecutionService:
    return ExecutionService(repo=mock_repo, executor=mock_executor)


@pytest.fixture
def admin_token() -> TokenData:
    return TokenData(id="admin-1", role=UserRole.ROOT)


@pytest.mark.asyncio
async def test_delete_execution_fails_fast_on_storage_error(
    execution_service: ExecutionService, admin_token: TokenData, mock_repo: MagicMock
) -> None:
    """Test that execution deletion fails fast and crashes if blob storage cleanup fails."""
    # Mock database returning raw execution with a trace storage path
    mock_repo.driver.get.return_value = {
        "id": "exe_123",
        "created_by": "admin-1",
        "organization_id": "org_1",
        "execution_trace_storage_path": "traces/exe_123.json",
    }

    with patch("backend_v2.services.execution.get_storage_driver") as mock_get_storage:
        mock_storage = AsyncMock()
        # Simulate storage being offline/failing
        mock_storage.delete.side_effect = Exception("AWS S3 Offline")
        mock_get_storage.return_value = mock_storage

        # The service MUST crash with 500, not swallow the error!
        with pytest.raises(AppException) as exc_info:
            await execution_service.delete_execution(initiator=admin_token, execution_id="exe_123")

        assert exc_info.value.status_code == 500
        assert exc_info.value.details["error_code"] == ErrorCodes.INTERNAL_SERVER_ERROR.value
        assert "Failed to clean up blob" in exc_info.value.message


@pytest.mark.asyncio
async def test_render_execution_fails_fast_on_corrupt_pdf(
    execution_service: ExecutionService, admin_token: TokenData, mock_repo: MagicMock
) -> None:
    """Test that PDF rendering fails fast if the pre-generated PDF is missing from storage."""
    # Mock an execution that is COMPLETED and has a PDF path
    mock_execution = MagicMock()
    from backend_v2.models.v2_core import ExecutionStatus

    mock_execution.status = ExecutionStatus.COMPLETED
    mock_execution.workflow_id = "wf_1"
    mock_execution.pdf_report_path = "pdfs/exe_123.pdf"
    mock_execution.profile_syntheses = {"default": {}}

    # Mock get_execution to return our mock execution
    mock_repo.get_execution.return_value = mock_execution

    # Mock workflow to bypass default_profile_id check and pass Pydantic validation
    mock_repo.get_workflow_by_id = AsyncMock(
        return_value={
            "id": "wf_1234567890abcdef",
            "slug": "test-workflow",
            "description": "Test",
            "status": "active",
            "version": 1,
            "default_profile_id": "default",
            "expected_inputs": [],
            "steps": [],
            "organization_id": "org_1",
            "name": "wf",
            "output_profiles": {
                "default": {"name": {"default_locale": "en", "translations": {"en": "Default Profile"}}}
            },
        }
    )

    with patch("backend_v2.services.execution.get_storage_driver") as mock_get_storage:
        mock_storage = AsyncMock()
        # Simulate storage read failure (e.g., file deleted manually)
        mock_storage.read.side_effect = Exception("File Not Found in S3")
        mock_get_storage.return_value = mock_storage

        mock_arq = AsyncMock()

        # The service MUST crash with 500 and NOT fall back to sync generation!
        with pytest.raises(AppException) as exc_info:
            await execution_service.render_execution(
                initiator=admin_token,
                execution_id="exe_123",
                format_type="pdf",
                profile_id="default",
                accept_language="en",
                arq_pool=mock_arq,
            )

        assert exc_info.value.status_code == 500
        assert exc_info.value.details["error_code"] == ErrorCodes.INTERNAL_SERVER_ERROR.value
        assert "Failed to fetch pre-generated PDF from storage" in exc_info.value.message
