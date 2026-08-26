import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.enums import XaiExtensionType
from backend_v2.models.v2_core import I18nText, OutputProfile
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext
from backend_v2.services.sdui.adapters.variance_adapter import VarianceAdapter


def test_build_missing_execution_raises_app_exception() -> None:
    profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(translations={"en": "Test"}),
        content_blocks=[],
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
    from backend_v2.models.v2_core import ExecutionRecord

    profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(translations={"en": "Test"}),
        content_blocks=[],
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
    from backend_v2.models.enums import VisualIntent
    from backend_v2.models.v2_core import ExecutionRecord, ExtensionMetricsDTO, RenderedSynthesisCache
    from backend_v2.models.view.sdui import AlertBlock, MarkdownBlock, ParagraphBlock, SduiMetrics1DBlock

    profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(translations={"en": "Test"}),
        content_blocks=[],
        visible_workflow_extensions=[XaiExtensionType.VARIANCE_VALIDATION],
        extension_labels={
            XaiExtensionType.VARIANCE_VALIDATION: I18nText(
                translations={"en": "Variance Validation", "fi": "Varianssivalidointi"}
            )
        },
        metric_mappings={
            "variance_mechanical": I18nText(translations={"en": "Mechanical"}),
            "variance_cognitive": I18nText(translations={"en": "Cognitive"}),
            "variance_total": I18nText(translations={"en": "Total Variance"}),
            "alignment_verdict": I18nText(translations={"en": "Alignment Verdict"}),
            "alignment_aligned": I18nText(translations={"en": "Aligned"}),
            "alignment_misaligned": I18nText(translations={"en": "Misaligned"}),
            "variance_fallback_explanation": I18nText(translations={"en": "Fallback: {} {}"}),
        },
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
        row_explanations={"variance_validation": "Detailed LLM variance explanation."},
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
    assert blocks[1].text == "Detailed LLM variance explanation."
    metrics_block = blocks[2]
    assert isinstance(metrics_block, SduiMetrics1DBlock)

    row_dto = metrics_block.axes[0]
    assert row_dto.row_explanation == ""
    alert_block = row_dto.inner_sdui_blocks[1]
    assert isinstance(alert_block, AlertBlock)
    assert alert_block.severity == VisualIntent.INFO
    assert "Alignment Verdict: Aligned" in alert_block.text


def test_build_success_with_fallback_explanation() -> None:
    from backend_v2.models.enums import VisualIntent
    from backend_v2.models.v2_core import ExecutionRecord, ExtensionMetricsDTO, RenderedSynthesisCache
    from backend_v2.models.view.sdui import AlertBlock, MarkdownBlock, ParagraphBlock, SduiMetrics1DBlock

    profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(translations={"en": "Test"}),
        content_blocks=[],
        visible_workflow_extensions=[XaiExtensionType.VARIANCE_VALIDATION],
        extension_labels={
            XaiExtensionType.VARIANCE_VALIDATION: I18nText(
                translations={"en": "Variance Validation", "fi": "Varianssivalidointi"}
            )
        },
        metric_mappings={
            "variance_mechanical": I18nText(translations={"en": "Mechanical"}),
            "variance_cognitive": I18nText(translations={"en": "Cognitive"}),
            "variance_total": I18nText(translations={"en": "Total Variance"}),
            "alignment_verdict": I18nText(translations={"en": "Alignment Verdict"}),
            "alignment_aligned": I18nText(translations={"en": "Aligned"}),
            "alignment_misaligned": I18nText(translations={"en": "Misaligned"}),
            "variance_fallback_explanation": I18nText(translations={"en": "Fallback: {} {}"}),
        },
    )
    execution = ExecutionRecord(
        id="ex_0123456789abcdef0123456789abcdef",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        execution_trace=[],
        context_variables={},
    )
    cache = RenderedSynthesisCache(
        extension_metrics=ExtensionMetricsDTO(
            authenticity_score=45.0,
            performative_phrases_count=5.0,
            variance_score=50.0,
            alignment_verdict="MISALIGNED",
        ),
        row_explanations={},
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
    assert isinstance(blocks[1], ParagraphBlock)
    assert blocks[1].text == "Fallback: 5.0 45.0"
    metrics_block = blocks[2]
    assert isinstance(metrics_block, SduiMetrics1DBlock)
    row_dto = metrics_block.axes[0]
    alert_block = row_dto.inner_sdui_blocks[1]
    assert isinstance(alert_block, AlertBlock)
    assert alert_block.severity == VisualIntent.WARNING
    assert "Alignment Verdict: Misaligned" in alert_block.text


def test_build_incomplete_metrics_raises_app_exception() -> None:
    from backend_v2.models.v2_core import ExecutionRecord, ExtensionMetricsDTO, RenderedSynthesisCache

    profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(translations={"en": "Test"}),
        content_blocks=[],
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
            authenticity_score=None,
            performative_phrases_count=2.0,
            variance_score=15.0,
            alignment_verdict="ALIGNED",
        ),
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
        VarianceAdapter.build(context)

    assert exc_info.value.status_code == 500
    assert "metrics are incomplete" in exc_info.value.message


def test_build_missing_metric_mappings_raises_app_exception() -> None:
    from backend_v2.models.v2_core import ExecutionRecord, ExtensionMetricsDTO, RenderedSynthesisCache

    profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(translations={"en": "Test"}),
        content_blocks=[],
        visible_workflow_extensions=[XaiExtensionType.VARIANCE_VALIDATION],
        metric_mappings={},
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
        VarianceAdapter.build(context)

    assert exc_info.value.status_code == 500
    assert "Missing metric_mappings translation" in exc_info.value.message


def test_build_missing_extension_labels_raises_app_exception() -> None:
    from backend_v2.models.v2_core import ExecutionRecord, ExtensionMetricsDTO, RenderedSynthesisCache

    profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(translations={"en": "Test"}),
        content_blocks=[],
        visible_workflow_extensions=[XaiExtensionType.VARIANCE_VALIDATION],
        extension_labels={},
        metric_mappings={
            "variance_mechanical": I18nText(translations={"en": "Mechanical"}),
            "variance_cognitive": I18nText(translations={"en": "Cognitive"}),
            "variance_total": I18nText(translations={"en": "Total Variance"}),
            "alignment_verdict": I18nText(translations={"en": "Alignment Verdict"}),
            "alignment_aligned": I18nText(translations={"en": "Aligned"}),
            "alignment_misaligned": I18nText(translations={"en": "Misaligned"}),
            "variance_fallback_explanation": I18nText(translations={"en": "Fallback: {} {}"}),
        },
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
        VarianceAdapter.build(context)

    assert exc_info.value.status_code == 500
    assert "Missing extension_labels mapping" in exc_info.value.message


def test_build_data_starvation_returns_empty() -> None:
    from backend_v2.models.dtos.trace import DataStarvationEvent
    from backend_v2.models.v2_core import ExecutionRecord, RenderedSynthesisCache

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
    )
    cache = RenderedSynthesisCache(
        data_starvation=DataStarvationEvent(total_atoms=0, reason="Data starvation"),
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
    assert blocks == []
