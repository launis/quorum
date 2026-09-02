"""Unit tests for the XAI Highlights adapter."""

import logging

import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.dtos.synthesis import XaiHighlightItem
from backend_v2.models.enums import VisualIntent, XaiExtensionType
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.state import TraceEvent
from backend_v2.models.v2_core import ExecutionRecord, I18nText, OutputProfile, RenderedSynthesisCache
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
        name=I18nText(translations={"en": "Test Profile"}),
        target_block_order=[],
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
        output_profile_id="prf_0123456789abcdef",
        execution_trace=[],
        target_locale="fi",
        metadata=ExecutionMetadata(),
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
    )
    blocks = XaiHighlightsAdapter.build(context)
    assert blocks == []


def test_build_single_extension_group_returns_blocks(valid_output_profile_fixture: OutputProfile) -> None:
    """Positive: single extension group parses from trace."""
    execution = ExecutionRecord(
        id="exe_0123456789abcdef",
        workflow_id="wfw_test",
        output_profile_id="prf_0123456789abcdef",
        execution_trace=[
            TraceEvent(
                event_type="output",
                step_name="step_1",
                content={
                    "step_id": "step_1",
                    "block_id": "block_1",
                    "payload": {"extensions": {"coaching": "Good job!\nKeep it up!"}},
                },
            )
        ],
        target_locale="fi",
        metadata=ExecutionMetadata(),
    )

    context = AdapterContext(
        execution=execution,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=valid_output_profile_fixture,
        profile_cache=RenderedSynthesisCache(
            section_syntheses={},
            cited_sources=[],
            xai_highlights=[XaiHighlightItem(extension_type="coaching", content="Good job!\nKeep it up!")],
        ),
        user_name=None,
        org_name=None,
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
        output_profile_id="prf_0123456789abcdef",
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
        target_locale="fi",
        metadata=ExecutionMetadata(),
    )
    context = AdapterContext(
        execution=execution,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=valid_output_profile_fixture,
        profile_cache=RenderedSynthesisCache(
            section_syntheses={},
            cited_sources=[],
            xai_highlights=[
                XaiHighlightItem(extension_type="coaching", content="Good job!"),
                XaiHighlightItem(extension_type="falsification", content="Bad logic!"),
            ],
        ),
        user_name=None,
        org_name=None,
    )

    blocks = XaiHighlightsAdapter.build(context)
    assert len(blocks) == 2
    titles = [b.title for b in blocks if isinstance(b, AccordionBlock)]
    assert "Coaching" in titles
    assert "Falsification" in titles


def test_build_does_not_mutate_context(valid_output_profile_fixture: OutputProfile) -> None:
    """Negative: context remains frozen after the call."""
    execution = ExecutionRecord(
        id="exe_0123456789abcdef",
        workflow_id="wfw_test",
        output_profile_id="prf_0123456789abcdef",
        execution_trace=[],
        target_locale="fi",
        metadata=ExecutionMetadata(),
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
    )

    XaiHighlightsAdapter.build(context)

    with pytest.raises(ValidationError):
        context.locale = "fi"  # type: ignore[misc]


def test_build_graceful_degradation_disabled_extensions(valid_output_profile_fixture: OutputProfile) -> None:
    """Boundary: visible_block_extensions=[] returns empty list."""
    execution = ExecutionRecord(
        id="exe_0123456789abcdef",
        workflow_id="wfw_test",
        output_profile_id="prf_0123456789abcdef",
        execution_trace=[],
        target_locale="fi",
        metadata=ExecutionMetadata(),
    )
    disabled_profile = valid_output_profile_fixture.model_copy(update={"visible_block_extensions": []})
    context = AdapterContext(
        execution=execution,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=disabled_profile,
        profile_cache=RenderedSynthesisCache(
            section_syntheses={},
            cited_sources=[],
            xai_highlights=[XaiHighlightItem(extension_type="coaching", content="Good job!")],
        ),
        user_name=None,
        org_name=None,
    )
    blocks = XaiHighlightsAdapter.build(context)
    assert blocks == []


