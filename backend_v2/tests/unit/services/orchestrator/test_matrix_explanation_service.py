"""Unit tests for the Matrix Explanation Service.

Tests for matrix explanation context generation, Status-Aware Dual Reporting,
and Ranked Round-Robin quote and unmet criteria curation.
"""

from types import SimpleNamespace
from typing import Any

import pytest
from pydantic import JsonValue, ValidationError

from backend_v2.exceptions import AppException
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.matrix import AntiPattern, ContrastivePairDTO, MatrixClaim, MatrixScale, TDAAssertion
from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock, PromptBlock
from backend_v2.models.dtos.atom_evaluation import ReducedAtomDTO
from backend_v2.models.dtos.atom_result import AtomResultDTO
from backend_v2.models.dtos.dag_models import CausalEdge
from backend_v2.models.dtos.lightweight_matrix import LevelStatsDTO, LightweightMatrixOutput
from backend_v2.models.dtos.synthesis import MatrixFailureDeficitDTO
from backend_v2.models.dtos.trace import TraceMatrixPayloadDTO
from backend_v2.models.enums import BlockDataType, ExecutionStatus, PromptBlockCategory
from backend_v2.models.state import StepOutputDTO
from backend_v2.services.orchestrator.matrix_explanation_service import (
    MatrixExplanationService,
    QuoteCandidateDTO,
)


def _create_matrix_block(
    block_id: str = "blk_0195f3a00000700980abcdef12345678",
    scales: list[MatrixScale] | None = None,
    tda_ids: list[str] | None = None,
) -> PromptBlock:
    """Helper to create a concrete, valid PromptBlock fixture without mocks."""
    if scales is None:
        ids = tda_ids or ["tda_00000000000000000000000000000001", "tda_00000000000000000000000000000002"]
        assertions = [
            TDAAssertion(
                tda_id=tid,
                inverse_evidence=False,
                aggregation_mode="ALL_MUST_COMPLY",
                concept_description=f"Concept Description Valid for {tid}",
            )
            for tid in ids
        ]
        scales = [
            MatrixScale(
                score=1,
                ai_label="INITIAL",
                claims=[
                    MatrixClaim(
                        label=I18nText(translations={"en": "Claim Label", "fi": "Väite"}),
                        tda_assertions=assertions,
                    )
                ],
            )
        ]

    return MatrixPromptBlock(
        id=block_id,
        slug=f"slug_{block_id}",
        label=I18nText(translations={"en": "Matrix Label", "fi": "Matriisin Otsikko"}),
        description=I18nText(translations={"en": "Description", "fi": "Kuvaus"}),
        ai_description="Cognitive instructions for matrix",
        category_id=PromptBlockCategory.MATRIX,
        type=BlockDataType.FLOAT,
        scales=scales,
    )


def _to_status(val: Any) -> ExecutionStatus:
    """Helper to safely convert raw string or enum to ExecutionStatus."""
    if isinstance(val, ExecutionStatus):
        return val
    return ExecutionStatus(str(val))


def _make_step_dtos(
    block_id: str,
    normalized_score: float,
    evaluated_atoms: dict[str, JsonValue],
    results: list[dict[str, JsonValue]] | None = None,
    level_breakdown: dict[str, LevelStatsDTO] | None = None,
    step_id: str = "step1",
    raw_score: float = 0.0,
) -> list[StepOutputDTO]:
    """Helper to construct strictly typed StepOutputDTO collections for atom and matrix steps."""
    dtos: list[StepOutputDTO] = []
    if results:
        atom_dtos: list[AtomResultDTO] = []
        for r in results:
            if r is not None and type(r) is dict and "tda_id" in r:
                atom_data: dict[str, JsonValue] = {
                    "tda_id": r["tda_id"],
                    "status": _to_status(r["status"]),
                }
                if "evaluation_reasoning" in r:
                    atom_data["evaluation_reasoning"] = r["evaluation_reasoning"]
                if "source_quotes" in r:
                    atom_data["source_quotes"] = r["source_quotes"]
                elif "source_quote" in r:
                    atom_data["source_quotes"] = r["source_quote"]
                if "contextual_override" in r:
                    atom_data["contextual_override"] = r["contextual_override"]
                if "is_inverse_evidence" in r:
                    atom_data["is_inverse_evidence"] = r["is_inverse_evidence"]
                if "depends_on_tda_ids" in r:
                    atom_data["depends_on_tda_ids"] = r["depends_on_tda_ids"]
                if "short_circuit_reason_tda_ids" in r:
                    atom_data["short_circuit_reason_tda_ids"] = r["short_circuit_reason_tda_ids"]
                atom_dtos.append(AtomResultDTO.model_validate(atom_data))
        if atom_dtos:
            dtos.append(
                StepOutputDTO(
                    step_id="step_atoms",
                    block_id="blk_atom_eval",
                    data_type="unknown",
                    payload=atom_dtos,
                )
            )
    dtos.append(
        StepOutputDTO(
            step_id=step_id,
            block_id=block_id,
            data_type="matrix",
            payload=LightweightMatrixOutput(
                raw_score=raw_score,
                normalized_score=normalized_score,
                evaluated_atoms={k: _to_status(v) for k, v in evaluated_atoms.items()},
                level_breakdown=level_breakdown,
            ),
        )
    )
    return dtos


def test_assemble_matrices_to_explain_basic() -> None:
    """Test basic assembly of matrices_to_explain from scored payloads with evaluated_atoms."""
    block_id = "blk_0195f3a0000070018111111111111111"
    results = [
        {
            "tda_id": "tda_00000000000000000000000000000001",
            "status": "PASSED",
            "evaluation_reasoning": "Reason",
            "source_quotes": "Quote A from source verbatim statement.",
            "depends_on_tda_ids": [],
            "short_circuit_reason_tda_ids": [],
        },
        {
            "tda_id": "tda_00000000000000000000000000000002",
            "status": "PASSED",
            "evaluation_reasoning": "Reason",
            "source_quotes": "Quote B from source verbatim statement.",
            "depends_on_tda_ids": [],
            "short_circuit_reason_tda_ids": [],
        },
    ]
    dtos = _make_step_dtos(
        block_id=block_id,
        normalized_score=78.5,
        evaluated_atoms={
            "tda_00000000000000000000000000000001": ExecutionStatus.PASSED,
            "tda_00000000000000000000000000000002": ExecutionStatus.PASSED,
        },
        results=results,
    )

    blocks_by_id = {block_id: _create_matrix_block(block_id=block_id)}

    result = MatrixExplanationService.assemble_matrices_to_explain(
        dtos, title_map={}, blocks_by_id=blocks_by_id, target_locale="en"
    )

    assert len(result) == 1
    assert result[0].matrix_id == "MX-0"
    assert result[0].real_matrix_id == block_id
    assert result[0].score == 78.5
    assert "SUPPORTING EVIDENCE:" in result[0].justification
    assert "Quote A from source verbatim statement." in result[0].justification
    assert "Quote B from source verbatim statement." in result[0].justification


