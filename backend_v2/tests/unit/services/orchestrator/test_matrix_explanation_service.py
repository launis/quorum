"""Unit tests for the Matrix Explanation Service.

Tests for matrix explanation context generation, Status-Aware Dual Reporting,
and Ranked Round-Robin quote and unmet criteria curation.
"""

from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock, PromptBlock
from backend_v2.models.enums import BlockDataType, ExecutionStatus, PromptBlockCategory
from backend_v2.models.state import StepOutputDTO
from backend_v2.models.v2_core import (
    I18nText,
    MatrixClaim,
    MatrixScale,
    SynthesisConfigDTO,
    TDAAssertion,
)
from backend_v2.services.orchestrator.matrix_explanation_service import MatrixExplanationService


def _create_matrix_block(
    block_id: str = "blk_1234567890abcdef12345678",
    scales: list[MatrixScale] | None = None,
) -> PromptBlock:
    """Helper to create a concrete, valid PromptBlock fixture without mocks."""
    if scales is None:
        scales = [
            MatrixScale(
                score=1,
                ai_label="INITIAL",
                claims=[
                    MatrixClaim(
                        label=I18nText(default_locale="en", translations={"en": "Claim Label", "fi": "Väite"}),
                        tda_assertions=[
                            TDAAssertion(
                                tda_id="tda_00000000000000000000000000000001",
                                inverse_evidence=False,
                                aggregation_mode="ALL_MUST_COMPLY",
                                concept_description="Concept Description Valid",
                            )
                        ],
                    )
                ],
            )
        ]

    return MatrixPromptBlock(
        id=block_id,
        slug=f"slug_{block_id}",
        label=I18nText(default_locale="en", translations={"en": "Matrix Label", "fi": "Matriisin Otsikko"}),
        description=I18nText(default_locale="en", translations={"en": "Description", "fi": "Kuvaus"}),
        ai_description="Cognitive instructions for matrix",
        category_id=PromptBlockCategory.MATRIX,
        type=BlockDataType.FLOAT,
        scales=scales,
    )


def test_assemble_matrices_to_explain_basic() -> None:
    """Test basic assembly of matrices_to_explain from scored payloads with evaluated_atoms."""
    block_id = "blk_111111111111111111111111"
    dtos = [
        StepOutputDTO(
            step_id="step1",
            block_id=block_id,
            data_type="matrix",
            payload={
                "normalized_score": 78.5,
                "results": [
                    {
                        "tda_id": "a1",
                        "status": "PASSED",
                        "evaluation_reasoning": "Reason",
                        "source_quote": "Quote A from source verbatim statement.",
                        "depends_on_tda_ids": [],
                        "short_circuit_reason_tda_ids": [],
                    },
                    {
                        "tda_id": "a2",
                        "status": "PASSED",
                        "evaluation_reasoning": "Reason",
                        "source_quote": "Quote B from source verbatim statement.",
                        "depends_on_tda_ids": [],
                        "short_circuit_reason_tda_ids": [],
                    },
                ],
                "evaluated_atoms": {
                    "a1": ExecutionStatus.PASSED,
                    "a2": ExecutionStatus.PASSED,
                },
            },
        ),
    ]

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
            payload={"normalized_score": 78.5},
        ),
    ]

    blocks_by_id = {block_id: _create_matrix_block(block_id=block_id)}

    result = MatrixExplanationService.assemble_matrices_to_explain(
        dtos, title_map={}, blocks_by_id=blocks_by_id, target_locale="en"
    )
    assert len(result) == 1
    assert result[0].justification == "No direct evidence quotes or specific deficits recorded for this matrix."


