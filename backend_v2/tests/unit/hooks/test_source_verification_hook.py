"""Unit tests for Source Verification Hook."""

import datetime
from unittest.mock import AsyncMock, patch

import pytest

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    GlobalContextVarsDTO,
    HookDependencies,
    HookState,
    hook_registry,
)
from backend_v2.exceptions import AppException
from backend_v2.hooks.source_verification_hook import source_verification_hook
from backend_v2.models.domain.source_verification import (
    SourceVerificationResultDTO,
    SourceVerificationStatus,
    VerifiedSourceDTO,
)
from backend_v2.models.dtos.source_extraction_schema import SourceVerificationInputsDTO
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.v2_core import MCPAuditTrace


@pytest.fixture
def mock_deps() -> HookDependencies:
    """Mock dependencies fixture for HookDependencies."""
    return HookDependencies(
        exec_repo=AsyncMock(),
        workflow_repo=AsyncMock(),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        audit_repo=AsyncMock(),
        system_repo=AsyncMock(),
    )


import backend_v2.hooks.source_verification_hook as hook_module


def test_source_verification_hook_exports() -> None:
    """Verify that source_verification_hook exports expected symbols via __all__."""
    assert hook_module.__all__ == ["source_verification_hook"]
    assert hasattr(hook_module, "source_verification_hook")


def test_source_verification_hook_registered_in_hook_registry() -> None:
    """TC-HOOK-00: Hook is properly registered in hook_registry."""
    hook_fn = hook_registry.get_hook("source_verification_hook")
    assert hook_fn is source_verification_hook


@pytest.mark.asyncio
async def test_source_verification_hook_empty_inputs(mock_deps: HookDependencies) -> None:
    """TC-HOOK-01: Empty inputs returns complete empty envelope without triggering service."""
    state = HookState(
        execution_id="exe_1111222233334444",
        workflow_id="wor_1111222233334444",
        metadata=ExecutionMetadata(target_locale="en"),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=ExecutionInputsDTO(raw_inputs={}),
    )

    result = await source_verification_hook(state, mock_deps)

    assert result.success is True
    assert result.state_delta is not None
    assert result.state_delta.metadata_updates == {"mcp_audit_traces": []}
    assert result.state_delta.delta == {"external_evidence": ""}


@pytest.mark.asyncio
async def test_source_verification_hook_empty_prior_analysis(mock_deps: HookDependencies) -> None:
    """TC-HOOK-01B: Prior analysis with empty string returns zero claims envelope."""
    state = HookState(
        execution_id="exe_1111222233334444",
        workflow_id="wor_1111222233334444",
        metadata=ExecutionMetadata(target_locale="en"),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=ExecutionInputsDTO(raw_inputs={"prior_analysis": ""}),
    )

    result = await source_verification_hook(state, mock_deps)

    assert result.success is True
    assert result.state_delta is not None
    assert result.state_delta.metadata_updates == {"mcp_audit_traces": []}
    assert result.state_delta.delta == {"external_evidence": ""}


@pytest.mark.asyncio
async def test_source_verification_hook_whitespace_prior_analysis_returns_zero_claims(
    mock_deps: HookDependencies,
) -> None:
    """TC-HOOK-01C: Whitespace-only prior analysis returns zero claims envelope."""
    state = HookState(
        execution_id="exe_1111222233334444",
        workflow_id="wor_1111222233334444",
        metadata=ExecutionMetadata(target_locale="en"),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=ExecutionInputsDTO(raw_inputs={"prior_analysis": "   \n\t  "}),
    )

    result = await source_verification_hook(state, mock_deps)

    assert result.success is True
    assert result.state_delta is not None
    assert result.state_delta.metadata_updates == {"mcp_audit_traces": []}
    assert result.state_delta.delta == {"external_evidence": ""}


@pytest.mark.asyncio
async def test_source_verification_hook_short_text_short_circuit(mock_deps: HookDependencies) -> None:
    """TC-HOOK-02: Short document text (< 15 chars) returns complete empty envelope."""
    state = HookState(
        execution_id="exe_1111222233334444",
        workflow_id="wor_1111222233334444",
        metadata=ExecutionMetadata(target_locale="en"),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=ExecutionInputsDTO(raw_inputs={"document_text": "too short"}),
    )

    result = await source_verification_hook(state, mock_deps)

    assert result.success is True
    assert result.state_delta is not None
    assert result.state_delta.metadata_updates == {"mcp_audit_traces": []}
    assert result.state_delta.delta == {"external_evidence": ""}