def test_assemble_matrices_to_explain_no_matching_quotes() -> None:
    """Test that matrices without evaluated_atoms are INCLUDED to prevent Fail-Fast crash in blueprint.py."""
    block_id = "blk_0195f3a0000070028222222222222222"
    dtos = [
        StepOutputDTO(
            step_id="step1",
            block_id=block_id,
            data_type="matrix",
            payload=LightweightMatrixOutput(normalized_score=78.5),
        ),
    ]

    blocks_by_id = {block_id: _create_matrix_block(block_id=block_id)}

    result = MatrixExplanationService.assemble_matrices_to_explain(
        dtos, title_map={}, blocks_by_id=blocks_by_id, target_locale="en"
    )
    assert len(result) == 1
    assert result[0].justification == "No direct evidence quotes or specific deficits recorded for this matrix."


def test_assemble_matrices_to_explain_empty_quotes_list() -> None:
    """Test that matrices with empty quote lists are INCLUDED with a fallback justification.

    Prevents Fail-Fast crash in blueprint.py.
    """
    block_id = "blk_0195f3a0000070038333333333333333"
    results = [
        {
            "tda_id": "tda_00000000000000000000000000000001",
            "status": "PASSED",
            "evaluation_reasoning": "Reason",
            "source_quotes": None,
            "contextual_override": True,
            "depends_on_tda_ids": [],
            "short_circuit_reason_tda_ids": [],
        }
    ]
    dtos = _make_step_dtos(
        block_id=block_id,
        normalized_score=78.5,
        evaluated_atoms={"tda_00000000000000000000000000000001": ExecutionStatus.PASSED},
        results=results,
    )

    blocks_by_id = {block_id: _create_matrix_block(block_id=block_id)}

    result = MatrixExplanationService.assemble_matrices_to_explain(
        dtos, title_map={}, blocks_by_id=blocks_by_id, target_locale="en"
    )
    assert len(result) == 1
    assert result[0].real_matrix_id == block_id
    assert result[0].justification == "No direct evidence quotes or specific deficits recorded for this matrix."


def test_assemble_matrices_to_explain_deduplicates_by_block_id() -> None:
    """Test that duplicate block_id entries are deduplicated (first wins)."""
    block_id = "blk_0195f3a0000070048444444444444444"
    dtos = _make_step_dtos(
        block_id=block_id,
        normalized_score=50.0,
        evaluated_atoms={"tda_00000000000000000000000000000001": ExecutionStatus.PASSED},
        results=[
            {
                "tda_id": "tda_00000000000000000000000000000001",
                "status": "PASSED",
                "evaluation_reasoning": "Reason",
                "source_quotes": "Quote 1 from the first step output.",
                "depends_on_tda_ids": [],
                "short_circuit_reason_tda_ids": [],
            }
        ],
        step_id="step1",
    ) + _make_step_dtos(
        block_id=block_id,
        normalized_score=90.0,
        evaluated_atoms={"tda_00000000000000000000000000000001": ExecutionStatus.PASSED},
        results=[
            {
                "tda_id": "tda_00000000000000000000000000000001",
                "status": "PASSED",
                "evaluation_reasoning": "Reason",
                "source_quotes": "Quote 2 from the second step output.",
                "depends_on_tda_ids": [],
                "short_circuit_reason_tda_ids": [],
            }
        ],
        step_id="step2",
    )

    blocks_by_id = {block_id: _create_matrix_block(block_id=block_id)}

    result = MatrixExplanationService.assemble_matrices_to_explain(
        dtos, title_map={}, blocks_by_id=blocks_by_id, target_locale="en"
    )
    assert len(result) == 1
    assert result[0].score == 50.0  # First entry wins


def test_assemble_matrices_to_explain_includes_failed_claims() -> None:
    """PROMISE: Matrix explanation includes both FAILED and N_A claims under UNMET CRITERIA / DEFICITS:."""
    block_id = "blk_0195f3a0000070058555555555555555"
    tda_id_1 = "tda_11111111111111111111111111111111"
    tda_id_3 = "tda_33333333333333333333333333333333"

    results = [
        {
            "tda_id": tda_id_1,
            "status": "FAILED",
            "evaluation_reasoning": "Reason",
            "source_quotes": None,
            "depends_on_tda_ids": [],
            "short_circuit_reason_tda_ids": [],
        },
        {
            "tda_id": tda_id_3,
            "status": "N_A",
            "evaluation_reasoning": "Reason",
            "source_quotes": None,
            "depends_on_tda_ids": [],
            "short_circuit_reason_tda_ids": [],
        },
    ]
    dtos = _make_step_dtos(
        block_id=block_id,
        normalized_score=78.5,
        evaluated_atoms={
            tda_id_1: ExecutionStatus.FAILED,
            tda_id_3: ExecutionStatus.N_A,
        },
        results=results,
    )

    scale = MatrixScale(
        score=1,
        ai_label="INITIAL",
        claims=[
            MatrixClaim(
                label=I18nText(translations={"en": "Claim 1"}),
                tda_assertions=[
                    TDAAssertion(
                        tda_id=tda_id_1,
                        inverse_evidence=False,
                        aggregation_mode="ALL_MUST_COMPLY",
                        concept_description="Concept 1 Long Enough",
                    )
                ],
            ),
            MatrixClaim(
                label=I18nText(translations={"en": "Claim 3"}),
                tda_assertions=[
                    TDAAssertion(
                        tda_id=tda_id_3,
                        inverse_evidence=False,
                        aggregation_mode="ALL_MUST_COMPLY",
                        concept_description="Concept 3 Long Enough",
                    )
                ],
            ),
        ],
    )

    blocks_by_id = {block_id: _create_matrix_block(block_id=block_id, scales=[scale])}

    result = MatrixExplanationService.assemble_matrices_to_explain(
        dtos, title_map={}, blocks_by_id=blocks_by_id, target_locale="en"
    )

    assert len(result) == 1
    assert "UNMET CRITERIA / DEFICITS:" in result[0].justification
    assert "Claim 1" in result[0].justification
    assert "Claim 3" in result[0].justification
    assert len(result[0].unmet_deficits) == 2


