import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.services.progress import DatabaseProgressTracker, ProgressService
from backend.database.repository import AbstractWorkflowRepository
from backend.exceptions import AppException, ErrorCodes

class TestProgressService:
    
    @pytest.mark.asyncio
    async def test_db_tracker_fail_fast(self):
        """Test that DatabaseProgressTracker raises AppException on DB failure."""
        mock_repo = AsyncMock(spec=AbstractWorkflowRepository)
        mock_repo.update_execution.side_effect = Exception("DB Down")
        
        tracker = DatabaseProgressTracker(repository=mock_repo, execution_id="exec-1")
        
        with pytest.raises(AppException) as excinfo:
            await tracker.start()
            
        assert excinfo.value.status_code == 500
        assert excinfo.value.details["error_code"] == ErrorCodes.PROGRESS_UPDATE_FAILED
        print("\n[TEST] DB Tracker: Fail Fast Successful")

    @pytest.mark.asyncio
    async def test_redis_service_fail_fast(self):
        """Test that ProgressService raises AppException on Redis failure."""
        mock_redis = AsyncMock()
        mock_redis.set.side_effect = Exception("Redis Down")
        
        service = ProgressService(redis_client=mock_redis)
        
        with pytest.raises(AppException) as excinfo:
            await service.emit_progress("exec-1", "task-1", "msg", 0.5)
            
        assert excinfo.value.status_code == 500
        assert excinfo.value.details["error_code"] == ErrorCodes.PROGRESS_UPDATE_FAILED
        print("\n[TEST] Redis Service: Fail Fast Successful")

if __name__ == "__main__":
    pass