def test_build_graceful_degradation_zero_max_items(valid_output_profile_fixture: OutputProfile) -> None:
    """Boundary: max_extension_items=0 returns empty list."""
    execution = ExecutionRecord(
        id="exe_0123456789abcdef",
        workflow_id="wfw_test",
        output_profile_id="prf_0123456789abcdef",
        execution_trace=[],
        target_locale="fi",
        metadata=ExecutionMetadata(),
    )
    zero_max_profile = valid_output_profile_fixture.model_copy(update={"max_extension_items": 0})
    context = AdapterContext(
        execution=execution,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=zero_max_profile,
        profile_cache=RenderedSynthesisCache(
            section_syntheses={},
            cited_sources=[],
            xai_highlights=[XaiHighlightItem(extension_type="coaching", content="Good job!")],
        ),
        user_name=None,
        org_name=None,
    )
    blocks = XaiHighlightsAdapter.build(context)
    assert blocks == []


def test_build_ranked_round_robin_distribution(valid_output_profile_fixture: OutputProfile) -> None:
    """Positive: 3 categories with 4 items each are curated fairly without Primacy Bias."""
    execution = ExecutionRecord(
        id="exe_0123456789abcdef",
        workflow_id="wfw_test",
        output_profile_id="prf_0123456789abcdef",
        execution_trace=[],
        target_locale="fi",
        metadata=ExecutionMetadata(),
    )
    profile = valid_output_profile_fixture.model_copy(update={"max_extension_items": 2})

    highlights = [
        # Coaching items of varying lengths
        XaiHighlightItem(extension_type="coaching", content="C1 short"),
        XaiHighlightItem(extension_type="coaching", content="C2 medium length insight"),
        XaiHighlightItem(extension_type="coaching", content="C3 longer coaching recommendation item"),
        XaiHighlightItem(extension_type="coaching", content="C4 the absolute longest coaching guidance sentence"),
        # Falsification items of varying lengths
        XaiHighlightItem(extension_type="falsification", content="F1 short"),
        XaiHighlightItem(extension_type="falsification", content="F2 medium length critique"),
        XaiHighlightItem(extension_type="falsification", content="F3 longer falsification analysis item"),
        XaiHighlightItem(
            extension_type="falsification", content="F4 the absolute longest falsification argument sentence"
        ),
        # Remediation items of varying lengths
        XaiHighlightItem(extension_type="remediation_steps", content="R1 short"),
        XaiHighlightItem(extension_type="remediation_steps", content="R2 medium length remediation"),
        XaiHighlightItem(extension_type="remediation_steps", content="R3 longer remediation action item"),
        XaiHighlightItem(
            extension_type="remediation_steps", content="R4 the absolute longest remediation action sentence"
        ),
    ]

    context = AdapterContext(
        execution=execution,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=profile,
        profile_cache=RenderedSynthesisCache(
            section_syntheses={},
            cited_sources=[],
            xai_highlights=highlights,
        ),
        user_name=None,
        org_name=None,
    )

    blocks = XaiHighlightsAdapter.build(context)
    assert len(blocks) == 3

    coaching_block = next(b for b in blocks if isinstance(b, AccordionBlock) and b.title == "Coaching")
    falsification_block = next(b for b in blocks if isinstance(b, AccordionBlock) and b.title == "Falsification")
    remediation_block = next(b for b in blocks if isinstance(b, AccordionBlock) and b.title == "Remediation Steps")

    # Each accordion should receive exactly max_extension_items (2) items
    assert len(coaching_block.children) == 2
    assert len(falsification_block.children) == 2
    assert len(remediation_block.children) == 2

    # Verify longest items were selected
    coaching_texts = [c.text for c in coaching_block.children if isinstance(c, AlertBlock)]
    assert "C4 the absolute longest coaching guidance sentence" in coaching_texts
    assert "C3 longer coaching recommendation item" in coaching_texts
    assert "C1 short" not in coaching_texts

    falsification_texts = [c.text for c in falsification_block.children if isinstance(c, AlertBlock)]
    assert "F4 the absolute longest falsification argument sentence" in falsification_texts
    assert "F3 longer falsification analysis item" in falsification_texts
    assert "F1 short" not in falsification_texts

    remediation_texts = [c.text for c in remediation_block.children if isinstance(c, AlertBlock)]
    assert "R4 the absolute longest remediation action sentence" in remediation_texts
    assert "R3 longer remediation action item" in remediation_texts
    assert "R1 short" not in remediation_texts


