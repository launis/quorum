from typing import Any

import pytest
from pydantic import BaseModel

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
from backend_v2.models.state import WorkflowState  # noqa: F401
from backend_v2.models.v2_core import (
    ExpectedInput,
    I18nText,
    MatrixClaim,
    MatrixScale,
    OutputProfile,
    TDAAssertion,
)
from backend_v2.services.matrix_domain_parser import MatrixDomainParser


def get_dummy_profile(
    display_scale: DisplayScale = DisplayScale.ORIGINAL,
    custom_scale_min: float | None = None,
    custom_scale_max: float | None = None,
    matrix_visible_columns: list[str] | None = None,
) -> OutputProfile:
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
        else ["label", "category", "target", "score", "level_breakdown"],
        target_block_order=[],
    )


def get_dummy_pb_5_scale() -> PromptBlock:
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


def get_dummy_pb(category: LaxPromptBlockCategory = PromptBlockCategory.MATRIX) -> PromptBlock:
    label = I18nText(translations={"en": "test"})
    desc = I18nText(translations={"en": "test"})
    cat_enum = PromptBlockCategory(category) if isinstance(category, str) else category
    if cat_enum != PromptBlockCategory.MATRIX:
        cls = PROMPT_BLOCK_REGISTRY.get(cat_enum, SystemRulePromptBlock)
        return cls(  # type: ignore[call-arg]
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
        category_id=category,
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
                            )
                        ],
                    )
                ],
            ),
        ],
    )


def test_clean_hallucinated_numbers() -> None:
    text = "This is a test. Taso: 5. Another sentence. piste:3."
    cleaned = MatrixDomainParser._clean_hallucinated_numbers(text)
    assert cleaned == "This is a test. Another sentence."


def test_clean_hallucinated_numbers_empty() -> None:
    assert MatrixDomainParser._clean_hallucinated_numbers("") == ""


def test_clean_hallucinated_numbers_no_match() -> None:
    text = "This is a normal sentence without scores."
    assert MatrixDomainParser._clean_hallucinated_numbers(text) == text


class MockDTO(BaseModel):
    step_id: str
    block_id: str
    payload: Any


def test_parse_matrices_empty_results() -> None:
    profile = get_dummy_profile()
    eval_m, info_m, all_parsed, step_atoms = MatrixDomainParser.parse_matrices(
        results=[],
        locale="en",
        blocks_by_id={},
        workflow_steps={},
        profile=profile,
        row_explanations_cache={},
        workflow_ext_values=[],
        row_curated_quotes_cache={},
    )
    assert not eval_m
    assert not info_m
    assert not all_parsed


def test_parse_matrices_skip_non_matrix() -> None:
    profile = get_dummy_profile()
    dto = MockDTO(step_id="step1", block_id="blk_1234567890abcdef1234567890abcdef", payload={"key": "val"})
    pb = get_dummy_pb(category=PromptBlockCategory.AGENT_ROLE)

    eval_m, info_m, all_parsed, step_atoms = MatrixDomainParser.parse_matrices(
        results=[dto],
        locale="en",
        blocks_by_id={"blk_1234567890abcdef1234567890abcdef": pb},
        workflow_steps={},
        profile=profile,
        row_explanations_cache={},
        workflow_ext_values=[],
        row_curated_quotes_cache={},
    )
    assert not eval_m


def test_parse_matrices_invalid_payload_fail_fast() -> None:
    profile = get_dummy_profile()

    class BadDTO:
        step_id = "step1"
        block_id = "blk_1234567890abcdef1234567890abcdef"
        payload = "not a dict"

    pb = get_dummy_pb(category=PromptBlockCategory.MATRIX)

    from backend_v2.exceptions import AppException

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


