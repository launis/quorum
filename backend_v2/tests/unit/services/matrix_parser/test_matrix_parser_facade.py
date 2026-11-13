"""End-to-end unit tests for the MatrixDomainParser package facade and QGR017 guardrail lockdown."""

from __future__ import annotations

from typing import Literal, overload

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.matrix import MatrixClaim, MatrixScale, TDAAssertion
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import (
    MatrixPromptBlock,
    PromptBlock,
    SystemRulePromptBlock,
)
from backend_v2.models.dtos.lightweight_matrix import LevelStatsDTO
from backend_v2.models.dtos.step_output import StepOutputDTO, StepPayloadValue
from backend_v2.models.dtos.trace import TraceMatrixPayloadDTO
from backend_v2.models.enums import (
    BlockDataType,
    DisplayScale,
    LaxPromptBlockCategory,
    PromptBlockCategory,
)
from backend_v2.services.matrix_parser import MatrixDomainParser
from scripts._ast_guardrails import GuardrailSeverity, scan_source_code_for_guardrails


def MockDTO(step_id: str, block_id: str, payload: StepPayloadValue = None) -> StepOutputDTO:
    """Test helper constructing a StepOutputDTO for matrix tests."""
    return StepOutputDTO.model_construct(
        step_id=step_id,
        block_id=block_id,
        data_type="matrix",
        payload=payload,
    )


def get_dummy_profile(
    display_scale: DisplayScale = DisplayScale.ORIGINAL,
    custom_scale_min: float | None = None,
    custom_scale_max: float | None = None,
    matrix_visible_columns: list[str] | None = None,
) -> OutputProfile:
    """Create a dummy OutputProfile for unit testing."""
    if display_scale == DisplayScale.CUSTOM and custom_scale_min is None and custom_scale_max is None:
        custom_scale_min = 4.0
        custom_scale_max = 10.0
    return OutputProfile(
        organization_id="org_0195f3a0000070008000000000000001",
        id="prf_1234567890abcdef1234567890abcdef",
        slug="test",
        workflow_id="wor_1234567890abcdef1234567890abcdef",
        name=I18nText(translations={"en": "test"}),
        display_scale=display_scale,
        custom_scale_min=custom_scale_min,
        custom_scale_max=custom_scale_max,
        visible_metadata=[],
        visible_block_extensions=[],
        visible_workflow_extensions=[],
        matrix_visible_columns=matrix_visible_columns
        if matrix_visible_columns is not None
        else ["label", "distribution", "raw_score"],
        matrix_synthesis_groups=[],
        target_block_order=[],
        content_blocks=[],
    )


@overload
def get_dummy_pb(category: Literal[PromptBlockCategory.MATRIX] = ...) -> MatrixPromptBlock: ...


@overload
def get_dummy_pb(category: LaxPromptBlockCategory) -> PromptBlock: ...


