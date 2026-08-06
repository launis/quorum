import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.v2_core import I18nText, MatrixScorecardRowDTO, OutputLayoutBlock, OutputProfile
from backend_v2.models.view.sdui import MarkdownBlock, SduiMatrixTableBlock
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext
from backend_v2.services.sdui.adapters.matrix_summary_table_adapter import MatrixSummaryTableAdapter


def test_matrix_summary_table_adapter_empty_layouts():
    profile = OutputProfile(
        id="prf_1234567890abcdef",
        slug="test",
        workflow_id="wf_123",
        name=I18nText(default_locale="en", translations={"en": "test"}),
        layouts=[],
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
    )
    blocks = MatrixSummaryTableAdapter.build(context)
    assert len(blocks) == 0


def test_matrix_summary_table_adapter_structural_failure():
    # matrix_summary requires at least 1 axis
    profile = OutputProfile(
        id="prf_1234567890abcdef",
        slug="test",
        workflow_id="wf_123",
        name=I18nText(default_locale="en", translations={"en": "test"}),
        layouts=[
            OutputLayoutBlock(
                preset_view="matrix_summary",
                title=I18nText(default_locale="en", translations={"en": "Summary"}),
                target_blocks=["m1"],
            )
        ],
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
    )
    with pytest.raises(AppException) as exc:
        MatrixSummaryTableAdapter.build(context)

    assert "Structurally incompatible: layout 'matrix_summary' requires at least 1 axes, found 0." in str(exc.value)


def test_matrix_summary_table_adapter_success():
    profile = OutputProfile(
        id="prf_1234567890abcdef",
        slug="test",
        workflow_id="wf_123",
        name=I18nText(default_locale="en", translations={"en": "test"}),
        layouts=[
            OutputLayoutBlock(
                preset_view="matrix_summary",
                title=I18nText(default_locale="en", translations={"en": "Table Summary"}),
                target_blocks=["m1"],
                matrix_visible_columns=["label", "score"],
            )
        ],
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
        parsed_matrices={
            "m1": MatrixScorecardRowDTO(
                block_id="m1",
                name="M1",
                score=5.0,
                scale_min=1.0,
                scale_max=5.0,
                is_evaluative=True,
                label_i18n=I18nText(default_locale="en", translations={"en": "M1"}),
                row_explanation="expl",
            )
        },
    )
    blocks = MatrixSummaryTableAdapter.build(context)
    assert len(blocks) == 2
    assert isinstance(blocks[0], MarkdownBlock)
    assert blocks[0].text == "### Table Summary"
    assert isinstance(blocks[1], SduiMatrixTableBlock)
    assert len(blocks[1].axes) == 1
    assert blocks[1].matrix_visible_columns == ["label", "score"]


def test_matrix_summary_table_adapter_validation_missing_id():
    """EP (Validation Missing ID): Target block not found in parsed_matrices triggers exception."""
    profile = OutputProfile(
        id="prf_1234567890abcdef",
        slug="test",
        workflow_id="wf_123",
        name=I18nText(default_locale="en", translations={"en": "test"}),
        layouts=[
            OutputLayoutBlock(
                preset_view="matrix_summary",
                title=I18nText(default_locale="en", translations={"en": "Summary"}),
                target_blocks=["invalid_id"],  # Missing ID in parsed_matrices
            )
        ],
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
        parsed_matrices={
            "m1": MatrixScorecardRowDTO(
                block_id="m1",
                name="M1",
                score=5.0,
                scale_min=1.0,
                scale_max=5.0,
                is_evaluative=True,
                label_i18n=I18nText(default_locale="en", translations={"en": "M1"}),
                row_explanation="expl",
            )
        },
    )
    with pytest.raises(AppException) as exc:
        MatrixSummaryTableAdapter.build(context)

    assert "requires at least 1 axes, found 0" in str(exc.value)


def test_matrix_summary_table_adapter_empty_scorecard_atoms():
    """BVA (Empty Scorecard Atoms): Provide a scorecard with an empty list of evaluated_atoms to assert it renders gracefully."""
    profile = OutputProfile(
        id="prf_1234567890abcdef",
        slug="test",
        workflow_id="wf_123",
        name=I18nText(default_locale="en", translations={"en": "test"}),
        layouts=[
            OutputLayoutBlock(
                preset_view="matrix_summary",
                title=I18nText(default_locale="en", translations={"en": "Table Summary"}),
                target_blocks=["m1"],
            )
        ],
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
        parsed_matrices={
            "m1": MatrixScorecardRowDTO(
                block_id="m1",
                name="M1",
                score=5.0,
                scale_min=1.0,
                scale_max=5.0,
                is_evaluative=True,
                label_i18n=I18nText(default_locale="en", translations={"en": "M1"}),
                row_explanation="expl",
                evaluated_atoms=[],  # Empty atoms list
            )
        },
    )
    blocks = MatrixSummaryTableAdapter.build(context)
    assert len(blocks) == 2
    assert isinstance(blocks[0], MarkdownBlock)
    assert isinstance(blocks[1], SduiMatrixTableBlock)
    assert len(blocks[1].axes) == 1
    assert blocks[1].axes[0].evaluated_atoms == []


