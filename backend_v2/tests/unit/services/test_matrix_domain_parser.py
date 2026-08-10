import pytest
from pydantic import BaseModel

from backend_v2.models.v2_core import I18nText, MatrixClaim, MatrixScale, OutputProfile, PromptBlock, TDAAssertion
from backend_v2.services.matrix_domain_parser import MatrixDomainParser


def get_dummy_profile():
    return OutputProfile(
        id="prof_1234567890abcdef1234567890abcdef",
        slug="test",
        workflow_id="wf1",
        name=I18nText(default_locale="en", translations={"en": "test"}),
        display_scale="original",
    )


def get_dummy_pb(category="matrix"):
    return PromptBlock(
        id="blk_1234567890abcdef1234567890abcdef",
        slug="test",
        category_id=category,
        type="float",
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


def test_clean_hallucinated_numbers():
    text = "This is a test. Taso: 5. Another sentence. piste:3."
    cleaned = MatrixDomainParser._clean_hallucinated_numbers(text)
    assert cleaned == "This is a test. Another sentence."


def test_clean_hallucinated_numbers_empty():
    assert MatrixDomainParser._clean_hallucinated_numbers("") == ""


def test_clean_hallucinated_numbers_no_match():
    text = "This is a normal sentence without scores."
    assert MatrixDomainParser._clean_hallucinated_numbers(text) == text


class MockDTO(BaseModel):
    step_id: str
    block_id: str
    payload: dict


def test_parse_matrices_empty_results():
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


def test_parse_matrices_skip_non_matrix():
    profile = get_dummy_profile()
    dto = MockDTO(step_id="step1", block_id="blk_1234567890abcdef1234567890abcdef", payload={"key": "val"})
    pb = get_dummy_pb(category="agent_role")

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


def test_parse_matrices_invalid_payload_fail_fast():
    profile = get_dummy_profile()

    class BadDTO:
        step_id = "step1"
        block_id = "blk_1234567890abcdef1234567890abcdef"
        payload = "not a dict"

    pb = get_dummy_pb(category="matrix")

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


def test_parse_matrices_success():
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