def test_assemble_matrices_to_explain_round_robin_diversity() -> None:
    """Verify alternating quote selection across claims under unbounded default and explicit limit."""
    block_id = "blk_0195f3a0000070068666666666666666"

    scale = MatrixScale(
        score=1,
        ai_label="DIVERSITY_SCALE",
        claims=[
            MatrixClaim(
                label=I18nText(translations={"en": "Claim Alpha"}),
                tda_assertions=[
                    TDAAssertion(
                        tda_id=f"tda_0195f3a00000700a800000000000000{i}",
                        inverse_evidence=False,
                        aggregation_mode="ALL_MUST_COMPLY",
                        concept_description=f"Alpha Concept {i}",
                    )
                    for i in range(4)
                ],
            ),
            MatrixClaim(
                label=I18nText(translations={"en": "Claim Beta"}),
                tda_assertions=[
                    TDAAssertion(
                        tda_id=f"tda_0195f3a00000700b800000000000000{i}",
                        inverse_evidence=False,
                        aggregation_mode="ALL_MUST_COMPLY",
                        concept_description=f"Beta Concept {i}",
                    )
                    for i in range(4)
                ],
            ),
        ],
    )

    results = []
    evaluated_atoms = {}
    for i in range(4):
        tda_a = f"tda_0195f3a00000700a800000000000000{i}"
        tda_b = f"tda_0195f3a00000700b800000000000000{i}"
        results.append(
            {
                "tda_id": tda_a,
                "status": "PASSED",
                "evaluation_reasoning": "Reason",
                "source_quotes": f"Alpha long verbatim quote sentence number {i}.",
                "depends_on_tda_ids": [],
                "short_circuit_reason_tda_ids": [],
            }
        )
        results.append(
            {
                "tda_id": tda_b,
                "status": "PASSED",
                "evaluation_reasoning": "Reason",
                "source_quotes": f"Beta long verbatim quote sentence number {i}.",
                "depends_on_tda_ids": [],
                "short_circuit_reason_tda_ids": [],
            }
        )
        evaluated_atoms[tda_a] = ExecutionStatus.PASSED
        evaluated_atoms[tda_b] = ExecutionStatus.PASSED

    dtos = _make_step_dtos(
        block_id=block_id,
        normalized_score=85.0,
        evaluated_atoms=evaluated_atoms,
        results=results,
    )

    blocks_by_id = {block_id: _create_matrix_block(block_id=block_id, scales=[scale])}

    # Unbounded default (0) retains all 8 quotes
    unbounded_result = MatrixExplanationService.assemble_matrices_to_explain(
        dtos, title_map={}, blocks_by_id=blocks_by_id, target_locale="en"
    )
    assert len(unbounded_result) == 1
    assert unbounded_result[0].justification.count('- "') == 8

    # Explicit limit (5) interleaves across claims up to 5 quotes
    result = MatrixExplanationService.assemble_matrices_to_explain(
        dtos, title_map={}, blocks_by_id=blocks_by_id, target_locale="en", max_quotes_per_matrix=5
    )

    assert len(result) == 1
    justification = result[0].justification
    assert "Alpha long verbatim quote" in justification
    assert "Beta long verbatim quote" in justification
    quote_count = justification.count('- "')
    assert quote_count == 5


def test_assemble_matrices_to_explain_deduplication_starvation_prevention() -> None:
    """Verify candidate pre-deduplication returns full quota of unique quotes even when TDAs share duplicate quotes."""
    block_id = "blk_0195f3a0000070078777777777777777"

    scale = MatrixScale(
        score=1,
        ai_label="DEDUP_SCALE",
        claims=[
            MatrixClaim(
                label=I18nText(translations={"en": "Claim A"}),
                tda_assertions=[
                    TDAAssertion(
                        tda_id=f"tda_0195f3a00000700a800000000000000{i}",
                        inverse_evidence=False,
                        aggregation_mode="ALL_MUST_COMPLY",
                        concept_description=f"Concept A {i}",
                    )
                    for i in range(5)
                ],
            ),
            MatrixClaim(
                label=I18nText(translations={"en": "Claim B"}),
                tda_assertions=[
                    TDAAssertion(
                        tda_id=f"tda_0195f3a00000700b800000000000000{i}",
                        inverse_evidence=False,
                        aggregation_mode="ALL_MUST_COMPLY",
                        concept_description=f"Concept B {i}",
                    )
                    for i in range(5)
                ],
            ),
        ],
    )

    results = []
    evaluated_atoms = {}
    for i in range(5):
        tda_a = f"tda_0195f3a00000700a800000000000000{i}"
        tda_b = f"tda_0195f3a00000700b800000000000000{i}"
        quote_a = f"Duplicate shared verbatim quote index {i if i < 2 else f'unique_a_{i}'}."
        quote_b = f"Duplicate shared verbatim quote index {i if i < 2 else f'unique_b_{i}'}."

        results.append(
            {
                "tda_id": tda_a,
                "status": "PASSED",
                "evaluation_reasoning": "Reason",
                "source_quotes": quote_a,
                "depends_on_tda_ids": [],
                "short_circuit_reason_tda_ids": [],
            }
        )
        results.append(
            {
                "tda_id": tda_b,
                "status": "PASSED",
                "evaluation_reasoning": "Reason",
                "source_quotes": quote_b,
                "depends_on_tda_ids": [],
                "short_circuit_reason_tda_ids": [],
            }
        )
        evaluated_atoms[tda_a] = ExecutionStatus.PASSED
        evaluated_atoms[tda_b] = ExecutionStatus.PASSED

    dtos = _make_step_dtos(
        block_id=block_id,
        normalized_score=90.0,
        evaluated_atoms=evaluated_atoms,
        results=results,
    )

    blocks_by_id = {block_id: _create_matrix_block(block_id=block_id, scales=[scale])}

    # Unbounded default retains all 8 unique quotes (2 shared + 6 unique)
    unbounded_result = MatrixExplanationService.assemble_matrices_to_explain(
        dtos, title_map={}, blocks_by_id=blocks_by_id, target_locale="en"
    )
    assert len(unbounded_result) == 1
    assert unbounded_result[0].justification.count('- "') == 8

    # Explicit budget of 5 returns full quota of 5 unique quotes
    result = MatrixExplanationService.assemble_matrices_to_explain(
        dtos, title_map={}, blocks_by_id=blocks_by_id, target_locale="en", max_quotes_per_matrix=5
    )

    assert len(result) == 1
    quote_count = result[0].justification.count('- "')
    assert quote_count == 5