def get_dummy_pb(category: LaxPromptBlockCategory = PromptBlockCategory.MATRIX) -> PromptBlock:
    """Create a dummy MatrixPromptBlock or PromptBlock for unit testing."""
    label = I18nText(translations={"en": "test"})
    desc = I18nText(translations={"en": "test"})
    cat_enum = PromptBlockCategory(category) if isinstance(category, str) else category
    if cat_enum != PromptBlockCategory.MATRIX:
        return SystemRulePromptBlock(
            organization_id="org_0195f3a0000070008000000000000001",
            id="blk_1234567890abcdef1234567890abcdef",
            slug="test",
            category_id=PromptBlockCategory.SYSTEM_RULE,
            type=BlockDataType.INSTRUCTION,
            label=label,
            description=desc,
            output_extensions=[],
        )
    return MatrixPromptBlock(
        organization_id="org_0195f3a0000070008000000000000001",
        id="blk_1234567890abcdef1234567890abcdef",
        slug="test",
        category_id=PromptBlockCategory.MATRIX,
        type=BlockDataType.FLOAT,
        is_evaluative=True,
        label=label,
        description=desc,
        output_extensions=[],
        computed_min=0,
        computed_max=1,
        scales=[
            MatrixScale(
                score=0,
                name=I18nText(translations={"en": "Bad"}),
                ai_label="BAD",
                claims=[
                    MatrixClaim(
                        label=I18nText(translations={"en": "Claim"}),
                        tda_assertions=[
                            TDAAssertion(
                                tda_id="tda_11111111111111111111111111111111",
                                inverse_evidence=False,
                                aggregation_mode="EXISTS",
                                concept_description="test concept description",
                                facts_to_find=[],
                                acceptance_criteria=[],
                                anti_patterns=[],
                                syntactic_anchors=[],
                                depends_on=(),
                            )
                        ],
                    )
                ],
            ),
            MatrixScale(
                score=1,
                name=I18nText(translations={"en": "Good"}),
                ai_label="GOOD",
                claims=[
                    MatrixClaim(
                        label=I18nText(translations={"en": "Claim"}),
                        tda_assertions=[
                            TDAAssertion(
                                tda_id="tda_22222222222222222222222222222222",
                                inverse_evidence=False,
                                aggregation_mode="EXISTS",
                                concept_description="test concept description",
                                facts_to_find=[],
                                acceptance_criteria=[],
                                anti_patterns=[],
                                syntactic_anchors=[],
                                depends_on=(),
                            )
                        ],
                    )
                ],
            ),
        ],
    )


def test_parse_matrices_empty_results() -> None:
    """Verify empty results return empty collections."""
    profile = get_dummy_profile()
    res = MatrixDomainParser.parse_matrices(
        results=[],
        locale="en",
        blocks_by_id={},
        workflow_steps={},
        profile=profile,
        row_explanations_cache={},
        workflow_ext_values=[],
        row_curated_quotes_cache={},
    )
    assert not res.evaluative_matrices
    assert not res.informational_matrices
    assert not res.all_parsed_matrices
    assert not res.step_scorecard_atoms


def test_parse_matrices_skip_non_matrix() -> None:
    """Verify non-matrix PromptBlocks are skipped."""
    profile = get_dummy_profile()
    dto = StepOutputDTO(
        step_id="step1",
        block_id="blk_1234567890abcdef1234567890abcdef",
        data_type="matrix",
        payload={"key": "val"},
    )
    pb = get_dummy_pb(category=PromptBlockCategory.AGENT_ROLE)

    res = MatrixDomainParser.parse_matrices(
        results=[dto],
        locale="en",
        blocks_by_id={"blk_1234567890abcdef1234567890abcdef": pb},
        workflow_steps={},
        profile=profile,
        row_explanations_cache={},
        workflow_ext_values=[],
        row_curated_quotes_cache={},
    )
    assert not res.evaluative_matrices
    assert not res.informational_matrices
    assert not res.all_parsed_matrices
    assert not res.step_scorecard_atoms


def test_parse_matrices_success() -> None:
    """Verify successful parsing of a matrix row through the MatrixDomainParser facade."""
    profile = get_dummy_profile()
    pb = get_dummy_pb()

    payload = TraceMatrixPayloadDTO(raw_score=1.0, normalized_score=100.0, evaluated_atoms={})
    dto = StepOutputDTO(
        step_id="step1",
        block_id="blk_1234567890abcdef1234567890abcdef",
        data_type="matrix",
        payload=payload,
    )

    res = MatrixDomainParser.parse_matrices(
        results=[dto],
        locale="en",
        blocks_by_id={"blk_1234567890abcdef1234567890abcdef": pb},
        workflow_steps={},
        profile=profile,
        row_explanations_cache={"blk_1234567890abcdef1234567890abcdef": "Good!"},
        workflow_ext_values=[],
        row_curated_quotes_cache={},
    )
    all_parsed = res.all_parsed_matrices
    assert "step1_blk_1234567890abcdef1234567890abcdef" in all_parsed
    matrix = all_parsed["step1_blk_1234567890abcdef1234567890abcdef"]
    assert matrix.row_explanation == "Good!"


