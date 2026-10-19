from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from backend_v2.models.core_base import I18nText
from backend_v2.models.dtos.atom_evaluation import ReasoningStepDTO
from backend_v2.models.dtos.matrix_scorecard import (
    HumanOverrideDTO,
    HumanOverrideRequest,
    MatrixScorecardRowDTO,
    ScorecardAtomDTO,
    TDADlq,
    TDAEvaluated,
    TDAPending,
)
from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO
from backend_v2.models.enums import ExecutionStatus, LaxExecutionStatus, VisualIntent


def test_human_override_request_and_dto() -> None:
    req = HumanOverrideRequest(
        new_status=LaxExecutionStatus.PASSED,
        reason="Manual override by reviewer",
        evidence_quotes=[
            QuoteEvidenceDTO.model_validate(
                {"source_quotes": ["verbatim evidence"], "source_alias": "DOC-1"},
                context={"alias_registry": {"DOC-1": "src_1"}},
            )
        ],
    )
    assert req.new_status == LaxExecutionStatus.PASSED
    assert len(req.evidence_quotes) == 1

    dto = HumanOverrideDTO(
        new_status=ExecutionStatus.PASSED,
        reason="Override verified",
        evidence_quotes=[],
        overridden_by="usr_admin",
        overridden_at=datetime.now(timezone.utc),
    )
    assert dto.overridden_by == "usr_admin"


def test_tda_unions() -> None:
    pending = TDAPending()
    assert pending.runtimeType == "pending"

    evaluated = TDAEvaluated(
        passed=True,
        display_quote="quoted",
        raw_anchor="anchor",
    )
    assert evaluated.runtimeType == "evaluated"

    dlq = TDADlq(
        user_reason="reason",
        backend_trace="trace",
    )
    assert dlq.runtimeType == "dlq"


def test_scorecard_atom_dto() -> None:
    atom = ScorecardAtomDTO(
        atom_id="atm_1",
        level=1,
        level_name="Taso 1",
        claim_label="Label",
        extracted_facts={"fact": "val"},
        exact_quotes=[],
        internal_logic_en=ReasoningStepDTO(
            step_1_identify_premise="1",
            step_2_scan_source="2",
            step_3_evaluate_anti_patterns="3",
            step_4_final_conclusion="4",
        ),
        status=LaxExecutionStatus.PASSED,
        semantic_reasoning="Reasoning",
        contextual_override=True,
        structural_location="L1",
        chart_display_label="Chart",
        visual_intent=VisualIntent.NEUTRAL,
    )
    assert atom.visual_intent == VisualIntent.WARNING


def test_tda_scorecard_atom_warning_intent_on_override() -> None:
    """Contract: TDAScorecardAtom with status=PASSED and contextual_override=True sets visual_intent=WARNING."""
    atom = ScorecardAtomDTO(
        atom_id="atm_override_1",
        level=2,
        level_name="Taso 2",
        claim_label="Override Claim",
        extracted_facts={"fact": "verified"},
        exact_quotes=[],
        internal_logic_en=ReasoningStepDTO(
            step_1_identify_premise="1",
            step_2_scan_source="2",
            step_3_evaluate_anti_patterns="3",
            step_4_final_conclusion="4",
        ),
        status=ExecutionStatus.PASSED,
        semantic_reasoning="Reasoning with override",
        contextual_override=True,
        structural_location="L2",
        chart_display_label="Chart Override",
        visual_intent=VisualIntent.NEUTRAL,
    )
    assert atom.visual_intent == VisualIntent.WARNING


def test_matrix_scorecard_row_dto() -> None:
    row = MatrixScorecardRowDTO(
        block_id="blk_1234567890123456",
        name="Row Name",
        label_i18n=I18nText(translations={"en": "English", "fi": "Suomi"}),
        row_explanation="Explanation of the row",
        is_evaluative=True,
    )
    assert row.block_id == "blk_1234567890123456"
    assert row.name == "Row Name"
    assert row.label_i18n.resolve("fi") == "Suomi"
    assert row.is_evaluative is True


