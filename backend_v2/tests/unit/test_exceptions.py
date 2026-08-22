"""Unit tests for backend_v2 exceptions.

Tests RFC 7807 problem details, error codes, format_validation_error, and exception hierarchy.
"""

from typing import Any

import pytest
from fastapi import status
from pydantic import BaseModel, Field, ValidationError

from backend_v2.exceptions import (
    AgentExecutionError,
    AppException,
    AuthenticationError,
    ConfigurationError,
    ConflictError,
    ErrorCodes,
    ExecutionNotFoundError,
    FatalInterruption,
    LLMSchemaValidationError,
    LogicalValidationError,
    MissingInputMappingError,
    MissingRoutingModeError,
    MissingXaiExtensionError,
    PermissionDeniedError,
    PydanticSyntaxError,
    ResourceNotFoundError,
    SecurityViolationError,
    SemanticEvidenceError,
    ServiceUnavailableError,
    StepNotFoundError,
    TokenLimitExceededError,
    WorkflowCompilationError,
    WorkflowExecutionError,
    WorkflowNotFoundError,
    format_validation_error,
)


class DummyModel(BaseModel):
    name: str
    age: int = Field(ge=0)


def test_format_validation_error_valid_pydantic() -> None:
    """Test that a valid Pydantic error is properly formatted."""
    try:
        DummyModel(name="test")  # type: ignore[call-arg]
    except ValidationError as e:
        result = format_validation_error(e)
        assert "DummyModel validation failed. Missing required fields: age" in result


def test_format_validation_error_internal_error(monkeypatch: Any) -> None:
    """Test the fail-fast behavior when Pydantic internal structure crashes the formatter."""
    import backend_v2.exceptions

    class FakeError(Exception):
        pass

    monkeypatch.setattr(backend_v2.exceptions, "ValidationError", FakeError)

    with pytest.raises(AppException) as exc_info:
        format_validation_error(FakeError("Fake error here"))

    assert exc_info.value.status_code == 500
    assert exc_info.value.error_code == "INTERNAL_SERVER_ERROR"
    assert "Internal error during error formatting" in str(exc_info.value)


def test_format_validation_error_non_pydantic() -> None:
    """Test format_validation_error with a regular Exception."""
    err = ValueError("Regular error message")
    res = format_validation_error(err)
    assert res == "Regular error message"


def test_app_exception_rfc7807_to_problem_detail() -> None:
    """Test RFC 7807 problem detail generation."""
    exc = AppException(
        message="Execution not found",
        status_code=status.HTTP_404_NOT_FOUND,
        details={"error_code": ErrorCodes.EXECUTION_NOT_FOUND.value, "execution_id": "exc_123"},
    )
    detail = exc.to_problem_detail(instance="/executions/exc_123")
    assert detail["status"] == 404
    assert detail["title"] == "Execution Not Found"
    assert detail["detail"] == "Execution not found"
    assert detail["instance"] == "/executions/exc_123"
    assert detail["type"] == "https://api.quorum.fi/errors/execution-not-found"
    assert detail["extensions"] == {"error_code": "EXECUTION_NOT_FOUND", "execution_id": "exc_123"}
    assert exc.error_code == "EXECUTION_NOT_FOUND"
    assert exc.status_code == 404
    assert str(exc) == "Execution not found"


def test_resource_not_found_hierarchy() -> None:
    """Test ResourceNotFoundError subclasses."""
    exc = WorkflowNotFoundError("wor_test123")
    assert exc.status_code == 404
    assert exc.error_code == ErrorCodes.WORKFLOW_NOT_FOUND.value
    assert "wor_test123" in str(exc)

    step_exc = StepNotFoundError("sp_step123")
    assert step_exc.status_code == 404
    assert step_exc.error_code == ErrorCodes.RESOURCE_NOT_FOUND.value

    exec_exc = ExecutionNotFoundError("exc_999")
    assert exec_exc.status_code == 404
    assert exec_exc.error_code == ErrorCodes.EXECUTION_NOT_FOUND.value

    gen_res = ResourceNotFoundError(resource_type="Document", resource_id="doc_1", details={"note": "custom"})
    assert gen_res.status_code == 404
    assert gen_res.error_code == ErrorCodes.RESOURCE_NOT_FOUND.value
    assert gen_res.details["note"] == "custom"

    anon_res = ResourceNotFoundError(resource_type="GenericResource")
    assert anon_res.status_code == 404
    assert str(anon_res) == "GenericResource"


def test_agent_execution_error() -> None:
    """Test AgentExecutionError formatting with original error and agent details."""
    orig = ValueError("Underlying tool failed")
    exc = AgentExecutionError(
        detail="AGENT_STEP_FAILED",
        original_error=orig,
        agent_name="AnalystAgent",
        step_id="sp_analyst",
    )
    assert exc.status_code == 500
    assert "AGENT_STEP_FAILED" in str(exc)
    assert "AnalystAgent" == exc.details["agent"]
    assert exc._format_cause(orig) == "Underlying tool failed"

    no_orig = AgentExecutionError(detail="AGENT_EMPTY_REPLY")
    assert no_orig.status_code == 500
    assert str(no_orig) == "AGENT_EMPTY_REPLY"