def test_assemble_matrices_to_explain_unmet_criteria_severity_order() -> None:
    """Verify Level 1 deficits prioritized over Level 5 aspirational misses."""
    block_id = "blk_0195f3a0000070088888888888888888"

    scales = [
        MatrixScale(
            score=1,
            ai_label="CRITICAL",
            claims=[
                MatrixClaim(
                    label=I18nText(translations={"en": f"Deficit Level 1 Claim {i}"}),
                    tda_assertions=[
                        TDAAssertion(
                            tda_id=f"tda_0195f3a000007001811111111111111{i}",
                            inverse_evidence=False,
                            aggregation_mode="ALL_MUST_COMPLY",
                            concept_description=f"Deficit Concept L1 {i}",
                        )
                    ],
                )
                for i in range(3)
            ],
        ),
        MatrixScale(
            score=2,
            ai_label="INTERMEDIATE",
            claims=[
                MatrixClaim(
                    label=I18nText(translations={"en": f"Deficit Level 2 Claim {i}"}),
                    tda_assertions=[
                        TDAAssertion(
                            tda_id=f"tda_0195f3a000007002822222222222222{i}",
                            inverse_evidence=False,
                            aggregation_mode="ALL_MUST_COMPLY",
                            concept_description=f"Deficit Concept L2 {i}",
                        )
                    ],
                )
                for i in range(3)
            ],
        ),
        MatrixScale(
            score=5,
            ai_label="ASPIRATIONAL",
            claims=[
                MatrixClaim(
                    label=I18nText(translations={"en": f"Deficit Level 5 Claim {i}"}),
                    tda_assertions=[
                        TDAAssertion(
                            tda_id=f"tda_0195f3a000007005855555555555555{i}",
                            inverse_evidence=False,
                            aggregation_mode="ALL_MUST_COMPLY",
                            concept_description=f"Deficit Concept L5 {i}",
                        )
                    ],
                )
                for i in range(3)
            ],
        ),
    ]

    results = []
    evaluated_atoms = {}
    for s in scales:
        for c in s.claims:
            tda_id = c.tda_assertions[0].tda_id
            results.append(
                {
                    "tda_id": tda_id,
                    "status": "FAILED",
                    "evaluation_reasoning": "Reason",
                    "source_quotes": None,
                    "depends_on_tda_ids": [],
                    "short_circuit_reason_tda_ids": [],
                }
            )
            evaluated_atoms[tda_id] = ExecutionStatus.FAILED

    dtos = _make_step_dtos(
        block_id=block_id,
        normalized_score=30.0,
        evaluated_atoms=evaluated_atoms,
        results=results,
    )

    blocks_by_id = {block_id: _create_matrix_block(block_id=block_id, scales=scales)}

    # Unbounded default (0) retains all 9 unmet claims ordered by severity
    unbounded_result = MatrixExplanationService.assemble_matrices_to_explain(
        dtos, title_map={}, blocks_by_id=blocks_by_id, target_locale="en"
    )
    assert len(unbounded_result) == 1
    assert unbounded_result[0].justification.count("- Deficit Level") == 9

    # Explicit max_unmet_criteria=5 retains top 5 highest-severity deficits
    result = MatrixExplanationService.assemble_matrices_to_explain(
        dtos, title_map={}, blocks_by_id=blocks_by_id, target_locale="en", max_unmet_criteria=5
    )

    assert len(result) == 1
    justification = result[0].justification
    assert "UNMET CRITERIA / DEFICITS:" in justification
    unmet_count = justification.count("- Deficit Level")
    assert unmet_count == 5
    assert "Deficit Level 1 Claim 0" in justification
    assert "Deficit Level 1 Claim 1" in justification
    assert "Deficit Level 1 Claim 2" in justification
    assert "Deficit Level 2 Claim 0" in justification
    assert "Deficit Level 2 Claim 1" in justification
    assert "Deficit Level 5" not in justification


def test_assemble_matrices_to_explain_short_quote_filtering() -> None:
    """Verify quotes < 15 characters are excluded from SUPPORTING EVIDENCE."""
    block_id = "blk_0195f3a0000070098999999999999999"
    results = [
        {
            "tda_id": "tda_00000000000000000000000000000001",
            "status": "PASSED",
            "evaluation_reasoning": "Reason",
            "source_quotes": "yes",  # 3 chars < 15
            "depends_on_tda_ids": [],
            "short_circuit_reason_tda_ids": [],
        },
        {
            "tda_id": "tda_00000000000000000000000000000002",
            "status": "PASSED",
            "evaluation_reasoning": "Reason",
            "source_quotes": "This is a sufficiently long valid quote from document.",
            "depends_on_tda_ids": [],
            "short_circuit_reason_tda_ids": [],
        },
    ]
    dtos = _make_step_dtos(
        block_id=block_id,
        normalized_score=80.0,
        evaluated_atoms={
            "tda_00000000000000000000000000000001": ExecutionStatus.PASSED,
            "tda_00000000000000000000000000000002": ExecutionStatus.PASSED,
        },
        results=results,
    )

    blocks_by_id = {block_id: _create_matrix_block(block_id=block_id)}

    result = MatrixExplanationService.assemble_matrices_to_explain(
        dtos, title_map={}, blocks_by_id=blocks_by_id, target_locale="en"
    )

    assert len(result) == 1
    assert "This is a sufficiently long valid quote from document." in result[0].justification
    assert '"yes"' not in result[0].justification


def test_assemble_matrices_to_explain_multilingual_resolution() -> None:
    """Verify target_locale='fi' resolves Finnish claim translations while target_locale='en' resolves English."""
    block_id = "blk_0195f3a00000700a8aaaaaaaaaaaaaaa"
    tda_id = "tda_99999999999999999999999999999999"

    scale = MatrixScale(
        score=1,
        ai_label="MULTILINGUAL",
        claims=[
            MatrixClaim(
                label=I18nText(translations={"en": "English Criteria Name", "fi": "Suomalainen Kriteeri"}),
                tda_assertions=[
                    TDAAssertion(
                        tda_id=tda_id,
                        inverse_evidence=False,
                        aggregation_mode="ALL_MUST_COMPLY",
                        concept_description="Multilingual Concept",
                    )
                ],
            )
        ],
    )

    results = [
        {
            "tda_id": tda_id,
            "status": "FAILED",
            "evaluation_reasoning": "Reason",
            "source_quotes": None,
            "depends_on_tda_ids": [],
            "short_circuit_reason_tda_ids": [],
        }
    ]
    dtos = _make_step_dtos(
        block_id=block_id,
        normalized_score=25.0,
        evaluated_atoms={tda_id: ExecutionStatus.FAILED},
        results=results,
    )

    blocks_by_id = {block_id: _create_matrix_block(block_id=block_id, scales=[scale])}

    # Test Finnish
    res_fi = MatrixExplanationService.assemble_matrices_to_explain(
        dtos, title_map={}, blocks_by_id=blocks_by_id, target_locale="fi"
    )
    assert len(res_fi) == 1
    assert "Suomalainen Kriteeri" in res_fi[0].justification
    assert "English Criteria Name" not in res_fi[0].justification

    # Test English
    res_en = MatrixExplanationService.assemble_matrices_to_explain(
        dtos, title_map={}, blocks_by_id=blocks_by_id, target_locale="en"
    )
    assert len(res_en) == 1
    assert "English Criteria Name" in res_en[0].justification
    assert "Suomalainen Kriteeri" not in res_en[0].justification


def test_assemble_matrices_to_explain_corrupt_level_stats_raises() -> None:
    """Verify malformed level stats trigger Fail-Fast AppException."""
    block_id = "blk_0195f3a00000700b8bbbbbbbbbbbbbbb"

    dtos = [
        StepOutputDTO.model_construct(
            step_id="step1",
            block_id=block_id,
            data_type="matrix",
            payload={
                "normalized_score": 75.0,
                "level_breakdown": {
                    "1": {"hits": 3, "total": 3},
                    "2": "corrupt_non_dict_level_stats",
                    "3": {"hits": 1, "total": 2},
                },
                "results": [],
                "evaluated_atoms": {},
            },
        )
    ]

    blocks_by_id = {block_id: _create_matrix_block(block_id=block_id)}

    with pytest.raises(AppException) as exc_info:
        MatrixExplanationService.assemble_matrices_to_explain(
            dtos, title_map={}, blocks_by_id=blocks_by_id, target_locale="en"
        )
    assert exc_info.value.status_code == 422


