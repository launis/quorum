import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.dependencies import get_llm_provider
from backend.exceptions import AppException, ErrorCodes

class TestDependencies:

    @pytest.mark.asyncio
    async def test_get_llm_provider_fail_fast(self):
        """Test Fail Fast when provider is missing in config."""
        # Mock Registry to return config without provider
        mock_registry = AsyncMock()
        mock_registry.resolve_model_config.return_value = {"model_name": "gpt-4"}
        
        mock_usage = MagicMock()

        with pytest.raises(AppException) as excinfo:
            await get_llm_provider("smart", mock_registry, mock_usage)
        
        assert excinfo.value.status_code == 500
        assert excinfo.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR
        assert "provider' missing" in excinfo.value.message
        print("\n[TEST] Missing Provider: Fail Fast Successful")

if __name__ == "__main__":
    pass
