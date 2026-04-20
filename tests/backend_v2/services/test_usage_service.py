import pytest
from unittest.mock import AsyncMock

from backend_v2.services.usage_service import UsageService
from backend_v2.exceptions import AppException

@pytest.mark.asyncio
async def test_quota_check_org_not_found_returns_404() -> None:
    # Arrange
    repo_mock = AsyncMock()
    repo_mock.get_organization.return_value = None  # Simulate org not found
    service = UsageService(repo=repo_mock)

    # Act & Assert
    with pytest.raises(AppException) as exc_info:
        await service.check_quota("org_unknown")

    # Due to the bug (Exception block double wrapping), this returns 500 instead of 404
    assert exc_info.value.status_code == 404
    assert "Organization 'org_unknown' not found" in exc_info.value.message
