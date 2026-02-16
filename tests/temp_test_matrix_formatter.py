import pytest
from backend.services.matrix_formatter import format_matrix_component
from backend.exceptions import AppException, ErrorCodes

class TestMatrixFormatter:

    def test_format_missing_name(self):
        """Test Fail Fast when name is missing."""
        component = {"content": {}}
        
        with pytest.raises(AppException) as excinfo:
            format_matrix_component(component)
            
        assert excinfo.value.status_code == 500
        assert excinfo.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR
        assert "missing root-level 'name'" in excinfo.value.message

    def test_format_invalid_scale(self):
        """Test Fail Fast when scale is invalid."""
        component = {
            "name": "Test Matrix",
            "content": {
                "scale": {"min": 5, "max": 1} # Invalid
            }
        }
        
        with pytest.raises(AppException) as excinfo:
            format_matrix_component(component)
            
        assert excinfo.value.status_code == 500
        assert excinfo.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR
        assert "scale invalid" in excinfo.value.message

    def test_format_invalid_anchors(self):
        """Test Fail Fast when anchors have non-integer keys."""
        component = {
            "name": "Test Matrix",
            "content": {
                "scale": {"min": 1, "max": 4},
                "criteria": [
                    {
                        "label": "Test",
                        "anchors": {"one": "Bad Key"} # Invalid key
                    }
                ]
            }
        }
        
        with pytest.raises(AppException) as excinfo:
            format_matrix_component(component)
            
        assert excinfo.value.status_code == 500
        assert excinfo.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR
        assert "Invalid anchor keys" in excinfo.value.message
        print("\n[TEST] Invalid Anchors: Fail Fast Successful")

    def test_format_success(self):
        """Test successful formatting."""
        component = {
            "name": "Valid Matrix",
            "content": {
                "scale": {"min": 1, "max": 5},
                "criteria": [
                    {
                        "label": "Clarity",
                        "id": "clarity",
                        "anchors": {"1": "Poor", "5": "Excellent"}
                    }
                ]
            }
        }
        
        result = format_matrix_component(component)
        assert "### EVALUATION MATRIX: Valid Matrix" in result
        assert "Scale: 1-5" in result
        assert "Level 1: Poor" in result
        print("\n[TEST] Success Case: Verified")

if __name__ == "__main__":
    pass
