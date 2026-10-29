"""Unit tests for metadata hook and metadata domain DTOs."""

import pytest
from pydantic import ValidationError

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    GlobalContextVarsDTO,
    HookDependencies,
    HookState,
)
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.hooks.metadata import inject_step_metadata
from backend_v2.models.domain.metadata import (
    MetadataHookPayloadDTO,
    MetadataHookResultDTO,
    StepMetadataDTO,
)
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


def _create_hook_deps(repo: InMemoryUnifiedWorkflowRepository | None = None) -> HookDependencies:
    r = repo or InMemoryUnifiedWorkflowRepository()
    return HookDependencies(
        exec_repo=r,
        workflow_repo=r,
        comp_repo=r,
        prompt_block_repo=r,
        output_profile_repo=r,
        identity_repo=r,
        audit_repo=r,
        system_repo=r,
    )


def test_inject_step_metadata_empty_state() -> None:
    """Test behavior when state is None."""
    deps = _create_hook_deps()

    result = inject_step_metadata(None, deps)

    assert result.success is True
    assert result.state_delta is not None
    assert not result.state_delta.delta


def test_inject_step_metadata_missing_execution_id_fails() -> None:
    """Test missing execution_id raises AppException with VALIDATION_FAILED."""
    state = HookState(
        execution_id="",
        workflow_id="wf_1",
        step_id="step_1",
        inputs=ExecutionInputsDTO(raw_inputs={}),
        global_context_vars=GlobalContextVarsDTO(),
        metadata=ExecutionMetadata(),
    )
    deps = _create_hook_deps()

    with pytest.raises(AppException) as exc_info:
        inject_step_metadata(state, deps)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "state.execution_id is strictly required" in exc_info.value.message


def test_inject_step_metadata_missing_step_id_fails() -> None:
    """Test missing step_id raises AppException with VALIDATION_FAILED."""
    state = HookState(
        execution_id="exec_1",
        workflow_id="wf_1",
        step_id="",
        inputs=ExecutionInputsDTO(raw_inputs={}),
        global_context_vars=GlobalContextVarsDTO(),
        metadata=ExecutionMetadata(),
    )
    deps = _create_hook_deps()

    with pytest.raises(AppException) as exc_info:
        inject_step_metadata(state, deps)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "state.step_id is strictly required" in exc_info.value.message


def test_inject_step_metadata_missing_workflow_id_fails() -> None:
    """Test missing workflow_id raises AppException with VALIDATION_FAILED."""
    state = HookState(
        execution_id="exec_1",
        workflow_id="",
        step_id="step_1",
        inputs=ExecutionInputsDTO(raw_inputs={}),
        global_context_vars=GlobalContextVarsDTO(),
        metadata=ExecutionMetadata(),
    )
    deps = _create_hook_deps()

    with pytest.raises(AppException) as exc_info:
        inject_step_metadata(state, deps)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "state.workflow_id is strictly required" in exc_info.value.message


def test_inject_step_metadata_missing_global_context_vars_fails() -> None:
    """Test missing global_context_vars raises AppException with VALIDATION_FAILED."""
    state = HookState.model_construct(
        execution_id="exec_1",
        workflow_id="wf_1",
        step_id="step_1",
        inputs=ExecutionInputsDTO(raw_inputs={}),
        metadata=ExecutionMetadata(),
        global_context_vars=None,
    )
    deps = _create_hook_deps()

    with pytest.raises(AppException) as exc_info:
        inject_step_metadata(state, deps)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "state.global_context_vars is strictly required" in exc_info.value.message


def test_inject_step_metadata_custom_values() -> None:
    """Test metadata injection when specific IDs and initiator are provided."""
    state = HookState(
        execution_id="exec_555",
        workflow_id="wf_999",
        step_id="step_123",
        inputs=ExecutionInputsDTO(raw_inputs={}),
        global_context_vars=GlobalContextVarsDTO(initiator_id="usr_777"),
        metadata=ExecutionMetadata(),
    )
    deps = _create_hook_deps()

    result = inject_step_metadata(state, deps)

    assert result.success is True
    assert result.state_delta is not None
    assert isinstance(result.state_delta.delta, MetadataHookResultDTO)
    meta = result.state_delta.delta.step_metadata
    assert meta.execution_id == "exec_555"
    assert meta.workflow_id == "wf_999"
    assert meta.step_id == "step_123"
    assert meta.initiator_id == "usr_777"

    audit_sig = result.state_delta.delta.audit_signature
    assert audit_sig.startswith("step_123:exec_555:")


def test_inject_step_metadata_validation_failure() -> None:
    """Test that strict Pydantic validation fails if context vars contain invalid types."""
    # Since strict=True, passing an integer instead of a string for initiator_id fails at construction
    with pytest.raises(ValidationError):
        GlobalContextVarsDTO(initiator_id=12345)


def test_step_metadata_dto_unix_time_boundary_valid() -> None:
    """Test StepMetadataDTO accepts boundary value unix_time=0."""
    dto = StepMetadataDTO(
        execution_id="exe_0123456789abcdef",
        workflow_id="wor_0123456789abcdef",
        step_id="stp_0123456789abcdef",
        initiator_id="usr_0123456789abcdef",
        timestamp_isot="2026-10-29T00:00:00Z",
        unix_time=0,
    )
    assert dto.unix_time == 0
    assert dto.v2_engine is True


def test_step_metadata_dto_negative_unix_time_raises_app_exception() -> None:
    """Test StepMetadataDTO rejects negative unix_time (-1 boundary) with AppException."""
    with pytest.raises(AppException) as exc_info:
        StepMetadataDTO(
            execution_id="exe_0123456789abcdef",
            workflow_id="wor_0123456789abcdef",
            step_id="stp_0123456789abcdef",
            initiator_id="usr_0123456789abcdef",
            timestamp_isot="2026-10-29T00:00:00Z",
            unix_time=-1,
        )

    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED
    assert "unix_time must be >= 0, got -1" in exc_info.value.message


def test_metadata_hook_payload_dto_extra_field_forbidden() -> None:
    """Test MetadataHookPayloadDTO forbids unknown extra fields and empty initiator."""
    with pytest.raises(ValidationError):
        MetadataHookPayloadDTO.model_validate({"_sys_initiator_id": ""})

    with pytest.raises(ValidationError):
        MetadataHookPayloadDTO.model_validate({"unknown_field": "val"})
