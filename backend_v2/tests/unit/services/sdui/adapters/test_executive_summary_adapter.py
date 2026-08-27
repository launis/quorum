import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.enums import RoleClassification, TargetBlockType
from backend_v2.models.v2_core import I18nText, OutputProfile, RenderedSynthesisCache
from backend_v2.models.view.sdui import ParagraphBlock
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext
from backend_v2.services.sdui.adapters.executive_summary_adapter import ExecutiveSummaryAdapter


def test_build_valid_role_returns_paragraph_block() -> None:
    """Test successful translation of user role into a ParagraphBlock."""
    profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(translations={"en": "Test"}),
        content_blocks=[],
        target_block_order=[],
        user_role_label=I18nText(translations={"en": "Role", "fi": "Rooli"}),
    )
    cache = RenderedSynthesisCache(
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
        user_name=None,
        org_name=None,
    )

    blocks = ExecutiveSummaryAdapter.build(context)
    assert len(blocks) == 1
    assert isinstance(blocks[0], ParagraphBlock)
    assert blocks[0].text == "**Rooli:** Navigaattori"


def test_build_valid_role_with_narrative_and_section_syntheses() -> None:
    """Test role badge combined with section_syntheses (user_role_justification omitted)."""
    profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(translations={"en": "Test"}),
        content_blocks=[],
        target_block_order=[],
        user_role_label=I18nText(translations={"en": "Role", "fi": "Rooli"}),
    )
    cache = RenderedSynthesisCache(
        user_role=RoleClassification.NAVIGATOR.value,
        user_role_justification="You have demonstrated strategic guidance across team objectives.",
        section_syntheses={
            TargetBlockType.EXECUTIVE_SUMMARY_BLOCK.value: [
                ParagraphBlock(
                    text="The organization is performing with high operational discipline.",
                    exact_quotes=[],
                    citations=[],
                )
            ]
        },
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

    blocks = ExecutiveSummaryAdapter.build(context)
    assert len(blocks) == 2
    assert isinstance(blocks[0], ParagraphBlock)
    assert blocks[0].text == "**Role:** Navigator"
    assert isinstance(blocks[1], ParagraphBlock)
    assert blocks[1].text == "The organization is performing with high operational discipline."


def test_build_legacy_unmapped_section_key_ignored_negative() -> None:
    """Negative Test: Verify legacy 'executive_summary' key in section_syntheses is strictly ignored."""
    profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(translations={"en": "Test"}),
        content_blocks=[],
        target_block_order=[],
        user_role_label=I18nText(translations={"en": "Role", "fi": "Rooli"}),
    )
    cache = RenderedSynthesisCache(
        user_role=RoleClassification.NAVIGATOR.value,
        user_role_justification="Test justification",
        section_syntheses={
            "executive_summary": [
                ParagraphBlock(
                    text="Legacy unmapped synthesis content.",
                    exact_quotes=[],
                    citations=[],
                )
            ]
        },
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

    blocks = ExecutiveSummaryAdapter.build(context)
    # Legacy key must NOT be picked up; only the role badge is produced
    assert len(blocks) == 1
    assert isinstance(blocks[0], ParagraphBlock)
    assert blocks[0].text == "**Role:** Navigator"


def test_build_missing_user_role_returns_empty_list() -> None:
    """Test that missing user role in cache returns empty list."""
    cache = RenderedSynthesisCache(
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
        profile=OutputProfile(
            id="prf_0123456789abcdef0123456789abcdef",
            slug="test",
            workflow_id="wf_0123456789abcdef0123456789abcdef",
            name=I18nText(translations={"en": "Test"}),
            content_blocks=[],
            target_block_order=[],
            user_role_label=I18nText(translations={"en": "Role", "fi": "Rooli"}),
        ),
        profile_cache=cache,
        user_name=None,
        org_name=None,
    )

    blocks = ExecutiveSummaryAdapter.build(context)
    assert len(blocks) == 0


def test_build_invalid_role_classification_raises_app_exception() -> None:
    """Test that an invalid role throws a ValueError wrapped in AppException."""
    profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(translations={"en": "Test"}),
        content_blocks=[],
        target_block_order=[],
        user_role_label=I18nText(translations={"en": "Role", "fi": "Rooli"}),
    )
    cache = RenderedSynthesisCache(
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
        user_name=None,
        org_name=None,
    )

    with pytest.raises(AppException) as exc:
        ExecutiveSummaryAdapter.build(context)

    assert exc.value.status_code == 500
    assert exc.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


def test_build_valid_role_with_default_label() -> None:
    """Test role badge resolution when user_role_label is None on OutputProfile."""
    profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(translations={"en": "Test"}),
        content_blocks=[],
        target_block_order=[],
        user_role_label=None,
    )
    cache = RenderedSynthesisCache(
        user_role=RoleClassification.DRIVER.value,
        user_role_justification="",
        section_syntheses={},
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

    blocks = ExecutiveSummaryAdapter.build(context)
    assert len(blocks) == 1
    assert isinstance(blocks[0], ParagraphBlock)
    assert blocks[0].text == "**User Role:** Driver"


def test_build_starved_returns_empty() -> None:
    from backend_v2.models.dtos.trace import DataStarvationEvent

    profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(translations={"en": "Test"}),
        content_blocks=[],
        target_block_order=[],
    )
    cache = RenderedSynthesisCache(
        data_starvation=DataStarvationEvent(total_atoms=0, reason="insufficient_tokens"),
        user_role=RoleClassification.DRIVER.value,
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
    blocks = ExecutiveSummaryAdapter.build(context)
    assert blocks == []


def test_build_unmapped_role_rule_raises_configuration_error(monkeypatch: pytest.MonkeyPatch) -> None:
    profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(translations={"en": "Test"}),
        content_blocks=[],
        target_block_order=[],
    )
    cache = RenderedSynthesisCache(
        user_role=RoleClassification.DRIVER.value,
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
    monkeypatch.setattr(
        "backend_v2.services.sdui.adapters.executive_summary_adapter.EXECUTIVE_SUMMARY_RULES",
        {},
    )
    with pytest.raises(AppException) as exc_info:
        ExecutiveSummaryAdapter.build(context)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR.value


