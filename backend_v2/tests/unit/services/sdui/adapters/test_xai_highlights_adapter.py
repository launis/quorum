"""Unit tests for the XAI Highlights adapter."""

import pytest
from pydantic import ValidationError

from backend_v2.models.enums import VisualIntent
from backend_v2.models.v2_core import I18nText, OutputProfile
from backend_v2.models.view.sdui import AccordionBlock, AlertBlock
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
    )


def test_build_empty_extensions_returns_empty_list(valid_output_profile_fixture: OutputProfile) -> None:
    """Boundary: empty accumulated_extensions returns empty list."""
    context = AdapterContext(
        execution=None,
        locale="fi",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        accumulated_extensions={},
        profile=valid_output_profile_fixture,
        profile_cache=None,
    )
    blocks = XaiHighlightsAdapter.build(context)
    assert blocks == []


def test_build_single_extension_group_returns_blocks(valid_output_profile_fixture: OutputProfile) -> None:
    """Positive: single extension group flattens correctly."""
    accordion = AccordionBlock(
        title="Risk Flags",
        severity="error",
        icon_name=None,
        children=[AlertBlock(severity=VisualIntent.INFO, text="test", exact_quotes=[], citations=[])],
    )
    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        accumulated_extensions={"global_extensions": [accordion]},
        profile=valid_output_profile_fixture,
        profile_cache=None,
    )
    blocks = XaiHighlightsAdapter.build(context)
    assert len(blocks) == 1
    assert blocks[0] == accordion


def test_build_multiple_extension_groups_flattens_all(valid_output_profile_fixture: OutputProfile) -> None:
    """Positive: multiple extension groups are flattened in order."""
    block1 = AccordionBlock(title="A", severity="info", children=[])
    block2 = AccordionBlock(title="B", severity="info", children=[])
    block3 = AccordionBlock(title="C", severity="info", children=[])

    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        accumulated_extensions={
            "group_a": [block1],
            "group_b": [block2, block3],
        },
        profile=valid_output_profile_fixture,
        profile_cache=None,
    )

    blocks = XaiHighlightsAdapter.build(context)
    assert len(blocks) == 3
    assert blocks == [block1, block2, block3]


def test_build_does_not_mutate_context(valid_output_profile_fixture: OutputProfile) -> None:
    """Negative: context remains frozen after the call."""
    block1 = AccordionBlock(title="A", severity="info", children=[])
    accumulated_extensions = {"group_a": [block1]}

    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        accumulated_extensions=accumulated_extensions.copy(),
        profile=valid_output_profile_fixture,
        profile_cache=None,
    )

    blocks = XaiHighlightsAdapter.build(context)

    assert len(blocks) == 1
    # Verify no mutation
    assert context.accumulated_extensions == accumulated_extensions
    with pytest.raises(ValidationError):
        context.accumulated_extensions = {}  # type: ignore[misc]


def test_build_none_extensions_value_raises(valid_output_profile_fixture: OutputProfile) -> None:
    """Error path: None value for accumulated_extensions raises ValidationError."""
    with pytest.raises(ValidationError):
        AdapterContext(
            execution=None,
            locale="en",
            penalties_applied=[],
            mcp_audit_map=None,
            global_score=None,
            accumulated_extensions=None,  # type: ignore[arg-type]
            profile=valid_output_profile_fixture,
            profile_cache=None,
        )