def test_build_malformed_highlight_item_skipped(
    valid_output_profile_fixture: OutputProfile, caplog: pytest.LogCaptureFixture
) -> None:
    """Error path: hallucinated or empty extension type is skipped with warning log."""
    from backend_v2.models.dtos.synthesis import XaiHighlightItem

    execution = ExecutionRecord(
        id="exe_0123456789abcdef",
        workflow_id="wfw_test",
        output_profile_id="prf_0123456789abcdef",
        execution_trace=[],
        target_locale="fi",
        metadata=ExecutionMetadata(),
    )
    context = AdapterContext(
        execution=execution,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=valid_output_profile_fixture,
        profile_cache=RenderedSynthesisCache(
            section_syntheses={},
            cited_sources=[],
            xai_highlights=[
                XaiHighlightItem(extension_type="hallucinated_extension_not_in_enum", content="Some insight."),
                XaiHighlightItem(extension_type="coaching", content="Valid coaching insight."),
            ],
        ),
        user_name=None,
        org_name=None,
    )

    with caplog.at_level(logging.WARNING):
        blocks = XaiHighlightsAdapter.build(context)

    assert len(blocks) == 1
    assert isinstance(blocks[0], AccordionBlock)
    assert blocks[0].title == "Coaching"
    assert len(blocks[0].children) == 1
    assert isinstance(blocks[0].children[0], AlertBlock)
    assert blocks[0].children[0].text == "Valid coaching insight."

    assert any(
        "LLM hallucinated extension type: hallucinated_extension_not_in_enum" in record.message
        for record in caplog.records
    )


def test_build_missing_aesthetics_rule_raises_app_exception(
    valid_output_profile_fixture: OutputProfile, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Error path: missing aesthetics rule mapping raises AppException with CONFIGURATION_ERROR."""
    from backend_v2.models.dtos.synthesis import XaiHighlightItem
    from backend_v2.services.sdui.adapters import xai_highlights_adapter

    execution = ExecutionRecord(
        id="exe_0123456789abcdef",
        workflow_id="wfw_test",
        output_profile_id="prf_0123456789abcdef",
        execution_trace=[],
        target_locale="fi",
        metadata=ExecutionMetadata(),
    )
    monkeypatch.setattr(xai_highlights_adapter, "XAI_AESTHETICS_RULES", {})

    context = AdapterContext(
        execution=execution,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=valid_output_profile_fixture,
        profile_cache=RenderedSynthesisCache(
            section_syntheses={},
            cited_sources=[],
            xai_highlights=[XaiHighlightItem(extension_type="coaching", content="Valid insight.")],
        ),
        user_name=None,
        org_name=None,
    )

    with pytest.raises(AppException) as exc_info:
        XaiHighlightsAdapter.build(context)

    assert "Missing rule mapping for extension key: coaching" in str(exc_info.value)
    assert exc_info.value.details == {"error_code": ErrorCodes.CONFIGURATION_ERROR.value}


@pytest.mark.parametrize("locale", ["en", "fi"])
def test_build_all_valid_xai_extension_types_have_aesthetics_rules(locale: str) -> None:
    """Regression test (Tier 4): All block-level XaiExtensionType enum values configured as visible block extensions MUST have aesthetic rules and build without KeyError/AppException across locales."""
    from backend_v2.models.dtos.synthesis import XaiHighlightItem
    from backend_v2.models.enums import XAI_EXTENSION_SCOPE, XaiExtensionScope

    execution = ExecutionRecord(
        id="exe_0123456789abcdef",
        workflow_id="wfw_test",
        output_profile_id="prf_0123456789abcdef",
        execution_trace=[],
        target_locale="fi",
        metadata=ExecutionMetadata(),
    )

    # Test each block-level extension type individually
    block_extensions = [e for e in XaiExtensionType if XAI_EXTENSION_SCOPE.get(e) == XaiExtensionScope.BLOCK]

    for i, ext_type in enumerate(block_extensions):
        profile = OutputProfile(
            id=f"prf_{i:016x}",
            slug=f"profile-{ext_type.value}",
            workflow_id="wfw_test",
            name=I18nText(translations={"en": f"Profile {ext_type.value}"}),
            target_block_order=[],
            visible_block_extensions=[ext_type],
        )
        context = AdapterContext(
            execution=execution,
            locale=locale,
            penalties_applied=[],
            mcp_audit_map=None,
            global_score=None,
            profile=profile,
            profile_cache=RenderedSynthesisCache(
                section_syntheses={},
                cited_sources=[],
                xai_highlights=[XaiHighlightItem(extension_type=ext_type.value, content="Insight text.")],
            ),
            user_name=None,
            org_name=None,
        )
        blocks = XaiHighlightsAdapter.build(context)
        assert len(blocks) == 1, f"Expected 1 block for extension {ext_type.value} in {locale}, got {len(blocks)}"
        assert isinstance(blocks[0], AccordionBlock)
        assert blocks[0].title != ""
