import pytest

from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.synthesis import RenderedSynthesisCache
from backend_v2.models.dtos.causal_discovery import (
    CausalGraphPayloadDTO,
    CausalNodeDTO,
    CausalTdaFusionResultDTO,
)
from backend_v2.models.dtos.matrix_scorecard import MatrixScorecardRowDTO
from backend_v2.models.enums import ExecutionStatus, RoleClassification, TargetBlockType
from backend_v2.models.view.sdui import BulletListBlock, BulletListItem, ParagraphBlock, SduiCausalGraphBlock
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext
from backend_v2.services.sdui.adapters.executive_summary_adapter import ExecutiveSummaryAdapter


def _make_matrix_row(
    block_id: str = "blk_53f32679aa514fcb",
    score: float | None = 4.0,
    raw_score: float | None = None,
    scale_min: float | None = 1.0,
    scale_max: float | None = 5.0,
    raw_scale_max: float | None = None,
    level_names: dict[str, str] | None = None,
) -> MatrixScorecardRowDTO:
    if raw_score is None:
        raw_score = score
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
        raw_score=raw_score,
        raw_scale_min=None,
        raw_scale_max=raw_scale_max,
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


def _make_context(
    profile: OutputProfile,
    locale: str = "fi",
    parsed_matrices: dict[str, MatrixScorecardRowDTO] | None = None,
    profile_cache: RenderedSynthesisCache | None = None,
    causal_result: CausalTdaFusionResultDTO | CausalGraphPayloadDTO | None = None,
) -> AdapterContext:
    return AdapterContext(
        execution=None,
        locale=locale,
        penalties_applied=[],
        mcp_audit_map=None,
        mcp_tools_map={},
        global_score=None,
        profile=profile,
        profile_cache=profile_cache,
        user_name=None,
        org_name=None,
        parsed_matrices=parsed_matrices if parsed_matrices is not None else {},
        causal_result=causal_result,
    )


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
        user_role_target_block="blk_53f32679aa514fcb",
    )
    matrix_row = _make_matrix_row(score=3.0)
    context = _make_context(
        locale="fi",
        profile=profile,
        parsed_matrices={"sr_0228db320e8f41bb_blk_53f32679aa514fcb": matrix_row},
    )

    blocks = ExecutiveSummaryAdapter.build(context)
    assert len(blocks) == 1
    assert isinstance(blocks[0], ParagraphBlock)
    assert blocks[0].text == "**Rooli:** Navigaattori"


