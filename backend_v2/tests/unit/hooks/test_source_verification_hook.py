"""Unit tests for Source Verification Hook."""

from unittest.mock import AsyncMock, patch

import pytest

from backend_v2.core.hook_registry import HookDependencies, HookState, hook_registry
from backend_v2.exceptions import AppException
from backend_v2.hooks.source_verification_hook import source_verification_hook
from backend_v2.models.domain.source_verification import (
    SourceVerificationResultDTO,
    SourceVerificationStatus,
    VerifiedSourceDTO,
)
from backend_v2.models.dtos.source_extraction_schema import SourceVerificationInputsDTO


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


def test_source_verification_hook_registered_in_hook_registry() -> None:
    """TC-HOOK-00: Hook is properly registered in hook_registry."""
    hook_fn = hook_registry.get_hook("source_verification")
    assert hook_fn is source_verification_hook


@pytest.mark.asyncio
async def test_source_verification_hook_empty_inputs(mock_deps: HookDependencies) -> None:
    """TC-HOOK-01: Empty inputs returns complete empty envelope without triggering service."""
    state = HookState(
        execution_id="exe_1111222233334444",
        workflow_id="wor_1111222233334444",
        metadata={},
        global_context_vars={},
        inputs={},
    )

    result = await source_verification_hook(state, mock_deps)

    assert result.success is True
    assert result.state_delta is not None
    assert "verified_sources" in result.state_delta
    payload = result.state_delta["verified_sources"]
    assert isinstance(payload, SourceVerificationResultDTO)
    assert payload.total_claims == 0
    assert payload.verified_count == 0
    assert payload.hallucination_count == 0
    assert payload.claims == []
    assert payload.verification_timestamp != ""


@pytest.mark.asyncio
async def test_source_verification_hook_empty_prior_analysis(mock_deps: HookDependencies) -> None:
    """TC-HOOK-01B: Prior analysis with empty string returns zero claims envelope."""
    state = HookState(
        execution_id="exe_1111222233334444",
        workflow_id="wor_1111222233334444",
        metadata={},
        global_context_vars={},
        inputs={"prior_analysis": ""},
    )

    result = await source_verification_hook(state, mock_deps)

    assert result.success is True
    assert result.state_delta is not None
    payload = result.state_delta["verified_sources"]
    assert isinstance(payload, SourceVerificationResultDTO)
    assert payload.total_claims == 0
    assert payload.claims == []


@pytest.mark.asyncio
async def test_source_verification_hook_whitespace_prior_analysis_returns_zero_claims(
    mock_deps: HookDependencies,
) -> None:
    """TC-HOOK-01C: Whitespace-only prior analysis returns zero claims envelope."""
    state = HookState(
        execution_id="exe_1111222233334444",
        workflow_id="wor_1111222233334444",
        metadata={},
        global_context_vars={},
        inputs={"prior_analysis": "   \n\t  "},
    )

    result = await source_verification_hook(state, mock_deps)

    assert result.success is True
    assert result.state_delta is not None
    payload = result.state_delta["verified_sources"]
    assert isinstance(payload, SourceVerificationResultDTO)
    assert payload.total_claims == 0
    assert payload.claims == []


@pytest.mark.asyncio
async def test_source_verification_hook_short_text_short_circuit(mock_deps: HookDependencies) -> None:
    """TC-HOOK-02: Short document text (< 15 chars) returns complete empty envelope."""
    state = HookState(
        execution_id="exe_1111222233334444",
        workflow_id="wor_1111222233334444",
        metadata={},
        global_context_vars={},
        inputs={"document_text": "too short"},
    )

    result = await source_verification_hook(state, mock_deps)

    assert result.success is True
    assert result.state_delta is not None
    payload = result.state_delta["verified_sources"]
    assert isinstance(payload, SourceVerificationResultDTO)
    assert payload.total_claims == 0
    assert payload.claims == []


@pytest.mark.asyncio
@patch("backend_v2.hooks.source_verification_hook.SourceVerificationService")
async def test_source_verification_hook_success(mock_service_cls: AsyncMock, mock_deps: HookDependencies) -> None:
    """TC-HOOK-03: Valid document text delegates to SourceVerificationService and preserves typed results."""
    mock_instance = AsyncMock()
    mock_service_cls.return_value = mock_instance

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
    )
    mock_instance.run_full_verification.return_value = mock_result_dto

    state = HookState(
        execution_id="exe_1111222233334444",
        workflow_id="wor_1111222233334444",
        metadata={},
        global_context_vars={},
        inputs={"document_text": "This is a valid long document text discussing quantum supremacy achievements."},
    )

    result = await source_verification_hook(state, mock_deps)

    assert result.success is True
    assert result.state_delta is not None
    payload = result.state_delta["verified_sources"]
    assert isinstance(payload, SourceVerificationResultDTO)
    assert payload.total_claims == 1
    assert payload.verified_count == 1
    assert len(payload.claims) == 1
    assert payload.claims[0].status == SourceVerificationStatus.VERIFIED
    mock_service_cls.assert_called_once_with(comp_repo=mock_deps.comp_repo, system_repo=mock_deps.system_repo)


