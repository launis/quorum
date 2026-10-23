"""Unit tests for matrix axis resolution, context target resolution, and scorecard row builder stage."""

from __future__ import annotations

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.matrix import TheoryGrounding
from backend_v2.models.domain.step import ExpectedInput, StepRule
from backend_v2.models.dtos.matrix_parser import (
    MatrixAtomHydrationResultDTO,
    MatrixContextTargetResultDTO,
    MatrixScaleProjectionDTO,
)
from backend_v2.models.dtos.trace import TraceMatrixExtensionsDTO, TraceMatrixPayloadDTO
from backend_v2.services.matrix_parser import MatrixDomainParser
from backend_v2.services.matrix_parser.row_builder_stage import (
    build_matrix_scorecard_row,
    resolve_axis_description,
    resolve_context_target,
    resolve_unique_axis_name,
)
from backend_v2.tests.unit.services.matrix_parser.test_matrix_parser_facade import (
    MockDTO,
    get_dummy_pb,
    get_dummy_profile,
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
    row = res.all_parsed_matrices["step1_blk_1234567890abcdef1234567890abcdef"]
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
    payload = {"raw_score": 1.0, "normalized_score": 100.0, "evaluated_atoms": {}}
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
    row = res.all_parsed_matrices["step1_blk_1234567890abcdef1234567890abcdef"]
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
    row2 = res2.all_parsed_matrices["step1_blk_1234567890abcdef1234567890abcdef"]
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
    row3 = res3.all_parsed_matrices["step1_blk_1234567890abcdef1234567890abcdef"]
    assert row3.context_target is None


def test_parse_matrices_negative_missing_input_mappings_and_extensions() -> None:
    """ISTQB Negative Partition: Test that missing input_mappings or extensions gracefully assign None."""
    profile = get_dummy_profile()
    pb = get_dummy_pb()
    payload = {"raw_score": 1.0, "normalized_score": 100.0, "evaluated_atoms": {}}
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
    row = res.all_parsed_matrices["step1_blk_1234567890abcdef1234567890abcdef"]
    assert row.context_target is None
    assert row.context_target_label is None
    assert row.remediation_steps is None
    assert row.coaching is None
    assert row.falsification is None


def test_parse_matrices_axis_collision_coverage() -> None:
    """Test axis name collision resolution loop for coverage."""
    profile = get_dummy_profile()
    pb = get_dummy_pb()
    step_rule1 = StepRule(id="sr_1234567890abcdef", task_blueprint="step_1234567890abcdef")
    step_rule2 = StepRule(id="sr_abcdef1234567890", task_blueprint="step_abcdef1234567890")
    payload = {"raw_score": 1.0, "normalized_score": 100.0, "evaluated_atoms": {}}
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
    assert len(res.all_parsed_matrices) == 2
    row2 = res.all_parsed_matrices["step2_blk_1234567890abcdef1234567890abcdef"]
    assert "sr_abcdef1234567890" in row2.name


def test_parse_matrices_prompt_block_explicit_target_input_key() -> None:
    """Verifies that MatrixPromptBlock.target_input_key resolves with SSOT precedence."""
    profile = get_dummy_profile()
    pb = get_dummy_pb()
    pb_with_target = pb.model_copy(update={"target_input_key": "product_text"})
    step_rule = StepRule(
        id="sr_1234567890abcdef",
        task_blueprint="step_1234567890abcdef",
        input_mappings={"context_a": "$inputs.product_text", "context_b": "$inputs.chat_log"},
    )
    payload = {"raw_score": 1.0, "normalized_score": 100.0, "evaluated_atoms": {}}
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
    row = res.all_parsed_matrices["step1_blk_1234567890abcdef1234567890abcdef"]
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
        input_mappings={"context_a": "$inputs.product_text", "context_b": "$inputs.chat_log"},
    )
    payload = {"raw_score": 1.0, "normalized_score": 100.0, "evaluated_atoms": {}}
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
    row = res.all_parsed_matrices["step1_blk_1234567890abcdef1234567890abcdef"]
    assert row.context_target == "all"
    assert row.context_target_label is not None
    assert row.context_target_label.resolve("en") == "All Inputs"
    assert row.context_target_label.resolve("fi") == "Kaikki syötteet"


def test_parse_matrices_theory_grounding_and_extensions() -> None:
    """Verifies that theory grounding citations and extension semantic reasoning are bound correctly."""
    profile = get_dummy_profile()
    tg = TheoryGrounding(citation_reference="Test Author 2026", source_url="https://example.com/source")
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


def test_resolve_unique_axis_name_missing_label_fail_fast() -> None:
    """ISTQB Negative: Verify resolve_unique_axis_name raises AppException when pb_meta.label is missing."""
    pb = get_dummy_pb().model_copy(update={"label": None})
    step_rule = StepRule(id="sr_1234567890abcdef", task_blueprint="bp_1")

    with pytest.raises(AppException) as exc_info:
        resolve_unique_axis_name(
            pb_meta=pb,
            block_id="blk_1234567890abcdef1234567890abcdef",
            locale="en",
            step_id="step1",
            workflow_steps={"step1": step_rule},
            all_parsed_matrices={},
        )
    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR.value


