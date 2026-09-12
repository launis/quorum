"""Unit tests verifying logging isolation and client validation error level compliance.

Ensures that:
1. RequestValidationError in FastAPI handlers logs at WARNING level (4xx client error),
   never at ERROR level (reserved for 5xx internal server crashes).
2. Test environment isolates log_file_name to prevent polluting live backend_debug.log.
"""

from __future__ import annotations

import logging
from unittest.mock import AsyncMock

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from backend_v2.main import app
from backend_v2.settings import get_settings


@pytest.fixture
def client() -> TestClient:
    """Provides a TestClient instance for testing route error logging."""
    return TestClient(app, raise_server_exceptions=False)


def test_validation_exception_handler_logs_as_warning_not_error(
    client: TestClient,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Proof of Failure: RequestValidationError must log as WARNING, not ERROR.

    When a client sends an invalid path parameter (e.g. 'invalid-id' matching regex pattern error),
    FastAPI returns 422. A 4xx client error must be logged at WARNING level, never ERROR.
    Currently, validation_exception_handler uses logger.error(), polluting logs with false alarms.
    """
    from backend_v2.api.dependencies import get_current_user_from_header, get_studio_output_profile_service
    from backend_v2.models.auth import TokenData, UserRole

    def mock_user() -> TokenData:
        return TokenData(
            email="root@test.com",
            id="usr_root999",
            role=UserRole.ROOT,
            organization_id="org_testorg123",
        )

    mock_service = AsyncMock()
    app.dependency_overrides[get_current_user_from_header] = mock_user
    app.dependency_overrides[get_studio_output_profile_service] = lambda: mock_service

    try:
        with caplog.at_level(logging.WARNING, logger="backend.main"):
            caplog.clear()
            response = client.post("/api/v2/output-profiles/invalid-id/clone")

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

            # Inspect captured records for backend.main
            error_records = [r for r in caplog.records if r.name == "backend.main" and r.levelno >= logging.ERROR]
            warning_records = [
                r
                for r in caplog.records
                if r.name == "backend.main" and r.levelno == logging.WARNING and "VALIDATION ERROR" in r.message
            ]

            # PROOF OF FAILURE: Currently error_records has 1 record, so this assertion fails!
            assert len(error_records) == 0, (
                f"Expected 0 ERROR records for 422 client validation, but got: {[r.message for r in error_records]}"
            )
            assert len(warning_records) == 1, "Expected 1 WARNING record for 422 client validation error"
    finally:
        app.dependency_overrides.clear()


def test_test_environment_isolates_log_file() -> None:
    """Proof of Failure: Test runs must isolate log_file_name away from backend_debug.log.

    When running inside pytest (PYTEST_CURRENT_TEST active), settings.log_file_name must
    be isolated (e.g. 'tests_debug.log' or None) so that 2,999 unit tests do not dump
    thousands of lines of synthetic error traces into the development server's backend_debug.log.
    Currently, settings.log_file_name remains 'backend_debug.log', causing mass log pollution.
    """
    settings = get_settings()
    assert settings.log_file_name != "backend_debug.log", (
        "In test environment, settings.log_file_name must not be 'backend_debug.log'. "
        "Test execution is actively polluting the development server log file!"
    )


def test_log_startup_system_parameters_banner(caplog: pytest.LogCaptureFixture) -> None:
    """Test that log_startup_system_parameters outputs an exhaustive ASCII table at INFO level."""
    from backend_v2.logging_config import log_startup_system_parameters

    test_logger = logging.getLogger("test.startup")
    with caplog.at_level(logging.INFO, logger="test.startup"):
        caplog.clear()
        log_startup_system_parameters(test_logger, "FASTAPI TEST SERVER")

    messages = [r.message for r in caplog.records if r.name == "test.startup"]
    full_output = "\n".join(messages)

    assert "[SYSTEM STARTUP CONFIGURATION] - FASTAPI TEST SERVER" in full_output
    assert "Environment:" in full_output
    assert "Matrix Sampling Limit:" in full_output
    assert "Mock Tokens Allowed:" in full_output
    assert "Storage Backend:" in full_output
    assert "Max Concurrent LLM Steps:" in full_output
    assert "Max Concurrent Workflows:" in full_output
    assert "LLM Max Retries:" in full_output
    assert "LLM Schema Retries:" in full_output
    assert "LLM Logical Retries:" in full_output
    assert "Disable Vertex Cache:" in full_output
    assert "Use Vertex LLM:" in full_output
    assert "Use Mock LLM:" in full_output
    assert "Pacing Delays (s):" in full_output

    # Verify log level and zero secret leakage
    for record in caplog.records:
        if record.name == "test.startup":
            assert record.levelno == logging.INFO
            assert "sk-" not in record.message
            assert "bearer" not in record.message.lower()


def test_log_startup_system_parameters_sampling_description(
    caplog: pytest.LogCaptureFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that log_startup_system_parameters renders accurate descriptions for prod vs dev sampling."""
    from backend_v2.logging_config import log_startup_system_parameters
    from backend_v2.settings import Settings

    test_logger = logging.getLogger("test.startup.sampling")

    # 1. Production sampling limit 0 -> All 305 atoms
    prod_settings = Settings(use_mock_llm=True, environment="production")
    monkeypatch.setattr("backend_v2.logging_config.get_settings", lambda: prod_settings)

    with caplog.at_level(logging.INFO, logger="test.startup.sampling"):
        caplog.clear()
        log_startup_system_parameters(test_logger, "PROD SERVER")
    prod_output = "\n".join(r.message for r in caplog.records)
    assert "All 305 atoms (Production)" in prod_output

    # 2. Dev sampling limit 1 -> Dev sampling
    dev_settings = Settings(use_mock_llm=True, environment="development")
    monkeypatch.setattr("backend_v2.logging_config.get_settings", lambda: dev_settings)

    with caplog.at_level(logging.INFO, logger="test.startup.sampling"):
        caplog.clear()
        log_startup_system_parameters(test_logger, "DEV SERVER")
    dev_output = "\n".join(r.message for r in caplog.records)
    assert "Dev sampling" in dev_output