def test_scorecard_atom_validate_from_instance() -> None:
    """Test map_contested_to_warning with an already instantiated ScorecardAtomDTO."""
    atom = ScorecardAtomDTO(
        atom_id="atm_2",
        level=1,
        level_name="Taso 1",
        claim_label="Label",
        extracted_facts={},
        exact_quotes=[],
        internal_logic_en=ReasoningStepDTO(
            step_1_identify_premise="1",
            step_2_scan_source="2",
            step_3_evaluate_anti_patterns="3",
            step_4_final_conclusion="4",
        ),
        status=LaxExecutionStatus.FAILED,
        semantic_reasoning="Reasoning",
        contextual_override=False,
        chart_display_label="Chart",
        visual_intent=VisualIntent.NEUTRAL,
    )
    validated = ScorecardAtomDTO.model_validate(atom)
    assert validated.atom_id == "atm_2"


def test_matrix_scorecard_models_forbid_extra() -> None:
    """Test that all models in matrix_scorecard forbid extra fields."""
    with pytest.raises(ValidationError):
        HumanOverrideRequest.model_validate({"new_status": "PASSED", "reason": "test", "extra_field": "forbidden"})

    with pytest.raises(ValidationError):
        HumanOverrideDTO.model_validate(
            {
                "new_status": "PASSED",
                "reason": "test",
                "evidence_quotes": [],
                "overridden_by": "usr_1",
                "overridden_at": datetime.now(timezone.utc),
                "extra": "bad",
            }
        )

    with pytest.raises(ValidationError):
        TDAPending.model_validate({"runtimeType": "pending", "extra": 123})

    with pytest.raises(ValidationError):
        TDAEvaluated.model_validate(
            {
                "runtimeType": "evaluated",
                "passed": True,
                "display_quote": "q",
                "raw_anchor": "a",
                "extra_prop": "bad",
            }
        )

    with pytest.raises(ValidationError):
        TDADlq.model_validate(
            {
                "runtimeType": "dlq",
                "user_reason": "r",
                "backend_trace": "t",
                "extra_prop": "bad",
            }
        )

    with pytest.raises(ValidationError):
        ScorecardAtomDTO.model_validate(
            {
                "atom_id": "atm_1",
                "level": 1,
                "level_name": "T1",
                "claim_label": "C",
                "extracted_facts": {},
                "exact_quotes": [],
                "internal_logic_en": {
                    "step_1_identify_premise": "1",
                    "step_2_scan_source": "2",
                    "step_3_evaluate_anti_patterns": "3",
                    "step_4_final_conclusion": "4",
                },
                "status": "PASSED",
                "semantic_reasoning": "R",
                "contextual_override": False,
                "chart_display_label": "CD",
                "visual_intent": "NEUTRAL",
                "unauthorized_prop": "error",
            }
        )

    with pytest.raises(ValidationError):
        MatrixScorecardRowDTO.model_validate(
            {
                "block_id": "blk_1",
                "name": "N",
                "label_i18n": {"translations": {"en": "E"}},
                "row_explanation": "X",
                "is_evaluative": True,
                "unexpected_field": "error",
            }
        )


def test_matrix_scorecard_models_require_mandatory_fields() -> None:
    """Test that missing mandatory fields trigger ValidationError fail-fast."""
    with pytest.raises(ValidationError):
        HumanOverrideRequest.model_validate({"reason": "missing status"})

    with pytest.raises(ValidationError):
        MatrixScorecardRowDTO.model_validate(
            {
                "name": "Missing block_id",
                "label_i18n": {"translations": {"en": "E"}},
                "row_explanation": "X",
                "is_evaluative": True,
            }
        )


def test_scorecard_atom_map_contested_non_dict_passthrough() -> None:
    """Test map_contested_to_warning passes through non-dict data untouched."""
    non_dict_obj = "raw_string_data"
    result = ScorecardAtomDTO.map_contested_to_warning(non_dict_obj)
    assert result == "raw_string_data"