def test_resolve_unique_axis_name_empty_string_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify resolve_unique_axis_name falls back to block_id when label resolves to empty string."""
    pb = get_dummy_pb()
    monkeypatch.setattr(I18nText, "resolve", lambda self, target_locale=None, fallback_locale="en": "")
    step_rule = StepRule(id="sr_1234567890abcdef", task_blueprint="bp_1")

    res = resolve_unique_axis_name(
        pb_meta=pb,
        block_id="blk_fallback_id",
        locale="en",
        step_id="step1",
        workflow_steps={"step1": step_rule},
        all_parsed_matrices={},
    )
    assert res == "blk_fallback_id"


def test_resolve_unique_axis_name_secondary_collision() -> None:
    """Verify collision counter increments when both base and step_title names collide."""
    profile = get_dummy_profile()
    pb = get_dummy_pb()
    step_rule1 = StepRule(id="sr_1234567890abcdef", task_blueprint="step_1")
    step_rule2 = StepRule(id="sr_1234567890abcdef", task_blueprint="step_2")
    step_rule3 = StepRule(id="sr_1234567890abcdef", task_blueprint="step_3")
    payload = {"raw_score": 1.0, "normalized_score": 100.0, "evaluated_atoms": {}}
    dto1 = MockDTO(step_id="step1", block_id="blk_1234567890abcdef1234567890abcdef", payload=payload)
    dto2 = MockDTO(step_id="step2", block_id="blk_1234567890abcdef1234567890abcdef", payload=payload)
    dto3 = MockDTO(step_id="step3", block_id="blk_1234567890abcdef1234567890abcdef", payload=payload)

    res = MatrixDomainParser.parse_matrices(
        results=[dto1, dto2, dto3],
        locale="en",
        blocks_by_id={"blk_1234567890abcdef1234567890abcdef": pb},
        workflow_steps={"step1": step_rule1, "step2": step_rule2, "step3": step_rule3},
        profile=profile,
        row_explanations_cache={"blk_1234567890abcdef1234567890abcdef": "Valid explanation."},
        workflow_ext_values=[],
        row_curated_quotes_cache={},
    )
    assert len(res.all_parsed_matrices) == 3
    row3 = res.all_parsed_matrices["step3_blk_1234567890abcdef1234567890abcdef"]
    assert "sr_1234567890abcdef 1" in row3.name


def test_resolve_axis_description_unset() -> None:
    """Verify resolve_axis_description returns empty string when description is None."""
    pb = get_dummy_pb().model_copy(update={"description": None})
    assert resolve_axis_description(pb, "en") == ""


def test_resolve_context_target_target_input_key_without_step_mappings() -> None:
    """Verify resolve_context_target resolves target_input_key when step input mappings are empty."""
    pb = get_dummy_pb().model_copy(update={"target_input_key": "custom_doc_key"})
    step_rule = StepRule(id="sr_1234567890abcdef", task_blueprint="bp_1", input_mappings={})

    res = resolve_context_target(
        step_id="step1",
        pb_meta=pb,
        workflow_steps={"step1": step_rule},
        expected_inputs_map=None,
    )
    assert res.context_target == "custom_doc_key"
    assert res.context_target_label is not None
    assert res.context_target_label.resolve("en") == "custom_doc_key"


def test_build_matrix_scorecard_row_google_citation_and_evidence_types() -> None:
    """Verify Google citation fallback and validated_evidence_type branches."""
    pb = get_dummy_pb().model_copy(update={"theory_grounding": None})
    scale_proj = MatrixScaleProjectionDTO(
        score_float=4.5,
        raw_score=4.5,
        math_min=1.0,
        math_max=5.0,
        display_scale_min=1.0,
        display_scale_max=5.0,
        norm_score=90.0,
        score_display_label="4.5 / 5.0",
        true_atoms=9,
        total_atoms=10,
    )
    atom_hydration = MatrixAtomHydrationResultDTO()
    ctx_res = MatrixContextTargetResultDTO(context_target="doc1", context_target_label=None)

    for ev_type in ("EXPLICIT_QUOTE", "IMPLIED_INTENT", "NO_EVIDENCE"):
        payload = TraceMatrixPayloadDTO(
            raw_score=4.5,
            normalized_score=90.0,
            extensions=TraceMatrixExtensionsDTO(
                google_citation="https://scholar.google.com/test",
                evidence_type=ev_type,
            ),
        )
        row = build_matrix_scorecard_row(
            block_id="blk_1",
            axis_name="Axis 1",
            axis_description="Desc 1",
            pb_meta=pb,
            matrix_payload=payload,
            scale_proj=scale_proj,
            axis_level_breakdown=None,
            cleaned_explanation="Explanation.",
            atom_hydration=atom_hydration,
            context_target_res=ctx_res,
        )
        assert row.cited_source_url == "https://scholar.google.com/test"
        assert row.evidence_type == ev_type

