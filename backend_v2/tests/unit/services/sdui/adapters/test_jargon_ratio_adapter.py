"""Unit tests for the JargonRatioAdapter SDUI adapter."""

import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.domain.linguistics import LinguisticsResultDTO, PerformativePatternDTO
from backend_v2.models.enums import VisualIntent
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.v2_core import (
    DataStarvationEvent,
    ExecutionRecord,
    I18nText,
    OutputProfile,
    RenderedSynthesisCache,
)
from backend_v2.models.view.sdui import AlertBlock, BulletListBlock, MarkdownBlock
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext
from backend_v2.services.sdui.adapters.jargon_ratio_adapter import JargonRatioAdapter


@pytest.fixture
def sample_profile() -> OutputProfile:
    """Fixture providing a valid OutputProfile for testing."""
    return OutputProfile(
        id="prf_0123456789abcdef",
        slug="test-profile",
        workflow_id="wfw_test",
        name=I18nText(translations={"en": "Test Profile"}),
        target_block_order=[],
    )


@pytest.fixture
def sample_execution() -> ExecutionRecord:
    """Fixture providing a valid ExecutionRecord for testing."""
    return ExecutionRecord(
        id="ex_0123456789abcdef0123456789abcdef",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        output_profile_id="prf_0123456789abcdef0123456789abcdef",
        execution_trace=[],
        context_variables={},
        target_locale="en",
        metadata=ExecutionMetadata(),
    )


def test_build_returns_empty_when_data_starved(sample_profile: OutputProfile) -> None:
    """Negative: returns empty list when context is data starved."""
    starved_cache = RenderedSynthesisCache(
        data_starvation=DataStarvationEvent(total_atoms=0, reason="insufficient_tokens")
    )
    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=sample_profile,
        profile_cache=starved_cache,
        user_name=None,
        org_name=None,
    )
    assert context.is_data_starved is True
    blocks = JargonRatioAdapter.build(context)
    assert blocks == []


def test_build_returns_empty_when_no_linguistics_in_context(
    sample_profile: OutputProfile, sample_execution: ExecutionRecord
) -> None:
    """Negative: returns empty list when step_linguistics is absent."""
    context = AdapterContext(
        execution=sample_execution,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=sample_profile,
        profile_cache=RenderedSynthesisCache(),
        user_name=None,
        org_name=None,
    )
    blocks = JargonRatioAdapter.build(context)
    assert blocks == []


def test_build_returns_clean_blocks_when_zero_patterns(
    sample_profile: OutputProfile, sample_execution: ExecutionRecord
) -> None:
    """Positive: returns MarkdownBlock and info AlertBlock when zero jargon is detected."""
    ling_dto = LinguisticsResultDTO(performative_patterns=[], total_word_count=500)
    exec_record = sample_execution.model_copy(
        update={"context_variables": {"step_linguistics": ling_dto.model_dump(mode="json")}}
    )
    context = AdapterContext(
        execution=exec_record,
        locale="fi",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=sample_profile,
        profile_cache=RenderedSynthesisCache(),
        user_name=None,
        org_name=None,
    )
    blocks = JargonRatioAdapter.build(context)
    assert len(blocks) == 2
    assert isinstance(blocks[0], MarkdownBlock)
    assert isinstance(blocks[1], AlertBlock)
    assert blocks[1].severity == VisualIntent.INFO
    assert "0.0%" in blocks[1].text


def test_build_returns_moderate_blocks_with_bullet_list(
    sample_profile: OutputProfile, sample_execution: ExecutionRecord
) -> None:
    """Positive: returns warning AlertBlock and BulletListBlock for moderate jargon load."""
    patterns = [
        PerformativePatternDTO(pattern_id="ptrn_1", detected_phrase="deep dive", category="filler"),
    ]
    ling_dto = LinguisticsResultDTO(performative_patterns=patterns, total_word_count=100)
    exec_record = sample_execution.model_copy(
        update={"context_variables": {"step_linguistics": ling_dto.model_dump(mode="json")}}
    )
    context = AdapterContext(
        execution=exec_record,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=sample_profile,
        profile_cache=RenderedSynthesisCache(),
        user_name=None,
        org_name=None,
    )
    blocks = JargonRatioAdapter.build(context)
    assert len(blocks) == 3
    assert isinstance(blocks[0], MarkdownBlock)
    assert isinstance(blocks[1], AlertBlock)
    assert blocks[1].severity == VisualIntent.WARNING
    assert "1.0%" in blocks[1].text
    assert isinstance(blocks[2], BulletListBlock)
    assert len(blocks[2].items) == 1
    assert "deep dive" in blocks[2].items[0].text


def test_build_returns_heavy_blocks_with_error_severity(
    sample_profile: OutputProfile, sample_execution: ExecutionRecord
) -> None:
    """Positive: returns error AlertBlock when density is high (>= 2.5%)."""
    patterns = [
        PerformativePatternDTO(pattern_id="ptrn_1", detected_phrase="game changer", category="filler"),
        PerformativePatternDTO(pattern_id="ptrn_2", detected_phrase="paradigm shift", category="filler"),
    ]
    ling_dto = LinguisticsResultDTO(performative_patterns=patterns, total_word_count=40)
    # Density: (2 / 40) * 100 = 5.0% >= 2.5% -> heavy
    exec_record = sample_execution.model_copy(
        update={"context_variables": {"step_linguistics": ling_dto.model_dump(mode="json")}}
    )
    context = AdapterContext(
        execution=exec_record,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=sample_profile,
        profile_cache=RenderedSynthesisCache(),
        user_name=None,
        org_name=None,
    )
    blocks = JargonRatioAdapter.build(context)
    assert len(blocks) == 3
    assert isinstance(blocks[1], AlertBlock)
    assert blocks[1].severity == VisualIntent.ERROR
    assert "5.0%" in blocks[1].text


def test_build_tampered_rules_dictionary_raises_app_exception(
    sample_profile: OutputProfile, sample_execution: ExecutionRecord, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Negative: Fail-Fast dictionary access raises AppException if rule mapping is missing."""
    monkeypatch.setattr("backend_v2.services.sdui.adapters.jargon_ratio_adapter.JARGON_RATIO_RULES", {})
    ling_dto = LinguisticsResultDTO(performative_patterns=[], total_word_count=100)
    exec_record = sample_execution.model_copy(
        update={"context_variables": {"step_linguistics": ling_dto.model_dump(mode="json")}}
    )
    context = AdapterContext(
        execution=exec_record,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=sample_profile,
        profile_cache=RenderedSynthesisCache(),
        user_name=None,
        org_name=None,
    )
    with pytest.raises(AppException) as excinfo:
        JargonRatioAdapter.build(context)
    assert excinfo.value.details["error_code"] == "CONFIGURATION_ERROR"
