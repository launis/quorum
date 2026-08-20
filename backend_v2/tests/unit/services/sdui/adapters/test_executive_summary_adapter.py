import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.enums import RoleClassification
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
        name=I18nText(default_locale="en", translations={"en": "Test"}),
        content_blocks=[],
        target_block_order=[],
        user_role_label=I18nText(default_locale="en", translations={"en": "Role", "fi": "Rooli"}),
        user_role_mappings={
            RoleClassification.NAVIGATOR.value: I18nText(
                default_locale="en", translations={"en": "Navigator", "fi": "Navigaattori"}
            ),
        },
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
        name=I18nText(default_locale="en", translations={"en": "Test"}),
        content_blocks=[],
        target_block_order=[],
        user_role_label=I18nText(default_locale="en", translations={"en": "Role", "fi": "Rooli"}),
        user_role_mappings={
            RoleClassification.NAVIGATOR.value: I18nText(
                default_locale="en", translations={"en": "Navigator", "fi": "Navigaattori"}
            ),
        },
    )
    cache = RenderedSynthesisCache(
        user_role=RoleClassification.NAVIGATOR.value,
        user_role_justification="You have demonstrated strategic guidance across team objectives.",
        section_syntheses={
            "executive_summary": [
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
    # user_role_justification is internal English trace, must NOT be emitted as SDUI block
    assert len(blocks) == 2
    assert isinstance(blocks[0], ParagraphBlock)
    assert blocks[0].text == "**Role:** Navigator"
    assert isinstance(blocks[1], ParagraphBlock)
    assert blocks[1].text == "The organization is performing with high operational discipline."


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
            name=I18nText(default_locale="en", translations={"en": "Test"}),
            content_blocks=[],
            target_block_order=[],
            user_role_label=I18nText(default_locale="en", translations={"en": "Role", "fi": "Rooli"}),
            user_role_mappings={},
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
        name=I18nText(default_locale="en", translations={"en": "Test"}),
        content_blocks=[],
        target_block_order=[],
        user_role_label=I18nText(default_locale="en", translations={"en": "Role", "fi": "Rooli"}),
        user_role_mappings={},
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
    assert exc.value.details["error_code"] == "VALIDATION_FAILED"


def test_build_missing_user_role_label_raises_app_exception() -> None:
    """Test that missing user_role_label raises AppException."""
    profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(default_locale="en", translations={"en": "Test"}),
        content_blocks=[],
        target_block_order=[],
        user_role_label=None,
        user_role_mappings={
            RoleClassification.NAVIGATOR.value: I18nText(
                default_locale="en", translations={"en": "Navigator", "fi": "Navigaattori"}
            ),
        },
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

    with pytest.raises(AppException) as exc:
        ExecutiveSummaryAdapter.build(context)

    assert exc.value.status_code == 500
    assert exc.value.details["error_code"] == "VALIDATION_FAILED"


def test_build_missing_role_mapping_raises_app_exception() -> None:
    """Test that a missing role mapping raises KeyError wrapped in AppException."""
    profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(default_locale="en", translations={"en": "Test"}),
        content_blocks=[],
        target_block_order=[],
        user_role_label=I18nText(default_locale="en", translations={"en": "Role", "fi": "Rooli"}),
        user_role_mappings={},  # Missing NAVIGATOR
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

    with pytest.raises(AppException) as exc:
        ExecutiveSummaryAdapter.build(context)

    assert exc.value.status_code == 500
    assert exc.value.details["error_code"] == "VALIDATION_FAILED"
