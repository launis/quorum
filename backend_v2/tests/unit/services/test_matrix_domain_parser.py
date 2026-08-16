from typing import Any

import pytest
from pydantic import BaseModel

from backend_v2.models.enums import BlockDataType, ExecutionStatus, LaxPromptBlockCategory, PromptBlockCategory
from backend_v2.models.v2_core import I18nText, MatrixClaim, MatrixScale, OutputProfile, PromptBlock, TDAAssertion
from backend_v2.services.matrix_domain_parser import MatrixDomainParser


def get_dummy_profile() -> OutputProfile:
    return OutputProfile(
        id="prof_1234567890abcdef1234567890abcdef",
        slug="test",
        workflow_id="wf1",
        name=I18nText(default_locale="en", translations={"en": "test"}),
        display_scale="original",
    )


def get_dummy_pb(category: LaxPromptBlockCategory = PromptBlockCategory.MATRIX) -> PromptBlock:
    return PromptBlock(
        id="blk_1234567890abcdef1234567890abcdef",
        slug="test",
        category_id=category,
        type=BlockDataType.FLOAT,
        is_evaluative=True,
        label=I18nText(default_locale="en", translations={"en": "test"}),
        description=I18nText(default_locale="en", translations={"en": "test"}),
        computed_min=0,
        computed_max=1,
        scales=[
            MatrixScale(
                score=0,
                name=I18nText(default_locale="en", translations={"en": "Bad"}),
                ai_label="BAD",
                claims=[
                    MatrixClaim(
                        label=I18nText(default_locale="en", translations={"en": "Claim"}),
                        ai_description="Desc",
                        tda_assertions=[
                            TDAAssertion(
                                inverse_evidence=False, aggregation_mode="EXISTS", concept_description="test concept"
                            )
                        ],
                    )
                ],
            ),
            MatrixScale(
                score=1,
                name=I18nText(default_locale="en", translations={"en": "Good"}),
                ai_label="GOOD",
                claims=[
                    MatrixClaim(
                        label=I18nText(default_locale="en", translations={"en": "Claim"}),
                        ai_description="Desc",
                        tda_assertions=[
                            TDAAssertion(
                                inverse_evidence=False, aggregation_mode="EXISTS", concept_description="test concept"
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
    payload: dict[str, Any]


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
