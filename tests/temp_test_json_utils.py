import pytest
from datetime import datetime
from backend.utils.json_utils import flexible_json_dump
from backend.exceptions import AppException, ErrorCodes

class TestJsonUtils:
    
    def test_flexible_json_dump_success(self):
        """Verify serialization of supported types."""
        data = {
            "str": "value",
            "date": datetime(2023, 1, 1, 12, 0, 0),
            "dict": {"nested": True}
        }
        json_str = flexible_json_dump(data)
        assert "2023-01-01T12:00:00" in json_str

    def test_flexible_json_dump_fail_fast(self):
        """Verify serialization failure raises AppException."""
        data = {"bad": {1, 2}} # Sets are not JSON serializable and don't have __dict__
        
        with pytest.raises(AppException) as excinfo:
            flexible_json_dump(data)
            
        assert excinfo.value.status_code == 500
        assert excinfo.value.details["error_code"] == ErrorCodes.INTERNAL_SERVER_ERROR
        assert "JSON Serialization Failed" in excinfo.value.message

if __name__ == "__main__":
    pass
