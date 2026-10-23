"""Unit tests for matrix axis resolution, context target resolution, and scorecard row builder stage."""

from __future__ import annotations

from typing import Any, Literal, overload

from pydantic import BaseModel

from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.matrix import MatrixClaim, MatrixScale, TDAAssertion, TheoryGrounding
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import (
    PROMPT_BLOCK_REGISTRY,
    MatrixPromptBlock,
    PromptBlock,
    SystemRulePromptBlock,
)
from backend_v2.models.domain.step import ExpectedInput, StepRule
from backend_v2.models.enums import (
    BlockDataType,
    DisplayScale,
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


def test_parse_matrices_context_target_and_xai_extensions() -> None:
    """Test extraction of context_target, context_target_label, remediation_steps, coaching, and falsification."""
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

    res = MatrixDomainParser.parse_matrices(
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
    all_parsed = res.all_parsed_matrices
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
    profile = get_dummy_profile()
    pb = get_dummy_pb()

    step_rule = StepRule(
        id="sr_1234567890abcdef",
        task_blueprint="step_1234567890abcdef",
        input_mappings={"context": "financials_q3"},
    )

    payload = {
        "raw_score": 1.0,
        "normalized_score": 100.0,
        "evaluated_atoms": {},
    }
    dto = MockDTO(step_id="step1", block_id="blk_1234567890abcdef1234567890abcdef", payload=payload)

    res = MatrixDomainParser.parse_matrices(
        results=[dto],
        locale="en",
        blocks_by_id={"blk_1234567890abcdef1234567890abcdef": pb},
        workflow_steps={"step1": step_rule},
        profile=profile,
        row_explanations_cache={"blk_1234567890abcdef1234567890abcdef": "Valid explanation."},
        workflow_ext_values=[],
        row_curated_quotes_cache={},
    )
    all_parsed = res.all_parsed_matrices
    row = all_parsed["step1_blk_1234567890abcdef1234567890abcdef"]
    assert row.context_target == "financials_q3"
    assert row.context_target_label is not None
    assert row.context_target_label.resolve("en") == "financials_q3"
    assert row.context_target_label.resolve("fi") == "financials_q3"

    expected_map = {
        "financials_q3": ExpectedInput(
            input_key="financials_q3",
            input_modes=["file"],
            required=True,
            description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
            label=I18nText(translations={"en": "Q3 Financials", "fi": "Q3 Talous"}),
        )
    }
    res2 = MatrixDomainParser.parse_matrices(
        results=[dto],
        locale="en",
        blocks_by_id={"blk_1234567890abcdef1234567890abcdef": pb},
        workflow_steps={"step1": step_rule},
        profile=profile,
        row_explanations_cache={"blk_1234567890abcdef1234567890abcdef": "Valid explanation."},
        workflow_ext_values=[],
        row_curated_quotes_cache={},
        expected_inputs_map=expected_map,
    )
    all_parsed2 = res2.all_parsed_matrices
    row2 = all_parsed2["step1_blk_1234567890abcdef1234567890abcdef"]
    assert row2.context_target == "financials_q3"
    assert row2.context_target_label is not None
    assert row2.context_target_label.resolve("en") == "Q3 Financials"

    unmapped_rule = StepRule(
        id="sr_1234567890abcdef",
        task_blueprint="step_1234567890abcdef",
        input_mappings={"context": "unmapped_doc"},
    )
    res3 = MatrixDomainParser.parse_matrices(
        results=[dto],
        locale="en",
        blocks_by_id={"blk_1234567890abcdef1234567890abcdef": pb},
        workflow_steps={"step1": unmapped_rule},
        profile=profile,
        row_explanations_cache={"blk_1234567890abcdef1234567890abcdef": "Valid explanation."},
        workflow_ext_values=[],
        row_curated_quotes_cache={},
        expected_inputs_map=expected_map,
    )
    all_parsed3 = res3.all_parsed_matrices
    row3 = all_parsed3["step1_blk_1234567890abcdef1234567890abcdef"]
    assert row3.context_target is None


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
    all_parsed = res.all_parsed_matrices
    row = all_parsed["step1_blk_1234567890abcdef1234567890abcdef"]
    assert row.context_target is None
    assert row.context_target_label is None
    assert row.remediation_steps is None
    assert row.coaching is None
    assert row.falsification is None


def test_parse_matrices_axis_collision_coverage() -> None:
    """Test axis name collision resolution loop for coverage."""
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

    res = MatrixDomainParser.parse_matrices(
        results=[dto1, dto2],
        locale="en",
        blocks_by_id={"blk_1234567890abcdef1234567890abcdef": pb},
        workflow_steps={"step1": step_rule1, "step2": step_rule2},
        profile=profile,
        row_explanations_cache={"blk_1234567890abcdef1234567890abcdef": "Valid explanation."},
        workflow_ext_values=[],
        row_curated_quotes_cache={},
    )
    all_parsed = res.all_parsed_matrices
    assert len(all_parsed) == 2
    row2 = all_parsed["step2_blk_1234567890abcdef1234567890abcdef"]
    assert "sr_abcdef1234567890" in row2.name


def test_parse_matrices_prompt_block_explicit_target_input_key() -> None:
    """Verifies that MatrixPromptBlock.target_input_key resolves with SSOT precedence."""
    profile = get_dummy_profile()
    pb = get_dummy_pb()
    pb_with_target = pb.model_copy(update={"target_input_key": "product_text"})

    step_rule = StepRule(
        id="sr_1234567890abcdef",
        task_blueprint="step_1234567890abcdef",
        input_mappings={
            "context_a": "$inputs.product_text",
            "context_b": "$inputs.chat_log",
        },
    )

    payload = {
        "raw_score": 1.0,
        "normalized_score": 100.0,
        "evaluated_atoms": {},
    }
    dto = MockDTO(step_id="step1", block_id="blk_1234567890abcdef1234567890abcdef", payload=payload)

    res = MatrixDomainParser.parse_matrices(
        results=[dto],
        locale="en",
        blocks_by_id={"blk_1234567890abcdef1234567890abcdef": pb_with_target},
        workflow_steps={"step1": step_rule},
        profile=profile,
        row_explanations_cache={"blk_1234567890abcdef1234567890abcdef": "Valid explanation."},
        workflow_ext_values=[],
        row_curated_quotes_cache={},
    )
    all_parsed = res.all_parsed_matrices
    row = all_parsed["step1_blk_1234567890abcdef1234567890abcdef"]
    assert row.context_target == "product_text"
    assert row.context_target_label is not None
    assert row.context_target_label.resolve("en") == "Deliverable"
    assert row.context_target_label.resolve("fi") == "Lopputuote"


def test_parse_matrices_multi_input_step_fallback_to_all() -> None:
    """Verifies that a multi-input step without explicit target_input_key defaults to 'all'."""
    profile = get_dummy_profile()
    pb = get_dummy_pb()

    step_rule = StepRule(
        id="sr_1234567890abcdef",
        task_blueprint="step_1234567890abcdef",
        input_mappings={
            "context_a": "$inputs.product_text",
            "context_b": "$inputs.chat_log",
        },
    )

    payload = {
        "raw_score": 1.0,
        "normalized_score": 100.0,
        "evaluated_atoms": {},
    }
    dto = MockDTO(step_id="step1", block_id="blk_1234567890abcdef1234567890abcdef", payload=payload)

    res = MatrixDomainParser.parse_matrices(
        results=[dto],
        locale="en",
        blocks_by_id={"blk_1234567890abcdef1234567890abcdef": pb},
        workflow_steps={"step1": step_rule},
        profile=profile,
        row_explanations_cache={"blk_1234567890abcdef1234567890abcdef": "Valid explanation."},
        workflow_ext_values=[],
        row_curated_quotes_cache={},
    )
    all_parsed = res.all_parsed_matrices
    row = all_parsed["step1_blk_1234567890abcdef1234567890abcdef"]
    assert row.context_target == "all"
    assert row.context_target_label is not None
    assert row.context_target_label.resolve("en") == "All Inputs"
    assert row.context_target_label.resolve("fi") == "Kaikki syötteet"


def test_parse_matrices_theory_grounding_and_extensions() -> None:
    """Verifies that theory grounding citations and extension semantic reasoning are bound correctly."""
    profile = get_dummy_profile()
    tg = TheoryGrounding(
        citation_reference="Test Author 2026",
        source_url="https://example.com/source",
    )
    pb = get_dummy_pb().model_copy(update={"theory_grounding": tg})

    payload = {
        "raw_score": 1.0,
        "normalized_score": 100.0,
        "evaluated_atoms": {},
        "extensions": {
            "semantic_reasoning": "Extended reasoning text.",
            "google_citation": "https://google.com/citation",
        },
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
    assert row.cited_source_title == "Test Author 2026"
    assert row.cited_source_url == "https://example.com/source"
    assert row.semantic_reasoning == "Extended reasoning text."
