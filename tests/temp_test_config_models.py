import sys
import os
import unittest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch

# Add project root to sys.path
sys.path.append(os.getcwd())

from backend.api.routes.config.models import list_models, update_model_config, delete_model_config
from backend.exceptions import AppException, ErrorCodes
from backend.models.llm import LLMProviderConfig

class TestConfigModelsRouter(unittest.IsolatedAsyncioTestCase):
    
    def setUp(self):
        self.mock_repo = MagicMock()
        self.mock_repo.get_model_registry = AsyncMock()
        self.mock_repo.update_model_registry = AsyncMock(return_value=True)
        self.mock_usage_service = MagicMock()
        
    async def test_list_models_fail_fast_invalid_structure(self):
        print("\n[TEST] List Models: Fail Fast on Invalid Structure")
        # Setup malformed registry
        self.mock_repo.get_model_registry.return_value = {"models": "NOT_A_DICT"}
        
        try:
            await list_models(repository=self.mock_repo)
            self.fail("Should have raised AppException")
        except AppException as e:
            self.assertEqual(e.details["error_code"], ErrorCodes.INVALID_REGISTRY_STRUCTURE)
            print("  [OK] Caught INVALID_REGISTRY_STRUCTURE")

    async def test_update_config_reject_legacy_id(self):
        print("\n[TEST] Update Config: Reject Legacy ID")
        config = LLMProviderConfig(id="legacy_id", provider="openai", model_name="gpt-4")
        
        try:
            await update_model_config(
                provider_id="legacy_id", 
                update_data=config, 
                repository=self.mock_repo
            )
            self.fail("Should have raised AppException")
        except AppException as e:
            self.assertEqual(e.details["error_code"], ErrorCodes.INVALID_MODEL_ID)
            print("  [OK] Caught INVALID_MODEL_ID")

    async def test_delete_config_reject_legacy_id(self):
        print("\n[TEST] Delete Config: Reject Legacy ID")
        
        # Patch settings to avoid system default check blocking first
        with patch("backend.api.routes.config.models.get_settings") as mock_settings:
            mock_settings.return_value.default_model_strategy = "other/strategy"
            
            try:
                await delete_model_config(
                    provider_id="legacy_id", 
                    repository=self.mock_repo
                )
                self.fail("Should have raised AppException")
            except AppException as e:
                self.assertEqual(e.details["error_code"], ErrorCodes.INVALID_MODEL_ID)
                print("  [OK] Caught INVALID_MODEL_ID")

    async def test_list_models_success_nested(self):
        print("\n[TEST] List Models: Success Nested")
        self.mock_repo.get_model_registry.return_value = {
            "models": {
                "openai": {
                    "fast": {"model_name": "gpt-3.5-turbo", "api_key": "sk-..."}
                }
            }
        }
        
        results = await list_models(repository=self.mock_repo)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, "openai/fast")
        self.assertEqual(results[0].api_key, "********")
        print("  [OK] Parsed nested config correctly")

if __name__ == "__main__":
    unittest.main()
