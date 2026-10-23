"""Unit tests for matrix scale boundary projection and step scorecard atom hydration stage."""

from __future__ import annotations

from typing import Any, Literal, overload

import pytest
from pydantic import BaseModel, JsonValue

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.matrix import MatrixClaim, MatrixScale, TDAAssertion
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import (
    PROMPT_BLOCK_REGISTRY,
    MatrixPromptBlock,
    PromptBlock,
    SystemRulePromptBlock,
)
from backend_v2.models.enums import (
    BlockDataType,
    DisplayScale,
    ExecutionStatus,
    LaxPromptBlockCategory,
    PromptBlockCategory,
)
from backend_v2.services.matrix_parser import MatrixDomainParser


class MockDTO(BaseModel):
    """Test helper DTO representing a folded step output item."""

    step_id: str
    block_id: str
    payload: Any


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
        id="prof_1234567890abcdef1234567890abcdef",
        slug="test",
        workflow_id="wf1",
        name=I18nText(translations={"en": "test"}),
        display_scale=display_scale,
        custom_scale_min=custom_scale_min,
        custom_scale_max=custom_scale_max,
        matrix_visible_columns=matrix_visible_columns
        if matrix_visible_columns is not None
        else ["label", "distribution", "raw_score"],
        target_block_order=[],
    )


def get_dummy_pb_5_scale() -> MatrixPromptBlock:
    """Create a 5-scale MatrixPromptBlock for custom scale projection testing."""
    label = I18nText(translations={"en": "test"})
    desc = I18nText(translations={"en": "test"})
    scales = [
        MatrixScale(
            score=i,
            name=I18nText(translations={"en": f"Level {i}"}),
            ai_label=f"LEVEL_{i}",
            claims=[
                MatrixClaim(
                    label=I18nText(translations={"en": f"Claim {i}"}),
                    tda_assertions=[
                        TDAAssertion(
                            inverse_evidence=False,
                            aggregation_mode="EXISTS",
                            concept_description="test concept description",
                            depends_on=(),
                        )
                    ],
                )
            ],
        )
        for i in range(1, 6)
    ]
    return MatrixPromptBlock(
        id="blk_1234567890abcdef1234567890abcdef",
        slug="test",
        category_id=PromptBlockCategory.MATRIX,
        type=BlockDataType.FLOAT,
        is_evaluative=True,
        label=label,
        description=desc,
        scales=scales,
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
        if cat_enum in PROMPT_BLOCK_REGISTRY:
            cls = PROMPT_BLOCK_REGISTRY[cat_enum]
        else:
            cls = SystemRulePromptBlock
        return cls(
            id="blk_1234567890abcdef1234567890abcdef",
            slug="test",
            category_id=cat_enum,
            type=BlockDataType.INSTRUCTION,
            label=label,
            description=desc,
        )
    return MatrixPromptBlock(
        id="blk_1234567890abcdef1234567890abcdef",
        slug="test",
        category_id=PromptBlockCategory.MATRIX,
        type=BlockDataType.FLOAT,
        is_evaluative=True,
        label=label,
        description=desc,
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
                                inverse_evidence=False,
                                aggregation_mode="EXISTS",
                                concept_description="test concept description",
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
                                inverse_evidence=False,
                                aggregation_mode="EXISTS",
                                concept_description="test concept description",
                                depends_on=(),
                            )
                        ],
                    )
                ],
            ),
        ],
    )


def test_parse_matrices_invalid_payload_fail_fast() -> None:
    """Verify non-dict string payload raises AppException."""
    profile = get_dummy_profile()

    class BadDTO:
        step_id = "step1"
        block_id = "blk_1234567890abcdef1234567890abcdef"
        payload = "not a dict"

    pb = get_dummy_pb(category=PromptBlockCategory.MATRIX)

    with pytest.raises(AppException) as exc_info:
        MatrixDomainParser.parse_matrices(
            results=[BadDTO()],
            locale="en",
            blocks_by_id={"blk_1234567890abcdef1234567890abcdef": pb},
            workflow_steps={},
            profile=profile,
            row_explanations_cache={},
            workflow_ext_values=[],
            row_curated_quotes_cache={},
        )
    assert "Invalid matrix payload format" in str(exc_info.value)


