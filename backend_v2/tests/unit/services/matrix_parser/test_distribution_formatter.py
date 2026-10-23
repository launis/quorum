"""Unit tests for matrix distribution and row explanation formatting utilities."""

from __future__ import annotations

from typing import Any, Literal, overload

import pytest
from pydantic import BaseModel

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.matrix import MatrixClaim, MatrixScale, TDAAssertion
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import (
    PROMPT_BLOCK_REGISTRY,
    MatrixPromptBlock,
    PromptBlock,
    SystemRulePromptBlock,
)
from backend_v2.models.domain.synthesis import MatrixSynthesisGroup, RenderedSynthesisCache
from backend_v2.models.dtos.lightweight_matrix import LevelStatsDTO
from backend_v2.models.dtos.trace import DataStarvationEvent
from backend_v2.models.enums import (
    BlockDataType,
    DisplayScale,
    LaxPromptBlockCategory,
    PromptBlockCategory,
)
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.services.matrix_parser import MatrixDomainParser, format_level_breakdown, format_level_distribution


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


def test_clean_hallucinated_numbers() -> None:
    """Verify sentences with hallucinated numeric level/score markers are stripped."""
    text = "This is a test. Taso: 5. Another sentence. piste:3."
    cleaned = MatrixDomainParser._clean_hallucinated_numbers(text)
    assert cleaned == "This is a test. Another sentence."


def test_clean_hallucinated_numbers_empty() -> None:
    """Verify empty text returns empty string."""
    assert MatrixDomainParser._clean_hallucinated_numbers("") == ""


def test_clean_hallucinated_numbers_no_match() -> None:
    """Verify sentences without numeric markers remain intact."""
    text = "This is a normal sentence without scores."
    assert MatrixDomainParser._clean_hallucinated_numbers(text) == text


def test_format_level_distribution_model_b_rules() -> None:
    """Verify Model B distribution rules across Pure Capability, Pure Error Radar, and Hybrid partitions."""
    # Rule 1: Pure Capability (single and plural)
    stat_cap_1 = LevelStatsDTO(hits=1, total=1, pos_hits=1, pos_total=1, inv_clean=0, inv_total=0)
    assert MatrixDomainParser._format_level_distribution(stat_cap_1, "en") == "1/1"
    stat_cap_n = LevelStatsDTO(hits=2, total=3, pos_hits=2, pos_total=3, inv_clean=0, inv_total=0)
    assert MatrixDomainParser._format_level_distribution(stat_cap_n, "en") == "2/3 skills"
    assert MatrixDomainParser._format_level_distribution(stat_cap_n, "fi") == "2/3 taitoa"

    # Rule 2: Pure Error Radar (clean vs defects)
    stat_err_clean = LevelStatsDTO(hits=2, total=2, pos_hits=0, pos_total=0, inv_clean=2, inv_total=2)
    assert MatrixDomainParser._format_level_distribution(stat_err_clean, "en") == "purity 2/2"
    stat_err_1 = LevelStatsDTO(hits=1, total=2, pos_hits=0, pos_total=0, inv_clean=1, inv_total=2)
    assert MatrixDomainParser._format_level_distribution(stat_err_1, "en") == "purity 1/2 (⚠️ 1 defect)"
    stat_err_n = LevelStatsDTO(hits=0, total=2, pos_hits=0, pos_total=0, inv_clean=0, inv_total=2)
    assert MatrixDomainParser._format_level_distribution(stat_err_n, "fi") == "puhtaus 0/2 (⚠️ 2 virhettä)"

    # Rule 3: Hybrid Level
    stat_hyb_clean = LevelStatsDTO(hits=3, total=3, pos_hits=1, pos_total=1, inv_clean=2, inv_total=2)
    assert MatrixDomainParser._format_level_distribution(stat_hyb_clean, "en") == "1/1, purity 2/2"
    stat_hyb_def = LevelStatsDTO(hits=2, total=4, pos_hits=1, pos_total=2, inv_clean=1, inv_total=2)
    assert MatrixDomainParser._format_level_distribution(stat_hyb_def, "en") == "1/2 skills, purity 1/2 (⚠️ 1 defect)"

    # Fractional level key formatting in format_level_breakdown
    bd = format_level_breakdown({"2.5": LevelStatsDTO(hits=1, total=2)}, "en", "blk_1234567890abcdef1234567890abcdef")
    assert bd == {"2.5": "1/2"}


def test_parse_matrices_level_breakdown_and_synthesis_cache() -> None:
    """Test level breakdown parsing, invalid level breakdown, and synthesis cache requirements."""
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

    res = MatrixDomainParser.parse_matrices(
        results=[dto_valid],
        locale="en",
        blocks_by_id={"blk_1234567890abcdef1234567890abcdef": pb},
        workflow_steps={},
        profile=profile_3d,
        row_explanations_cache={},
        workflow_ext_values=[],
        row_curated_quotes_cache={},
    )
    all_parsed = res.all_parsed_matrices
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
            row_explanations_cache={},
            workflow_ext_values=[],
            row_curated_quotes_cache={},
        )
    assert exc_synth.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR.value


def test_parse_matrices_data_starvation_bypasses_missing_row_explanations_cache() -> None:
    """Test that data starvation bypasses the missing row_explanations_cache check."""
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
        output_profile_id=profile.id,
        profile_syntheses={profile.id: starvation_cache},
        target_locale="fi",
        metadata=ExecutionMetadata(),
    )

    res = MatrixDomainParser.parse_matrices(
        results=[dto_valid],
        locale="en",
        blocks_by_id={"blk_1234567890abcdef1234567890abcdef": pb},
        workflow_steps={},
        profile=profile_synth,
        row_explanations_cache={},
        workflow_ext_values=[],
        row_curated_quotes_cache={},
        execution=exec_record,
    )
    all_parsed = res.all_parsed_matrices
    matrix = all_parsed["step1_blk_1234567890abcdef1234567890abcdef"]
    assert matrix.row_explanation == ""


def test_parse_matrices_invalid_level_breakdown_key_fail_fast() -> None:
    """Verifies that non-numeric level breakdown keys fail fast with VALIDATION_FAILED."""
    profile = get_dummy_profile()
    pb = get_dummy_pb()

    payload = {
        "raw_score": 1.0,
        "normalized_score": 100.0,
        "evaluated_atoms": {},
        "level_breakdown": {"invalid_level_key": {"hits": 1, "total": 2}},
    }
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
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "Invalid level key" in str(exc_info.value)