def test_parse_matrices_success() -> None:
    profile = get_dummy_profile()
    pb = get_dummy_pb()

    payload = {"raw_score": 1.0, "normalized_score": 100.0, "evaluated_atoms": {}}
    dto = MockDTO(step_id="step1", block_id="blk_1234567890abcdef1234567890abcdef", payload=payload)

    eval_m, info_m, all_parsed, step_atoms = MatrixDomainParser.parse_matrices(
        results=[dto],
        locale="en",
        blocks_by_id={"blk_1234567890abcdef1234567890abcdef": pb},
        workflow_steps={},
        profile=profile,
        row_explanations_cache={"blk_1234567890abcdef1234567890abcdef": "Good!"},
        workflow_ext_values=[],
        row_curated_quotes_cache={},
    )
    assert "step1_blk_1234567890abcdef1234567890abcdef" in all_parsed
    matrix = all_parsed["step1_blk_1234567890abcdef1234567890abcdef"]
    assert matrix.row_explanation == "Good!"


def test_parse_matrices_na_bypass() -> None:
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

    eval_m, info_m, all_parsed, step_atoms = MatrixDomainParser.parse_matrices(
        results=[dto],
        locale="en",
        blocks_by_id={"blk_1234567890abcdef1234567890abcdef": pb},
        workflow_steps={},
        profile=profile,
        row_explanations_cache={"blk_1234567890abcdef1234567890abcdef": "N/A!"},
        workflow_ext_values=[],
        row_curated_quotes_cache={},
    )
    matrix = all_parsed["step1_blk_1234567890abcdef1234567890abcdef"]
    assert matrix.score is None
    assert matrix.normalized_score is None
    assert matrix.true_atoms == 0
    assert matrix.total_atoms == 0


def test_parse_matrices_failed_does_not_increment() -> None:
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

    eval_m, info_m, all_parsed, step_atoms = MatrixDomainParser.parse_matrices(
        results=[dto],
        locale="en",
        blocks_by_id={"blk_1234567890abcdef1234567890abcdef": pb},
        workflow_steps={},
        profile=profile,
        row_explanations_cache={"blk_1234567890abcdef1234567890abcdef": "Mixed!"},
        workflow_ext_values=[],
        row_curated_quotes_cache={},
    )
    matrix = all_parsed["step1_blk_1234567890abcdef1234567890abcdef"]
    assert matrix.true_atoms == 1
    assert matrix.total_atoms == 3
    assert matrix.score == 0.3


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
    """ISTQB Partitions:
    1. Evaluative=True, Override=True
    2. Evaluative=True, Override=False
    3. Evaluative=False, Override=True
    4. Evaluative=False, Override=False
    Verifies that axis_name is never mutated with string asterisks and DTO flags are strictly preserved.
    """
    profile = get_dummy_profile()
    pb = get_dummy_pb()
    pb = pb.model_copy(update={"is_evaluative": is_evaluative, "allow_contextual_override": allow_override})

    payload = {"raw_score": 0.8, "normalized_score": 80.0, "evaluated_atoms": {}}
    dto = MockDTO(step_id="step1", block_id="blk_1234567890abcdef1234567890abcdef", payload=payload)

    eval_m, info_m, all_parsed, step_atoms = MatrixDomainParser.parse_matrices(
        results=[dto],
        locale="en",
        blocks_by_id={"blk_1234567890abcdef1234567890abcdef": pb},
        workflow_steps={},
        profile=profile,
        row_explanations_cache={"blk_1234567890abcdef1234567890abcdef": "Valid explanation."},
        workflow_ext_values=[],
        row_curated_quotes_cache={},
    )

    assert len(eval_m) == expected_eval_count
    assert len(info_m) == expected_info_count

    matrix = all_parsed["step1_blk_1234567890abcdef1234567890abcdef"]
    # Clean axis name without appended asterisks
    assert matrix.name == "test"
    assert not matrix.name.endswith("*")
    assert matrix.is_evaluative is is_evaluative
    assert matrix.allow_contextual_override is allow_override