def test_parse_matrices_invalid_payload_fails_fast() -> None:
    """ISTQB Negative: Non-dict / malformed payload triggers fail-fast AppException."""
    profile = get_dummy_profile()
    pb = get_dummy_pb()

    dto = MockDTO(step_id="step1", block_id="blk_1234567890abcdef1234567890abcdef", payload=12345)

    with pytest.raises(AppException) as exc_info:
        MatrixDomainParser.parse_matrices(
            results=[dto],
            locale="en",
            blocks_by_id={"blk_1234567890abcdef1234567890abcdef": pb},
            workflow_steps={},
            profile=profile,
            row_explanations_cache={},
            workflow_ext_values=[],
            row_curated_quotes_cache={},
        )
    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


def test_parse_matrices_na_bypass() -> None:
    """Verify N_A atoms bypass scoring and set score and normalized_score to None."""
    profile = get_dummy_profile()
    pb = get_dummy_pb()

    payload = {
        "raw_score": None,
        "normalized_score": None,
        "evaluated_atoms": {
            "atom_1": ExecutionStatus.N_A,
            "atom_2": ExecutionStatus.N_A,
        },
    }
    dto = MockDTO(step_id="step1", block_id="blk_1234567890abcdef1234567890abcdef", payload=payload)

    res = MatrixDomainParser.parse_matrices(
        results=[dto],
        locale="en",
        blocks_by_id={"blk_1234567890abcdef1234567890abcdef": pb},
        workflow_steps={},
        profile=profile,
        row_explanations_cache={"blk_1234567890abcdef1234567890abcdef": "N/A!"},
        workflow_ext_values=[],
        row_curated_quotes_cache={},
    )
    all_parsed = res.all_parsed_matrices
    matrix = all_parsed["step1_blk_1234567890abcdef1234567890abcdef"]
    assert matrix.score is None
    assert matrix.normalized_score is None
    assert matrix.true_atoms == 0
    assert matrix.total_atoms == 0


def test_parse_matrices_failed_does_not_increment() -> None:
    """Verify FAILED and SYSTEM_ERROR increment total_atoms but not true_atoms."""
    profile = get_dummy_profile()
    pb = get_dummy_pb()

    payload = {
        "raw_score": None,
        "normalized_score": None,
        "evaluated_atoms": {
            "atom_1": ExecutionStatus.PASSED,
            "atom_2": ExecutionStatus.FAILED,
            "atom_3": ExecutionStatus.SYSTEM_ERROR,
            "atom_4": ExecutionStatus.N_A,
        },
    }
    dto = MockDTO(step_id="step1", block_id="blk_1234567890abcdef1234567890abcdef", payload=payload)

    res = MatrixDomainParser.parse_matrices(
        results=[dto],
        locale="en",
        blocks_by_id={"blk_1234567890abcdef1234567890abcdef": pb},
        workflow_steps={},
        profile=profile,
        row_explanations_cache={"blk_1234567890abcdef1234567890abcdef": "Mixed!"},
        workflow_ext_values=[],
        row_curated_quotes_cache={},
    )
    all_parsed = res.all_parsed_matrices
    matrix = all_parsed["step1_blk_1234567890abcdef1234567890abcdef"]
    assert matrix.true_atoms == 1
    assert matrix.total_atoms == 3
    assert matrix.score == 0.3


def test_parse_matrix_normalized_100_display_scale() -> None:
    """Positive test: display_scale=NORMALIZED_100 normalizes score to 0-100 and uses display bounds 0.0 to 100.0."""
    profile = get_dummy_profile(display_scale=DisplayScale.NORMALIZED_100)
    pb = get_dummy_pb()

    payload = {"raw_score": 0.8, "normalized_score": 80.0, "evaluated_atoms": {}}
    dto = MockDTO(step_id="step1", block_id="blk_1234567890abcdef1234567890abcdef", payload=payload)

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
    all_parsed = res.all_parsed_matrices
    matrix = all_parsed["step1_blk_1234567890abcdef1234567890abcdef"]
    assert matrix.scale_min == 0.0
    assert matrix.scale_max == 100.0
    assert matrix.score == 80.0
    assert matrix.score_display_label == "80.0 / 100.0"