def test_matrix_summary_table_adapter_wildcard_target_blocks():
    """EP (Wildcard Target Blocks): Provide target_blocks=["*"] to trigger the list(all_parsed_matrices.values()) branch."""
    profile = OutputProfile(
        id="prf_1234567890abcdef",
        slug="test",
        workflow_id="wf_123",
        name=I18nText(default_locale="en", translations={"en": "test"}),
        layouts=[
            OutputLayoutBlock(
                preset_view="matrix_summary",
                title=I18nText(default_locale="en", translations={"en": "Table Summary"}),
                target_blocks=["*"],
            )
        ],
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
        parsed_matrices={
            "m1": MatrixScorecardRowDTO(
                block_id="m1",
                name="M1",
                score=5.0,
                scale_min=1.0,
                scale_max=5.0,
                is_evaluative=True,
                label_i18n=I18nText(default_locale="en", translations={"en": "M1"}),
                row_explanation="expl",
            ),
            "m2": MatrixScorecardRowDTO(
                block_id="m2",
                name="M2",
                score=4.0,
                scale_min=1.0,
                scale_max=5.0,
                is_evaluative=True,
                label_i18n=I18nText(default_locale="en", translations={"en": "M2"}),
                row_explanation="expl2",
            ),
        },
    )
    blocks = MatrixSummaryTableAdapter.build(context)
    assert len(blocks) == 2
    assert isinstance(blocks[0], MarkdownBlock)
    assert isinstance(blocks[1], SduiMatrixTableBlock)
    assert len(blocks[1].axes) == 2


def test_matrix_summary_table_adapter_layout_description_and_section_syntheses():
    """EP (Layout Description and Section Syntheses): verify description and section_blocks injection."""
    from backend_v2.models.v2_core import RenderedSynthesisCache, SynthesisConfigDTO
    from backend_v2.models.view.sdui import MarkdownBlock, ParagraphBlock

    profile = OutputProfile(
        id="prf_1234567890abcdef",
        slug="test",
        workflow_id="wf_123",
        name=I18nText(default_locale="en", translations={"en": "test"}),
        layouts=[
            OutputLayoutBlock(
                preset_view="matrix_summary",
                title=I18nText(default_locale="en", translations={"en": "Table Summary"}),
                target_blocks=["m1"],
                description=I18nText(default_locale="en", translations={"en": "Test description"}),
                synthesis=SynthesisConfigDTO(enable_pii_masking=False),
            )
        ],
    )
    cache = RenderedSynthesisCache(
        section_syntheses={"layout_0_matrix_summary": [MarkdownBlock(text="Synthesis markdown content")]}
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
        parsed_matrices={
            "m1": MatrixScorecardRowDTO(
                block_id="m1",
                name="M1",
                score=5.0,
                scale_min=1.0,
                scale_max=5.0,
                is_evaluative=True,
                label_i18n=I18nText(default_locale="en", translations={"en": "M1"}),
                row_explanation="expl",
            )
        },
    )
    blocks = MatrixSummaryTableAdapter.build(context)
    assert len(blocks) == 4
    assert isinstance(blocks[0], MarkdownBlock)
    assert blocks[0].text == "### Table Summary"
    assert isinstance(blocks[1], ParagraphBlock)
    assert blocks[1].text == "Test description"
    assert isinstance(blocks[2], MarkdownBlock)
    assert blocks[2].text == "Synthesis markdown content"
    assert isinstance(blocks[3], SduiMatrixTableBlock)


class MockDict:
    """Mock dictionary for testing KeyError."""

    def __contains__(self, item: object) -> bool:
        """Mock contains."""
        return True

    def __getitem__(self, item: object) -> object:
        """Mock getitem."""
        raise KeyError(item)


def test_matrix_summary_table_adapter_key_error(monkeypatch: pytest.MonkeyPatch):
    """Negative Path (Configuration Error): Mock a deletion in MATRIX_SUMMARY_RULES dynamically to trigger KeyError."""
    from backend_v2.services.sdui.adapters import matrix_summary_table_adapter

    monkeypatch.setattr(matrix_summary_table_adapter, "MATRIX_SUMMARY_RULES", MockDict())

    profile = OutputProfile(
        id="prf_1234567890abcdef",
        slug="test",
        workflow_id="wf_123",
        name=I18nText(default_locale="en", translations={"en": "test"}),
        layouts=[
            OutputLayoutBlock(
                preset_view="matrix_summary",
                title=I18nText(default_locale="en", translations={"en": "Table Summary"}),
                target_blocks=["m1"],
            )
        ],
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
        parsed_matrices={
            "m1": MatrixScorecardRowDTO(
                block_id="m1",
                name="M1",
                score=5.0,
                scale_min=1.0,
                scale_max=5.0,
                is_evaluative=True,
                label_i18n=I18nText(default_locale="en", translations={"en": "M1"}),
                row_explanation="expl",
            )
        },
    )
    with pytest.raises(AppException) as exc:
        MatrixSummaryTableAdapter.build(context)

    assert "Missing rule mapping for preset_view: matrix_summary" in str(exc.value)