@pytest.mark.parametrize(
    "is_evaluative,allow_override,expected_eval_count,expected_info_count",
    [
        (True, True, 1, 0),
        (True, False, 1, 0),
        (False, True, 0, 1),
        (False, False, 0, 1),
    ],
)
def test_parse_matrices_indicator_partitions(
    is_evaluative: bool,
    allow_override: bool,
    expected_eval_count: int,
    expected_info_count: int,
) -> None:
    """ISTQB Partitions for evaluative and contextual override flags."""
    profile = get_dummy_profile()
    pb = get_dummy_pb()
    pb = pb.model_copy(update={"is_evaluative": is_evaluative, "allow_contextual_override": allow_override})

    payload = TraceMatrixPayloadDTO(raw_score=0.8, normalized_score=80.0, evaluated_atoms={})
    dto = StepOutputDTO(
        step_id="step1",
        block_id="blk_1234567890abcdef1234567890abcdef",
        data_type="matrix",
        payload=payload,
    )

    res = MatrixDomainParser.parse_matrices(
        results=[dto],
        locale="en",
        blocks_by_id={"blk_1234567890abcdef1234567890abcdef": pb},
        workflow_steps={},
        profile=profile,
        row_explanations_cache={"blk_1234567890abcdef1234567890abcdef": "Valid explanation."},
        workflow_ext_values=[],
        row_curated_quotes_cache={},
    )
    eval_m = res.evaluative_matrices
    info_m = res.informational_matrices
    all_parsed = res.all_parsed_matrices

    assert len(eval_m) == expected_eval_count
    assert len(info_m) == expected_info_count

    matrix = all_parsed["step1_blk_1234567890abcdef1234567890abcdef"]
    assert matrix.name == "test"
    assert not matrix.name.endswith("*")
    assert matrix.is_evaluative is is_evaluative
    assert matrix.allow_contextual_override is allow_override


def test_matrix_parser_facade_full_parse_matrices_parity() -> None:
    """Contract test: Verify MatrixDomainParser facade preserves 100% parity across evaluative and info rows."""
    profile = get_dummy_profile()
    eval_pb = get_dummy_pb().model_copy(
        update={
            "id": "blk_11111111111111111111111111111111",
            "label": I18nText(translations={"en": "Evaluative Axis"}),
            "is_evaluative": True,
        }
    )
    info_pb = get_dummy_pb().model_copy(
        update={
            "id": "blk_22222222222222222222222222222222",
            "label": I18nText(translations={"en": "Informational Axis"}),
            "is_evaluative": False,
        }
    )

    dto_eval = StepOutputDTO(
        step_id="step1",
        block_id=eval_pb.id,
        data_type="matrix",
        payload=TraceMatrixPayloadDTO(raw_score=1.0, normalized_score=100.0, evaluated_atoms={}),
    )
    dto_info = StepOutputDTO(
        step_id="step1",
        block_id=info_pb.id,
        data_type="matrix",
        payload=TraceMatrixPayloadDTO(raw_score=0.5, normalized_score=50.0, evaluated_atoms={}),
    )

    res = MatrixDomainParser.parse_matrices(
        results=[dto_eval, dto_info],
        locale="en",
        blocks_by_id={eval_pb.id: eval_pb, info_pb.id: info_pb},
        workflow_steps={},
        profile=profile,
        row_explanations_cache={
            eval_pb.id: "Eval explanation.",
            info_pb.id: "Info explanation.",
        },
        workflow_ext_values=[],
        row_curated_quotes_cache={},
    )
    assert len(res.evaluative_matrices) == 1
    assert len(res.informational_matrices) == 1
    assert res.evaluative_matrices[0].name == "Evaluative Axis"
    assert res.informational_matrices[0].name == "Informational Axis"
    assert f"step1_{eval_pb.id}" in res.all_parsed_matrices
    assert f"step1_{info_pb.id}" in res.all_parsed_matrices
    assert MatrixDomainParser._format_level_distribution(LevelStatsDTO(hits=1, total=2), "en") == "1/2"
    assert MatrixDomainParser._clean_hallucinated_numbers("Valid claim text.") == "Valid claim text."