def test_assemble_matrices_to_explain_with_synthesis_config_profile_overrides() -> None:
    """PROMISE: Verify synthesis_config profile overrides for max_quotes_per_matrix and max_unmet_criteria."""
    block_id = "blk_11112222333344445555666677778888"

    scale = MatrixScale(
        score=1,
        ai_label="OVERRIDE_SCALE",
        claims=[
            MatrixClaim(
                label=I18nText(translations={"en": f"Claim {i}"}),
                tda_assertions=[
                    TDAAssertion(
                        tda_id=f"tda_{i:032x}",
                        inverse_evidence=False,
                        aggregation_mode="ALL_MUST_COMPLY",
                        concept_description=f"Concept {i} Long Enough",
                    )
                ],
            )
            for i in range(10)
        ],
    )

    results = []
    evaluated_atoms = {}
    for i in range(5):
        tda_id = f"tda_{i:032x}"
        results.append(
            {
                "tda_id": tda_id,
                "status": "PASSED",
                "evaluation_reasoning": "Reason",
                "source_quotes": f"Valid quote number {i} with sufficient character length.",
                "depends_on_tda_ids": [],
                "short_circuit_reason_tda_ids": [],
            }
        )
        evaluated_atoms[tda_id] = ExecutionStatus.PASSED

    for i in range(5, 10):
        tda_id = f"tda_{i:032x}"
        results.append(
            {
                "tda_id": tda_id,
                "status": "FAILED",
                "evaluation_reasoning": "Failed reason",
                "source_quotes": None,
                "depends_on_tda_ids": [],
                "short_circuit_reason_tda_ids": [],
            }
        )
        evaluated_atoms[tda_id] = ExecutionStatus.FAILED

    dtos = _make_step_dtos(
        block_id=block_id,
        normalized_score=60.0,
        evaluated_atoms=evaluated_atoms,
        results=results,
    )

    blocks_by_id = {block_id: _create_matrix_block(block_id=block_id, scales=[scale])}

    result = MatrixExplanationService.assemble_matrices_to_explain(
        dtos,
        title_map={},
        blocks_by_id=blocks_by_id,
        target_locale="en",
        max_quotes_per_matrix=2,
        max_unmet_criteria=1,
    )

    assert len(result) == 1
    justification = result[0].justification
    quote_count = justification.count('- "')
    assert quote_count == 2
    unmet_count = justification.count("- Claim ")
    assert unmet_count == 1


def test_assemble_matrices_to_explain_malformed_atom_result_raises() -> None:
    """Test that malformed atom results raise AppException(VALIDATION_FAILED)."""
    block_id = "blk_0195f3a0000070038333333333333333"
    dtos = [
        StepOutputDTO.model_construct(
            step_id="step_atoms",
            block_id=block_id,
            data_type="unknown",
            payload=[{"invalid_field": "corrupted"}],
        ),
        StepOutputDTO(
            step_id="step1",
            block_id=block_id,
            data_type="matrix",
            payload=LightweightMatrixOutput(
                normalized_score=78.5,
                evaluated_atoms={},
            ),
        ),
    ]
    blocks_by_id = {block_id: _create_matrix_block(block_id=block_id)}

    with pytest.raises(AppException):
        MatrixExplanationService.assemble_matrices_to_explain(
            dtos, title_map={}, blocks_by_id=blocks_by_id, target_locale="en"
        )


def test_assemble_matrices_to_explain_invalid_matrix_payload_raises() -> None:
    """Test that invalid matrix payload raises AppException(VALIDATION_FAILED)."""
    block_id = "blk_0195f3a0000070038333333333333333"
    dtos = [
        StepOutputDTO.model_construct(
            step_id="step1",
            block_id=block_id,
            data_type="matrix",
            payload={
                "normalized_score": "not_a_valid_float_score",
                "results": [],
            },
        ),
    ]
    blocks_by_id = {block_id: _create_matrix_block(block_id=block_id)}

    with pytest.raises(AppException):
        MatrixExplanationService.assemble_matrices_to_explain(
            dtos, title_map={}, blocks_by_id=blocks_by_id, target_locale="en"
        )


def test_assemble_matrices_to_explain_atom_missing_from_claim_map_raises() -> None:
    """Test that evaluated atom not declared in matrix block raises AppException."""
    block_id = "blk_0195f3a0000070038333333333333333"
    dtos = [
        StepOutputDTO(
            step_id="step1",
            block_id=block_id,
            data_type="matrix",
            payload=LightweightMatrixOutput(
                normalized_score=50.0,
                evaluated_atoms={"tda_undeclared00000000000000000000": ExecutionStatus.PASSED},
            ),
        ),
    ]
    blocks_by_id = {block_id: _create_matrix_block(block_id=block_id)}

    with pytest.raises(AppException):
        MatrixExplanationService.assemble_matrices_to_explain(
            dtos, title_map={}, blocks_by_id=blocks_by_id, target_locale="en"
        )


def test_assemble_matrices_to_explain_raw_level_breakdown_variations() -> None:
    """Test level breakdown non-mapping validation and valid level distribution formatting."""
    block_id = "blk_0195f3a0000070038333333333333333"

    # 1. Non-mapping raw_level_breakdown raises AppException
    dtos_invalid = [
        StepOutputDTO.model_construct(
            step_id="step1",
            block_id=block_id,
            data_type="matrix",
            payload={
                "normalized_score": 70.0,
                "results": [],
                "evaluated_atoms": {},
                "level_breakdown": "not_a_mapping",
            },
        ),
    ]
    blocks_by_id = {block_id: _create_matrix_block(block_id=block_id)}

    with pytest.raises(AppException):
        MatrixExplanationService.assemble_matrices_to_explain(
            dtos_invalid, title_map={}, blocks_by_id=blocks_by_id, target_locale="en"
        )

    # 2. Valid mapping includes distribution context
    dtos_valid = [
        StepOutputDTO(
            step_id="step1",
            block_id=block_id,
            data_type="matrix",
            payload=LightweightMatrixOutput(
                normalized_score=70.0,
                evaluated_atoms={},
                level_breakdown={
                    "1": LevelStatsDTO(hits=2, total=3),
                    "2": LevelStatsDTO(hits=1, total=2),
                },
            ),
        ),
    ]
    result = MatrixExplanationService.assemble_matrices_to_explain(
        dtos_valid, title_map={}, blocks_by_id=blocks_by_id, target_locale="en"
    )
    assert len(result) == 1
    assert "[DISTRIBUTION CONTEXT: Level 1: 2/3 hits, Level 2: 1/2 hits]" in result[0].justification


def test_assemble_matrices_to_explain_payload_skips() -> None:
    """Test skipping of non-matrix blocks, missing blocks, scalar payloads, and non-dict atoms."""
    from backend_v2.models.domain.prompt_blocks import SystemRulePromptBlock

    block_id = "blk_0195f3a0000070038333333333333333"
    instruction_block = SystemRulePromptBlock.model_construct(
        id="blk_0195f3a0000070048444444444444444",
        category_id=PromptBlockCategory.SYSTEM_RULE,
    )
    matrix_block = _create_matrix_block(block_id=block_id)
    blocks_by_id = {
        block_id: matrix_block,
        "blk_0195f3a0000070048444444444444444": instruction_block,
    }

    dtos = [
        # Scalar payload
        StepOutputDTO(step_id="s1", block_id=block_id, data_type="matrix", payload="scalar_string"),
        # None payload
        StepOutputDTO(step_id="s2", block_id=block_id, data_type="matrix", payload=None),
        # Unknown block_id
        StepOutputDTO(step_id="s3", block_id="blk_unknown0000000000000000000", data_type="matrix", payload=None),
        # Non-matrix block category (system_rule)
        StepOutputDTO(step_id="s4", block_id="blk_0195f3a0000070048444444444444444", data_type="text", payload=None),
        # Results containing None and scalar atoms
        StepOutputDTO.model_construct(
            step_id="s_atoms",
            block_id=block_id,
            data_type="unknown",
            payload=[None, "invalid_scalar_atom"],
        ),
        StepOutputDTO(
            step_id="s5",
            block_id=block_id,
            data_type="matrix",
            payload=LightweightMatrixOutput(
                normalized_score=85.0,
                evaluated_atoms={},
            ),
        ),
    ]

    result = MatrixExplanationService.assemble_matrices_to_explain(
        dtos, title_map={}, blocks_by_id=blocks_by_id, target_locale="en"
    )
    assert len(result) == 1
    assert result[0].real_matrix_id == block_id


