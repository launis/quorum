import pytest
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from backend.services.drivers.local_file_driver import LocalFileDriver
from backend.services.storage import get_storage_driver
from backend.settings import StorageBackend, Settings
from backend.exceptions import AppException, ErrorCodes

# Temporary test directory
TEST_DIR = Path("./test_storage_tmp")

class TestStorageService:

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        if TEST_DIR.exists():
            shutil.rmtree(TEST_DIR)
        TEST_DIR.mkdir()
        yield
        if TEST_DIR.exists():
            shutil.rmtree(TEST_DIR)

    @pytest.mark.asyncio
    async def test_local_driver_traversal_protection(self):
        """Test strict path traversal prevention."""
        driver = LocalFileDriver(base_path=str(TEST_DIR))
        
        # Attack attempt: write outside base
        with pytest.raises(AppException) as excinfo:
            await driver.save("../outside.txt", "data")
            
        assert excinfo.value.status_code == 400
        assert excinfo.value.details["error_code"] == ErrorCodes.FILESYSTEM_VIOLATION
        print("\n[TEST] Path Traversal: Blocked")

    def test_factory_config_fail_fast(self):
        """Test factory raises AppException for missing config."""
        with patch("backend.services.storage.get_settings") as mock:
            mock.return_value.active_backend = StorageBackend.FIRESTORE
            mock.return_value.storage_bucket_name = None # Missing!
            
            with pytest.raises(AppException) as excinfo:
                get_storage_driver()
                
            assert excinfo.value.status_code == 500
            assert excinfo.value.details["error_code"] == ErrorCodes.STORAGE_CONFIG_ERROR
            print("\n[TEST] Factory Config: Fail Fast Successful")

    @pytest.mark.asyncio
    async def test_local_driver_crud(self):
        """Test basic CRUD operations."""
        driver = LocalFileDriver(base_path=str(TEST_DIR))
        
        # Save
        await driver.save("test.txt", "Hello")
        assert (TEST_DIR / "test.txt").exists()
        
        # Read
        content = await driver.read("test.txt")
        assert content == b"Hello"
        
        # Delete
        deleted = await driver.delete("test.txt")
        assert deleted is True
        assert not (TEST_DIR / "test.txt").exists()
        print("\n[TEST] CRUD: Successful")

if __name__ == "__main__":
    pass