def test_parse_matrix_normalized_100_display_scale() -> None:
    """Positive test: display_scale=NORMALIZED_100 normalizes score to 0-100 and uses display bounds 0.0 to 100.0."""
    profile = get_dummy_profile(display_scale=DisplayScale.NORMALIZED_100)
    pb = get_dummy_pb()

    payload = {"raw_score": 0.8, "normalized_score": 80.0, "evaluated_atoms": {}}
    dto = MockDTO(step_id="step1", block_id="blk_1234567890abcdef1234567890abcdef", payload=payload)

    _eval_m, _info_m, all_parsed, _step_atoms = MatrixDomainParser.parse_matrices(
        results=[dto],
        locale="en",
        blocks_by_id={"blk_1234567890abcdef1234567890abcdef": pb},
        workflow_steps={},
        profile=profile,
        row_explanations_cache={},
        workflow_ext_values=[],
        row_curated_quotes_cache={},
    )
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

    _eval_m, _info_m, all_parsed, _step_atoms = MatrixDomainParser.parse_matrices(
        results=[dto],
        locale="en",
        blocks_by_id={"blk_1234567890abcdef1234567890abcdef": pb},
        workflow_steps={},
        profile=profile,
        row_explanations_cache={},
        workflow_ext_values=[],
        row_curated_quotes_cache={},
    )
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

    _eval_m, _info_m, all_parsed, _step_atoms = MatrixDomainParser.parse_matrices(
        results=[dto],
        locale="en",
        blocks_by_id={"blk_1234567890abcdef1234567890abcdef": pb},
        workflow_steps={},
        profile=profile,
        row_explanations_cache={},
        workflow_ext_values=[],
        row_curated_quotes_cache={},
    )
    matrix = all_parsed["step1_blk_1234567890abcdef1234567890abcdef"]
    assert matrix.scale_min == 0.0
    assert matrix.scale_max == 1.0
    assert matrix.score == 1.0
    assert matrix.score_display_label == "1.0 / 1.0"


def test_parse_matrix_custom_display_scale_missing_bounds_fail_fast() -> None:
    """Negative test: display_scale=CUSTOM with missing bounds on OutputProfile raises AppException(CONFIGURATION_ERROR)."""
    from backend_v2.exceptions import AppException, ErrorCodes

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
    from backend_v2.exceptions import AppException, ErrorCodes

    profile = get_dummy_profile()
    dto = MockDTO(
        step_id="step1",
        block_id="blk_1234567890abcdef1234567890abcdef",
        payload={"raw_score": 1.0, "normalized_score": 100.0, "evaluated_atoms": {}},
    )

    # 1. Missing label
    pb_no_label = get_dummy_pb()
    object.__setattr__(pb_no_label, "label", None)
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

    # 2. Missing computed_min
    pb_no_min = get_dummy_pb()
    object.__setattr__(pb_no_min, "computed_min", None)
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

    # 3. Missing scales
    pb_no_scales = get_dummy_pb()
    object.__setattr__(pb_no_scales, "scales", [])
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

    # 4. Scale missing name
    pb_scale_no_name = get_dummy_pb()
    assert pb_scale_no_name.scales is not None
    object.__setattr__(pb_scale_no_name.scales[0], "name", None)
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