def test_quote_candidate_dto_model() -> None:
    """Test QuoteCandidateDTO model validation, immutability, and attribute access."""
    candidate = QuoteCandidateDTO(
        claim_label="Test Claim",
        quote="A sufficiently long quote string for testing candidate DTO.",
        quote_length=56,
    )
    assert candidate.claim_label == "Test Claim"
    assert candidate.quote_length == 56

    with pytest.raises((TypeError, ValueError)):
        candidate.quote = "mutated"


def test_assemble_matrices_to_explain_non_mapping_container_payload_skips() -> None:
    """Test skipping when payload is a non-mapping collection like a set."""
    block_id = "blk_0195f3a0000070038333333333333333"
    matrix_block = _create_matrix_block(block_id=block_id)
    blocks_by_id = {block_id: matrix_block}

    dtos = [
        StepOutputDTO.model_construct(
            step_id="s_set",
            block_id=block_id,
            data_type="matrix",
            payload={1, 2, 3},  # Set is not Mapping and not scalar
        ),
    ]

    result = MatrixExplanationService.assemble_matrices_to_explain(
        dtos, title_map={}, blocks_by_id=blocks_by_id, target_locale="en"
    )
    assert len(result) == 0


def test_assemble_matrices_to_explain_with_matrix_reducer_output_does_not_crash() -> None:
    """Regression test proving matrix_reducer outputs in available_dtos do not crash explanation assembly."""
    matrix_block_id = "blk_0195f3a00000700583f32679aa514fcb"
    tda_id = "tda_71e60846894545b2bc43a3361b7a5a9c"
    matrix_block = _create_matrix_block(block_id=matrix_block_id, tda_ids=[tda_id])
    blocks_by_id = {matrix_block_id: matrix_block}

    dtos = [
        StepOutputDTO(
            step_id="matrix_reducer",
            block_id="reduced_atoms",
            data_type="unknown",
            payload=[
                ReducedAtomDTO(
                    tda_id=tda_id,
                    status=ExecutionStatus.FAILED,
                    reasoning="Käyttäjä ei esitä kriittisiä tai sokraattisia kysymyksiä...",
                    source_quotes=None,
                    extracted_data=None,
                )
            ],
        ),
        StepOutputDTO(
            step_id="matrix_reducer",
            block_id="evaluated_matrices",
            data_type="unknown",
            payload=[matrix_block_id],
        ),
        StepOutputDTO(
            step_id="step_eval",
            block_id="results",
            data_type="unknown",
            payload=[
                AtomResultDTO(
                    tda_id=tda_id,
                    status=ExecutionStatus.FAILED,
                    evaluation_reasoning="Käyttäjä ei esitä kriittisiä tai sokraattisia kysymyksiä...",
                    source_quotes=None,
                )
            ],
        ),
        StepOutputDTO(
            step_id="step_eval",
            block_id=matrix_block_id,
            data_type="matrix",
            payload=LightweightMatrixOutput(
                normalized_score=50.0,
                evaluated_atoms={tda_id: ExecutionStatus.FAILED},
            ),
        ),
    ]

    result = MatrixExplanationService.assemble_matrices_to_explain(
        dtos, title_map={}, blocks_by_id=blocks_by_id, target_locale="fi"
    )
    assert len(result) == 1
    assert result[0].real_matrix_id == matrix_block_id


