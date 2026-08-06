"""Unit tests for Synthesis Text Adapter."""

from backend_v2.models.v2_core import I18nText, OutputProfile
from backend_v2.models.view.sdui import ParagraphBlock
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
    )

    blocks = SynthesisTextAdapter.build(context)
    assert len(blocks) == 1

    assert isinstance(blocks[0], ParagraphBlock)
    assert blocks[0].text == "Predefined content block"