@pytest.mark.asyncio
@patch("backend_v2.hooks.source_verification_hook.LLMClient.from_strategy")
@patch("backend_v2.hooks.source_verification_hook.SourceVerificationService")
async def test_source_verification_hook_success(
    mock_service_cls: AsyncMock,
    mock_from_strategy: AsyncMock,
    mock_deps: HookDependencies,
) -> None:
    """TC-HOOK-03: Valid document text delegates to SourceVerificationService and produces external_evidence XML and traces."""
    mock_llm_client = AsyncMock()
    mock_from_strategy.return_value = mock_llm_client

    mock_instance = AsyncMock()
    mock_service_cls.return_value = mock_instance

    mock_trace = MCPAuditTrace(
        id="tavily_12345678",
        tool_id="mcp_tavily_search",
        step_name="source_verification",
        query="Verify claim",
        reasoning="Fact checking",
        response_summary="Google claimed quantum supremacy in Nature in 2019.",
        source_urls=["https://nature.com/articles/s41586-019-1666-5"],
        timestamp=datetime.datetime.now(datetime.timezone.utc),
        duration_ms=100,
    )

    mock_result_dto = SourceVerificationResultDTO(
        claims=[
            VerifiedSourceDTO(
                claim_text="Quantum supremacy was demonstrated by Google in 2019",
                status=SourceVerificationStatus.VERIFIED,
                source_urls=["https://nature.com/articles/s41586-019-1666-5"],
                tavily_answer="Google claimed quantum supremacy in Nature in 2019.",
            )
        ],
        verification_timestamp="2026-08-23T12:00:00Z",
        total_claims=1,
        verified_count=1,
        hallucination_count=0,
        audit_traces=[mock_trace],
    )
    mock_instance.run_full_verification.return_value = mock_result_dto

    state = HookState(
        execution_id="exe_1111222233334444",
        workflow_id="wor_1111222233334444",
        metadata=ExecutionMetadata(target_locale="en"),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=ExecutionInputsDTO(
            raw_inputs={"document_text": "This is a valid long document text discussing quantum supremacy achievements."}
        ),
    )

    result = await source_verification_hook(state, mock_deps)

    assert result.success is True
    assert result.state_delta is not None
    assert result.state_delta.metadata_updates is not None
    assert "mcp_audit_traces" in result.state_delta.metadata_updates
    traces = result.state_delta.metadata_updates["mcp_audit_traces"]
    assert len(traces) == 1
    assert traces[0]["id"] == "tavily_12345678"

    assert "external_evidence" in result.state_delta.delta
    evidence_xml = result.state_delta.delta["external_evidence"]
    assert '<claim status="VERIFIED" query="Quantum supremacy was demonstrated by Google in 2019">' in evidence_xml
    assert "<answer>Google claimed quantum supremacy in Nature in 2019.</answer>" in evidence_xml


@pytest.mark.asyncio
async def test_source_verification_hook_missing_system_repo_raises() -> None:
    """TC-HOOK-03B: Missing system_repo in HookDependencies triggers Fail-Fast AppException."""
    deps_no_repo = HookDependencies(
        exec_repo=AsyncMock(),
        workflow_repo=AsyncMock(),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        audit_repo=AsyncMock(),
        system_repo=None,  # type: ignore[arg-type]
    )

    state = HookState(
        execution_id="exe_1111222233334444",
        workflow_id="wor_1111222233334444",
        metadata=ExecutionMetadata(target_locale="en"),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=ExecutionInputsDTO(
            raw_inputs={"document_text": "Valid document text that will fail due to missing system repo."}
        ),
    )

    with pytest.raises(AppException) as exc:
        await source_verification_hook(state, deps_no_repo)

    assert exc.value.status_code == 500


