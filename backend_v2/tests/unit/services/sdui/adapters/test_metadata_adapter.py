"""Unit tests for Metadata Adapter."""

from __future__ import annotations

from datetime import datetime

import pytest
from pydantic import ValidationError

from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.dtos.context_variables import ContextVariablesDTO
from backend_v2.models.dtos.sdui_rules import MetadataAestheticsDTO
from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.view.sdui import SduiMetadataBlock
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext
from backend_v2.services.sdui.adapters.metadata_adapter import METADATA_RULES, MetadataAdapter


def _create_sample_profile(locale: str = "en") -> OutputProfile:
    """Create a sample OutputProfile fixture for metadata adapter testing.

    Args:
        locale: Target locale code (unused in static fixture construction).

    Returns:
        Configured OutputProfile instance.
    """
    _ = locale
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
    """Positive: builds localized English SduiMetadataBlock with user, org, and formatted created_at date."""
    profile = _create_sample_profile()
    execution = ExecutionRecord(
        id="exe_0123456789abcdef0123456789abcdef",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        output_profile_id=profile.id,
        status=ExecutionStatus.PASSED,
        created_at=datetime(2026, 1, 1, 12, 0),
        execution_trace=[],
        context_variables=ContextVariablesDTO(),
        target_locale="fi",
        metadata=ExecutionMetadata(),
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
        mcp_tools_map={},
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
    """Positive: builds localized Finnish SduiMetadataBlock with user, org, and formatted created_at date."""
    profile = _create_sample_profile()
    execution = ExecutionRecord(
        id="exe_0123456789abcdef0123456789abcdef",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        output_profile_id=profile.id,
        status=ExecutionStatus.PASSED,
        created_at=datetime(2026, 1, 1, 12, 0),
        execution_trace=[],
        context_variables=ContextVariablesDTO(),
        target_locale="fi",
        metadata=ExecutionMetadata(),
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
        mcp_tools_map={},
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
    """Positive: populates all visible_metadata fields including pre-formatted local_time_str, cost, and tokens."""
    profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="full-test",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(translations={"en": "Full Report"}),
        content_blocks=[],
        target_block_order=[],
        visible_metadata=["user", "organization", "date", "scoring_engine", "strictness", "cost", "tokens"],
    )
    execution = ExecutionRecord(
        id="exe_0123456789abcdef0123456789abcdef",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        output_profile_id=profile.id,
        status=ExecutionStatus.PASSED,
        created_at=datetime(2026, 1, 1, 10, 0),
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
        profile=profile,
        profile_cache=None,
        user_name="Jane Doe",
        org_name="Tech Corp",
        parsed_matrices={},
        mcp_tools_map={},
        local_time_str="2026-01-01 12:00 EET",
        scoring_engine="TopologicalV2",
        strictness_level=85,
        cost=1.25,
        tokens=1500,
    )

    blocks = MetadataAdapter.build(context)
    assert len(blocks) == 1
    header = blocks[0]
    assert isinstance(header, SduiMetadataBlock)
    assert header.costs == "$1.25"
    assert header.tokens == {"total": "1500"}
    assert header.custom_preface_md is None

    metadata_texts = " ".join(header.metadata_lines)
    assert "2026-01-01 12:00 EET" in metadata_texts
    assert "Scoring Engine: TopologicalV2" in metadata_texts
    assert "Strictness: 85%" in metadata_texts


def test_metadata_adapter_negative_omits_missing_optional_context_fields() -> None:
    """Negative: omits user, org, date, scoring_engine, cost, and tokens when context values are None."""
    profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="sparse-test",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(translations={"en": "Sparse Report"}),
        content_blocks=[],
        target_block_order=[],
        visible_metadata=["user", "organization", "date", "scoring_engine", "cost", "tokens"],
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
        parsed_matrices={},
        mcp_tools_map={},
        scoring_engine=None,
        cost=None,
        tokens=None,
    )

    blocks = MetadataAdapter.build(context)
    assert len(blocks) == 1
    header = blocks[0]
    assert isinstance(header, SduiMetadataBlock)
    assert header.metadata_lines == []
    assert header.costs is None
    assert header.tokens is None
    assert header.custom_preface_md is None


def test_metadata_adapter_boundary_empty_visible_metadata_and_strict_schema() -> None:
    """Boundary & Negative: empty visible_metadata produces empty lines; strict DTO rejects extra keys."""
    profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="empty-meta",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(translations={"en": "Empty Metadata Report"}),
        content_blocks=[],
        target_block_order=[],
        visible_metadata=[],
    )
    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=profile,
        profile_cache=None,
        user_name="John Doe",
        org_name="Acme Corp",
        parsed_matrices={},
        mcp_tools_map={},
        cost=0.0,
        tokens=0,
    )

    blocks = MetadataAdapter.build(context)
    assert len(blocks) == 1
    header = blocks[0]
    assert isinstance(header, SduiMetadataBlock)
    assert header.metadata_lines == []
    assert header.costs is None
    assert header.tokens is None

    with pytest.raises(ValidationError):
        MetadataAestheticsDTO.model_validate({"default_metadata": {}, "unexpected_field": "invalid"})


def test_metadata_rules() -> None:
    """Verify METADATA_RULES export is a valid MetadataAestheticsDTO."""
    assert isinstance(METADATA_RULES, MetadataAestheticsDTO)
