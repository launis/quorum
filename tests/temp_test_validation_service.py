import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from backend.services.validation_service import WorkflowValidator
from backend.models.dtos.config import ValidationReportResponse
from backend.exceptions import AppException, ErrorCodes

class TestValidationService:
    @pytest.fixture
    def mock_registry(self):
        registry = MagicMock()
        registry.repository = AsyncMock()
        return registry

    @pytest.fixture
    def steps_db_map(self):
        return {
            "step1": {"component": "mock_agent"}
        }

    async def test_validate_success(self, mock_registry, steps_db_map):
        """Test happy path."""
        # Setup registry to return valid component
        mock_registry.repository.get_component_by_name.return_value = {
            "module": "backend.services.validation_service", # Self for easy import
            "class_name": "WorkflowValidator" # Valid class
        }

        # Execute
        report = await WorkflowValidator.validate_flow_configuration(
            sequence=["step1"],
            steps_db_map=steps_db_map,
            registry=mock_registry
        )

        # Verify
        assert isinstance(report, ValidationReportResponse)
        assert report.valid is True
        assert len(report.errors) == 0
        print("\n[TEST] Validation Success")

    async def test_validate_unknown_step(self, mock_registry):
        """Test user error (unknown step) is reported, not raised."""
        # Execute
        report = await WorkflowValidator.validate_flow_configuration(
            sequence=["unknown_step"],
            steps_db_map={},
            registry=mock_registry
        )

        # Verify
        assert report.valid is False
        assert "Unknown Step" in report.errors[0]
        print("\n[TEST] Validation Unknown Step: Caught")

    async def test_validate_registry_corruption(self, mock_registry, steps_db_map):
        """Test fail fast on registry corruption."""
        # Setup registry to return corrupt component (missing module)
        mock_registry.repository.get_component_by_name.return_value = {
            "module": None,
            "class_name": "SomeClass"
        }

        # Execute & Verify
        try:
            await WorkflowValidator.validate_flow_configuration(
                sequence=["step1"],
                steps_db_map=steps_db_map,
                registry=mock_registry
            )
            assert False, "Should have raised AppException"
        except AppException as e:
            assert e.details["error_code"] == ErrorCodes.REGISTRY_CORRUPTION
            assert e.status_code == 500
            print("\n[TEST] Registry Corruption: Caught (Fail Fast)")

    async def test_validate_import_error(self, mock_registry, steps_db_map):
        """Test fail fast on import error."""
        # Setup registry to return non-existent module
        mock_registry.repository.get_component_by_name.return_value = {
            "module": "non_existent_module_xyz",
            "class_name": "SomeClass"
        }

        # Execute & Verify
        try:
            await WorkflowValidator.validate_flow_configuration(
                sequence=["step1"],
                steps_db_map=steps_db_map,
                registry=mock_registry
            )
            assert False, "Should have raised AppException"
        except AppException as e:
            assert e.details["error_code"] == ErrorCodes.INTERNAL_SERVER_ERROR
            assert "Failed to load code" in e.message
            print("\n[TEST] Import Error: Caught (Fail Fast)")

if __name__ == "__main__":
    import asyncio
    t = TestValidationService()
    
    # Mock mocks
    registry = MagicMock()
    registry.repository = AsyncMock()
    steps = {"step1": {"component": "mock_agent"}}
    
    print("\n--- Running Manual Tests ---")
    loop = asyncio.new_event_loop()
    loop.run_until_complete(t.test_validate_success(registry, steps))
    
    loop.run_until_complete(t.test_validate_unknown_step(registry))
    
    loop.run_until_complete(t.test_validate_registry_corruption(registry, steps))
    loop.run_until_complete(t.test_validate_import_error(registry, steps))
    print("\n--- All Manual Tests Passed ---")