def test_parse_matrices_level_breakdown_and_synthesis_cache() -> None:
    """Test level breakdown parsing, invalid level breakdown, and synthesis cache requirements."""
    from backend_v2.exceptions import AppException, ErrorCodes
    from backend_v2.models.v2_core import MatrixSynthesisGroup

    profile = get_dummy_profile()
    pb = get_dummy_pb()

    # 1. Valid level breakdown with 3D matrix visible columns
    profile_3d = profile.model_copy(
        update={
            "matrix_synthesis_groups": [
                MatrixSynthesisGroup(
                    id="grp_1234567890123456",
                    title=I18nText(translations={"en": "Matrix"}),
                    target_blocks=["blk_1234567890abcdef1234567890abcdef"],
                )
            ]
        }
    )

    payload_valid = {
        "raw_score": 1.0,
        "normalized_score": 100.0,
        "evaluated_atoms": {},
        "level_breakdown": {
            "0": {"hits": 1, "total": 2},
            "1.0": {"hits": 2, "total": 2},
        },
    }
    dto_valid = MockDTO(step_id="step1", block_id="blk_1234567890abcdef1234567890abcdef", payload=payload_valid)

    _eval_m, _info_m, all_parsed, _step_atoms = MatrixDomainParser.parse_matrices(
        results=[dto_valid],
        locale="en",
        blocks_by_id={"blk_1234567890abcdef1234567890abcdef": pb},
        workflow_steps={},
        profile=profile_3d,
        row_explanations_cache={},
        workflow_ext_values=[],
        row_curated_quotes_cache={},
    )
    matrix = all_parsed["step1_blk_1234567890abcdef1234567890abcdef"]
    assert matrix.level_breakdown == {"0": "1/2", "1": "2/2"}

    # 2. Row explanations expected but missing in row_explanations_cache -> fail-fast
    profile_synth = profile.model_copy(update={"matrix_visible_columns": ["label", "row_explanation"]})
    with pytest.raises(AppException) as exc_synth:
        MatrixDomainParser.parse_matrices(
            results=[dto_valid],
            locale="en",
            blocks_by_id={"blk_1234567890abcdef1234567890abcdef": pb},
            workflow_steps={},
            profile=profile_synth,
            row_explanations_cache={},  # Missing entry for pb.id
            workflow_ext_values=[],
            row_curated_quotes_cache={},
        )
    assert exc_synth.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR.value


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

    eval_record: dict[str, Any] = {
        "tda_id": atom_id,
        "status": ExecutionStatus.PASSED,
        "evaluation_reasoning": "Strong evidence found.",
        "contextual_override": False,
        "source_quote": "Exact verbatim quote.",
        "depends_on_tda_ids": [],
        "short_circuit_reason_tda_ids": [],
    }

    dto_evals = MockDTO(
        step_id="step1",
        block_id="results",
        payload=[eval_record],
    )

    _eval_m, _info_m, all_parsed, step_atoms = MatrixDomainParser.parse_matrices(
        results=[dto_matrix, dto_evals],
        locale="en",
        blocks_by_id={"blk_1234567890abcdef1234567890abcdef": pb},
        workflow_steps={},
        profile=profile,
        row_explanations_cache={},
        workflow_ext_values=[],
        row_curated_quotes_cache={},
    )
    matrix = all_parsed["step1_blk_1234567890abcdef1234567890abcdef"]
    assert len(matrix.evaluated_atoms) == 2
    assert "step1" in step_atoms
    assert atom_id in step_atoms["step1"]
    atom_dto = step_atoms["step1"][atom_id]
    assert atom_dto.status == ExecutionStatus.PASSED
    assert atom_dto.semantic_reasoning == "Strong evidence found."
    assert atom_dto.chart_display_label != "N/A"
    assert len(atom_dto.exact_quotes) == 1
    assert atom_dto.exact_quotes[0].quote == "Exact verbatim quote."


