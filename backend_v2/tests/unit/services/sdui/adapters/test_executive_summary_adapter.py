import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.enums import RoleClassification
from backend_v2.models.v2_core import I18nText, OutputProfile, RenderedSynthesisCache
from backend_v2.models.view.sdui import ParagraphBlock
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext
from backend_v2.services.sdui.adapters.executive_summary_adapter import ExecutiveSummaryAdapter


def test_build_executive_summary_success() -> None:
    """Test successful translation of user role into a ParagraphBlock."""
    profile = OutputProfile(
        id="test_profile",
        name="Test",
        target_audience="test",
        category_weights={},
        content_blocks=[],
        user_role_label=I18nText(en="Role", fi="Rooli"),
        user_role_mappings={
            RoleClassification.NAVIGATOR.value: I18nText(en="Navigator", fi="Navigaattori"),
        },
    )
    cache = RenderedSynthesisCache(
        synthesized_markdown="",
        user_role=RoleClassification.NAVIGATOR.value,
        user_role_justification="",
        section_syntheses={},
    )
    context = AdapterContext(
        execution=None,
        locale="fi",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=profile,
        profile_cache=cache,
    )

    blocks = ExecutiveSummaryAdapter.build(context)
    assert len(blocks) == 1
    assert isinstance(blocks[0], ParagraphBlock)
    assert blocks[0].text == "**Rooli:** Navigaattori"


def test_build_executive_summary_invalid_role() -> None:
    """Test that an invalid role throws a ValueError wrapped in AppException."""
    profile = OutputProfile(
        id="test_profile",
        name="Test",
        target_audience="test",
        category_weights={},
        content_blocks=[],
    )
    cache = RenderedSynthesisCache(
        synthesized_markdown="",
        user_role="UNKNOWN_ROLE",
        user_role_justification="",
        section_syntheses={},
    )
    context = AdapterContext(
        execution=None,
        locale="fi",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=profile,
        profile_cache=cache,
    )

    with pytest.raises(AppException) as exc:
        ExecutiveSummaryAdapter.build(context)

    assert exc.value.status_code == 500
    assert exc.value.details["error_code"] == "VALIDATION_FAILED"


def test_build_executive_summary_empty_cache() -> None:
    """Test that missing cache returns empty list."""
    context = AdapterContext(
        execution=None,
        locale="fi",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=OutputProfile(id="t", name="t", target_audience="t", category_weights={}, content_blocks=[]),
        profile_cache=None,
    )

    blocks = ExecutiveSummaryAdapter.build(context)
    assert len(blocks) == 0


def test_build_executive_summary_empty_role() -> None:
    """Test that empty role in cache returns empty list."""
    cache = RenderedSynthesisCache(
        synthesized_markdown="",
        user_role=None,
        user_role_justification="",
        section_syntheses={},
    )
    context = AdapterContext(
        execution=None,
        locale="fi",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=OutputProfile(id="t", name="t", target_audience="t", category_weights={}, content_blocks=[]),
        profile_cache=cache,
    )

    blocks = ExecutiveSummaryAdapter.build(context)
    assert len(blocks) == 0
