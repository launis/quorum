"""Unit tests for the Matrix Explanation Service.

Tests for matrix explanation context generation, Status-Aware Dual Reporting,
and Ranked Round-Robin quote and unmet criteria curation.
"""

from typing import Any

import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.matrix import MatrixClaim, MatrixScale, TDAAssertion
from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock, PromptBlock
from backend_v2.models.dtos.atom_result import AtomResultDTO
from backend_v2.models.dtos.lightweight_matrix import LevelStatsDTO, LightweightMatrixOutput
from backend_v2.models.enums import BlockDataType, ExecutionStatus, LaxExecutionStatus, PromptBlockCategory
from backend_v2.models.state import StepOutputDTO
from backend_v2.services.orchestrator.matrix_explanation_service import (
    MatrixExplanationService,
    QuoteCandidateDTO,
)


def _create_matrix_block(
    block_id: str = "blk_1234567890abcdef12345678",
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
    raw = str(val.value if hasattr(val, "value") else val)
    return ExecutionStatus(raw)


def _make_step_dtos(
    block_id: str,
    normalized_score: float,
    evaluated_atoms: dict[str, Any],
    results: list[dict[str, Any]] | None = None,
    level_breakdown: dict[str, LevelStatsDTO] | None = None,
    step_id: str = "step1",
) -> list[StepOutputDTO]:
    """Helper to construct strictly typed StepOutputDTO collections for atom and matrix steps."""
    dtos: list[StepOutputDTO] = []
    if results:
        atom_dtos = [
            AtomResultDTO(
                tda_id=r["tda_id"],
                status=_to_status(r["status"]),
                evaluation_reasoning=r.get("evaluation_reasoning"),
                source_quote=r.get("source_quote"),
                contextual_override=r.get("contextual_override", False),
                is_inverse_evidence=r.get("is_inverse_evidence", False),
            )
            for r in results
            if r is not None and isinstance(r, dict) and "tda_id" in r
        ]
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
                normalized_score=normalized_score,
                evaluated_atoms={k: _to_status(v) for k, v in evaluated_atoms.items()},
                level_breakdown=level_breakdown,
            ),
        )
    )
    return dtos