def test_parse_matrix_custom_display_scale() -> None:
    """Positive test: display_scale=CUSTOM uses custom_scale_min/max from OutputProfile and projects scores."""
    profile = get_dummy_profile(
        display_scale=DisplayScale.CUSTOM,
        custom_scale_min=4.0,
        custom_scale_max=10.0,
    )
    pb = get_dummy_pb_5_scale()

    payload = {"raw_score": 3.0, "normalized_score": 50.0, "evaluated_atoms": {}}
    dto = MockDTO(step_id="step1", block_id="blk_1234567890abcdef1234567890abcdef", payload=payload)

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
    all_parsed = res.all_parsed_matrices
    matrix = all_parsed["step1_blk_1234567890abcdef1234567890abcdef"]
    assert matrix.scale_min == 4.0
    assert matrix.scale_max == 10.0
    assert matrix.score == 7.0
    assert matrix.score_display_label == "7.0 / 10.0"


def test_parse_matrix_original_display_scale() -> None:
    """Positive test: display_scale=ORIGINAL uses computed_min/computed_max bounds."""
    profile = get_dummy_profile(display_scale=DisplayScale.ORIGINAL)
    pb = get_dummy_pb()

    payload = {"raw_score": 1.0, "normalized_score": 100.0, "evaluated_atoms": {}}
    dto = MockDTO(step_id="step1", block_id="blk_1234567890abcdef1234567890abcdef", payload=payload)

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
    all_parsed = res.all_parsed_matrices
    matrix = all_parsed["step1_blk_1234567890abcdef1234567890abcdef"]
    assert matrix.scale_min == 0.0
    assert matrix.scale_max == 1.0
    assert matrix.score == 1.0
    assert matrix.score_display_label == "1.0 / 1.0"


def test_parse_matrix_custom_display_scale_missing_bounds_fail_fast() -> None:
    """Negative test: display_scale=CUSTOM with missing bounds on OutputProfile raises AppException."""
    profile = OutputProfile.model_construct(
        id="prof_1234567890abcdef1234567890abcdef",
        slug="test",
        workflow_id="wf1",
        name=I18nText(translations={"en": "test"}),
        display_scale=DisplayScale.CUSTOM,
        custom_scale_min=None,
        custom_scale_max=None,
        target_block_order=[],
    )
    pb = get_dummy_pb_5_scale()

    payload = {"raw_score": 3.0, "normalized_score": 60.0, "evaluated_atoms": {}}
    dto = MockDTO(step_id="step1", block_id="blk_1234567890abcdef1234567890abcdef", payload=payload)

    with pytest.raises(AppException) as exc_info:
        MatrixDomainParser.parse_matrices(
            results=[dto],
            locale="en",
            blocks_by_id={"blk_1234567890abcdef1234567890abcdef": pb},
            workflow_steps={},
            profile=profile,
            row_explanations_cache={},
            workflow_ext_values=[],
            row_curated_quotes_cache={},
        )
    assert exc_info.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR.value
    assert "OutputProfile" in str(exc_info.value)
    assert "missing custom_scale_min/max" in str(exc_info.value)


