from __future__ import annotations

from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.synthesis import RenderedSynthesisCache
from backend_v2.models.dtos.base import DataStarvationEvent
from backend_v2.models.view.sdui import MarkdownBlock, ParagraphBlock
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext
from backend_v2.services.sdui.adapters.synthesis_text_adapter import (
    SYNTHESIS_TEXT_RULES,
    SynthesisTextAdapter,
)


def test_synthesis_text_adapter_builds_markdown_blocks() -> None:
    """Test that SynthesisTextAdapter correctly processes synthesis text."""
    cb = ParagraphBlock(text="Predefined content block", exact_quotes=[], citations=[])

    profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test-slug",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(translations={"en": "Test Profile"}),
        content_blocks=[cb],
        target_block_order=[],
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
    )

    blocks = SynthesisTextAdapter.build(context)
    assert len(blocks) == 1
    assert isinstance(blocks[0], ParagraphBlock)
    assert blocks[0].text == "Predefined content block"


def test_synthesis_text_adapter_ignores_section_syntheses() -> None:
    """Test that SynthesisTextAdapter strictly emits content_blocks, ignoring section_syntheses."""
    cb = ParagraphBlock(text="Static preface block", exact_quotes=[], citations=[])

    profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test-slug",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(translations={"en": "Test Profile"}),
        content_blocks=[cb],
        target_block_order=[],
    )

    cache = RenderedSynthesisCache(
        section_syntheses={
            "sec_1": [MarkdownBlock(text="Dynamic section 1 analysis")],
            "sec_2": [ParagraphBlock(text="Dynamic section 2 summary", exact_quotes=[], citations=[])],
        }
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
    )

    blocks = SynthesisTextAdapter.build(context)
    # Section syntheses are rendered exclusively by MatrixGraphsAdapter
    assert len(blocks) == 1
    assert isinstance(blocks[0], ParagraphBlock)
    assert blocks[0].text == "Static preface block"


def test_synthesis_text_adapter_data_starved_returns_empty() -> None:
    """Test that SynthesisTextAdapter returns empty list when execution is data starved."""
    cb = ParagraphBlock(text="Static preface block", exact_quotes=[], citations=[])
    profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test-slug",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(translations={"en": "Test Profile"}),
        content_blocks=[cb],
        target_block_order=[],
    )
    starved_cache = RenderedSynthesisCache(
        data_starvation=DataStarvationEvent(
            total_atoms=0,
            reason="Data starved test",
        )
    )
    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=profile,
        profile_cache=starved_cache,
        user_name=None,
        org_name=None,
    )
    assert context.is_data_starved is True
    blocks = SynthesisTextAdapter.build(context)
    assert blocks == []


def test_synthesis_text_adapter_empty_content_blocks() -> None:
    """Test that SynthesisTextAdapter returns empty list when profile content_blocks is empty."""
    profile_empty_blocks = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test-slug",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(translations={"en": "Test Profile"}),
        content_blocks=[],
        target_block_order=[],
    )
    context_empty_blocks = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=profile_empty_blocks,
        profile_cache=None,
        user_name=None,
        org_name=None,
    )
    assert SynthesisTextAdapter.build(context_empty_blocks) == []


def test_synthesis_text_rules_attributes() -> None:
    """Test that SYNTHESIS_TEXT_RULES conforms to SynthesisTextAestheticsDTO schema."""
    assert SYNTHESIS_TEXT_RULES.model_config.get("extra") == "forbid"