@pytest.mark.asyncio
async def test_source_verification_hook_invalid_input_type(mock_deps: HookDependencies) -> None:
    """TC-HOOK-04: Non-string and non-dict inputs raise validation AppException."""
    state = HookState(
        execution_id="exe_1111222233334444",
        workflow_id="wor_1111222233334444",
        metadata=ExecutionMetadata(target_locale="en"),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=ExecutionInputsDTO(raw_inputs={"document_text": 12345}),  # type: ignore[dict-item]
    )

    with pytest.raises(AppException) as exc:
        await source_verification_hook(state, mock_deps)

    assert exc.value.status_code == 400


@pytest.mark.asyncio
@patch("backend_v2.hooks.source_verification_hook.LLMClient.from_strategy")
@patch("backend_v2.hooks.source_verification_hook.SourceVerificationService")
async def test_source_verification_hook_multi_key_string_inputs(
    mock_service_cls: AsyncMock,
    mock_from_strategy: AsyncMock,
    mock_deps: HookDependencies,
) -> None:
    """TC-HOOK-05: Non-recognized key inputs synthesize string text parts for verification."""
    mock_from_strategy.return_value = AsyncMock()
    mock_instance = AsyncMock()
    mock_service_cls.return_value = mock_instance
    mock_instance.run_full_verification.return_value = SourceVerificationResultDTO(
        claims=[],
        verification_timestamp="2026-08-23T12:00:00Z",
        total_claims=0,
        verified_count=0,
        hallucination_count=0,
        audit_traces=[],
    )

    state = HookState(
        execution_id="exe_1111222233334444",
        workflow_id="wor_1111222233334444",
        metadata=ExecutionMetadata(target_locale="en"),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=ExecutionInputsDTO(
            raw_inputs={"section_a": "First paragraph text here.", "section_b": "Second paragraph text here."}
        ),
    )

    result = await source_verification_hook(state, mock_deps)

    assert result.success is True
    mock_instance.run_full_verification.assert_called_once_with(
        "First paragraph text here.\n\nSecond paragraph text here."
    )


@pytest.mark.asyncio
@patch("backend_v2.hooks.source_verification_hook.LLMClient.from_strategy")
@patch("backend_v2.hooks.source_verification_hook.SourceVerificationService")
async def test_source_verification_hook_dto_inputs_handled_safely(
    mock_service_cls: AsyncMock,
    mock_from_strategy: AsyncMock,
    mock_deps: HookDependencies,
) -> None:
    """TC-HOOK-05C: SourceVerificationInputsDTO passed as state.inputs delegates safely."""
    mock_from_strategy.return_value = AsyncMock()
    mock_instance = AsyncMock()
    mock_service_cls.return_value = mock_instance
    mock_instance.run_full_verification.return_value = SourceVerificationResultDTO(
        claims=[],
        verification_timestamp="2026-08-23T12:00:00Z",
        total_claims=0,
        verified_count=0,
        hallucination_count=0,
        audit_traces=[],
    )

    state = HookState(
        execution_id="exe_1111222233334444",
        workflow_id="wor_1111222233334444",
        metadata=ExecutionMetadata(target_locale="en"),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=ExecutionInputsDTO(raw_inputs={}),
    )
    object.__setattr__(
        state,
        "inputs",
        SourceVerificationInputsDTO(prior_analysis="Valid analytical text discussing scientific findings."),
    )

    result = await source_verification_hook(state, mock_deps)

    assert result.success is True
    mock_instance.run_full_verification.assert_called_once_with("Valid analytical text discussing scientific findings.")


@pytest.mark.asyncio
@patch("backend_v2.hooks.source_verification_hook.LLMClient.from_strategy")
@patch("backend_v2.hooks.source_verification_hook.SourceVerificationService")
async def test_source_verification_hook_service_error_propagates(
    mock_service_cls: AsyncMock,
    mock_from_strategy: AsyncMock,
    mock_deps: HookDependencies,
) -> None:
    """TC-HOOK-06: Exceptions from SourceVerificationService propagate cleanly."""
    mock_from_strategy.return_value = AsyncMock()
    mock_instance = AsyncMock()
    mock_service_cls.return_value = mock_instance
    mock_instance.run_full_verification.side_effect = AppException(message="Fatal verification error", status_code=502)

    state = HookState(
        execution_id="exe_1111222233334444",
        workflow_id="wor_1111222233334444",
        metadata=ExecutionMetadata(target_locale="en"),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=ExecutionInputsDTO(
            raw_inputs={"document_text": "This is valid text that encounters service failure."}
        ),
    )

    with pytest.raises(AppException) as exc:
        await source_verification_hook(state, mock_deps)

    assert exc.value.status_code == 502