def test_parse_matrices_data_starvation_bypasses_missing_row_explanations_cache() -> None:
    """Test that data starvation bypasses the missing row_explanations_cache check."""
    from backend_v2.models.dtos.trace import DataStarvationEvent
    from backend_v2.models.v2_core import ExecutionRecord, RenderedSynthesisCache

    profile = get_dummy_profile()
    pb = get_dummy_pb()
    profile_synth = profile.model_copy(update={"matrix_visible_columns": ["label", "row_explanation"]})

    payload_valid = {
        "raw_score": 1.0,
        "normalized_score": 100.0,
        "evaluated_atoms": {},
    }
    dto_valid = MockDTO(step_id="step1", block_id="blk_1234567890abcdef1234567890abcdef", payload=payload_valid)

    starvation_cache = RenderedSynthesisCache(
        section_syntheses={},
        row_explanations={},
        cited_sources=[],
        xai_highlights=[],
        user_role=None,
        user_role_justification=None,
        extension_metrics=None,
        data_starvation=DataStarvationEvent(total_atoms=0, reason="Data starvation"),
    )

    exec_record = ExecutionRecord(
        id="exe_1234567890abcdef",
        workflow_id="wf_1234567890abcdef",
        profile_syntheses={profile.id: starvation_cache},
    )

    _eval_m, _info_m, all_parsed, _step_atoms = MatrixDomainParser.parse_matrices(
        results=[dto_valid],
        locale="en",
        blocks_by_id={"blk_1234567890abcdef1234567890abcdef": pb},
        workflow_steps={},
        profile=profile_synth,
        row_explanations_cache={},  # Empty row_explanations_cache
        workflow_ext_values=[],
        row_curated_quotes_cache={},
        execution=exec_record,
    )
    matrix = all_parsed["step1_blk_1234567890abcdef1234567890abcdef"]
    assert matrix.row_explanation == ""


def test_parse_matrices_context_target_and_xai_extensions() -> None:
    """Test extraction of context_target, context_target_label, remediation_steps, coaching, and falsification."""
    from backend_v2.models.v2_core import StepRule

    profile = get_dummy_profile()
    pb = get_dummy_pb()

    step_rule = StepRule(
        id="sr_1234567890abcdef",
        task_blueprint="step_1234567890abcdef",
        input_mappings={"context": "$inputs.chat_log"},
    )

    payload = {
        "raw_score": 1.0,
        "normalized_score": 100.0,
        "evaluated_atoms": {},
        "extensions": {
            "remediation_steps": "Actionable step 1, step 2.",
            "coaching": "Coaching tips for improvement.",
            "falsification": "Falsification threshold breached if X.",
        },
    }
    dto = MockDTO(step_id="step1", block_id="blk_1234567890abcdef1234567890abcdef", payload=payload)

    expected_inputs_map = {
        "chat_log": ExpectedInput(
            input_key="chat_log",
            label=I18nText(translations={"en": "Chat Log", "fi": "Keskusteluloki"}),
            required=True,
            is_chat_history=True,
            scan_for_performative_patterns=False,
            input_modes=["paste"],
            description=I18nText(translations={"en": "Chat log", "fi": "Keskusteluloki"}),
        )
    }

    _eval_m, _info_m, all_parsed, _step_atoms = MatrixDomainParser.parse_matrices(
        results=[dto],
        locale="en",
        blocks_by_id={"blk_1234567890abcdef1234567890abcdef": pb},
        workflow_steps={"step1": step_rule},
        profile=profile,
        row_explanations_cache={"blk_1234567890abcdef1234567890abcdef": "Valid explanation."},
        workflow_ext_values=[],
        row_curated_quotes_cache={},
        expected_inputs_map=expected_inputs_map,
    )
    row = all_parsed["step1_blk_1234567890abcdef1234567890abcdef"]
    assert row.context_target == "chat_log"
    assert row.context_target_label is not None
    assert row.context_target_label.resolve("en") == "Chat Log"
    assert row.context_target_label.resolve("fi") == "Keskusteluloki"
    assert row.remediation_steps == "Actionable step 1, step 2."
    assert row.coaching == "Coaching tips for improvement."
    assert row.falsification == "Falsification threshold breached if X."