def test_build_valid_role_with_narrative_and_section_syntheses() -> None:
    """Test role badge combined with section_syntheses."""
    profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(translations={"en": "Test"}),
        content_blocks=[],
        target_block_order=[],
        user_role_label=I18nText(translations={"en": "Role", "fi": "Rooli"}),
        user_role_target_block="blk_53f32679aa514fcb",
    )
    matrix_row = _make_matrix_row(score=3.0, level_names={"3": "Navigator"})
    cache = RenderedSynthesisCache(
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
    context = _make_context(
        locale="en",
        profile=profile,
        profile_cache=cache,
        parsed_matrices={"sr_0228db320e8f41bb_blk_53f32679aa514fcb": matrix_row},
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
        user_role_target_block="blk_53f32679aa514fcb",
    )
    matrix_row = _make_matrix_row(score=3.0, level_names={"3": "Navigator"})
    cache = RenderedSynthesisCache(
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
    context = _make_context(
        locale="en",
        profile=profile,
        profile_cache=cache,
        parsed_matrices={"sr_0228db320e8f41bb_blk_53f32679aa514fcb": matrix_row},
    )

    blocks = ExecutiveSummaryAdapter.build(context)
    # Legacy key must NOT be picked up; only the role badge is produced
    assert len(blocks) == 1
    assert isinstance(blocks[0], ParagraphBlock)
    assert blocks[0].text == "**Role:** Navigator"


def test_build_missing_user_role_returns_empty_list() -> None:
    """Test that missing user role target block returns empty list."""
    cache = RenderedSynthesisCache(
        user_role=None,
        user_role_justification="",
        section_syntheses={},
    )
    context = _make_context(
        locale="fi",
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
    )

    blocks = ExecutiveSummaryAdapter.build(context)
    assert len(blocks) == 0


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
        user_role_target_block="blk_53f32679aa514fcb",
    )
    matrix_row = _make_matrix_row(score=4.0, level_names={"4": "Driver"})
    context = _make_context(
        locale="en",
        profile=profile,
        parsed_matrices={"sr_0228db320e8f41bb_blk_53f32679aa514fcb": matrix_row},
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
    context = _make_context(
        locale="en",
        profile=profile,
        profile_cache=cache,
    )
    blocks = ExecutiveSummaryAdapter.build(context)
    assert blocks == []


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
    context = _make_context(
        locale="en",
        profile=profile,
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
    context = _make_context(
        locale="fi",
        profile=profile,
        parsed_matrices={"blk_53f32679aa514fcb": matrix_row},
    )
    blocks = ExecutiveSummaryAdapter.build(context)
    assert len(blocks) == 1
    assert isinstance(blocks[0], ParagraphBlock)
    assert blocks[0].text == "**Käyttäjärooli:** Ohjaaja"


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
    context = _make_context(
        locale="en",
        profile=profile,
        parsed_matrices={"blk_53f32679aa514fcb": matrix_row},
    )
    blocks = ExecutiveSummaryAdapter.build(context)
    assert len(blocks) == 1
    assert isinstance(blocks[0], ParagraphBlock)
    assert blocks[0].text == "**User Role:** Driver"


@pytest.mark.parametrize(
    ("score", "expected_role_suffix"),
    [
        (0.2, "Matkustaja"),
        (1.0, "Matkustaja"),
        (2.4, "Matkustaja"),
        (3.4, "Navigaattori"),
        (3.7, "Ohjaaja"),
        (5.0, "Arkkitehti"),
        (5.8, "Arkkitehti"),
    ],
)
def test_build_matrix_target_block_clamping_boundary_scores(score: float, expected_role_suffix: str) -> None:
    """Test boundary scores clamping to integer bounds [1, 5] and mapping to canonical enum names."""
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
    context = _make_context(
        locale="fi",
        profile=profile,
        parsed_matrices={"blk_53f32679aa514fcb": matrix_row},
    )
    blocks = ExecutiveSummaryAdapter.build(context)
    assert len(blocks) == 1
    assert isinstance(blocks[0], ParagraphBlock)
    assert blocks[0].text == f"**Käyttäjärooli:** {expected_role_suffix}"


def test_role_classification_extreme_boundary_clamping() -> None:
    """TC-ROLE-005: Negative test for extreme boundary clamping in RoleClassification."""
    assert RoleClassification.from_score(-10.0) == RoleClassification.PASSENGER
    assert RoleClassification.from_score(99.0) == RoleClassification.ARCHITECT


def test_build_matrix_target_block_custom_levels_not_leaked() -> None:
    """TC-ROLE-002: Negative test ensuring custom level_names from prompt do not leak into role badge."""
    profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(translations={"en": "Test"}),
        content_blocks=[],
        target_block_order=[],
        user_role_target_block="blk_53f32679aa514fcb",
    )
    custom_levels = {"1": "Perusvuorovaikutus (Noviisi)"}
    matrix_row = _make_matrix_row(score=1.0, level_names=custom_levels)
    context = _make_context(
        locale="fi",
        profile=profile,
        parsed_matrices={"blk_53f32679aa514fcb": matrix_row},
    )
    blocks = ExecutiveSummaryAdapter.build(context)
    assert len(blocks) == 1
    assert isinstance(blocks[0], ParagraphBlock)
    assert blocks[0].text == "**Käyttäjärooli:** Matkustaja"
    assert "Perusvuorovaikutus" not in blocks[0].text


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
    context = _make_context(
        locale="fi",
        profile=profile,
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
    context = _make_context(
        locale="fi",
        profile=profile,
        profile_cache=cache,
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
    context = _make_context(
        locale="en",
        profile=profile,
        parsed_matrices={"blk_53f32679aa514fcb": matrix_row},
    )
    blocks = ExecutiveSummaryAdapter.build(context)
    assert len(blocks) == 1
    assert isinstance(blocks[0], ParagraphBlock)
    assert blocks[0].text == "**User Role:** Driver"


def test_build_matrix_target_block_raw_score_none_omits_badge() -> None:
    """Test that None raw_score in target matrix omits badge without error."""
    profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(translations={"en": "Test"}),
        content_blocks=[],
        target_block_order=[],
        user_role_target_block="blk_53f32679aa514fcb",
    )
    matrix_row = _make_matrix_row(score=None, raw_score=None, level_names={})
    context = _make_context(
        locale="en",
        profile=profile,
        parsed_matrices={"blk_53f32679aa514fcb": matrix_row},
    )
    blocks = ExecutiveSummaryAdapter.build(context)
    assert blocks == []


def test_build_matrix_target_block_with_composite_step_block_id_key() -> None:
    """Regression test: parsed_matrices is keyed by composite f'{step_id}_{block_id}' from MatrixDomainParser."""
    profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(translations={"en": "Test"}),
        content_blocks=[],
        target_block_order=[],
        user_role_target_block="blk_53f32679aa514fcb",
    )
    matrix_row = _make_matrix_row(
        block_id="blk_53f32679aa514fcb",
        score=4.0,
        level_names={"4": "Driver (Critical Guide)"},
    )
    context = _make_context(
        locale="en",
        profile=profile,
        parsed_matrices={"sr_0228db320e8f41bb_blk_53f32679aa514fcb": matrix_row},
    )
    blocks = ExecutiveSummaryAdapter.build(context)
    assert len(blocks) == 1
    assert isinstance(blocks[0], ParagraphBlock)
    assert blocks[0].text == "**User Role:** Driver"


def test_build_matrix_target_block_absent_omits_badge_without_fallback() -> None:
    """Zero Fallback Mandate: if user_role_target_block is not in parsed_matrices, do not fall back to legacy strings."""
    profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(translations={"en": "Test"}),
        content_blocks=[],
        target_block_order=[],
        user_role_target_block="blk_53f32679aa514fcb",
    )
    cache = RenderedSynthesisCache(
        user_role=RoleClassification.PASSENGER.value,
        user_role_justification="Derived deterministically",
        section_syntheses={},
    )
    context = _make_context(
        locale="fi",
        profile=profile,
        profile_cache=cache,
        parsed_matrices={},
    )
    blocks = ExecutiveSummaryAdapter.build(context)
    assert blocks == []


def test_build_section_syntheses_with_bullet_list_and_causal_graph() -> None:
    """Verifies that BulletListBlock is ordered as recommendation and causal action card is injected."""
    profile = OutputProfile(
        id="prf_0123456789abcdef0123456789abcdef",
        slug="test",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        name=I18nText(translations={"en": "Test"}),
        content_blocks=[],
        target_block_order=[],
        user_role_label=None,
        user_role_target_block=None,
    )
    node = CausalNodeDTO(
        node_id="atm_01",
        claim="Claim 1",
        source_quotes=("Quote 1",),
        paragraph_ref="Section 1",
        status=ExecutionStatus.PASSED,
        blame_parent_ids=[],
        dependent_child_ids=[],
        tda_score=5.0,
        tda_level_key="L5",
    )
    causal_payload = CausalGraphPayloadDTO(
        nodes=[node],
        edges=[],
        root_cause_node_ids=["atm_01"],
        cycle_detected=False,
        isolated_node_ids=[],
    )
    cache = RenderedSynthesisCache(
        section_syntheses={
            TargetBlockType.EXECUTIVE_SUMMARY_BLOCK.value: [
                ParagraphBlock(text="Narrative intro", exact_quotes=[], citations=[]),
                BulletListBlock(
                    items=[
                        BulletListItem(text="Strategic recommendation 1", exact_quotes=[], citations=[]),
                        BulletListItem(text="Strategic recommendation 2", exact_quotes=[], citations=[]),
                    ]
                ),
            ]
        }
    )
    context = _make_context(
        locale="fi",
        profile=profile,
        profile_cache=cache,
        parsed_matrices={},
        causal_result=causal_payload,
    )
    blocks = ExecutiveSummaryAdapter.build(context)
    # Order: Narrative ParagraphBlock -> SduiCausalGraphBlock -> BulletListBlock
    assert len(blocks) == 3
    assert isinstance(blocks[0], ParagraphBlock)
    assert blocks[0].text == "Narrative intro"
    assert isinstance(blocks[1], SduiCausalGraphBlock)
    assert isinstance(blocks[2], BulletListBlock)
    assert len(blocks[2].items) == 2
