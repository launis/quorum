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
                {"quote": "verbatim evidence", "source_alias": "DOC-1"},
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