def test_parse_matrices_missing_label_and_scales_fail_fast() -> None:
    """Negative tests: missing label, missing min/max, missing scales, and scale missing name."""
    profile = get_dummy_profile()
    dto = MockDTO(
        step_id="step1",
        block_id="blk_1234567890abcdef1234567890abcdef",
        payload={"raw_score": 1.0, "normalized_score": 100.0, "evaluated_atoms": {}},
    )

    pb_no_label = get_dummy_pb().model_copy(update={"label": None})
    with pytest.raises(AppException) as exc1:
        MatrixDomainParser.parse_matrices(
            results=[dto],
            locale="en",
            blocks_by_id={"blk_1234567890abcdef1234567890abcdef": pb_no_label},
            workflow_steps={},
            profile=profile,
            row_explanations_cache={},
            workflow_ext_values=[],
            row_curated_quotes_cache={},
        )
    assert exc1.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR.value

    pb_no_min = get_dummy_pb().model_copy(update={"computed_min": None})
    with pytest.raises(AppException) as exc2:
        MatrixDomainParser.parse_matrices(
            results=[dto],
            locale="en",
            blocks_by_id={"blk_1234567890abcdef1234567890abcdef": pb_no_min},
            workflow_steps={},
            profile=profile,
            row_explanations_cache={},
            workflow_ext_values=[],
            row_curated_quotes_cache={},
        )
    assert exc2.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR.value

    pb_no_scales = get_dummy_pb().model_copy(update={"scales": []})
    with pytest.raises(AppException) as exc3:
        MatrixDomainParser.parse_matrices(
            results=[dto],
            locale="en",
            blocks_by_id={"blk_1234567890abcdef1234567890abcdef": pb_no_scales},
            workflow_steps={},
            profile=profile,
            row_explanations_cache={},
            workflow_ext_values=[],
            row_curated_quotes_cache={},
        )
    assert exc3.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR.value

    pb_dummy = get_dummy_pb()
    assert pb_dummy.scales is not None
    scale_no_name = pb_dummy.scales[0].model_copy(update={"name": None})
    pb_scale_no_name = pb_dummy.model_copy(update={"scales": [scale_no_name, pb_dummy.scales[1]]})
    with pytest.raises(AppException) as exc4:
        MatrixDomainParser.parse_matrices(
            results=[dto],
            locale="en",
            blocks_by_id={"blk_1234567890abcdef1234567890abcdef": pb_scale_no_name},
            workflow_steps={},
            profile=profile,
            row_explanations_cache={},
            workflow_ext_values=[],
            row_curated_quotes_cache={},
        )
    assert exc4.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


def test_parse_matrices_evaluations_quotes_and_atom_results() -> None:
    """Test parsing of evaluations trace DTOs into ScorecardAtomDTOs."""
    profile = get_dummy_profile()
    pb = get_dummy_pb()
    assert pb.scales is not None
    atom_id = pb.scales[0].claims[0].tda_assertions[0].tda_id

    dto_matrix = MockDTO(
        step_id="step1",
        block_id="blk_1234567890abcdef1234567890abcdef",
        payload={"raw_score": 1.0, "normalized_score": 100.0, "evaluated_atoms": {}},
    )

    eval_record: dict[str, JsonValue] = {
        "tda_id": atom_id,
        "status": ExecutionStatus.PASSED,
        "evaluation_reasoning": "Strong evidence found.",
        "contextual_override": False,
        "source_quotes": ["Exact verbatim quote."],
        "depends_on_tda_ids": [],
        "short_circuit_reason_tda_ids": [],
    }

    dto_evals = MockDTO(
        step_id="step1",
        block_id="results",
        payload=[eval_record],
    )

    res = MatrixDomainParser.parse_matrices(
        results=[dto_matrix, dto_evals],
        locale="en",
        blocks_by_id={"blk_1234567890abcdef1234567890abcdef": pb},
        workflow_steps={},
        profile=profile,
        row_explanations_cache={},
        workflow_ext_values=[],
        row_curated_quotes_cache={},
    )
    all_parsed = res.all_parsed_matrices
    step_atoms = res.step_scorecard_atoms
    matrix = all_parsed["step1_blk_1234567890abcdef1234567890abcdef"]
    assert len(matrix.evaluated_atoms) == 2
    assert "step1" in step_atoms
    assert atom_id in step_atoms["step1"]
    atom_dto = step_atoms["step1"][atom_id]
    assert atom_dto.status == ExecutionStatus.PASSED
    assert atom_dto.semantic_reasoning == "Strong evidence found."
    assert atom_dto.chart_display_label != "N/A"
    assert len(atom_dto.exact_quotes) == 1
    assert atom_dto.exact_quotes[0].source_quotes == ("Exact verbatim quote.",)