@pytest.mark.asyncio
async def test_source_verification_hook_invalid_input_type(mock_deps: HookDependencies) -> None:
    """TC-HOOK-04: Non-string and non-dict inputs raise validation AppException."""
    state = HookState(
        execution_id="exe_1111222233334444",
        workflow_id="wor_1111222233334444",
        metadata={},
        global_context_vars={},
        inputs={"document_text": 12345},  # Invalid type for document_text
    )

    with pytest.raises(AppException) as exc:
        await source_verification_hook(state, mock_deps)

    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_source_verification_hook_invalid_general_input_type(mock_deps: HookDependencies) -> None:
    """TC-HOOK-04B: Non-dict non-BaseModel input raises validation AppException."""
    state = HookState(
        execution_id="exe_1111222233334444",
        workflow_id="wor_1111222233334444",
        metadata={},
        global_context_vars={},
        inputs={},
    )
    object.__setattr__(state, "inputs", "invalid string inputs")

    with pytest.raises(AppException) as exc:
        await source_verification_hook(state, mock_deps)

    assert exc.value.status_code == 400


@pytest.mark.asyncio
@patch("backend_v2.hooks.source_verification_hook.SourceVerificationService")
async def test_source_verification_hook_multi_key_string_inputs(
    mock_service_cls: AsyncMock, mock_deps: HookDependencies
) -> None:
    """TC-HOOK-05: Non-recognized key inputs synthesize string text parts for verification."""
    mock_instance = AsyncMock()
    mock_service_cls.return_value = mock_instance
    mock_instance.run_full_verification.return_value = SourceVerificationResultDTO(
        claims=[],
        verification_timestamp="2026-08-23T12:00:00Z",
        total_claims=0,
        verified_count=0,
        hallucination_count=0,
    )

    state = HookState(
        execution_id="exe_1111222233334444",
        workflow_id="wor_1111222233334444",
        metadata={},
        global_context_vars={},
        inputs={"section_a": "First paragraph text here.", "section_b": "Second paragraph text here."},
    )

    result = await source_verification_hook(state, mock_deps)

    assert result.success is True
    mock_instance.run_full_verification.assert_called_once_with(
        "First paragraph text here.\n\nSecond paragraph text here."
    )


@pytest.mark.asyncio
async def test_source_verification_hook_multi_key_non_string_raises(mock_deps: HookDependencies) -> None:
    """TC-HOOK-05B: Multi-key inputs containing non-string value raise validation AppException."""
    state = HookState(
        execution_id="exe_1111222233334444",
        workflow_id="wor_1111222233334444",
        metadata={},
        global_context_vars={},
        inputs={"section_a": "First paragraph text here.", "section_b": 12345},
    )

    with pytest.raises(AppException) as exc:
        await source_verification_hook(state, mock_deps)

    assert exc.value.status_code == 400


@pytest.mark.asyncio
@patch("backend_v2.hooks.source_verification_hook.SourceVerificationService")
async def test_source_verification_hook_dto_inputs_handled_safely(
    mock_service_cls: AsyncMock, mock_deps: HookDependencies
) -> None:
    """TC-HOOK-05C: SourceVerificationInputsDTO passed as state.inputs delegates safely."""
    mock_instance = AsyncMock()
    mock_service_cls.return_value = mock_instance
    mock_instance.run_full_verification.return_value = SourceVerificationResultDTO(
        claims=[],
        verification_timestamp="2026-08-23T12:00:00Z",
        total_claims=0,
        verified_count=0,
        hallucination_count=0,
    )

    state = HookState(
        execution_id="exe_1111222233334444",
        workflow_id="wor_1111222233334444",
        metadata={},
        global_context_vars={},
        inputs={},
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
async def test_source_verification_hook_invalid_dto_raises(mock_deps: HookDependencies) -> None:
    """TC-HOOK-05D: Non-SourceVerificationInputsDTO BaseModel raises AppException."""
    from backend_v2.models.core_base import V2CoreBase

    class OtherDTO(V2CoreBase):
        name: str

    state = HookState(
        execution_id="exe_1111222233334444",
        workflow_id="wor_1111222233334444",
        metadata={},
        global_context_vars={},
        inputs={},
    )
    object.__setattr__(state, "inputs", OtherDTO(name="test"))

    with pytest.raises(AppException) as exc:
        await source_verification_hook(state, mock_deps)

    assert exc.value.status_code == 400


@pytest.mark.asyncio
@patch("backend_v2.hooks.source_verification_hook.SourceVerificationService")
async def test_source_verification_hook_service_error_propagates(
    mock_service_cls: AsyncMock, mock_deps: HookDependencies
) -> None:
    """TC-HOOK-06: Exceptions from SourceVerificationService propagate cleanly."""
    mock_instance = AsyncMock()
    mock_service_cls.return_value = mock_instance
    mock_instance.run_full_verification.side_effect = AppException(message="Fatal verification error", status_code=502)

    state = HookState(
        execution_id="exe_1111222233334444",
        workflow_id="wor_1111222233334444",
        metadata={},
        global_context_vars={},
        inputs={"document_text": "This is valid text that encounters service failure."},
    )

    with pytest.raises(AppException) as exc:
        await source_verification_hook(state, mock_deps)

    assert exc.value.status_code == 502
