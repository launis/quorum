import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.enums import XaiExtensionType
from backend_v2.models.v2_core import (
    ExecutionRecord,
    ExtensionMetricsDTO,
    I18nText,
    OutputProfile,
    RenderedSynthesisCache,
)
from backend_v2.models.view.sdui import MarkdownBlock, ParagraphBlock, SduiMetrics1DBlock
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext
from backend_v2.services.sdui.adapters.variance_adapter import VarianceAdapter


def test_build_missing_execution_raises_app_exception() -> None:
    profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(translations={"en": "Test"}),
        content_blocks=[],
        target_block_order=[],
        visible_workflow_extensions=[XaiExtensionType.VARIANCE_VALIDATION],
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

    with pytest.raises(AppException) as exc_info:
        VarianceAdapter.build(context)

    assert exc_info.value.status_code == 500
    assert "context.execution cannot be None" in exc_info.value.message


def test_build_missing_metrics_raises_app_exception() -> None:
    profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(translations={"en": "Test"}),
        content_blocks=[],
        target_block_order=[],
        visible_workflow_extensions=[XaiExtensionType.VARIANCE_VALIDATION],
    )
    execution = ExecutionRecord(
        id="ex_0123456789abcdef0123456789abcdef",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        execution_trace=[],
        context_variables={},
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
        VarianceAdapter.build(context)

    assert exc_info.value.status_code == 500
    assert "Strict Fail-Fast Enforced: 'variance_validation' requested" in exc_info.value.message


def test_build_empty_when_extension_not_requested() -> None:
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
    blocks = VarianceAdapter.build(context)
    assert blocks == []


def test_build_success_with_llm_explanation() -> None:
    profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(translations={"en": "Test"}),
        content_blocks=[],
        target_block_order=[],
        visible_workflow_extensions=[XaiExtensionType.VARIANCE_VALIDATION],
    )
    execution = ExecutionRecord(
        id="ex_0123456789abcdef0123456789abcdef",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        execution_trace=[],
        context_variables={},
    )
    cache = RenderedSynthesisCache(
        extension_metrics=ExtensionMetricsDTO(
            authenticity_score=85.0,
            performative_phrases_count=2.0,
            variance_score=15.0,
            alignment_verdict="ALIGNED",
        ),
        row_explanations={"variance_validation": "Model reasoning aligned closely with target assertions."},
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

    blocks = VarianceAdapter.build(context)
    assert len(blocks) == 3
    assert isinstance(blocks[0], MarkdownBlock)
    assert blocks[0].text == "### Variance Validation"
    assert isinstance(blocks[1], ParagraphBlock)
    assert blocks[1].text == "Model reasoning aligned closely with target assertions."
    assert isinstance(blocks[2], SduiMetrics1DBlock)


def test_build_starved_returns_empty() -> None:
    from backend_v2.models.dtos.trace import DataStarvationEvent

    profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(translations={"en": "Test"}),
        content_blocks=[],
        target_block_order=[],
        visible_workflow_extensions=[XaiExtensionType.VARIANCE_VALIDATION],
    )
    cache = RenderedSynthesisCache(
        data_starvation=DataStarvationEvent(total_atoms=0, reason="insufficient_tokens"),
    )
    context = AdapterContext(
        execution=None,
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
    blocks = VarianceAdapter.build(context)
    assert blocks == []


def test_build_misaligned_and_fallback_explanation() -> None:
    profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(translations={"en": "Test"}),
        content_blocks=[],
        target_block_order=[],
        visible_workflow_extensions=[XaiExtensionType.VARIANCE_VALIDATION],
    )
    execution = ExecutionRecord(
        id="ex_0123456789abcdef0123456789abcdef",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        execution_trace=[],
        context_variables={},
    )
    cache = RenderedSynthesisCache(
        extension_metrics=ExtensionMetricsDTO(
            authenticity_score=40.0,
            performative_phrases_count=6.0,
            variance_score=60.0,
            alignment_verdict="MISALIGNED",
        ),
    )
    context = AdapterContext(
        execution=execution,
        locale="fi",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=profile,
        profile_cache=cache,
        user_name=None,
        org_name=None,
        parsed_matrices={},
    )

    blocks = VarianceAdapter.build(context)
    assert len(blocks) == 3
    assert isinstance(blocks[0], MarkdownBlock)
    assert blocks[0].text == "### Varianssivalidointi"
    assert isinstance(blocks[1], ParagraphBlock)
    assert isinstance(blocks[2], SduiMetrics1DBlock)

