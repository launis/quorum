"""Unit tests for synthesis DTO models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.models.core_base import generate_opaque_id
from backend_v2.models.domain.proposition_graph import FalsifiedClaimMatch
from backend_v2.models.dtos.causal_discovery import (
    AntiFluffAuditDTO,
    CausalGraphPayloadDTO,
    CausalNodeDTO,
    CausalRootCauseDiagnosisDTO,
    CausalTdaFusionResultDTO,
    FairScoringBreakdownDTO,
    PrescriptiveRemediationDTO,
)
from backend_v2.models.dtos.synthesis import (
    CausalSynthesisBriefDTO,
    ExecutiveSummarySectionResult,
    MatrixExplanationContextDTO,
    MatrixExplanationContextList,
    MatrixExplanationsResult,
    MatrixFailureDeficitDTO,
    MatrixSectionSynthesesResult,
    SynthesisDistillationDTO,
    SynthesisOutputDTO,
    SynthesisRowExplanationDTO,
    SynthesisSectionDTO,
    XaiHighlightItem,
    XaiHighlightsResult,
)
from backend_v2.models.enums import DependencyRelationType, EntityPrefix, ExecutionStatus, RoleClassification
from backend_v2.models.view.sdui import ParagraphBlock


def test_synthesis_section_strictness() -> None:
    """Test SynthesisSectionDTO positive instantiation, min_length boundary, extra forbid, and frozen immutability."""
    dto = SynthesisSectionDTO(
        layout_id="lay_1",
        content_blocks=[ParagraphBlock(block_type="paragraph", text="content", exact_quotes=[], citations=[])],
    )
    assert dto.layout_id == "lay_1"

    with pytest.raises(ValidationError):
        SynthesisSectionDTO.model_validate(
            {
                "layout_id": "lay_1",
                "content_blocks": [
                    ParagraphBlock(block_type="paragraph", text="content", exact_quotes=[], citations=[])
                ],
                "extra": "fail",
            }
        )

    with pytest.raises(ValidationError):
        SynthesisSectionDTO(layout_id="lay_1", content_blocks=[])


def test_xai_highlight_strictness() -> None:
    """Test XaiHighlightItem positive instantiation, extra forbid, and type violation."""
    dto = XaiHighlightItem(extension_type="risk_flag", content="High risk detected.")
    assert dto.extension_type == "risk_flag"

    with pytest.raises(ValidationError):
        XaiHighlightItem.model_validate({"extension_type": "risk", "content": "text", "extra": "fail"})

    with pytest.raises(ValidationError):
        XaiHighlightItem.model_validate({"extension_type": 123, "content": "text"})


def test_executive_summary_section_result_strictness() -> None:
    """Test ExecutiveSummarySectionResult positive instantiation and negative validation cases."""
    dto = ExecutiveSummarySectionResult(
        user_role=RoleClassification.ARCHITECT,
        user_role_justification="High maturity",
        cited_sources=["src_1"],
        executive_summary=[
            ParagraphBlock(block_type="paragraph", text="Summary paragraph", exact_quotes=[], citations=[])
        ],
    )
    assert dto.user_role == RoleClassification.ARCHITECT
    assert len(dto.executive_summary) == 1

    with pytest.raises(ValidationError):
        ExecutiveSummarySectionResult.model_validate(
            {
                "user_role": RoleClassification.ARCHITECT,
                "user_role_justification": "High maturity",
                "executive_summary": [
                    ParagraphBlock(block_type="paragraph", text="Valid", exact_quotes=[], citations=[])
                ],
                "extra_field": "fail",
            }
        )

    with pytest.raises(ValidationError):
        ExecutiveSummarySectionResult.model_validate(
            {
                "user_role": "ROLE_EXECUTIVE_STRATEGIST",
                "user_role_justification": "Invalid role hallucination",
                "executive_summary": [
                    ParagraphBlock(block_type="paragraph", text="Valid", exact_quotes=[], citations=[])
                ],
            }
        )


def test_matrix_section_syntheses_result_strictness() -> None:
    """Test MatrixSectionSynthesesResult positive instantiation, extra forbid, and type violation."""
    dto = MatrixSectionSynthesesResult(
        sections=[
            SynthesisSectionDTO(
                layout_id="layout_0_1d_metrics",
                content_blocks=[
                    ParagraphBlock(block_type="paragraph", text="1D metrics", exact_quotes=[], citations=[])
                ],
            )
        ]
    )
    assert len(dto.sections) == 1

    with pytest.raises(ValidationError):
        MatrixSectionSynthesesResult.model_validate(
            {
                "sections": [],
                "extra_forbidden": "fail",
            }
        )

    with pytest.raises(ValidationError):
        MatrixSectionSynthesesResult.model_validate({"sections": "invalid_not_a_list"})


def test_xai_highlights_result_strictness() -> None:
    """Test XaiHighlightsResult positive instantiation, extra forbid, and type violation."""
    dto = XaiHighlightsResult(
        xai_highlights=[
            XaiHighlightItem(extension_type="authenticity_evaluation", content="Authentic communication verified.")
        ]
    )
    assert len(dto.xai_highlights) == 1

    with pytest.raises(ValidationError):
        XaiHighlightsResult.model_validate(
            {
                "xai_highlights": [],
                "extra_forbidden": "fail",
            }
        )

    with pytest.raises(ValidationError):
        XaiHighlightsResult.model_validate({"xai_highlights": "not_a_list"})


def test_synthesis_output_strictness() -> None:
    """Test SynthesisOutputDTO positive instantiation, extra forbid, and frozen immutability."""
    dto = SynthesisOutputDTO(
        user_role="ROLE_ARCHITECT",
        user_role_justification="Test",
        cited_sources=["source1"],
        section_syntheses=[
            SynthesisSectionDTO(
                layout_id="l1",
                content_blocks=[ParagraphBlock(block_type="paragraph", text="test", exact_quotes=[], citations=[])],
            )
        ],
        xai_highlights=[],
    )
    assert len(dto.section_syntheses) == 1

    with pytest.raises(ValidationError):
        SynthesisOutputDTO.model_validate(
            {
                "user_role": "ROLE_ARCHITECT",
                "user_role_justification": "Test",
                "extra": "fail",
            }
        )

    with pytest.raises(ValidationError):
        SynthesisOutputDTO.model_validate({"user_role": 999})


def test_executive_summary_section_result_role_optional() -> None:
    """Verify that user_role and user_role_justification default to None and are optional."""
    dto = ExecutiveSummarySectionResult(
        cited_sources=[],
        executive_summary=[
            ParagraphBlock(block_type="paragraph", text="Summary narrative", exact_quotes=[], citations=[])
        ],
    )
    assert dto.user_role is None
    assert dto.user_role_justification is None
    assert len(dto.executive_summary) == 1


def test_synthesis_output_role_optional() -> None:
    """Verify that SynthesisOutputDTO validates successfully when user_role is omitted."""
    dto = SynthesisOutputDTO(
        cited_sources=[],
        section_syntheses=[],
        xai_highlights=[],
    )
    assert dto.user_role is None
    assert dto.user_role_justification is None


def test_executive_summary_section_result_requires_executive_summary() -> None:
    """Regression test: ExecutiveSummarySectionResult must strictly require non-empty executive_summary."""
    with pytest.raises(ValidationError):
        ExecutiveSummarySectionResult(
            cited_sources=[],
            executive_summary=[],
        )


def test_matrix_explanation_context_strictness() -> None:
    """Test MatrixExplanationContextDTO and TypeAdapter list validation."""
    dto = MatrixExplanationContextDTO(
        real_matrix_id="blk_0195f3a00000700283456789abcdef01",
        matrix_id="m0",
        matrix_label="Strategic Alignment",
        score=4.5,
        justification="Strong alignment observed.",
    )
    assert dto.real_matrix_id == "blk_0195f3a00000700283456789abcdef01"
    assert dto.score == 4.5

    validated_list = MatrixExplanationContextList.validate_python([dto])
    assert len(validated_list) == 1
    assert validated_list[0].matrix_id == "m0"

    with pytest.raises(ValidationError):
        MatrixExplanationContextDTO.model_validate(
            {
                "real_matrix_id": "blk_0195f3a00000700283456789abcdef01",
                "matrix_id": "m0",
                "matrix_label": "Strategic Alignment",
                "justification": "Justification",
                "extra": "forbidden",
            }
        )

    with pytest.raises(ValidationError):
        MatrixExplanationContextDTO.model_validate(
            {
                "real_matrix_id": "blk_0195f3a00000700283456789abcdef01",
                "matrix_id": "m0",
                "matrix_label": "Strategic Alignment",
                "score": "not_a_float",
                "justification": "Justification",
            }
        )


def test_synthesis_distillation_strictness() -> None:
    """Test SynthesisDistillationDTO defaults, strict validation, and extra forbid."""
    dto = SynthesisDistillationDTO(distilled_inputs="Concatenated input text.")
    assert dto.distilled_inputs == "Concatenated input text."
    assert dto.max_extensions == 5
    assert dto.target_locale == "en"

    with pytest.raises(ValidationError):
        SynthesisDistillationDTO.model_validate({"distilled_inputs": 123})

    with pytest.raises(ValidationError):
        SynthesisDistillationDTO.model_validate({"distilled_inputs": "test", "unknown_field": "fail"})


def test_row_explanation_and_matrix_explanations_result_strictness() -> None:
    """Test SynthesisRowExplanationDTO and MatrixExplanationsResult strict validation."""
    row = SynthesisRowExplanationDTO(
        matrix_id="m0",
        row_explanation="High focus on strategic clarity.",
        curated_quotes=["clarity quote"],
    )
    assert row.matrix_id == "m0"
    assert len(row.curated_quotes) == 1

    res = MatrixExplanationsResult(explanations=[row])
    assert len(res.explanations) == 1

    with pytest.raises(ValidationError):
        SynthesisRowExplanationDTO.model_validate(
            {
                "matrix_id": "m0",
                "row_explanation": "Explanation",
                "extra": "forbidden",
            }
        )

    with pytest.raises(ValidationError):
        SynthesisRowExplanationDTO.model_validate(
            {
                "matrix_id": 123,
                "row_explanation": "Explanation",
            }
        )

    with pytest.raises(ValidationError):
        MatrixExplanationsResult.model_validate(
            {
                "explanations": [row],
                "extra": "forbidden",
            }
        )

    with pytest.raises(ValidationError):
        MatrixExplanationsResult.model_validate({"explanations": "not_a_list"})


def test_matrix_failure_deficit_dto_and_causal_synthesis_brief_dto() -> None:
    """Test MatrixFailureDeficitDTO and CausalSynthesisBriefDTO positive, boundary, and negative cases."""
    deficit = MatrixFailureDeficitDTO(
        claim="Quantified ROI Metric",
        status="FAILED",
        scale_score=3,
        evaluation_reasoning="Step 4: Missing ROI calculation.",
        is_inverse_evidence=True,
        short_circuited_by_claims=[],
        anti_patterns=["Vague benefit statements"],
        contrastive_rejected="ROI will be good.",
        contrastive_acceptable="NPV is 1.2M EUR over 36 months.",
    )
    assert deficit.status == "FAILED"
    assert deficit.scale_score == 3

    with pytest.raises(ValidationError):
        MatrixFailureDeficitDTO.model_validate(
            {
                "claim": "Valid claim",
                "status": "PASSED",
                "scale_score": 2,
            }
        )

    with pytest.raises(ValidationError):
        MatrixFailureDeficitDTO.model_validate(
            {
                "claim": "Valid claim",
                "status": "FAILED",
                "scale_score": 2,
                "extra_field": "forbidden",
            }
        )

    claim_id = generate_opaque_id(EntityPrefix.NODE)
    warrant_id = generate_opaque_id(EntityPrefix.NODE)
    rebuttal_id = generate_opaque_id(EntityPrefix.NODE)

    fusion_payload = CausalTdaFusionResultDTO(
        graph=CausalGraphPayloadDTO(
            nodes=[
                CausalNodeDTO(
                    node_id=warrant_id,
                    claim="Warrant Claim",
                    status=ExecutionStatus.FAILED,
                ),
                CausalNodeDTO(
                    node_id=claim_id,
                    claim="Target Claim",
                    status=ExecutionStatus.FAILED,
                ),
                CausalNodeDTO(
                    node_id=rebuttal_id,
                    claim="Rebuttal Claim",
                    status=ExecutionStatus.PASSED,
                ),
            ],
            edges=[],
            root_cause_node_ids=[warrant_id],
            cycle_detected=False,
        ),
        root_cause_diagnoses=[
            CausalRootCauseDiagnosisDTO(
                root_cause_parent_id=warrant_id,
                root_cause_claim="",
                failing_node_id=claim_id,
                failing_node_claim="",
                warrant_relation=DependencyRelationType.WARRANTS,
                paragraph_ref="p1",
                explanation="Warrant missing.",
                penalty_points=1.25,
            )
        ],
        falsified_claims=[
            FalsifiedClaimMatch(
                falsified_claim_id=claim_id,
                claim_statement="Target Claim",
                invalidated_warrant_id=warrant_id,
                rebuttal_id=rebuttal_id,
                rebuttal_confidence=0.95,
            )
        ],
        prescriptive_remediations=[
            PrescriptiveRemediationDTO(
                target_node_id=claim_id,
                required_action="Fix warrant.",
                unlocks_node_ids=[],
                potential_score_impact=1.25,
            )
        ],
        anti_fluff_audit=AntiFluffAuditDTO(
            isolated_concept_count=0,
            cycle_detected=False,
            unsupported_claims_count=0,
            logical_cohesion_score=0.75,
        ),
        fair_scoring=FairScoringBreakdownDTO(
            independent_error_count=1,
            cascading_fault_count=1,
            raw_penalty_points=2.0,
            deduplicated_penalty_points=1.25,
            dampened_savings_points=0.75,
        ),
    )

    brief = CausalSynthesisBriefDTO.from_causal_payload(fusion_payload)
    formatted = brief.format_for_prompt()
    assert "Intact Propositions: 1/3" in formatted
    assert "Logical Cohesion: 0.75" in formatted
    assert "Warrant Claim -> Target Claim (warrants): Warrant missing." in formatted
    assert "Rebuttal Claim -> Warrant Claim -> Target Claim (confidence: 0.95)" in formatted
    assert "Target Claim: Fix warrant. (impact: +1.25)" in formatted
    assert "Fair Scoring Summary:" in formatted

    graph_only = CausalGraphPayloadDTO(
        nodes=[
            CausalNodeDTO(
                node_id="node_a",
                claim="Standalone Premise",
                status=ExecutionStatus.PASSED,
            ),
            CausalNodeDTO(
                node_id="node_b",
                claim="   ",
                status=ExecutionStatus.FAILED,
            ),
        ],
        edges=[],
        root_cause_node_ids=["node_a", "node_b"],
        cycle_detected=True,
    )
    brief_graph = CausalSynthesisBriefDTO.from_causal_payload(graph_only)
    formatted_graph = brief_graph.format_for_prompt()
    assert "Total Propositions: 2" in formatted_graph
    assert "Cycle Detected: True" in formatted_graph
    assert "Root Cause Proposition: Standalone Premise" in formatted_graph
    assert "Root Cause Proposition: node_b" in formatted_graph

    with pytest.raises(ValidationError):
        CausalSynthesisBriefDTO(intact_propositions=-1, total_propositions=1)

    with pytest.raises(ValidationError):
        CausalSynthesisBriefDTO.model_validate({"intact_propositions": 1, "extra_unknown": "forbidden"})
