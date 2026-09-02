from unittest.mock import MagicMock

import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.enums import XaiExtensionType
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.v2_core import (
    ExecutionRecord,
    ExtensionMetricsDTO,
    I18nText,
    OutputProfile,
    RenderedSynthesisCache,
)
from backend_v2.models.view.sdui import MarkdownBlock, ParagraphBlock, SduiMetrics1DBlock
from backend_v2.services.sdui.adapters.authenticity_adapter import AuthenticityAdapter
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext


@pytest.fixture(autouse=True)
def mock_authenticity_settings(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Mock Settings for AuthenticityAdapter tests to decouple from environment."""
    mock_settings = MagicMock()
    mock_settings.authenticity_threshold_high = 80.0
    mock_settings.authenticity_threshold_low = 50.0
    monkeypatch.setattr(
        "backend_v2.services.sdui.adapters.authenticity_adapter.get_settings",
        lambda: mock_settings,
    )
    return mock_settings


def _create_base_profile() -> OutputProfile:
    return OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(translations={"en": "Test"}),
        content_blocks=[],
        target_block_order=[],
        visible_workflow_extensions=[XaiExtensionType.AUTHENTICITY_EVALUATION],
    )


def test_build_not_requested_returns_empty() -> None:
    profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(translations={"en": "Test"}),
        content_blocks=[],
        target_block_order=[],
        visible_workflow_extensions=[],
    )
    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=profile,
        profile_cache=None,
        user_name=None,
        org_name=None,
        parsed_matrices={},
    )
    blocks = AuthenticityAdapter.build(context)
    assert blocks == []


def test_build_missing_execution_raises_app_exception() -> None:
    profile = _create_base_profile()
    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=profile,
        profile_cache=None,
        user_name=None,
        org_name=None,
        parsed_matrices={},
    )
    with pytest.raises(AppException) as exc_info:
        AuthenticityAdapter.build(context)

    assert exc_info.value.status_code == 500
    assert "context.execution cannot be None" in exc_info.value.message


def test_build_missing_metrics_raises_app_exception() -> None:
    profile = _create_base_profile()
    execution = ExecutionRecord(
        id="ex_0123456789abcdef0123456789abcdef",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        output_profile_id=profile.id,
        execution_trace=[],
        context_variables={},
        target_locale="fi",
        metadata=ExecutionMetadata(),
    )
    context = AdapterContext(
        execution=execution,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=profile,
        profile_cache=None,
        user_name=None,
        org_name=None,
        parsed_matrices={},
    )
    with pytest.raises(AppException) as exc_info:
        AuthenticityAdapter.build(context)

    assert exc_info.value.status_code == 500
    assert "Strict Fail-Fast Enforced: 'authenticity_evaluation' requested" in exc_info.value.message


def test_build_success_with_metrics() -> None:
    profile = _create_base_profile()
    execution = ExecutionRecord(
        id="ex_0123456789abcdef0123456789abcdef",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        output_profile_id=profile.id,
        execution_trace=[],
        context_variables={},
        target_locale="fi",
        metadata=ExecutionMetadata(),
    )
    cache = RenderedSynthesisCache(
        extension_metrics=ExtensionMetricsDTO(
            authenticity_score=85.0,
            performative_phrases_count=2.0,
            variance_score=15.0,
            alignment_verdict="ALIGNED",
        ),
        row_explanations={"authenticity_evaluation": "High degree of authenticity identified in execution traces."},
    )
    context = AdapterContext(
        execution=execution,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=profile,
        profile_cache=cache,
        user_name=None,
        org_name=None,
        parsed_matrices={},
    )

    blocks = AuthenticityAdapter.build(context)
    assert len(blocks) == 3
    assert isinstance(blocks[0], MarkdownBlock)
    assert blocks[0].text == "### Authenticity Evaluation"
    assert isinstance(blocks[1], ParagraphBlock)
    assert blocks[1].text == "High degree of authenticity identified in execution traces."
    assert isinstance(blocks[2], SduiMetrics1DBlock)


def test_build_starved_returns_empty() -> None:
    from backend_v2.models.dtos.trace import DataStarvationEvent

    profile = _create_base_profile()
    execution = ExecutionRecord(
        id="ex_0123456789abcdef0123456789abcdef",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        output_profile_id=profile.id,
        execution_trace=[],
        context_variables={},
        target_locale="fi",
        metadata=ExecutionMetadata(),
    )
    cache = RenderedSynthesisCache(
        data_starvation=DataStarvationEvent(
            total_atoms=0,
            reason="insufficient_tokens",
        )
    )
    context = AdapterContext(
        execution=execution,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=profile,
        profile_cache=cache,
        user_name=None,
        org_name=None,
        parsed_matrices={},
    )
    blocks = AuthenticityAdapter.build(context)
    assert blocks == []


def test_build_missing_authenticity_score_raises_app_exception() -> None:
    profile = _create_base_profile()
    execution = ExecutionRecord(
        id="ex_0123456789abcdef0123456789abcdef",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        output_profile_id=profile.id,
        execution_trace=[],
        context_variables={},
        target_locale="fi",
        metadata=ExecutionMetadata(),
    )
    cache = RenderedSynthesisCache(
        extension_metrics=ExtensionMetricsDTO(
            authenticity_score=None,
            performative_phrases_count=2.0,
            variance_score=15.0,
            alignment_verdict="ALIGNED",
        )
    )
    context = AdapterContext(
        execution=execution,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=profile,
        profile_cache=cache,
        user_name=None,
        org_name=None,
        parsed_matrices={},
    )
    with pytest.raises(AppException) as exc_info:
        AuthenticityAdapter.build(context)

    assert exc_info.value.status_code == 500
    assert "authenticity_score is missing" in exc_info.value.message


def test_build_fallback_explanation_and_medium_low_levels() -> None:
    profile = _create_base_profile()
    execution = ExecutionRecord(
        id="ex_0123456789abcdef0123456789abcdef",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        output_profile_id=profile.id,
        execution_trace=[],
        context_variables={},
        target_locale="fi",
        metadata=ExecutionMetadata(),
    )
    # Medium level with no custom row_explanation
    cache_med = RenderedSynthesisCache(
        extension_metrics=ExtensionMetricsDTO(
            authenticity_score=60.0,
            performative_phrases_count=2.0,
            variance_score=15.0,
            alignment_verdict="ALIGNED",
        )
    )
    context_med = AdapterContext(
        execution=execution,
        locale="fi",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=profile,
        profile_cache=cache_med,
        user_name=None,
        org_name=None,
        parsed_matrices={},
    )
    blocks_med = AuthenticityAdapter.build(context_med)
    assert len(blocks_med) == 3
    assert isinstance(blocks_med[0], MarkdownBlock)
    assert blocks_med[0].text == "### Autenttisuusarviointi"

    # Low level
    cache_low = RenderedSynthesisCache(
        extension_metrics=ExtensionMetricsDTO(
            authenticity_score=30.0,
            performative_phrases_count=5.0,
            variance_score=50.0,
            alignment_verdict="MISALIGNED",
        )
    )
    context_low = AdapterContext(
        execution=execution,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=profile,
        profile_cache=cache_low,
        user_name=None,
        org_name=None,
        parsed_matrices={},
    )
    blocks_low = AuthenticityAdapter.build(context_low)
    assert len(blocks_low) == 3
