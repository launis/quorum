from unittest.mock import MagicMock

import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.enums import VisualIntent, XaiExtensionType
from backend_v2.models.v2_core import (
    ExecutionRecord,
    ExtensionMetricsDTO,
    I18nText,
    OutputProfile,
    RenderedSynthesisCache,
)
from backend_v2.models.view.sdui import AlertBlock, MarkdownBlock, ParagraphBlock, SduiMetrics1DBlock
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


def _create_base_profile(
    metric_mappings: dict[str, I18nText] | None = None,
    extension_labels: dict[XaiExtensionType, I18nText] | None = None,
) -> OutputProfile:
    if metric_mappings is None:
        metric_mappings = {
            "jargon_score": I18nText(default_locale="en", translations={"en": "Jargon Score"}),
            "authenticity_level": I18nText(default_locale="en", translations={"en": "Authenticity Level"}),
            "level_high": I18nText(default_locale="en", translations={"en": "High"}),
            "level_medium": I18nText(default_locale="en", translations={"en": "Medium"}),
            "level_low": I18nText(default_locale="en", translations={"en": "Low"}),
            "authenticity_fallback_explanation": I18nText(
                default_locale="en",
                translations={"en": "Authenticity score is {}."},
            ),
        }
    if extension_labels is None:
        extension_labels = {
            XaiExtensionType.AUTHENTICITY_EVALUATION: I18nText(
                default_locale="en",
                translations={"en": "Authenticity Evaluation"},
            ),
        }
    return OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(default_locale="en", translations={"en": "Test"}),
        content_blocks=[],
        target_block_order=[],
        visible_workflow_extensions=[XaiExtensionType.AUTHENTICITY_EVALUATION],
        metric_mappings=metric_mappings,
        extension_labels=extension_labels,
    )


def test_build_not_requested_returns_empty() -> None:
    profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(default_locale="en", translations={"en": "Test"}),
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
        AuthenticityAdapter.build(context)

    assert exc_info.value.status_code == 500
    assert "extension_metrics is missing in cache" in exc_info.value.message


def test_build_missing_authenticity_score_raises_app_exception() -> None:
    profile = _create_base_profile()
    execution = ExecutionRecord(
        id="ex_0123456789abcdef0123456789abcdef",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        execution_trace=[],
        context_variables={},
    )
    cache = RenderedSynthesisCache(
        extension_metrics=ExtensionMetricsDTO(authenticity_score=None),
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


def test_build_missing_metric_mapping_key_raises_app_exception() -> None:
    profile = _create_base_profile(metric_mappings={})
    execution = ExecutionRecord(
        id="ex_0123456789abcdef0123456789abcdef",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        execution_trace=[],
        context_variables={},
    )
    cache = RenderedSynthesisCache(
        extension_metrics=ExtensionMetricsDTO(authenticity_score=85.0),
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
    assert "Missing metric_mappings translation" in exc_info.value.message


def test_build_missing_extension_label_raises_app_exception() -> None:
    profile = _create_base_profile(extension_labels={})
    execution = ExecutionRecord(
        id="ex_0123456789abcdef0123456789abcdef",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        execution_trace=[],
        context_variables={},
    )
    cache = RenderedSynthesisCache(
        extension_metrics=ExtensionMetricsDTO(authenticity_score=85.0),
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
    assert "Missing extension_labels mapping" in exc_info.value.message


@pytest.mark.parametrize(
    ("score", "expected_severity", "expected_level_text"),
    [
        (80.0, VisualIntent.INFO, "High"),
        (79.99, VisualIntent.WARNING, "Medium"),
        (50.0, VisualIntent.WARNING, "Medium"),
        (49.99, VisualIntent.ERROR, "Low"),
    ],
)
def test_build_boundary_classifications(
    score: float, expected_severity: VisualIntent, expected_level_text: str
) -> None:
    profile = _create_base_profile()
    execution = ExecutionRecord(
        id="ex_0123456789abcdef0123456789abcdef",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        execution_trace=[],
        context_variables={},
    )
    cache = RenderedSynthesisCache(
        extension_metrics=ExtensionMetricsDTO(authenticity_score=score),
        row_explanations={"authenticity_evaluation": "Detailed AI analysis."},
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
    assert blocks[1].text == "Detailed AI analysis."
    metrics_block = blocks[2]
    assert isinstance(metrics_block, SduiMetrics1DBlock)

    row_dto = metrics_block.axes[0]
    assert row_dto.row_explanation == ""
    alert_block = row_dto.inner_sdui_blocks[1]
    assert isinstance(alert_block, AlertBlock)
    assert alert_block.severity == expected_severity
    assert f"Authenticity Level: {expected_level_text}" in alert_block.text


def test_build_dynamic_settings_thresholds(monkeypatch: pytest.MonkeyPatch) -> None:
    mock_settings = MagicMock()
    mock_settings.authenticity_threshold_high = 90.0
    mock_settings.authenticity_threshold_low = 60.0
    monkeypatch.setattr(
        "backend_v2.services.sdui.adapters.authenticity_adapter.get_settings",
        lambda: mock_settings,
    )

    profile = _create_base_profile()
    execution = ExecutionRecord(
        id="ex_0123456789abcdef0123456789abcdef",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        execution_trace=[],
        context_variables={},
    )
    cache = RenderedSynthesisCache(
        extension_metrics=ExtensionMetricsDTO(authenticity_score=85.0),
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
    assert isinstance(blocks[1], ParagraphBlock)
    metrics_block = blocks[2]
    assert isinstance(metrics_block, SduiMetrics1DBlock)
    row_dto = metrics_block.axes[0]
    alert_block = row_dto.inner_sdui_blocks[1]
    assert isinstance(alert_block, AlertBlock)
    assert alert_block.severity == VisualIntent.WARNING
    assert "Authenticity Level: Medium" in alert_block.text


def test_authenticity_adapter_dual_logging_on_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    """Negative test: verify dual-logging pattern (logger.error with exc_info=True) before AppException."""
    from unittest.mock import MagicMock

    mock_logger_error = MagicMock()
    monkeypatch.setattr("backend_v2.services.sdui.adapters.authenticity_adapter.logger.error", mock_logger_error)

    profile = _create_base_profile()
    context = AdapterContext(
        execution=None,  # triggers exception
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

    with pytest.raises(AppException):
        AuthenticityAdapter.build(context)

    assert mock_logger_error.called
    _args, kwargs = mock_logger_error.call_args
    assert kwargs.get("exc_info") is True
