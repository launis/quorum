"""Unit tests for logging_config module, StructuredLogContextDTO, and filters."""

import json
import logging
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.logging_config import (
    ContextFilter,
    JSONFormatter,
    StructuredLogContextDTO,
    UvicornPollingFilter,
    configure_logfire,
    log_error,
    log_startup_system_parameters,
    setup_logging,
)
from backend_v2.settings import Settings


def test_logging_config_structured_context_dto() -> None:
    """Test contract 5: Structured log event formatted with StructuredLogContextDTO emits valid JSON without hasattr/getattr reflection."""
    formatter = JSONFormatter()
    logger = logging.getLogger("test.structured_dto")

    context = StructuredLogContextDTO(
        execution_id="exe_test123456",
        context_id="ctx_test987654",
        error_code="VALIDATION_FAILED",
        details={"field": "summary", "reason": "empty"},
    )

    record = logger.makeRecord(
        name="test.structured_dto",
        level=logging.ERROR,
        fn="test_fn",
        lno=42,
        msg="Structured test error occurred",
        args=(),
        exc_info=None,
        extra={"context_dto": context},
    )

    formatted_json = formatter.format(record)
    parsed = json.loads(formatted_json)

    assert parsed["level"] == "ERROR"
    assert parsed["logger"] == "test.structured_dto"
    assert parsed["message"] == "Structured test error occurred"
    assert parsed["execution_id"] == "exe_test123456"
    assert parsed["context_id"] == "ctx_test987654"
    assert parsed["error_code"] == "VALIDATION_FAILED"
    assert parsed["details"] == {"field": "summary", "reason": "empty"}


def test_json_formatter_default_and_dict_context() -> None:
    """Test JSONFormatter defaults to SYSTEM when no execution_id is provided."""
    formatter = JSONFormatter()
    logger = logging.getLogger("test.json_defaults")

    record = logger.makeRecord(
        name="test.json_defaults",
        level=logging.INFO,
        fn="test_fn",
        lno=10,
        msg="Standard info message",
        args=(),
        exc_info=None,
    )

    formatted_json = formatter.format(record)
    parsed = json.loads(formatted_json)

    assert parsed["execution_id"] == "SYSTEM"
    assert parsed["context_id"] == "SYSTEM"
    assert "error_code" not in parsed
    assert "details" not in parsed


def test_json_formatter_extra_fields_dict() -> None:
    """Test JSONFormatter parses execution_id and error_code from extra fields dictionary."""
    formatter = JSONFormatter()
    logger = logging.getLogger("test.extra_dict")

    record = logger.makeRecord(
        name="test.extra_dict",
        level=logging.WARNING,
        fn="test_fn",
        lno=20,
        msg="Warning message",
        args=(),
        exc_info=None,
        extra={
            "execution_id": "exe_custom_id",
            "context_id": "ctx_custom_id",
            "error_code": "RESOURCE_NOT_FOUND",
            "details": {"id": "123"},
        },
    )

    formatted_json = formatter.format(record)
    parsed = json.loads(formatted_json)

    assert parsed["execution_id"] == "exe_custom_id"
    assert parsed["context_id"] == "ctx_custom_id"
    assert parsed["error_code"] == "RESOURCE_NOT_FOUND"
    assert parsed["details"] == {"id": "123"}


def test_json_formatter_with_exception_info() -> None:
    """Test JSONFormatter serializes exc_info when present on the LogRecord."""
    formatter = JSONFormatter()
    logger = logging.getLogger("test.exc_info")

    try:
        raise ValueError("Simulated fault")
    except ValueError:
        import sys

        exc_info = sys.exc_info()

    record = logger.makeRecord(
        name="test.exc_info",
        level=logging.ERROR,
        fn="test_fn",
        lno=30,
        msg="Error with trace",
        args=(),
        exc_info=exc_info,
    )

    formatted_json = formatter.format(record)
    parsed = json.loads(formatted_json)

    assert "exc_info" in parsed
    assert "ValueError: Simulated fault" in parsed["exc_info"]


