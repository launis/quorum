import pytest
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime

from backend.services.usage_service import UsageService
from backend.models.domain import UsageRecord
from backend.exceptions import AppException, ErrorCodes

class TestUsageService:
    @pytest.fixture
    def mock_repo(self):
        repo = AsyncMock()
        return repo

    async def test_track_usage_success(self, mock_repo):
        """Test happy path tracking."""
        service = UsageService(mock_repo)
        
        # Execute
        record = await service.track_usage(
            org_id="org1", user_id="user1", model="gpt-4",
            input_tokens=10, output_tokens=10, cost_usd=0.001
        )

        # Verify
        assert isinstance(record, UsageRecord)
        mock_repo.log_usage.assert_called_once()
        print("\n[TEST] Track Usage: Success")

    async def test_track_usage_fail_fast(self, mock_repo):
        """Test fail fast on tracking error."""
        service = UsageService(mock_repo)
        mock_repo.log_usage.side_effect = Exception("DB Error")

        # Execute & Verify
        try:
            await service.track_usage("org1", "user1", "gpt-4", 10, 10, 0.001)
            assert False, "Should have raised AppException"
        except AppException as e:
            assert e.details["error_code"] == ErrorCodes.USAGE_TRACKING_FAILED
            assert e.status_code == 500
            print("\n[TEST] Track Usage Failure: Caught (Fail Fast)")

    async def test_check_quota_safe(self, mock_repo):
        """Test quota check safe."""
        service = UsageService(mock_repo)
        mock_repo.get_organization.return_value = {"quota_limit": 10.0}
        mock_repo.get_org_usage_total.return_value = 5.0

        # Execute
        result = await service.check_quota("org1")

        # Verify
        assert result is True
        print("\n[TEST] Quota Check: Safe")

    async def test_check_quota_exceeded(self, mock_repo):
        """Test quota check exceeded."""
        service = UsageService(mock_repo)
        mock_repo.get_organization.return_value = {"quota_limit": 10.0}
        mock_repo.get_org_usage_total.return_value = 15.0

        # Execute
        result = await service.check_quota("org1")

        # Verify
        assert result is False
        print("\n[TEST] Quota Check: Exceeded")

    async def test_check_quota_fail_fast(self, mock_repo):
        """Test fail fast on quota DB error."""
        service = UsageService(mock_repo)
        mock_repo.get_organization.side_effect = Exception("DB Down")

        # Execute & Verify
        try:
            await service.check_quota("org1")
            assert False, "Should have raised AppException"
        except AppException as e:
            assert e.details["error_code"] == ErrorCodes.QUOTA_CHECK_FAILED
            assert e.status_code == 500
            print("\n[TEST] Quota Check Config Failure: Caught (Fail Fast)")

if __name__ == "__main__":
    import asyncio
    t = TestUsageService()
    
    # Mock mocks
    repo = AsyncMock()
    
    print("\n--- Running Manual Tests ---")
    loop = asyncio.new_event_loop()
    loop.run_until_complete(t.test_track_usage_success(repo))
    
    repo.log_usage.side_effect = Exception("DB Error")
    loop.run_until_complete(t.test_track_usage_fail_fast(repo))
    
    # Reset side effect
    repo = AsyncMock()
    
    loop.run_until_complete(t.test_check_quota_safe(repo))
    loop.run_until_complete(t.test_check_quota_exceeded(repo))
    
    repo.get_organization.side_effect = Exception("DB Down")
    loop.run_until_complete(t.test_check_quota_fail_fast(repo))
    print("\n--- All Manual Tests Passed ---")
