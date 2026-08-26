"""Unit tests for the WarningCardAdapter."""

import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.dtos.trace import DataStarvationEvent
from backend_v2.models.enums import VisualIntent
from backend_v2.models.v2_core import I18nText, OutputProfile, RenderedSynthesisCache
from backend_v2.models.view.sdui import AlertBlock
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext
from backend_v2.services.sdui.adapters.warning_card_adapter import WarningCardAdapter


@pytest.fixture
def base_output_profile() -> OutputProfile:
    """Fixture for an output profile."""
    return OutputProfile(
        id="prf_0123456789abcdef",
        slug="test-profile",
        workflow_id="wfw_test",
        name=I18nText(translations={"en": "Test Profile"}),
        target_block_order=[],
    )


def test_warning_card_adapter_starvation_success(base_output_profile: OutputProfile) -> None:
    """Tests that WarningCardAdapter returns an AlertBlock with expected fields upon starvation."""
    starvation_evt = DataStarvationEvent(total_atoms=0)
    cache = RenderedSynthesisCache(data_starvation=starvation_evt)

    # Test English locale
    context_en = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=base_output_profile,
        profile_cache=cache,
        user_name=None,
        org_name=None,
    )
    blocks_en = WarningCardAdapter.build(context_en)
    assert len(blocks_en) == 1
    block_en = blocks_en[0]
    assert isinstance(block_en, AlertBlock)
    assert block_en.id == "alert_starvation_starvation"
    assert block_en.severity == VisualIntent.WARNING
    assert block_en.text == "Evaluation data was insufficient to generate synthesis."
    assert block_en.exact_quotes == []
    assert block_en.citations == []

    # Test Finnish locale
    context_fi = AdapterContext(
        execution=None,
        locale="fi",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=base_output_profile,
        profile_cache=cache,
        user_name=None,
        org_name=None,
    )
    blocks_fi = WarningCardAdapter.build(context_fi)
    assert len(blocks_fi) == 1
    block_fi = blocks_fi[0]
    assert isinstance(block_fi, AlertBlock)
    assert block_fi.text == "Arviointiaineisto ei sisältänyt riittävästi havaintoja synteesin tuottamiseksi."


def test_warning_card_adapter_no_starvation(base_output_profile: OutputProfile) -> None:
    """Tests that WarningCardAdapter returns an empty list when data_starvation is None or profile_cache is None."""
    # Case 1: cache exists, data_starvation is None
    cache_no_starvation = RenderedSynthesisCache(data_starvation=None)
    context_1 = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=base_output_profile,
        profile_cache=cache_no_starvation,
        user_name=None,
        org_name=None,
    )
    assert WarningCardAdapter.build(context_1) == []

    # Case 2: profile_cache is None
    context_2 = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=base_output_profile,
        profile_cache=None,
        user_name=None,
        org_name=None,
    )
    assert WarningCardAdapter.build(context_2) == []


def test_warning_card_adapter_missing_rule_fail_fast(base_output_profile: OutputProfile) -> None:
    """Tests that an unmapped event_type triggers AppException with CONFIGURATION_ERROR."""
    starvation_unmapped = DataStarvationEvent.model_construct(
        total_atoms=0,
        event_type="unmapped_event_type",
        reason="Test unmapped event",
    )
    cache = RenderedSynthesisCache.model_construct(data_starvation=starvation_unmapped)

    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=base_output_profile,
        profile_cache=cache,
        user_name=None,
        org_name=None,
    )

    with pytest.raises(AppException) as exc_info:
        WarningCardAdapter.build(context)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details is not None
    assert exc_info.value.details.get("error_code") == "CONFIGURATION_ERROR"
