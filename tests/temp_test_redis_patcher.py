import pytest
import sys
from unittest.mock import patch
from backend.utils.redis_patcher import get_patched_fakeredis_pool
from backend.exceptions import AppException, ErrorCodes

class TestRedisPatcher:
    
    def test_redis_patcher_success(self):
        """Verify success if fakeredis is installed (assuming it is in dev/test env)."""
        # If fakeredis is installed, this should return an object
        # We can just check it doesn't raise
        try:
             get_patched_fakeredis_pool()
        except AppException as e:
             if e.details.get("error_code") == ErrorCodes.CONFIGURATION_ERROR:
                 pytest.skip("fakeredis not installed")
             raise

    def test_redis_patcher_fail_fast_missing_dep(self):
        """Verify Fail Fast if fakeredis is missing."""
        # Clean sys.modules to force re-import
        with patch.dict(sys.modules):
            # Mask fakeredis to raise ImportError
            sys.modules["fakeredis"] = None
            sys.modules["fakeredis.aioredis"] = None
            
            # Since the function imports inside, it should hit the error
            # But we might need to bypass the 'import' statement check if it's already loaded?
            # Standard python import machinery will see None and raise ModuleNotFoundError
            
            with pytest.raises(AppException) as excinfo:
                get_patched_fakeredis_pool()
                
            assert excinfo.value.status_code == 500
            assert excinfo.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR
            assert "Missing dependency 'fakeredis'" in excinfo.value.message

if __name__ == "__main__":
    pass