def test_assemble_matrices_to_explain_basic() -> None:
    """Test basic assembly of matrices_to_explain from scored payloads with evaluated_atoms."""
    block_id = "blk_111111111111111111111111"
    results = [
        {
            "tda_id": "tda_00000000000000000000000000000001",
            "status": "PASSED",
            "evaluation_reasoning": "Reason",
            "source_quote": "Quote A from source verbatim statement.",
            "depends_on_tda_ids": [],
            "short_circuit_reason_tda_ids": [],
        },
        {
            "tda_id": "tda_00000000000000000000000000000002",
            "status": "PASSED",
            "evaluation_reasoning": "Reason",
            "source_quote": "Quote B from source verbatim statement.",
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
    block_id = "blk_222222222222222222222222"
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
    block_id = "blk_333333333333333333333333"
    results = [
        {
            "tda_id": "tda_00000000000000000000000000000001",
            "status": "PASSED",
            "evaluation_reasoning": "Reason",
            "source_quote": None,
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
    block_id = "blk_444444444444444444444444"
    dtos = _make_step_dtos(
        block_id=block_id,
        normalized_score=50.0,
        evaluated_atoms={"tda_00000000000000000000000000000001": ExecutionStatus.PASSED},
        results=[
            {
                "tda_id": "tda_00000000000000000000000000000001",
                "status": "PASSED",
                "evaluation_reasoning": "Reason",
                "source_quote": "Quote 1 from the first step output.",
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
                "source_quote": "Quote 2 from the second step output.",
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
    """PROMISE: Matrix explanation must include FAILED claims under UNMET CRITERIA / DEFICITS: and skip N_A claims."""
    block_id = "blk_555555555555555555555555"
    tda_id_1 = "tda_11111111111111111111111111111111"
    tda_id_3 = "tda_33333333333333333333333333333333"

    results = [
        {
            "tda_id": tda_id_1,
            "status": "FAILED",
            "evaluation_reasoning": "Reason",
            "source_quote": None,
            "depends_on_tda_ids": [],
            "short_circuit_reason_tda_ids": [],
        },
        {
            "tda_id": tda_id_3,
            "status": "N_A",
            "evaluation_reasoning": "Reason",
            "source_quote": None,
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
    assert "Claim 3" not in result[0].justification


def test_assemble_matrices_to_explain_round_robin_diversity() -> None:
    """Verify alternating quote selection across claims up to max synthesis quotes per matrix (5)."""
    block_id = "blk_666666666666666666666666"

    scale = MatrixScale(
        score=1,
        ai_label="DIVERSITY_SCALE",
        claims=[
            MatrixClaim(
                label=I18nText(translations={"en": "Claim Alpha"}),
                tda_assertions=[
                    TDAAssertion(
                        tda_id=f"tda_a000000000000000000000000000000{i}",
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
                        tda_id=f"tda_b000000000000000000000000000000{i}",
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
        tda_a = f"tda_a000000000000000000000000000000{i}"
        tda_b = f"tda_b000000000000000000000000000000{i}"
        results.append(
            {
                "tda_id": tda_a,
                "status": "PASSED",
                "evaluation_reasoning": "Reason",
                "source_quote": f"Alpha long verbatim quote sentence number {i}.",
                "depends_on_tda_ids": [],
                "short_circuit_reason_tda_ids": [],
            }
        )
        results.append(
            {
                "tda_id": tda_b,
                "status": "PASSED",
                "evaluation_reasoning": "Reason",
                "source_quote": f"Beta long verbatim quote sentence number {i}.",
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

    result = MatrixExplanationService.assemble_matrices_to_explain(
        dtos, title_map={}, blocks_by_id=blocks_by_id, target_locale="en"
    )

    assert len(result) == 1
    justification = result[0].justification
    assert "Alpha long verbatim quote" in justification
    assert "Beta long verbatim quote" in justification
    quote_count = justification.count('- "')
    assert quote_count == 5


def test_assemble_matrices_to_explain_deduplication_starvation_prevention() -> None:
    """Verify candidate pre-deduplication returns full quota of unique quotes even when TDAs share duplicate quotes."""
    block_id = "blk_777777777777777777777777"

    scale = MatrixScale(
        score=1,
        ai_label="DEDUP_SCALE",
        claims=[
            MatrixClaim(
                label=I18nText(translations={"en": "Claim A"}),
                tda_assertions=[
                    TDAAssertion(
                        tda_id=f"tda_da00000000000000000000000000000{i}",
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
                        tda_id=f"tda_db00000000000000000000000000000{i}",
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
        tda_a = f"tda_da00000000000000000000000000000{i}"
        tda_b = f"tda_db00000000000000000000000000000{i}"
        quote_a = f"Duplicate shared verbatim quote index {i if i < 2 else f'unique_a_{i}'}."
        quote_b = f"Duplicate shared verbatim quote index {i if i < 2 else f'unique_b_{i}'}."

        results.append(
            {
                "tda_id": tda_a,
                "status": "PASSED",
                "evaluation_reasoning": "Reason",
                "source_quote": quote_a,
                "depends_on_tda_ids": [],
                "short_circuit_reason_tda_ids": [],
            }
        )
        results.append(
            {
                "tda_id": tda_b,
                "status": "PASSED",
                "evaluation_reasoning": "Reason",
                "source_quote": quote_b,
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

    result = MatrixExplanationService.assemble_matrices_to_explain(
        dtos, title_map={}, blocks_by_id=blocks_by_id, target_locale="en"
    )

    assert len(result) == 1
    quote_count = result[0].justification.count('- "')
    assert quote_count == 5


def test_assemble_matrices_to_explain_unmet_criteria_severity_order() -> None:
    """Verify Level 1 deficits prioritized over Level 5 aspirational misses."""
    block_id = "blk_888888888888888888888888"

    scales = [
        MatrixScale(
            score=1,
            ai_label="CRITICAL",
            claims=[
                MatrixClaim(
                    label=I18nText(translations={"en": f"Deficit Level 1 Claim {i}"}),
                    tda_assertions=[
                        TDAAssertion(
                            tda_id=f"tda_1111111111111111111111111111111{i}",
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
                            tda_id=f"tda_2222222222222222222222222222222{i}",
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
                            tda_id=f"tda_5555555555555555555555555555555{i}",
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
                    "source_quote": None,
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

    result = MatrixExplanationService.assemble_matrices_to_explain(
        dtos, title_map={}, blocks_by_id=blocks_by_id, target_locale="en"
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
    block_id = "blk_999999999999999999999999"
    results = [
        {
            "tda_id": "tda_00000000000000000000000000000001",
            "status": "PASSED",
            "evaluation_reasoning": "Reason",
            "source_quote": "yes",  # 3 chars < 15
            "depends_on_tda_ids": [],
            "short_circuit_reason_tda_ids": [],
        },
        {
            "tda_id": "tda_00000000000000000000000000000002",
            "status": "PASSED",
            "evaluation_reasoning": "Reason",
            "source_quote": "This is a sufficiently long valid quote from document.",
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
    block_id = "blk_aaaaaaaaaaaaaaaaaaaaaaaa"
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
            "source_quote": None,
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
    block_id = "blk_bbbbbbbbbbbbbbbbbbbbbbbb"

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
                "source_quote": f"Valid quote number {i} with sufficient character length.",
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
                "source_quote": None,
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
    block_id = "blk_333333333333333333333333"
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
    block_id = "blk_333333333333333333333333"
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
    block_id = "blk_333333333333333333333333"
    dtos = [
        StepOutputDTO(
            step_id="step1",
            block_id=block_id,
            data_type="matrix",
            payload=LightweightMatrixOutput(
                normalized_score=50.0,
                evaluated_atoms={"tda_undeclared00000000000000000000": LaxExecutionStatus.PASSED},
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
    block_id = "blk_333333333333333333333333"

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

    block_id = "blk_333333333333333333333333"
    instruction_block = SystemRulePromptBlock.model_construct(
        id="blk_444444444444444444444444",
        category_id=PromptBlockCategory.SYSTEM_RULE,
    )
    matrix_block = _create_matrix_block(block_id=block_id)
    blocks_by_id = {
        block_id: matrix_block,
        "blk_444444444444444444444444": instruction_block,
    }

    dtos = [
        # Scalar payload
        StepOutputDTO(step_id="s1", block_id=block_id, data_type="matrix", payload="scalar_string"),
        # None payload
        StepOutputDTO(step_id="s2", block_id=block_id, data_type="matrix", payload=None),
        # Unknown block_id
        StepOutputDTO(step_id="s3", block_id="blk_unknown0000000000000000000", data_type="matrix", payload=None),
        # Non-matrix block category (system_rule)
        StepOutputDTO(step_id="s4", block_id="blk_444444444444444444444444", data_type="text", payload=None),
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
        candidate.quote = "mutated"  # type: ignore[misc]


def test_assemble_matrices_to_explain_non_mapping_container_payload_skips() -> None:
    """Test skipping when payload is a non-mapping collection like a set."""
    block_id = "blk_333333333333333333333333"
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
    matrix_block_id = "blk_53f32679aa514fcb"
    tda_id = "tda_71e60846894545b2bc43a3361b7a5a9c"
    matrix_block = _create_matrix_block(block_id=matrix_block_id, tda_ids=[tda_id])
    blocks_by_id = {matrix_block_id: matrix_block}

    dtos = [
        StepOutputDTO.model_construct(
            step_id="matrix_reducer",
            block_id="reduced_atoms",
            data_type="unknown",
            payload=[
                {
                    "tda_id": tda_id,
                    "status": "FAILED",
                    "reasoning": "Käyttäjä ei esitä kriittisiä tai sokraattisia kysymyksiä...",
                    "source_quote": None,
                    "extracted_data": None,
                }
            ],
        ),
        StepOutputDTO.model_construct(
            step_id="matrix_reducer",
            block_id="evaluated_matrices",
            data_type="unknown",
            payload=[{"matrix_id": matrix_block_id}],
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
                    source_quote=None,
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

