"""Unit tests for Metadata Adapter."""

from datetime import datetime

import pytest

from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.v2_core import ExecutionRecord, I18nText, OutputProfile
from backend_v2.models.view.sdui import SduiMetadataBlock
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext
from backend_v2.services.sdui.adapters.metadata_adapter import MetadataAdapter


def _create_sample_profile(locale: str = "en") -> OutputProfile:
    return OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test-slug",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(
            translations={"en": "Executive Report", "fi": "Johdon raportti"},
        ),
        custom_preface=I18nText(
            translations={"en": "Welcome to the executive summary.", "fi": "Tervetuloa johdon katsaukseen."},
        ),
        content_blocks=[],
        target_block_order=[],
        visible_metadata=["user", "organization", "date"],
    )


def test_metadata_adapter_builds_header_block_bilingual_en() -> None:
    profile = _create_sample_profile()
    execution = ExecutionRecord(
        id="exe_0123456789abcdef0123456789abcdef",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        status=ExecutionStatus.PASSED,
        created_at=datetime(2026, 1, 1, 12, 0),
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
        user_name="John Doe",
        org_name="Acme Corp",
        parsed_matrices={},
    )

    blocks = MetadataAdapter.build(context)
    assert len(blocks) == 1
    header = blocks[0]
    assert isinstance(header, SduiMetadataBlock)
    assert header.title == "Executive Report"
    assert header.custom_preface_md == "Welcome to the executive summary."

    metadata_texts = " ".join(header.metadata_lines)
    assert "User: John Doe" in metadata_texts
    assert "Organization: Acme Corp" in metadata_texts
    assert "2026-01-01 12:00" in metadata_texts


def test_metadata_adapter_builds_header_block_bilingual_fi() -> None:
    profile = _create_sample_profile()
    execution = ExecutionRecord(
        id="exe_0123456789abcdef0123456789abcdef",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        status=ExecutionStatus.PASSED,
        created_at=datetime(2026, 1, 1, 12, 0),
        execution_trace=[],
        context_variables={},
    )
    context = AdapterContext(
        execution=execution,
        locale="fi",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=profile,
        profile_cache=None,
        user_name="Matti Meikäläinen",
        org_name="Esimerkki Oy",
        parsed_matrices={},
    )

    blocks = MetadataAdapter.build(context)
    assert len(blocks) == 1
    header = blocks[0]
    assert isinstance(header, SduiMetadataBlock)
    assert header.title == "Johdon raportti"
    assert header.custom_preface_md == "Tervetuloa johdon katsaukseen."

    metadata_texts = " ".join(header.metadata_lines)
    assert "Käyttäjä: Matti Meikäläinen" in metadata_texts
    assert "Organisaatio: Esimerkki Oy" in metadata_texts
    assert "01.01.2026 klo 12:00" in metadata_texts


def test_metadata_adapter_all_fields_with_local_time_and_costs() -> None:
    profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="full-test",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(translations={"en": "Full Report"}),
        content_blocks=[],
        target_block_order=[],
        visible_metadata=["user", "organization", "date", "scoring_engine", "strictness", "cost", "tokens"],
        strictness_level=85,
    )
    execution = ExecutionRecord(
        id="exe_0123456789abcdef0123456789abcdef",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        status=ExecutionStatus.PASSED,
        created_at=datetime(2026, 1, 1, 10, 0),
        execution_trace=[],
    )
    context = AdapterContext(
        execution=execution,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=profile,
        profile_cache=None,
        user_name="Jane Doe",
        org_name="Tech Corp",
        parsed_matrices={},
        scoring_engine="TopologicalV2",
        cost=1.25,
        tokens=1500,
    )

    blocks = MetadataAdapter.build(context)
    assert len(blocks) == 1
    header = blocks[0]
    assert isinstance(header, SduiMetadataBlock)
    assert header.costs == "$1.25"
    assert header.tokens == {"total": "1500"}

    metadata_texts = " ".join(header.metadata_lines)
    assert "Scoring Engine: TopologicalV2" in metadata_texts
    assert "Strictness: 85" in metadata_texts