def test_log_error_with_app_exception(caplog: pytest.LogCaptureFixture) -> None:
    """Test log_error extracts error_code and details from AppException via type narrowing."""
    test_logger = logging.getLogger("test.log_error_app")
    formatter = JSONFormatter()

    with caplog.at_level(logging.ERROR, logger="test.log_error_app"):
        caplog.clear()
        exc = AppException(
            message="Item could not be found",
            status_code=404,
            details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value, "item_id": "item_99"},
        )
        log_error(test_logger, exc, "Fetch failure")

    assert len(caplog.records) == 1
    record = caplog.records[0]
    formatted_json = formatter.format(record)
    parsed = json.loads(formatted_json)

    assert parsed["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value
    assert parsed["details"]["item_id"] == "item_99"
    assert "Fetch failure" in parsed["message"]


def test_log_error_with_standard_exception(caplog: pytest.LogCaptureFixture) -> None:
    """Test log_error derives SNAKE_CASE error_code from standard Exception class name."""
    test_logger = logging.getLogger("test.log_error_std")
    formatter = JSONFormatter()

    with caplog.at_level(logging.ERROR, logger="test.log_error_std"):
        caplog.clear()
        exc = ValueError("Invalid numeric value")
        log_error(test_logger, exc, "Computation failed")

    assert len(caplog.records) == 1
    record = caplog.records[0]
    formatted_json = formatter.format(record)
    parsed = json.loads(formatted_json)

    assert parsed["error_code"] == "VALUE_ERROR"
    assert "Computation failed" in parsed["message"]


def test_context_filter_execution_and_request_ids(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test ContextFilter injects execution_id, request_id, or SYSTEM."""
    c_filter = ContextFilter()
    logger = logging.getLogger("test.filter")

    # 1. Execution ID takes precedence
    monkeypatch.setattr("backend_v2.logging_config.get_execution_context", lambda: "exec_1234567890")
    monkeypatch.setattr("backend_v2.context.get_request_context", lambda: "req_abcdef")

    record1 = logger.makeRecord("test.filter", logging.INFO, "fn", 1, "msg", (), None)
    c_filter.filter(record1)
    assert record1.context_id == "EXEC:exec_123"
    assert record1.execution_id == "exec_1234567890"

    # 2. Request ID when no execution ID
    monkeypatch.setattr("backend_v2.logging_config.get_execution_context", lambda: None)
    monkeypatch.setattr("backend_v2.context.get_request_context", lambda: "req_9876543210")

    record2 = logger.makeRecord("test.filter", logging.INFO, "fn", 2, "msg", (), None)
    c_filter.filter(record2)
    assert record2.context_id == "REQ:req_9876"
    assert record2.execution_id == "req_9876543210"

    # 3. Fallback to SYSTEM
    monkeypatch.setattr("backend_v2.logging_config.get_execution_context", lambda: None)
    monkeypatch.setattr("backend_v2.context.get_request_context", lambda: None)

    record3 = logger.makeRecord("test.filter", logging.INFO, "fn", 3, "msg", (), None)
    c_filter.filter(record3)
    assert record3.context_id == "SYSTEM"
    assert record3.execution_id == "SYSTEM"


def test_uvicorn_polling_filter() -> None:
    """Test UvicornPollingFilter suppresses 202 render polling messages."""
    p_filter = UvicornPollingFilter()
    logger = logging.getLogger("uvicorn.access")

    suppressed = logger.makeRecord(
        "uvicorn.access",
        logging.INFO,
        "fn",
        1,
        '127.0.0.1:5000 - "GET /api/v2/execution/executions/exe_123/render HTTP/1.1" 202 Accepted',
        (),
        None,
    )
    assert p_filter.filter(suppressed) is False

    allowed = logger.makeRecord(
        "uvicorn.access",
        logging.INFO,
        "fn",
        2,
        '127.0.0.1:5000 - "POST /api/v2/execution/executions HTTP/1.1" 200 OK',
        (),
        None,
    )
    assert p_filter.filter(allowed) is True


def test_configure_logfire_behavior(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test configure_logfire idempotency, environment disable, and error paths."""
    # 0. When logfire is None
    monkeypatch.setattr("backend_v2.logging_config.logfire", None)
    configure_logfire()

    # 1. Idempotency when already configured
    monkeypatch.setattr("backend_v2.logging_config._LOGFIRE_CONFIGURED", True)
    configure_logfire()

    # 2. Disabled via env var
    monkeypatch.setattr("backend_v2.logging_config._LOGFIRE_CONFIGURED", False)
    monkeypatch.setenv("DISABLE_LOGFIRE", "true")
    configure_logfire()

    # 3. Exception path during configuration
    monkeypatch.setattr("backend_v2.logging_config._LOGFIRE_CONFIGURED", False)
    monkeypatch.delenv("DISABLE_LOGFIRE", raising=False)
    mock_logfire = MagicMock()
    mock_logfire.configure.side_effect = RuntimeError("Logfire mock failed")
    monkeypatch.setattr("backend_v2.logging_config.logfire", mock_logfire)

    configure_logfire()  # Should handle RuntimeError gracefully without crashing


def test_setup_logging_litellm_configuration_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test setup_logging raises AppException when litellm configuration fails."""
    mock_settings = Settings(use_mock_llm=True, use_json_logging=True)
    monkeypatch.setattr(Settings, "log_file_path", property(lambda self: str(tmp_path / "litellm_err.log")))
    monkeypatch.setattr("backend_v2.logging_config.get_settings", lambda: mock_settings)
    monkeypatch.setattr("backend_v2.logging_config._LOGFIRE_CONFIGURED", True)

    class BrokenLiteLLM:
        @property
        def set_verbose(self) -> Any:
            raise RuntimeError("LiteLLM verbose failure")

    with patch.dict("sys.modules", {"litellm": BrokenLiteLLM()}):
        with pytest.raises(AppException) as exc_info:
            setup_logging(logging.INFO)
        assert exc_info.value.status_code == 500


def test_setup_logging_lifecycle(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test setup_logging with JSON format, text format, and directory creation."""
    log_file = tmp_path / "test_run.log"
    mock_settings = Settings(
        use_mock_llm=True,
        use_json_logging=True,
        environment="development",
    )
    monkeypatch.setattr(Settings, "log_file_path", property(lambda self: str(log_file)))
    monkeypatch.setattr("backend_v2.logging_config.get_settings", lambda: mock_settings)
    monkeypatch.setattr("backend_v2.logging_config._LOGFIRE_CONFIGURED", True)

    mock_logfire = MagicMock()
    mock_logfire.LogfireLoggingHandler.return_value = logging.NullHandler()
    monkeypatch.setattr("backend_v2.logging_config.logfire", mock_logfire)

    # Run setup_logging in json mode
    setup_logging(logging.INFO)

    root = logging.getLogger()
    assert len(root.handlers) > 0

    # Run setup_logging in text mode
    mock_settings_text = Settings(
        use_mock_llm=True,
        use_json_logging=False,
        environment="development",
    )
    monkeypatch.setattr(Settings, "log_file_path", property(lambda self: str(tmp_path / "text.log")))
    monkeypatch.setattr("backend_v2.logging_config.get_settings", lambda: mock_settings_text)

    # Also test logfire attach exception
    mock_logfire.LogfireLoggingHandler.side_effect = RuntimeError("Attach failed")
    setup_logging(logging.DEBUG)


def test_setup_logging_directory_creation_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test setup_logging raises AppException if log directory cannot be created."""
    mock_settings = Settings(use_mock_llm=True)
    monkeypatch.setattr(Settings, "log_file_path", property(lambda self: "/nonexistent/invalid/path/test.log"))
    monkeypatch.setattr("backend_v2.logging_config.get_settings", lambda: mock_settings)
    monkeypatch.setattr(Path, "exists", lambda self: False)

    def failing_mkdir(*args: Any, **kwargs: Any) -> None:
        raise OSError("Permission denied creating directory")

    monkeypatch.setattr(Path, "mkdir", failing_mkdir)

    with pytest.raises(AppException) as exc_info:
        setup_logging(logging.INFO)

    assert exc_info.value.status_code == 500


def test_log_startup_system_parameters_banner(caplog: pytest.LogCaptureFixture) -> None:
    """Test that log_startup_system_parameters outputs an exhaustive ASCII table at INFO level."""
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


def test_log_startup_system_parameters_descriptions(
    caplog: pytest.LogCaptureFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that log_startup_system_parameters renders accurate descriptions for prod vs dev sampling."""
    test_logger = logging.getLogger("test.startup.sampling")

    prod_settings = Settings(use_mock_llm=True, environment="production")
    monkeypatch.setattr("backend_v2.logging_config.get_settings", lambda: prod_settings)

    with caplog.at_level(logging.INFO, logger="test.startup.sampling"):
        caplog.clear()
        log_startup_system_parameters(test_logger, "PROD SERVER")
    prod_output = "\n".join(r.message for r in caplog.records)
    assert "All 305 atoms (Production)" in prod_output

    dev_settings = Settings(use_mock_llm=True, environment="development")
    monkeypatch.setattr("backend_v2.logging_config.get_settings", lambda: dev_settings)

    with caplog.at_level(logging.INFO, logger="test.startup.sampling"):
        caplog.clear()
        log_startup_system_parameters(test_logger, "DEV SERVER")
    dev_output = "\n".join(r.message for r in caplog.records)
    assert "Dev sampling" in dev_output