def test_parse_matrices_custom_scale_none_raw_score() -> None:
    """Verifies that under custom scale, when raw_score is None, score_float resolves to None."""
    profile = get_dummy_profile(
        display_scale=DisplayScale.CUSTOM,
        custom_scale_min=1.0,
        custom_scale_max=10.0,
    )
    pb = get_dummy_pb()

    payload: dict[str, JsonValue] = {
        "raw_score": None,
        "normalized_score": None,
        "evaluated_atoms": {},
    }
    dto = MockDTO(step_id="step1", block_id="blk_1234567890abcdef1234567890abcdef", payload=payload)

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
    row = res.all_parsed_matrices["step1_blk_1234567890abcdef1234567890abcdef"]
    assert row.score is None
    assert row.score_display_label == "-"


def test_parse_matrices_math_max_equals_math_min() -> None:
    """Verifies that when computed_min equals computed_max, ui_plot_ratio resolves to 0.0."""
    profile = get_dummy_profile()
    pb = get_dummy_pb().model_copy(update={"computed_min": 5.0, "computed_max": 5.0})

    payload = {
        "raw_score": 5.0,
        "normalized_score": 100.0,
        "evaluated_atoms": {},
    }
    dto = MockDTO(step_id="step1", block_id="blk_1234567890abcdef1234567890abcdef", payload=payload)

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
    row = res.all_parsed_matrices["step1_blk_1234567890abcdef1234567890abcdef"]
    assert row.ui_plot_ratio == 0.0


def test_parse_matrices_invalid_atom_payload_in_results_fail_fast() -> None:
    """Verifies that invalid payloads inside results block fail fast with VALIDATION_FAILED."""
    profile = get_dummy_profile()
    pb = get_dummy_pb()

    dto_matrix = MockDTO(
        step_id="step1",
        block_id="blk_1234567890abcdef1234567890abcdef",
        payload={"raw_score": 1.0, "normalized_score": 100.0, "evaluated_atoms": {}},
    )
    dto_evals = MockDTO(
        step_id="step1",
        block_id="results",
        payload=[{"invalid_atom": "missing_required_fields"}],
    )

    with pytest.raises(AppException) as exc_info:
        MatrixDomainParser.parse_matrices(
            results=[dto_matrix, dto_evals],
            locale="en",
            blocks_by_id={"blk_1234567890abcdef1234567890abcdef": pb},
            workflow_steps={},
            profile=profile,
            row_explanations_cache={},
            workflow_ext_values=[],
            row_curated_quotes_cache={},
        )
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


def test_parse_matrices_eval_atom_concept_description_fallback() -> None:
    """Verifies that when claim label is empty, concept_description is used as display_label."""
    profile = get_dummy_profile()
    pb = get_dummy_pb()
    claim_empty = pb.scales[0].claims[0].model_copy(update={"label": None})
    scale_empty = pb.scales[0].model_copy(update={"claims": [claim_empty]})
    pb_empty = pb.model_copy(update={"scales": [scale_empty, pb.scales[1]]})

    payload = {
        "raw_score": 1.0,
        "normalized_score": 100.0,
        "evaluated_atoms": {},
    }
    dto = MockDTO(step_id="step1", block_id="blk_1234567890abcdef1234567890abcdef", payload=payload)

    res = MatrixDomainParser.parse_matrices(
        results=[dto],
        locale="en",
        blocks_by_id={"blk_1234567890abcdef1234567890abcdef": pb_empty},
        workflow_steps={},
        profile=profile,
        row_explanations_cache={},
        workflow_ext_values=[],
        row_curated_quotes_cache={},
    )
    atom = res.all_parsed_matrices["step1_blk_1234567890abcdef1234567890abcdef"].evaluated_atoms[0]
    assert atom.chart_display_label == "test concept description"
    assert atom.status == ExecutionStatus.FAILED
