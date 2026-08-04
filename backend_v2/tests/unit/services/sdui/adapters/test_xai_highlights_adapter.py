"""Unit tests for the XAI Highlights adapter."""

import pytest
from pydantic import ValidationError

from backend_v2.models.enums import VisualIntent, XaiExtensionType
from backend_v2.models.state import TraceEvent
from backend_v2.models.v2_core import ExecutionRecord, I18nText, OutputProfile
from backend_v2.models.view.sdui import AccordionBlock
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext
from backend_v2.services.sdui.adapters.xai_highlights_adapter import XaiHighlightsAdapter


@pytest.fixture
def valid_output_profile_fixture() -> OutputProfile:
    """Fixture for a valid output profile to use in tests."""
    return OutputProfile(
        id="prf_0123456789abcdef",
        slug="test-profile",
        workflow_id="wfw_test",
        name=I18nText(default_locale="en", translations={"en": "Test Profile"}),
        layouts=[],
        extension_labels={
            XaiExtensionType.COACHING: I18nText(default_locale="en", translations={"en": "Coaching"}),
            XaiExtensionType.FALSIFICATION: I18nText(default_locale="en", translations={"en": "Falsification"}),
            XaiExtensionType.REMEDIATION_STEPS: I18nText(default_locale="en", translations={"en": "Remediation"}),
        },
        visible_block_extensions=[
            XaiExtensionType.COACHING,
            XaiExtensionType.FALSIFICATION,
            XaiExtensionType.REMEDIATION_STEPS,
        ],
    )


def test_build_empty_execution_trace_returns_empty_list(valid_output_profile_fixture: OutputProfile) -> None:
    """Boundary: empty execution trace returns empty list."""
    execution = ExecutionRecord(
        id="exe_0123456789abcdef",
        workflow_id="wfw_test",
        execution_trace=[],
    )
    context = AdapterContext(
        execution=execution,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=valid_output_profile_fixture,
        profile_cache=None,
        user_name=None,
        org_name=None,
        synthesis_md=None,
    )
    blocks = XaiHighlightsAdapter.build(context)
    assert blocks == []


def test_build_single_extension_group_returns_blocks(valid_output_profile_fixture: OutputProfile) -> None:
    """Positive: single extension group parses from trace."""
    execution = ExecutionRecord(
        id="exe_0123456789abcdef",
        workflow_id="wfw_test",
        execution_trace=[
            TraceEvent(
                event_type="output",
                step_name="step_1",
                content={
                    "step_id": "step_1",
                    "block_id": "block_1",
                    "payload": {"extensions": {"coaching": "Good job!\\nKeep it up!"}},
                },
            )
        ],
    )

    context = AdapterContext(
        execution=execution,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=valid_output_profile_fixture,
        profile_cache=None,
        user_name=None,
        org_name=None,
        synthesis_md=None,
    )
    blocks = XaiHighlightsAdapter.build(context)
    assert len(blocks) == 1
    assert isinstance(blocks[0], AccordionBlock)
    assert blocks[0].title == "Coaching"
    assert blocks[0].severity == VisualIntent.SUCCESS.value
    assert len(blocks[0].children) == 1


def test_build_multiple_extension_groups_flattens_all(valid_output_profile_fixture: OutputProfile) -> None:
    """Positive: multiple extensions from trace are correctly extracted."""
    execution = ExecutionRecord(
        id="exe_0123456789abcdef",
        workflow_id="wfw_test",
        execution_trace=[
            TraceEvent(
                event_type="output",
                step_name="step_1",
                content={
                    "step_id": "step_1",
                    "block_id": "block_1",
                    "payload": {"extensions": {"coaching": "Good job!", "falsification": "Bad logic!"}},
                },
            )
        ],
    )
    context = AdapterContext(
        execution=execution,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=valid_output_profile_fixture,
        profile_cache=None,
        user_name=None,
        org_name=None,
        synthesis_md=None,
    )

    blocks = XaiHighlightsAdapter.build(context)
    assert len(blocks) == 2
    titles = [b.title for b in blocks if isinstance(b, AccordionBlock)]
    assert "Coaching" in titles
    assert "Falsification" in titles


def test_build_does_not_mutate_context(valid_output_profile_fixture: OutputProfile) -> None:
    """Negative: context remains frozen after the call."""
    execution = ExecutionRecord(id="exe_0123456789abcdef", workflow_id="wfw_test", execution_trace=[])
    context = AdapterContext(
        execution=execution,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=valid_output_profile_fixture,
        profile_cache=None,
        user_name=None,
        org_name=None,
        synthesis_md=None,
    )

    XaiHighlightsAdapter.build(context)

    with pytest.raises(ValidationError):
        context.locale = "fi"  # type: ignore[misc]
