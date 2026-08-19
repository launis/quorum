from backend_v2.models.v2_core import I18nText, OutputProfile, RenderedSynthesisCache
from backend_v2.models.view.sdui import MarkdownBlock, ParagraphBlock
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext
from backend_v2.services.sdui.adapters.synthesis_text_adapter import SynthesisTextAdapter


def test_synthesis_text_adapter_builds_markdown_blocks() -> None:
    """Test that SynthesisTextAdapter correctly processes synthesis text."""
    cb = ParagraphBlock(text="Predefined content block", exact_quotes=[], citations=[])

    profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test-slug",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(default_locale="en", translations={"en": "Test Profile"}),
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


def test_synthesis_text_adapter_renders_both_content_blocks_and_section_syntheses() -> None:
    """Test that SynthesisTextAdapter appends both static content_blocks and dynamic section_syntheses."""
    cb = ParagraphBlock(text="Static preface block", exact_quotes=[], citations=[])

    profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test-slug",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(default_locale="en", translations={"en": "Test Profile"}),
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
    assert len(blocks) == 3
    assert isinstance(blocks[0], ParagraphBlock)
    assert blocks[0].text == "Static preface block"
    assert isinstance(blocks[1], MarkdownBlock)
    assert blocks[1].text == "Dynamic section 1 analysis"
    assert isinstance(blocks[2], ParagraphBlock)
    assert blocks[2].text == "Dynamic section 2 summary"