def test_assemble_matrices_to_explain_empty_quotes_list() -> None:
    """Test that matrices with empty quote lists are INCLUDED with a fallback justification to prevent Fail-Fast crash in blueprint.py."""
    block_id = "blk_333333333333333333333333"
    dtos = [
        StepOutputDTO(
            step_id="step1",
            block_id=block_id,
            data_type="matrix",
            payload={
                "normalized_score": 78.5,
                "results": [
                    {
                        "tda_id": "a1",
                        "status": "PASSED",
                        "evaluation_reasoning": "Reason",
                        "source_quote": None,
                        "depends_on_tda_ids": [],
                        "short_circuit_reason_tda_ids": [],
                    }
                ],
                "evaluated_atoms": {"a1": ExecutionStatus.PASSED},
            },
        ),
    ]

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
    dtos = [
        StepOutputDTO(
            step_id="step1",
            block_id=block_id,
            data_type="matrix",
            payload={
                "normalized_score": 50.0,
                "results": [
                    {
                        "tda_id": "a1",
                        "status": "PASSED",
                        "evaluation_reasoning": "Reason",
                        "source_quote": "Quote 1 from the first step output.",
                        "depends_on_tda_ids": [],
                        "short_circuit_reason_tda_ids": [],
                    }
                ],
                "evaluated_atoms": {"a1": ExecutionStatus.PASSED},
            },
        ),
        StepOutputDTO(
            step_id="step2",
            block_id=block_id,
            data_type="matrix",
            payload={
                "normalized_score": 90.0,
                "results": [
                    {
                        "tda_id": "a1",
                        "status": "PASSED",
                        "evaluation_reasoning": "Reason",
                        "source_quote": "Quote 2 from the second step output.",
                        "depends_on_tda_ids": [],
                        "short_circuit_reason_tda_ids": [],
                    }
                ],
                "evaluated_atoms": {"a1": ExecutionStatus.PASSED},
            },
        ),
    ]

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

    dtos = [
        StepOutputDTO(
            step_id="step1",
            block_id=block_id,
            data_type="matrix",
            payload={
                "normalized_score": 78.5,
                "results": [
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
                ],
                "evaluated_atoms": {
                    tda_id_1: ExecutionStatus.FAILED,
                    tda_id_3: ExecutionStatus.N_A,
                },
            },
        ),
    ]

    scale = MatrixScale(
        score=1,
        ai_label="INITIAL",
        claims=[
            MatrixClaim(
                label=I18nText(default_locale="en", translations={"en": "Claim 1"}),
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
                label=I18nText(default_locale="en", translations={"en": "Claim 3"}),
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

    # Claim A has 4 quotes, Claim B has 4 quotes
    scale = MatrixScale(
        score=1,
        ai_label="DIVERSITY_SCALE",
        claims=[
            MatrixClaim(
                label=I18nText(default_locale="en", translations={"en": "Claim Alpha"}),
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
                label=I18nText(default_locale="en", translations={"en": "Claim Beta"}),
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

    dtos = [
        StepOutputDTO(
            step_id="step1",
            block_id=block_id,
            data_type="matrix",
            payload={
                "normalized_score": 85.0,
                "results": results,
                "evaluated_atoms": evaluated_atoms,
            },
        )
    ]

    blocks_by_id = {block_id: _create_matrix_block(block_id=block_id, scales=[scale])}

    result = MatrixExplanationService.assemble_matrices_to_explain(
        dtos, title_map={}, blocks_by_id=blocks_by_id, target_locale="en"
    )

    assert len(result) == 1
    justification = result[0].justification
    # Must contain quotes from both Claim Alpha and Claim Beta
    assert "Alpha long verbatim quote" in justification
    assert "Beta long verbatim quote" in justification
    # Exactly 5 quotes total
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
                label=I18nText(default_locale="en", translations={"en": "Claim A"}),
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
                label=I18nText(default_locale="en", translations={"en": "Claim B"}),
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
    # da_0, da_1 share exact duplicate quote with db_0, db_1
    for i in range(5):
        tda_a = f"tda_da00000000000000000000000000000{i}"
        tda_b = f"tda_db00000000000000000000000000000{i}"
        # Unique quotes for i >= 2, duplicate for i < 2
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

    dtos = [
        StepOutputDTO(
            step_id="step1",
            block_id=block_id,
            data_type="matrix",
            payload={
                "normalized_score": 90.0,
                "results": results,
                "evaluated_atoms": evaluated_atoms,
            },
        )
    ]

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
                    label=I18nText(default_locale="en", translations={"en": f"Deficit Level 1 Claim {i}"}),
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
                    label=I18nText(default_locale="en", translations={"en": f"Deficit Level 2 Claim {i}"}),
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
                    label=I18nText(default_locale="en", translations={"en": f"Deficit Level 5 Claim {i}"}),
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

    dtos = [
        StepOutputDTO(
            step_id="step1",
            block_id=block_id,
            data_type="matrix",
            payload={
                "normalized_score": 30.0,
                "results": results,
                "evaluated_atoms": evaluated_atoms,
            },
        )
    ]

    blocks_by_id = {block_id: _create_matrix_block(block_id=block_id, scales=scales)}

    result = MatrixExplanationService.assemble_matrices_to_explain(
        dtos, title_map={}, blocks_by_id=blocks_by_id, target_locale="en"
    )

    assert len(result) == 1
    justification = result[0].justification
    assert "UNMET CRITERIA / DEFICITS:" in justification

    # Exactly 5 unmet criteria selected
    unmet_count = justification.count("- Deficit Level")
    assert unmet_count == 5

    # All 3 Level 1 claims must be present
    assert "Deficit Level 1 Claim 0" in justification
    assert "Deficit Level 1 Claim 1" in justification
    assert "Deficit Level 1 Claim 2" in justification

    # 2 Level 2 claims must be present
    assert "Deficit Level 2 Claim 0" in justification
    assert "Deficit Level 2 Claim 1" in justification

    # Level 5 claims must NOT be present (discarded due to lower priority)
    assert "Deficit Level 5" not in justification


def test_assemble_matrices_to_explain_short_quote_filtering() -> None:
    """Verify quotes < 15 characters are excluded from SUPPORTING EVIDENCE."""
    block_id = "blk_999999999999999999999999"

    dtos = [
        StepOutputDTO(
            step_id="step1",
            block_id=block_id,
            data_type="matrix",
            payload={
                "normalized_score": 80.0,
                "results": [
                    {
                        "tda_id": "a1",
                        "status": "PASSED",
                        "evaluation_reasoning": "Reason",
                        "source_quote": "yes",  # 3 chars < 15
                        "depends_on_tda_ids": [],
                        "short_circuit_reason_tda_ids": [],
                    },
                    {
                        "tda_id": "a2",
                        "status": "PASSED",
                        "evaluation_reasoning": "Reason",
                        "source_quote": "This is a sufficiently long valid quote from document.",
                        "depends_on_tda_ids": [],
                        "short_circuit_reason_tda_ids": [],
                    },
                ],
                "evaluated_atoms": {
                    "a1": ExecutionStatus.PASSED,
                    "a2": ExecutionStatus.PASSED,
                },
            },
        )
    ]

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
                label=I18nText(
                    default_locale="en", translations={"en": "English Criteria Name", "fi": "Suomalainen Kriteeri"}
                ),
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

    dtos = [
        StepOutputDTO(
            step_id="step1",
            block_id=block_id,
            data_type="matrix",
            payload={
                "normalized_score": 25.0,
                "results": [
                    {
                        "tda_id": tda_id,
                        "status": "FAILED",
                        "evaluation_reasoning": "Reason",
                        "source_quote": None,
                        "depends_on_tda_ids": [],
                        "short_circuit_reason_tda_ids": [],
                    }
                ],
                "evaluated_atoms": {tda_id: ExecutionStatus.FAILED},
            },
        )
    ]

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


def test_assemble_matrices_to_explain_corrupt_level_stats_graceful_handling() -> None:
    """Verify malformed level stats are logged and skipped without crashing."""
    block_id = "blk_bbbbbbbbbbbbbbbbbbbbbbbb"

    dtos = [
        StepOutputDTO(
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

    result = MatrixExplanationService.assemble_matrices_to_explain(
        dtos, title_map={}, blocks_by_id=blocks_by_id, target_locale="en"
    )

    assert len(result) == 1
    justification = result[0].justification
    assert "[DISTRIBUTION CONTEXT: Level 1: 3/3 hits, Level 3: 1/2 hits]" in justification


def test_assemble_matrices_to_explain_with_synthesis_config_profile_overrides() -> None:
    """PROMISE: Verify synthesis_config profile overrides for max_quotes_per_matrix and max_unmet_criteria."""
    block_id = "blk_11112222333344445555666677778888"

    scale = MatrixScale(
        score=1,
        ai_label="OVERRIDE_SCALE",
        claims=[
            MatrixClaim(
                label=I18nText(default_locale="en", translations={"en": f"Claim {i}"}),
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

    dtos = [
        StepOutputDTO(
            step_id="step1",
            block_id=block_id,
            data_type="matrix",
            payload={
                "normalized_score": 60.0,
                "results": results,
                "evaluated_atoms": evaluated_atoms,
            },
        )
    ]

    blocks_by_id = {block_id: _create_matrix_block(block_id=block_id, scales=[scale])}

    # Override: max_quotes_per_matrix = 2, max_unmet_criteria = 1
    synthesis_config = SynthesisConfigDTO(
        max_quotes_per_matrix=2,
        max_unmet_criteria=1,
    )

    result = MatrixExplanationService.assemble_matrices_to_explain(
        dtos, title_map={}, blocks_by_id=blocks_by_id, target_locale="en", synthesis_config=synthesis_config
    )

    assert len(result) == 1
    justification = result[0].justification
    # Verify quotes count is capped at 2
    quote_count = justification.count('- "')
    assert quote_count == 2

    # Verify unmet count is capped at 1
    unmet_count = justification.count("- Claim ")
    assert unmet_count == 1
