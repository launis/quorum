import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.dtos.matrix_scorecard import MatrixScorecardRowDTO
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


def test_build_none_profile_cache_returns_empty_list() -> None:
    """Negative Test: Verify that None profile_cache in AdapterContext returns empty list."""
    profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(translations={"en": "Test"}),
        content_blocks=[],
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
    blocks = ExecutiveSummaryAdapter.build(context)
    assert blocks == []


def test_role_classification_l10n_key_strict_mapping() -> None:
    """Test that all RoleClassification enum variants have explicit camelCase l10n_key mapping."""
    expected_mappings = {
        RoleClassification.PASSENGER: "rolePassenger",
        RoleClassification.NAVIGATOR: "roleNavigator",
        RoleClassification.DRIVER: "roleDriver",
        RoleClassification.ARCHITECT: "roleArchitect",
    }
    for role, expected_key in expected_mappings.items():
        assert role.l10n_key == expected_key


@pytest.mark.parametrize(
    ("role", "locale", "expected_text"),
    [
        (RoleClassification.PASSENGER, "fi", "**Käyttäjärooli:** Matkustaja"),
        (RoleClassification.PASSENGER, "en", "**User Role:** Passenger"),
        (RoleClassification.NAVIGATOR, "fi", "**Käyttäjärooli:** Navigaattori"),
        (RoleClassification.NAVIGATOR, "en", "**User Role:** Navigator"),
        (RoleClassification.DRIVER, "fi", "**Käyttäjärooli:** Kuljettaja"),
        (RoleClassification.DRIVER, "en", "**User Role:** Driver"),
        (RoleClassification.ARCHITECT, "fi", "**Käyttäjärooli:** Arkkitehti"),
        (RoleClassification.ARCHITECT, "en", "**User Role:** Architect"),
    ],
)
def test_build_all_role_classifications_bilingual(role: RoleClassification, locale: str, expected_text: str) -> None:
    """Test that all four roles resolve correctly in both Finnish and English."""
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
        user_role=role.value,
        user_role_justification="",
        section_syntheses={},
    )
    context = AdapterContext(
        execution=None,
        locale=locale,
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
    assert blocks[0].text == expected_text


def _make_matrix_row(
    block_id: str = "blk_53f32679aa514fcb",
    score: float | None = 4.0,
    scale_min: float | None = 1.0,
    scale_max: float | None = 5.0,
    level_names: dict[str, str] | None = None,
) -> MatrixScorecardRowDTO:
    if level_names is None:
        level_names = {
            "1": "Matkustaja (Sokea usko)",
            "2": "Reaktiivinen huomioija",
            "3": "Navigaattori (Pintapuolinen)",
            "4": "Kuljettaja (Kriittinen ohjaaja)",
            "5": "Arkkitehti (Aktiivinen haastaja)",
        }
    return MatrixScorecardRowDTO(
        block_id=block_id,
        name="Aktiivinen ohjaus",
        label_i18n=I18nText(translations={"fi": "Aktiivinen ohjaus", "en": "Active Guidance"}),
        description=None,
        score=score,
        score_display_label=None,
        scale_min=scale_min,
        scale_max=scale_max,
        normalized_score=None,
        true_atoms=None,
        total_atoms=None,
        row_explanation="Evaluated active guidance score.",
        evidence_type=None,
        cited_source_id=None,
        cited_text_quote=None,
        cited_web_citation=None,
        cited_source_title=None,
        cited_source_url=None,
        context_target=None,
        context_target_label=None,
        remediation_steps=None,
        coaching=None,
        falsification=None,
        confidence=None,
        inner_sdui_blocks=[],
        contextual_override=None,
        semantic_reasoning=None,
        level_breakdown=None,
        level_names=level_names,
        ui_plot_ratio=None,
        ui_boundary_labels={},
        is_evaluative=True,
        allow_contextual_override=False,
        used_evidence_ids=[],
        evaluated_atoms=[],
        clustered_row_sources=[],
        tda_state=None,
    )


def test_build_matrix_target_block_resolves_deterministic_role_badge() -> None:
    """Test deterministic role badge resolution from context.parsed_matrices."""
    profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(translations={"en": "Test"}),
        content_blocks=[],
        target_block_order=[],
        user_role_target_block="blk_53f32679aa514fcb",
    )
    matrix_row = _make_matrix_row(score=4.0)
    context = AdapterContext(
        execution=None,
        locale="fi",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=profile,
        profile_cache=None,
        user_name=None,
        org_name=None,
        parsed_matrices={"blk_53f32679aa514fcb": matrix_row},
    )
    blocks = ExecutiveSummaryAdapter.build(context)
    assert len(blocks) == 1
    assert isinstance(blocks[0], ParagraphBlock)
    assert blocks[0].text == "**Käyttäjärooli:** Kuljettaja (Kriittinen ohjaaja)"