@pytest.mark.asyncio
@patch("backend_v2.hooks.source_verification_hook.LLMClient.from_strategy")
@patch("backend_v2.hooks.source_verification_hook.SourceVerificationService")
async def test_source_verification_hook_raw_string_and_list_inputs(
    mock_service_cls: AsyncMock,
    mock_from_strategy: AsyncMock,
    mock_deps: HookDependencies,
) -> None:
    """TC-HOOK-07: Tests pure string inputs and list inputs."""
    mock_from_strategy.return_value = AsyncMock()
    mock_instance = AsyncMock()
    mock_service_cls.return_value = mock_instance
    mock_instance.run_full_verification.return_value = SourceVerificationResultDTO(
        claims=[],
        verification_timestamp="2026-08-23T12:00:00Z",
        total_claims=0,
        verified_count=0,
        hallucination_count=0,
        audit_traces=[],
    )

    # 1. Test pure string input
    state_str = HookState(
        execution_id="exe_1111222233334444",
        workflow_id="wor_1111222233334444",
        metadata=ExecutionMetadata(target_locale="en"),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=ExecutionInputsDTO(raw_inputs={}),
    )
    object.__setattr__(state_str, "inputs", "A direct string input for source checking.")

    result_str = await source_verification_hook(state_str, mock_deps)
    assert result_str.success is True
    mock_instance.run_full_verification.assert_called_with("A direct string input for source checking.")

    # 2. Test list of items input
    state_list = HookState(
        execution_id="exe_1111222233334444",
        workflow_id="wor_1111222233334444",
        metadata=ExecutionMetadata(target_locale="en"),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=ExecutionInputsDTO(raw_inputs={}),
    )
    object.__setattr__(state_list, "inputs", ["Line one of content.", "Line two of content."])

    result_list = await source_verification_hook(state_list, mock_deps)
    assert result_list.success is True
    mock_instance.run_full_verification.assert_called_with("Line one of content.\n\nLine two of content.")


@pytest.mark.asyncio
@patch("backend_v2.hooks.source_verification_hook.LLMClient.from_strategy")
@patch("backend_v2.hooks.source_verification_hook.SourceVerificationService")
async def test_source_verification_hook_generic_basemodel_and_non_app_exception(
    mock_service_cls: AsyncMock,
    mock_from_strategy: AsyncMock,
    mock_deps: HookDependencies,
) -> None:
    """TC-HOOK-08: Tests generic BaseModel inputs and non-AppException wrapping."""
    from pydantic import BaseModel

    class CustomDataModel(BaseModel):
        text: str

    mock_from_strategy.return_value = AsyncMock()
    mock_instance = AsyncMock()
    mock_service_cls.return_value = mock_instance
    mock_instance.run_full_verification.return_value = SourceVerificationResultDTO(
        claims=[],
        verification_timestamp="2026-08-23T12:00:00Z",
        total_claims=0,
        verified_count=0,
        hallucination_count=0,
        audit_traces=[],
    )

    state_bm = HookState(
        execution_id="exe_1111222233334444",
        workflow_id="wor_1111222233334444",
        metadata=ExecutionMetadata(target_locale="en"),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=ExecutionInputsDTO(raw_inputs={}),
    )
    object.__setattr__(state_bm, "inputs", CustomDataModel(text="Generic base model text for verification."))

    res = await source_verification_hook(state_bm, mock_deps)
    assert res.success is True

    # Test non-AppException wrapping into AppException(500)
    mock_instance.run_full_verification.side_effect = RuntimeError("Unexpected stdlib error")
    with pytest.raises(AppException) as exc_info:
        await source_verification_hook(state_bm, mock_deps)

    assert exc_info.value.status_code == 500
