"""Unit tests for Metadata Adapter."""

from datetime import datetime

from backend_v2.models.v2_core import ExecutionRecord, I18nText, OutputProfile
from backend_v2.models.view.sdui import SduiMetadataBlock
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext
from backend_v2.services.sdui.adapters.metadata_adapter import MetadataAdapter


def test_metadata_adapter_builds_header_block() -> None:
    """Test that MetadataAdapter correctly builds a SduiMetadataBlock."""
    profile = OutputProfile(
        id="prf_0123456789abcdef",
        slug="test-slug",
        workflow_id="wf_1",
        name=I18nText(default_locale="en", translations={"en": "Test Profile"}),
        layouts=[],
    )

    execution = ExecutionRecord(
        id="exe_0123456789abcdef", workflow_id="wf_1", status="PASSED", created_at=datetime(2026, 1, 1, 12, 0)
    )

    context = AdapterContext(
        execution=execution,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=profile,
        profile_cache=None,
        user_name="John Doe",
        org_name="Acme Corp",
        synthesis_md=None,
    )

    blocks = MetadataAdapter.build(context)
    assert len(blocks) == 1
    assert isinstance(blocks[0], SduiMetadataBlock)

    header = blocks[0]
    assert header.title == "Test Profile"
    assert "PASSED" in header.badges

    metadata_texts = " ".join(header.metadata_lines)
    assert "Käyttäjä: John Doe" in metadata_texts
    assert "Organisaatio: Acme Corp" in metadata_texts
    assert "01.01.2026 12:00" in metadata_texts