def test_parse_matrices_dynamic_filename_context_target() -> None:
    """Test extraction of dynamic filename context_target without standard localization mapping."""
    from backend_v2.models.v2_core import StepRule

    profile = get_dummy_profile()
    pb = get_dummy_pb()

    step_rule = StepRule(
        id="sr_1234567890abcdef",
        task_blueprint="step_1234567890abcdef",
        input_mappings={"context": "financials_q3.pdf"},
    )

    payload = {
        "raw_score": 1.0,
        "normalized_score": 100.0,
        "evaluated_atoms": {},
    }
    dto = MockDTO(step_id="step1", block_id="blk_1234567890abcdef1234567890abcdef", payload=payload)

    _eval_m, _info_m, all_parsed, _step_atoms = MatrixDomainParser.parse_matrices(
        results=[dto],
        locale="en",
        blocks_by_id={"blk_1234567890abcdef1234567890abcdef": pb},
        workflow_steps={"step1": step_rule},
        profile=profile,
        row_explanations_cache={"blk_1234567890abcdef1234567890abcdef": "Valid explanation."},
        workflow_ext_values=[],
        row_curated_quotes_cache={},
    )
    row = all_parsed["step1_blk_1234567890abcdef1234567890abcdef"]
    assert row.context_target == "financials_q3.pdf"
    assert row.context_target_label is not None
    assert row.context_target_label.resolve("en") == "financials_q3.pdf"
    assert row.context_target_label.resolve("fi") == "financials_q3.pdf"
    assert row.remediation_steps is None
    assert row.coaching is None
    assert row.falsification is None


def test_parse_matrices_negative_missing_input_mappings_and_extensions() -> None:
    """ISTQB Negative Partition: Test that missing input_mappings or extensions gracefully assign None."""
    profile = get_dummy_profile()
    pb = get_dummy_pb()

    payload = {
        "raw_score": 1.0,
        "normalized_score": 100.0,
        "evaluated_atoms": {},
    }
    dto = MockDTO(step_id="step1", block_id="blk_1234567890abcdef1234567890abcdef", payload=payload)

    _eval_m, _info_m, all_parsed, _step_atoms = MatrixDomainParser.parse_matrices(
        results=[dto],
        locale="en",
        blocks_by_id={"blk_1234567890abcdef1234567890abcdef": pb},
        workflow_steps={},  # Missing step rule
        profile=profile,
        row_explanations_cache={"blk_1234567890abcdef1234567890abcdef": "Valid explanation."},
        workflow_ext_values=[],
        row_curated_quotes_cache={},
    )
    row = all_parsed["step1_blk_1234567890abcdef1234567890abcdef"]
    assert row.context_target is None
    assert row.context_target_label is None
    assert row.remediation_steps is None
    assert row.coaching is None
    assert row.falsification is None


def test_parse_matrices_axis_collision_coverage() -> None:
    """Test axis name collision resolution loop for coverage."""
    from backend_v2.models.v2_core import StepRule

    profile = get_dummy_profile()
    pb = get_dummy_pb()

    step_rule1 = StepRule(
        id="sr_1234567890abcdef",
        task_blueprint="step_1234567890abcdef",
    )
    step_rule2 = StepRule(
        id="sr_abcdef1234567890",
        task_blueprint="step_abcdef1234567890",
    )

    payload = {
        "raw_score": 1.0,
        "normalized_score": 100.0,
        "evaluated_atoms": {},
    }
    dto1 = MockDTO(step_id="step1", block_id="blk_1234567890abcdef1234567890abcdef", payload=payload)
    dto2 = MockDTO(step_id="step2", block_id="blk_1234567890abcdef1234567890abcdef", payload=payload)

    _eval_m, _info_m, all_parsed, _step_atoms = MatrixDomainParser.parse_matrices(
        results=[dto1, dto2],
        locale="en",
        blocks_by_id={"blk_1234567890abcdef1234567890abcdef": pb},
        workflow_steps={"step1": step_rule1, "step2": step_rule2},
        profile=profile,
        row_explanations_cache={"blk_1234567890abcdef1234567890abcdef": "Valid explanation."},
        workflow_ext_values=[],
        row_curated_quotes_cache={},
    )
    assert len(all_parsed) == 2
    row2 = all_parsed["step2_blk_1234567890abcdef1234567890abcdef"]
    assert "sr_abcdef1234567890" in row2.name