def test_build_matrix_target_block_resolves_bilingual_english() -> None:
    """Test deterministic role badge resolution with English level names."""
    profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(translations={"en": "Test"}),
        content_blocks=[],
        target_block_order=[],
        user_role_target_block="blk_53f32679aa514fcb",
    )
    en_levels = {
        "1": "Passenger (Blind Faith)",
        "2": "Reactive Observer",
        "3": "Navigator (Superficial)",
        "4": "Driver (Critical Guide)",
        "5": "Architect (Active Challenger)",
    }
    matrix_row = _make_matrix_row(score=4.0, level_names=en_levels)
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
        parsed_matrices={"blk_53f32679aa514fcb": matrix_row},
    )
    blocks = ExecutiveSummaryAdapter.build(context)
    assert len(blocks) == 1
    assert isinstance(blocks[0], ParagraphBlock)
    assert blocks[0].text == "**User Role:** Driver (Critical Guide)"


@pytest.mark.parametrize(
    ("score", "expected_role_suffix"),
    [
        (0.2, "Matkustaja (Sokea usko)"),
        (1.0, "Matkustaja (Sokea usko)"),
        (2.4, "Reaktiivinen huomioija"),
        (3.4, "Navigaattori (Pintapuolinen)"),
        (3.7, "Kuljettaja (Kriittinen ohjaaja)"),
        (5.0, "Arkkitehti (Aktiivinen haastaja)"),
        (5.8, "Arkkitehti (Aktiivinen haastaja)"),
    ],
)
def test_build_matrix_target_block_clamping_boundary_scores(score: float, expected_role_suffix: str) -> None:
    """Test boundary scores clamping to integer bounds [1, 5] and mapping to level names."""
    profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(translations={"en": "Test"}),
        content_blocks=[],
        target_block_order=[],
        user_role_target_block="blk_53f32679aa514fcb",
    )
    matrix_row = _make_matrix_row(score=score)
    context = AdapterContext(
        execution=None,
        locale="fi",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=profile,
        profile_cache=None,
        user_name=None,
        org_name=None,
        parsed_matrices={"blk_53f32679aa514fcb": matrix_row},
    )
    blocks = ExecutiveSummaryAdapter.build(context)
    assert len(blocks) == 1
    assert isinstance(blocks[0], ParagraphBlock)
    assert blocks[0].text == f"**Käyttäjärooli:** {expected_role_suffix}"


def test_build_matrix_target_block_missing_from_parsed_matrices_omits_badge() -> None:
    """Negative Test: Target block configured but not evaluated in DAG trace returns empty list."""
    profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(translations={"en": "Test"}),
        content_blocks=[],
        target_block_order=[],
        user_role_target_block="blk_53f32679aa514fcb",
    )
    context = AdapterContext(
        execution=None,
        locale="fi",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=profile,
        profile_cache=None,
        user_name=None,
        org_name=None,
        parsed_matrices={},
    )
    blocks = ExecutiveSummaryAdapter.build(context)
    assert blocks == []


def test_build_matrix_target_block_score_none_omits_badge_gracefully() -> None:
    """Negative Test: Evaluated target block has score=None, role badge is omitted gracefully."""
    profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(translations={"en": "Test"}),
        content_blocks=[],
        target_block_order=[],
        user_role_target_block="blk_53f32679aa514fcb",
    )
    matrix_row = _make_matrix_row(score=None)
    cache = RenderedSynthesisCache(
        section_syntheses={
            TargetBlockType.EXECUTIVE_SUMMARY_BLOCK.value: [
                ParagraphBlock(text="Executive synthesis content.", exact_quotes=[], citations=[])
            ]
        },
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
        parsed_matrices={"blk_53f32679aa514fcb": matrix_row},
    )
    blocks = ExecutiveSummaryAdapter.build(context)
    assert len(blocks) == 1
    assert isinstance(blocks[0], ParagraphBlock)
    assert blocks[0].text == "Executive synthesis content."


def test_build_matrix_target_block_float_key_lookup() -> None:
    """Test lookup when level_names uses float string keys ('4.0')."""
    profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(translations={"en": "Test"}),
        content_blocks=[],
        target_block_order=[],
        user_role_target_block="blk_53f32679aa514fcb",
    )
    matrix_row = _make_matrix_row(score=4.0, level_names={"4.0": "Driver Float Key"})
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
        parsed_matrices={"blk_53f32679aa514fcb": matrix_row},
    )
    blocks = ExecutiveSummaryAdapter.build(context)
    assert len(blocks) == 1
    assert isinstance(blocks[0], ParagraphBlock)
    assert blocks[0].text == "**User Role:** Driver Float Key"


def test_build_matrix_target_block_level_names_empty_omits_badge() -> None:
    """Test that empty level_names in target matrix omits badge without error."""
    profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(translations={"en": "Test"}),
        content_blocks=[],
        target_block_order=[],
        user_role_target_block="blk_53f32679aa514fcb",
    )
    matrix_row = _make_matrix_row(score=4.0, level_names={})
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
        parsed_matrices={"blk_53f32679aa514fcb": matrix_row},
    )
    blocks = ExecutiveSummaryAdapter.build(context)
    assert blocks == []