def test_assemble_matrices_to_explain_trace_matrix_payload_and_reduced_atom_and_title_map(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify TraceMatrixPayloadDTO hydration, single AtomResultDTO, single ReducedAtomDTO, and title_map resolution."""
    block_id = "blk_0195f3a00000700c8ccccccccccccccc"
    tda_1 = "tda_00000000000000000000000000000001"
    tda_2 = "tda_00000000000000000000000000000002"
    matrix_block = _create_matrix_block(block_id=block_id, tda_ids=[tda_1, tda_2])
    blocks_by_id = {block_id: matrix_block}

    monkeypatch.setattr(
        "backend_v2.services.orchestrator.matrix_explanation_service.get_settings",
        lambda: SimpleNamespace(
            min_synthesis_quote_length=15,
            max_synthesis_quote_length=25,
            max_synthesis_quotes_per_matrix=0,
            max_synthesis_unmet_criteria_per_matrix=0,
        ),
    )

    atom_1 = AtomResultDTO(
        tda_id=tda_1,
        status=ExecutionStatus.PASSED,
        evaluation_reasoning="Reasoning 1",
        source_quotes=("1234567890123456789012345_EXTRA_CLIPPED",),
    )
    atom_2 = ReducedAtomDTO(
        tda_id=tda_2,
        status=ExecutionStatus.PASSED,
        reasoning="Reasoning 2",
        source_quotes=("Second valid quote from ReducedAtomDTO",),
    )

    dtos = [
        # Single AtomResultDTO payload
        StepOutputDTO(
            step_id="step_single_atom",
            block_id="blk_single",
            data_type="unknown",
            payload=atom_1,
        ),
        # Single ReducedAtomDTO payload
        StepOutputDTO(
            step_id="step_reduced_atom",
            block_id="blk_reduced",
            data_type="unknown",
            payload=atom_2,
        ),
        # TraceMatrixPayloadDTO payload
        StepOutputDTO(
            step_id="step_trace_matrix",
            block_id=block_id,
            data_type="matrix",
            payload=TraceMatrixPayloadDTO(
                raw_score=3.5,
                normalized_score=70.0,
                justification="Initial trace justification",
                level_breakdown={"1": LevelStatsDTO(hits=2, total=2)},
                evaluated_atoms={tda_1: ExecutionStatus.PASSED, tda_2: ExecutionStatus.PASSED},
            ),
        ),
    ]

    result = MatrixExplanationService.assemble_matrices_to_explain(
        dtos,
        title_map={block_id.lower(): "Resolved Matrix Title"},
        blocks_by_id=blocks_by_id,
        target_locale="en",
    )

    assert len(result) == 1
    assert result[0].matrix_label == "Resolved Matrix Title"
    assert '"1234567890123456789012345"' in result[0].justification
    assert "EXTRA_CLIPPED" not in result[0].justification
    assert '"Second valid quote from R"' in result[0].justification


def test_assemble_matrices_to_explain_retains_all_deficits_and_contrastive_pairs_across_all_scales(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify unbounded retention of all 6 deficits with contrastive pairs across scales 2, 3, 4 and 8 600-char quotes."""
    monkeypatch.setattr(
        "backend_v2.services.orchestrator.matrix_explanation_service.get_settings",
        lambda: SimpleNamespace(
            min_synthesis_quote_length=15,
            max_synthesis_quote_length=0,
            max_synthesis_quotes_per_matrix=0,
            max_synthesis_unmet_criteria_per_matrix=0,
        ),
    )

    block_id = "blk_0195f3a00000700d8ddddddddddddddd"

    # 8 passed TDAs on Scale 1 + 2 failed TDAs each on Scales 2, 3, and 4 (total 6 failed)
    scale_1_claims = [
        MatrixClaim(
            label=I18nText(translations={"en": f"Passed Claim {i}"}),
            tda_assertions=[
                TDAAssertion(
                    tda_id=f"tda_0195f3a000007001800000000000000{i}",
                    inverse_evidence=False,
                    aggregation_mode="ALL_MUST_COMPLY",
                    concept_description=f"Passed Concept Description {i}",
                )
            ],
        )
        for i in range(8)
    ]

    scales = [MatrixScale(score=1, ai_label="SCALE_1", claims=scale_1_claims)]
    failed_tda_ids: list[str] = []
    for scale_num in (2, 3, 4):
        scale_claims: list[MatrixClaim] = []
        for j in range(2):
            tda_id = f"tda_0195f3a00000700{scale_num}800000000000000{j}"
            failed_tda_ids.append(tda_id)
            scale_claims.append(
                MatrixClaim(
                    label=I18nText(translations={"en": f"Scale {scale_num} Deficit {j}"}),
                    tda_assertions=[
                        TDAAssertion(
                            tda_id=tda_id,
                            inverse_evidence=(scale_num == 2 and j == 0),
                            aggregation_mode="EXISTS" if (scale_num == 2 and j == 0) else "ALL_MUST_COMPLY",
                            concept_description=f"Failed Concept Scale {scale_num} Item {j}",
                            anti_patterns=[AntiPattern(pattern=f"Anti-pattern S{scale_num}-{j}")],
                            contrastive_example=ContrastivePairDTO(
                                acceptable=f"Acceptable exemplar for scale {scale_num} item {j}.",
                                rejected=f"Rejected exemplar for scale {scale_num} item {j}.",
                            ),
                        )
                    ],
                )
            )
        scales.append(MatrixScale(score=scale_num, ai_label=f"SCALE_{scale_num}", claims=scale_claims))

    results: list[dict[str, JsonValue]] = []
    evaluated_atoms: dict[str, JsonValue] = {}
    for i in range(8):
        tid = f"tda_0195f3a000007001800000000000000{i}"
        long_quote = f"Quote_{i}_" + ("X" * (600 - len(f"Quote_{i}_")))
        assert len(long_quote) == 600
        results.append(
            {
                "tda_id": tid,
                "status": "PASSED",
                "evaluation_reasoning": f"Passed reasoning {i}",
                "source_quotes": [long_quote],
            }
        )
        evaluated_atoms[tid] = ExecutionStatus.PASSED

    for idx, tid in enumerate(failed_tda_ids):
        results.append(
            {
                "tda_id": tid,
                "status": "FAILED",
                "evaluation_reasoning": f"Step 4: Micro-CoT reasoning for failure {idx}",
                "source_quotes": None,
            }
        )
        evaluated_atoms[tid] = ExecutionStatus.FAILED

    dtos = _make_step_dtos(
        block_id=block_id,
        raw_score=2.0,
        normalized_score=40.0,
        evaluated_atoms=evaluated_atoms,
        results=results,
    )
    blocks_by_id = {block_id: _create_matrix_block(block_id=block_id, scales=scales)}

    result = MatrixExplanationService.assemble_matrices_to_explain(
        dtos, title_map={}, blocks_by_id=blocks_by_id, target_locale="en"
    )

    assert len(result) == 1
    ctx = result[0]
    assert len(ctx.unmet_deficits) == 6
    assert [d.scale_score for d in ctx.unmet_deficits] == [2, 2, 3, 3, 4, 4]
    assert ctx.unmet_deficits[0].is_inverse_evidence is True
    assert "[INVERSE EVIDENCE / POISON HIT]" in ctx.justification

    for deficit in ctx.unmet_deficits:
        assert deficit.status == "FAILED"
        assert deficit.evaluation_reasoning is not None
        assert "Step 4: Micro-CoT reasoning for failure" in deficit.evaluation_reasoning
        assert len(deficit.anti_patterns) == 1
        assert deficit.contrastive_rejected is not None
        assert deficit.contrastive_acceptable is not None
        assert deficit.contrastive_rejected in ctx.justification
        assert deficit.contrastive_acceptable in ctx.justification

    # All 8 quotes retained at full 600-character length
    assert ctx.justification.count('- "Quote_') == 8
    for i in range(8):
        expected_quote = f"Quote_{i}_" + ("X" * (600 - len(f"Quote_{i}_")))
        assert expected_quote in ctx.justification


def test_assemble_matrices_to_explain_transitively_hydrates_na_parent_claim_and_reasoning() -> None:
    """Verify N_A atoms transitively resolve parent claim labels and parent evaluation_reasoning."""
    block_id = "blk_0195f3a00000700e8eeeeeeeeeeeeeee"
    other_block_id = "blk_0195f3a00000700f8fffffffffffffff"
    tda_parent = "tda_0195f3a0000070018aaaaaaaaaaaaaaa"
    tda_mid_na = "tda_0195f3a0000070028bbbbbbbbbbbbbbb"
    tda_child_na = "tda_0195f3a0000070038ccccccccccccccc"
    tda_edge_na = "tda_0195f3a0000070048ddddddddddddddd"
    tda_cross_matrix = "tda_0195f3a0000070058eeeeeeeeeeeeeee"
    tda_unmapped = "tda_0195f3a0000070068fffffffffffffff"

    scales = [
        MatrixScale(
            score=1,
            ai_label="FOUNDATION",
            claims=[
                MatrixClaim(
                    label=I18nText(translations={"en": "Parent Claim"}),
                    tda_assertions=[
                        TDAAssertion(
                            tda_id=tda_parent,
                            inverse_evidence=False,
                            aggregation_mode="ALL_MUST_COMPLY",
                            concept_description="Parent Prerequisite Concept",
                        )
                    ],
                )
            ],
        ),
        MatrixScale(
            score=2,
            ai_label="INTERMEDIATE",
            claims=[
                MatrixClaim(
                    label=I18nText(translations={"en": "Mid Blocked Claim"}),
                    tda_assertions=[
                        TDAAssertion(
                            tda_id=tda_mid_na,
                            inverse_evidence=False,
                            aggregation_mode="ALL_MUST_COMPLY",
                            concept_description="Mid Blocked Concept",
                        )
                    ],
                )
            ],
        ),
        MatrixScale(
            score=3,
            ai_label="ADVANCED",
            claims=[
                MatrixClaim(
                    label=I18nText(translations={"en": "Blocked Claim"}),
                    tda_assertions=[
                        TDAAssertion(
                            tda_id=tda_child_na,
                            inverse_evidence=False,
                            aggregation_mode="ALL_MUST_COMPLY",
                            concept_description="Child Blocked Concept",
                        )
                    ],
                ),
                MatrixClaim(
                    label=I18nText(translations={"en": "Static Edge Blocked Claim"}),
                    tda_assertions=[
                        TDAAssertion(
                            tda_id=tda_edge_na,
                            inverse_evidence=False,
                            aggregation_mode="ALL_MUST_COMPLY",
                            concept_description="Static Edge Blocked Concept",
                            depends_on=(
                                CausalEdge(
                                    edge_reasoning="Requires cross matrix prerequisite",
                                    tda_id=tda_cross_matrix,
                                    source_id="chk_0",
                                ),
                                CausalEdge(
                                    edge_reasoning="Requires unmapped prerequisite",
                                    tda_id=tda_unmapped,
                                    source_id="chk_0",
                                ),
                            ),
                        )
                    ],
                ),
            ],
        ),
    ]

    other_scales = [
        MatrixScale(
            score=1,
            ai_label="OTHER",
            claims=[
                MatrixClaim(
                    label=I18nText(translations={"en": "Cross Matrix Prerequisite Claim"}),
                    tda_assertions=[
                        TDAAssertion(
                            tda_id=tda_cross_matrix,
                            inverse_evidence=False,
                            aggregation_mode="ALL_MUST_COMPLY",
                            concept_description="Cross Matrix Concept",
                        )
                    ],
                )
            ],
        )
    ]

    results: list[dict[str, JsonValue]] = [
        {
            "tda_id": tda_parent,
            "status": "FAILED",
            "evaluation_reasoning": "Step 4: Failed due to missing metric",
            "source_quotes": None,
            "depends_on_tda_ids": [],
            "short_circuit_reason_tda_ids": [],
        },
        {
            "tda_id": tda_mid_na,
            "status": "N_A",
            "evaluation_reasoning": None,
            "source_quotes": None,
            "depends_on_tda_ids": [tda_parent],
            "short_circuit_reason_tda_ids": [tda_parent],
        },
        {
            "tda_id": tda_child_na,
            "status": "N_A",
            "evaluation_reasoning": None,
            "source_quotes": None,
            "depends_on_tda_ids": [tda_mid_na],
            "short_circuit_reason_tda_ids": [tda_mid_na],
        },
    ]

    dtos = _make_step_dtos(
        block_id=block_id,
        raw_score=1.0,
        normalized_score=20.0,
        evaluated_atoms={
            tda_parent: ExecutionStatus.FAILED,
            tda_mid_na: ExecutionStatus.N_A,
            tda_child_na: ExecutionStatus.N_A,
            tda_edge_na: ExecutionStatus.N_A,
        },
        results=results,
    )

    blocks_by_id = {
        block_id: _create_matrix_block(block_id=block_id, scales=scales),
        other_block_id: _create_matrix_block(block_id=other_block_id, scales=other_scales),
    }

    result = MatrixExplanationService.assemble_matrices_to_explain(
        dtos, title_map={}, blocks_by_id=blocks_by_id, target_locale="en"
    )

    assert len(result) == 1
    deficits_by_claim = {d.claim: d for d in result[0].unmet_deficits}
    assert "Blocked Claim" in deficits_by_claim
    child_deficit = deficits_by_claim["Blocked Claim"]
    assert child_deficit.status == "N_A"
    assert any(
        "Parent Claim" in item and "Step 4: Failed due to missing metric" in item
        for item in child_deficit.short_circuited_by_claims
    )
    assert (
        "[Blocked Claim] <-- SHORT-CIRCUITED BY PREREQUISITE FAILURE: "
        "[Parent Claim: Step 4: Failed due to missing metric]"
    ) in child_deficit.short_circuited_by_claims

    edge_deficit = deficits_by_claim["Static Edge Blocked Claim"]
    assert edge_deficit.status == "N_A"
    assert any("Cross Matrix Prerequisite Claim" in item for item in edge_deficit.short_circuited_by_claims)
    assert all("tda_" not in item for item in edge_deficit.short_circuited_by_claims)


def test_assemble_matrices_to_explain_max_score_row_has_zero_unmet_deficits() -> None:
    """Verify matrix row where achieved_score equals computed_max (5 of 5) has empty unmet_deficits."""
    block_id = "blk_0195f3a00000700a9999999999999999"
    tda_1 = "tda_0195f3a0000070019999999999999991"
    tda_5 = "tda_0195f3a0000070059999999999999995"

    scales = [
        MatrixScale(
            score=1,
            ai_label="SCALE_1",
            claims=[
                MatrixClaim(
                    label=I18nText(translations={"en": "Scale 1 Claim"}),
                    tda_assertions=[
                        TDAAssertion(
                            tda_id=tda_1,
                            inverse_evidence=False,
                            aggregation_mode="ALL_MUST_COMPLY",
                            concept_description="Scale 1 Concept Description",
                        )
                    ],
                )
            ],
        ),
        MatrixScale(
            score=5,
            ai_label="SCALE_5",
            claims=[
                MatrixClaim(
                    label=I18nText(translations={"en": "Scale 5 Claim"}),
                    tda_assertions=[
                        TDAAssertion(
                            tda_id=tda_5,
                            inverse_evidence=False,
                            aggregation_mode="ALL_MUST_COMPLY",
                            concept_description="Scale 5 Concept Description",
                        )
                    ],
                )
            ],
        ),
    ]

    dtos = _make_step_dtos(
        block_id=block_id,
        raw_score=5.0,
        normalized_score=100.0,
        evaluated_atoms={
            tda_1: ExecutionStatus.FAILED,
            tda_5: ExecutionStatus.PASSED,
        },
        results=[
            {
                "tda_id": tda_1,
                "status": "FAILED",
                "evaluation_reasoning": "Minor omission on scale 1",
                "source_quotes": None,
            },
            {
                "tda_id": tda_5,
                "status": "PASSED",
                "evaluation_reasoning": "Achieved mastery on scale 5",
                "source_quotes": ["Comprehensive mastery quote exceeding minimum length."],
            },
        ],
    )
    blocks_by_id = {block_id: _create_matrix_block(block_id=block_id, scales=scales)}

    result = MatrixExplanationService.assemble_matrices_to_explain(
        dtos, title_map={}, blocks_by_id=blocks_by_id, target_locale="en"
    )

    assert len(result) == 1
    assert result[0].unmet_deficits == []
    assert "UNMET CRITERIA / DEFICITS:" not in result[0].justification


def test_matrix_failure_deficit_dto_invalid_status_raises_validation_error() -> None:
    """Verify MatrixFailureDeficitDTO raises ValidationError when instantiated with status='PASSED'."""
    with pytest.raises(ValidationError):
        MatrixFailureDeficitDTO.model_validate(
            {
                "claim": "Invalid Status Claim",
                "status": "PASSED",
                "scale_score": 1,
                "evaluation_reasoning": "Should fail validation",
                "is_inverse_evidence": False,
                "short_circuited_by_claims": [],
                "anti_patterns": [],
                "contrastive_rejected": None,
                "contrastive_acceptable": None,
            }
        )