def test_parse_matrices_skips_unmapped_block_id() -> None:
    """Verify StepOutputDTO items whose block_id is absent from blocks_by_id are safely skipped."""
    profile = get_dummy_profile()
    dto = StepOutputDTO(
        step_id="step1",
        block_id="blk_99999999999999999999999999999999",
        data_type="matrix",
        payload=TraceMatrixPayloadDTO(raw_score=1.0, normalized_score=100.0, evaluated_atoms={}),
    )
    res = MatrixDomainParser.parse_matrices(
        results=[dto],
        locale="en",
        blocks_by_id={},
        workflow_steps={},
        profile=profile,
        row_explanations_cache={},
        workflow_ext_values=[],
        row_curated_quotes_cache={},
    )
    assert not res.all_parsed_matrices


def test_parse_matrices_raises_validation_failed_on_invalid_payload() -> None:
    """Negative test: Verify malformed matrix payload raises AppException (VALIDATION_FAILED)."""
    profile = get_dummy_profile()
    pb = get_dummy_pb()
    dto = MockDTO(
        step_id="step1",
        block_id=pb.id,
        payload="invalid_non_object_payload",
    )
    with pytest.raises(AppException) as exc_info:
        MatrixDomainParser.parse_matrices(
            results=[dto],
            locale="en",
            blocks_by_id={pb.id: pb},
            workflow_steps={},
            profile=profile,
            row_explanations_cache={},
            workflow_ext_values=[],
            row_curated_quotes_cache={},
        )
    assert exc_info.value.error_code == ErrorCodes.VALIDATION_FAILED


def test_parse_matrices_raises_configuration_error_on_empty_scales() -> None:
    """Negative test: Verify MatrixPromptBlock with empty scales raises AppException (CONFIGURATION_ERROR)."""
    profile = get_dummy_profile()
    pb = MatrixPromptBlock.model_construct(
        id="blk_1234567890abcdef1234567890abcdef",
        slug="test",
        category_id=PromptBlockCategory.MATRIX,
        type=BlockDataType.FLOAT,
        is_evaluative=True,
        label=I18nText(translations={"en": "test"}),
        description=I18nText(translations={"en": "test"}),
        output_extensions=[],
        computed_min=0,
        computed_max=1,
        scales=[],
    )
    dto = StepOutputDTO(
        step_id="step1",
        block_id=pb.id,
        data_type="matrix",
        payload=TraceMatrixPayloadDTO(raw_score=1.0, normalized_score=100.0, evaluated_atoms={}),
    )
    with pytest.raises(AppException) as exc_info:
        MatrixDomainParser.parse_matrices(
            results=[dto],
            locale="en",
            blocks_by_id={pb.id: pb},
            workflow_steps={},
            profile=profile,
            row_explanations_cache={},
            workflow_ext_values=[],
            row_curated_quotes_cache={},
        )
    assert exc_info.value.error_code == ErrorCodes.CONFIGURATION_ERROR


def test_qgr017_bans_legacy_matrix_domain_parser_import() -> None:
    """Contract test: Verify QGR017 flags any import from backend_v2.services.matrix_domain_parser."""
    snippets = [
        "import backend_v2.services.matrix_domain_parser\n",
        "from backend_v2.services.matrix_domain_parser import MatrixDomainParser\n",
        "from backend_v2.services import matrix_domain_parser\n",
    ]
    for code in snippets:
        violations = scan_source_code_for_guardrails("backend_v2/services/sample.py", code.encode("utf-8"))
        qgr017_violations = [v for v in violations if v.rule_code == "QGR017"]
        assert len(qgr017_violations) == 1
        assert qgr017_violations[0].severity == GuardrailSeverity.FATAL
        assert "backend_v2.services.matrix_parser" in qgr017_violations[0].remediation
