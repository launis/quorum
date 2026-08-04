"""Unit tests for Synthesis Text Adapter."""

from backend_v2.models.v2_core import I18nText, OutputLayoutBlock, OutputProfile, SynthesisConfigDTO
from backend_v2.models.view.sdui import MarkdownBlock, ParagraphBlock
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext
from backend_v2.services.sdui.adapters.synthesis_text_adapter import SynthesisTextAdapter


def test_synthesis_text_adapter_builds_markdown_blocks() -> None:
    """Test that SynthesisTextAdapter correctly processes synthesis text."""
    cb = ParagraphBlock(text="Predefined content block", exact_quotes=[], citations=[])

    profile = OutputProfile(
        id="prf_0123456789abcdef",
        slug="test-slug",
        workflow_id="wf_1",
        name=I18nText(default_locale="en", translations={"en": "Test Profile"}),
        layouts=[],
        content_blocks=[cb],
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
        synthesis_md="<script>alert(1)</script>Hello <b>World</b> test@example.com",
    )

    blocks = SynthesisTextAdapter.build(context)
    assert len(blocks) == 2

    assert isinstance(blocks[0], ParagraphBlock)
    assert blocks[0].text == "Predefined content block"

    assert isinstance(blocks[1], MarkdownBlock)

    # Check that bleach was applied (script stripped)
    assert "<script>" not in blocks[1].text
    assert "<b>World</b>" in blocks[1].text


def test_synthesis_text_adapter_pii_masking_trigger() -> None:
    """EP (PII Masking Trigger): Mock profile.layouts where enable_pii_masking = True to trigger the masking logic."""
    layout = OutputLayoutBlock(preset_view="default", synthesis=SynthesisConfigDTO(enable_pii_masking=True))
    profile = OutputProfile(
        id="prf_0123456789abcdef",
        slug="test-slug",
        workflow_id="wf_1",
        name=I18nText(default_locale="en", translations={"en": "Test Profile"}),
        layouts=[layout],
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
        synthesis_md="Contact test@example.com or 123-456-7890.",
    )
    blocks = SynthesisTextAdapter.build(context)
    assert len(blocks) == 1
    assert isinstance(blocks[0], MarkdownBlock)
    assert "[REDACTED EMAIL]" in blocks[0].text
    assert "[REDACTED PHONE]" in blocks[0].text
    assert "test@example.com" not in blocks[0].text
    assert "123-456-7890" not in blocks[0].text
