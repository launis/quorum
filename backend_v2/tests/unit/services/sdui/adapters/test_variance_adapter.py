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
        name=I18nText(default_locale="en", translations={"en": "Test"}),
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
        name=I18nText(default_locale="en", translations={"en": "Test"}),
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