def test_domain_exception_subclasses() -> None:
    """Test domain-specific exception subclasses for appropriate status codes and error codes."""
    fatal = FatalInterruption(step_name="sp_node", reason="User cancelled", details={"note": "debug"})
    assert fatal.status_code == 500
    assert fatal.error_code == "INTERNAL_SERVER_ERROR"
    assert fatal.step_name == "sp_node"
    assert fatal.reason == "User cancelled"

    fatal_simple = FatalInterruption(step_name="sp_node2", reason="Crash")
    assert fatal_simple.status_code == 500

    cfg = ConfigurationError("Bad config", details={"key": "max_retries"})
    assert cfg.status_code == 500
    assert cfg.error_code == ErrorCodes.CONFIGURATION_ERROR.value

    cfg_simple = ConfigurationError("Bad config simple")
    assert cfg_simple.status_code == 500

    conf = ConflictError("Resource state conflict", details={"state": "locked"})
    assert conf.status_code == 409
    assert conf.error_code == ErrorCodes.CONFLICT_ERROR.value

    conf_simple = ConflictError("Simple conflict")
    assert conf_simple.status_code == 409

    perm = PermissionDeniedError("Access restricted", details={"user": "usr_anon"})
    assert perm.status_code == 403
    assert perm.error_code == ErrorCodes.PERMISSION_DENIED.value

    perm_simple = PermissionDeniedError()
    assert perm_simple.status_code == 403

    serv = ServiceUnavailableError("Upstream timeout", details={"upstream": "gemini"})
    assert serv.status_code == 503
    assert serv.error_code == ErrorCodes.SERVICE_UNAVAILABLE.value

    serv_simple = ServiceUnavailableError()
    assert serv_simple.status_code == 503

    auth = AuthenticationError("Invalid token", details={"token": "expired"})
    assert auth.status_code == 401
    assert auth.error_code == ErrorCodes.AUTHENTICATION_FAILED.value

    auth_simple = AuthenticationError()
    assert auth_simple.status_code == 401

    sec = SecurityViolationError("SQL Injection detected", details={"threat": "high"})
    assert sec.status_code == 400
    assert sec.error_code == ErrorCodes.SECURITY_VIOLATION.value

    sec_simple = SecurityViolationError("Prompt injection")
    assert sec_simple.status_code == 400

    wf_exec = WorkflowExecutionError(
        step_id="sp_def",
        task_key="task_key_1",
        original_error=ValueError("inner err"),
        details={"attempt": 2},
    )
    assert wf_exec.status_code == 500
    assert wf_exec.error_code == ErrorCodes.WORKFLOW_EXECUTION_FAILED.value

    wf_comp = WorkflowCompilationError(step_id="sp_def", message="Missing root node")
    assert wf_comp.status_code == 422
    assert wf_comp.error_code == ErrorCodes.WORKFLOW_COMPILATION_ERROR.value
    assert wf_comp.step_id == "sp_def"

    tok = TokenLimitExceededError("Context window exceeded", details={"tokens": 150000})
    assert tok.status_code == 413
    assert tok.error_code == ErrorCodes.TOKEN_LIMIT_EXCEEDED.value

    tok_simple = TokenLimitExceededError()
    assert tok_simple.status_code == 413

    inp = MissingInputMappingError("step_1.output", "dict", "KeyError")
    assert inp.status_code == 400
    assert inp.error_code == ErrorCodes.INPUT_RESOLUTION_FAILED.value

    xai = MissingXaiExtensionError("xai_matrix_graph", step_id="sp_matrix")
    assert xai.status_code == 400
    assert xai.error_code == ErrorCodes.MISSING_XAI_EXTENSION.value

    xai_simple = MissingXaiExtensionError("xai_plain")
    assert xai_simple.status_code == 400

    route = MissingRoutingModeError("steps.mode")
    assert route.status_code == 400
    assert route.error_code == ErrorCodes.MISSING_ROUTING_MODE.value


def test_llm_validation_exceptions() -> None:
    """Test LLMSchemaValidationError, LogicalValidationError, and SemanticEvidenceError."""
    schema_err = LLMSchemaValidationError(
        raw_llm_payload='{"invalid": true}',
        validation_error_msg="Missing field 'result'",
        is_eof=True,
        token_usage={"total_tokens": 120},
    )
    assert schema_err.status_code == 500
    assert schema_err.error_code == ErrorCodes.AGENT_SCHEMA_VALIDATION_FAILED.value
    assert schema_err.raw_llm_payload == '{"invalid": true}'
    assert schema_err.is_eof is True
    assert schema_err.token_usage == {"total_tokens": 120}

    syntax_err = PydanticSyntaxError(
        raw_llm_payload="bad json",
        validation_error_msg="JSON decode error",
    )
    assert syntax_err.status_code == 500

    logic_err = LogicalValidationError("Claim is contradictory")
    assert logic_err.status_code == 500
    assert logic_err.error_code == ErrorCodes.AGENT_LOGICAL_VALIDATION_FAILED.value
    assert logic_err.validation_error_msg == "Claim is contradictory"

    evidence_err = SemanticEvidenceError("Evidence quote not found in source text")
    assert evidence_err.status_code == 400
    assert evidence_err.error_code == ErrorCodes.AGENT_LOGICAL_VALIDATION_FAILED.value

    evidence_custom = SemanticEvidenceError("Quote mismatch", details={"error_code": "CUSTOM_EVIDENCE_ERROR"})
    assert evidence_custom.status_code == 400
    assert evidence_custom.error_code == "CUSTOM_EVIDENCE_ERROR"
