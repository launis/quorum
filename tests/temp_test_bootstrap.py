import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from backend.bootstrap import bootstrap_application
from backend.exceptions import AppException, ErrorCodes, FatalInterruption

class TestBootstrap:

    @pytest.mark.asyncio
    async def test_bootstrap_success(self):
        """Test successful bootstrap."""
        with patch("backend.bootstrap.get_engine", new_callable=AsyncMock) as mock_get_engine:
             # Mock dependencies to avoid actual DB connection
             with patch("backend.bootstrap.get_db_client_dep"), \
                  patch("backend.bootstrap.get_async_repository", new_callable=AsyncMock), \
                  patch("backend.bootstrap.get_agent_registry_dep", new_callable=AsyncMock), \
                  patch("backend.bootstrap.get_prompt_builder_dep", new_callable=AsyncMock), \
                  patch("backend.bootstrap.get_storage_service_dep"), \
                  patch("backend.bootstrap.get_document_service_dep"):
                
                engine = await bootstrap_application()
                assert engine is not None

    @pytest.mark.asyncio
    async def test_bootstrap_failure(self):
        """Test Fail Fast: Convert generic exception to AppException."""
        with patch("backend.bootstrap.get_engine", side_effect=Exception("Database Connection Failed")):
             with patch("backend.bootstrap.get_db_client_dep"), \
                  patch("backend.bootstrap.get_async_repository", new_callable=AsyncMock), \
                  patch("backend.bootstrap.get_agent_registry_dep", new_callable=AsyncMock), \
                  patch("backend.bootstrap.get_prompt_builder_dep", new_callable=AsyncMock), \
                  patch("backend.bootstrap.get_storage_service_dep"), \
                  patch("backend.bootstrap.get_document_service_dep"):

                with pytest.raises(AppException) as excinfo:
                    await bootstrap_application()
                
                assert excinfo.value.status_code == 500
                assert excinfo.value.details["error_code"] == ErrorCodes.INTERNAL_SERVER_ERROR
                assert "Database Connection Failed" in excinfo.value.message

    @pytest.mark.asyncio
    async def test_bootstrap_fatal_interruption_pass_through(self):
        """Test FatalInterruption is re-raised as is (preserving existing error codes)."""
        fatal = FatalInterruption(step_name="Init", reason="Critical Failure")
        
        with patch("backend.bootstrap.get_engine", side_effect=fatal):
             with patch("backend.bootstrap.get_db_client_dep"), \
                  patch("backend.bootstrap.get_async_repository", new_callable=AsyncMock), \
                  patch("backend.bootstrap.get_agent_registry_dep", new_callable=AsyncMock), \
                  patch("backend.bootstrap.get_prompt_builder_dep", new_callable=AsyncMock), \
                  patch("backend.bootstrap.get_storage_service_dep"), \
                  patch("backend.bootstrap.get_document_service_dep"):

                with pytest.raises(FatalInterruption) as excinfo:
                    await bootstrap_application()
                
                assert excinfo.value.step_name == "Init"

if __name__ == "__main__":
    pass
