"""Regression tests for Tier 4 bug: Matrix Summary Table 'Jakauma' distribution values.

Bug 1 (Toulmin Model):
In Track B diagnostic matrices (such as Toulmin's Argumentation Model), Levels 1 & 2
contain exclusively inverse error radar assertions (inverse_evidence=True).
In matrix_hook.py, block_scale_stats[s_val].total is only incremented for affirmative claims.
Consequently, block_scale_stats for Levels 1 & 2 remains total=0, hits=0, causing
MatrixDomainParser to render '0/0' in the Jakauma column.

Bug 2 (Causal Cohesion Model):
CausalCohesionEvaluator constructs level_stats with float values:
hits=1.0, total=1.0, and keys str(float(lvl)) ('1.0').
MatrixDomainParser string-interpolates f"{hits}/{total}", rendering '1.0/1.0' and '0.0/1.0'
on Dumb Painter frontend surfaces.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    GlobalContextVarsDTO,
    HookDependencies,
    HookState,
)
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.matrix import MatrixClaim, MatrixScale, TDAAssertion
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock
from backend_v2.models.domain.step import Step
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.atom_result import AtomResultDTO
from backend_v2.models.dtos.causal_discovery import AntiFluffAuditDTO
from backend_v2.models.dtos.lightweight_matrix import LevelStatsDTO
from backend_v2.models.enums import ExecutionStatus, PromptBlockCategory, ReportMatrixColumn
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.services.matrix_domain_parser import MatrixDomainParser
from backend_v2.services.orchestrator.causal_cohesion_evaluator import (
    CausalCohesionEvaluator,
)
from backend_v2.settings import get_settings
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


def test_causal_cohesion_evaluator_emits_integer_level_stats() -> None:
    """RED TEST: CausalCohesionEvaluator MUST emit integer hits/totals and clean keys.

    Floats like 1.0 or 0.0 directly leak into SDUI distribution strings as '1.0/1.0'.
    """
    settings = get_settings()
    evaluator = CausalCohesionEvaluator()
    audit = AntiFluffAuditDTO(
        isolated_concept_count=2,
        cycle_detected=False,
        unsupported_claims_count=0,
        logical_cohesion_score=0.92,
        detected_hollow_terms=[],
    )

    result = evaluator.evaluate_causal_cohesion(
        audit=audit,
        total_nodes=50,
        strictness_level=70,
        matrix_block_id=settings.causal_cohesion_matrix_block_id,
    )

    assert result.matrix_output.level_breakdown is not None

    for lvl_key, stats in result.matrix_output.level_breakdown.items():
        # Keys must not contain trailing float zeros like '1.0'
        assert "." not in lvl_key, f"Level key '{lvl_key}' should be an integer string like '1', not '1.0'"
        # Hits and total must be integer types, not floats
        assert isinstance(stats.hits, int), f"Level {lvl_key} hits={stats.hits} should be int, not float"
        assert isinstance(stats.total, int), f"Level {lvl_key} total={stats.total} should be int, not float"


def test_matrix_domain_parser_formats_float_level_stats_as_clean_integers() -> None:
    """RED TEST: MatrixDomainParser MUST format whole-number floats as clean integers.

    f"{1.0}/{1.0}" evaluates to "1.0/1.0". The parser must format integer-valued
    floats as "1/1" and "0/1" so the Flutter Dumb Painter receives clean strings.
    """
    pb_id = "blk_c0a1e50000000001"
    pb = MatrixPromptBlock.model_validate(
        {
            "id": pb_id,
            "slug": "causal_cohesion",
            "label": {"translations": {"en": "Causal Cohesion", "fi": "Kausaalinen eheys"}},
            "description": {"translations": {"en": "Desc", "fi": "Kuvaus"}},
            "type": "float",
            "category_id": PromptBlockCategory.MATRIX.value,
            "ai_description": "Assess cohesion.",
            "scales": [
                {
                    "score": 1,
                    "ai_label": "Level 1",
                    "name": {"translations": {"fi": "Heikko", "en": "Poor"}},
                    "claims": [],
                },
                {
                    "score": 2,
                    "ai_label": "Level 2",
                    "name": {"translations": {"fi": "Välttävä", "en": "Fair"}},
                    "claims": [],
                },
            ],
        }
    )

    profile = OutputProfile.model_validate(
        {
            "id": "prof_0123456789abcdef0123456789abcdef",
            "slug": "test_profile",
            "name": {"translations": {"en": "Test Profile"}},
            "workflow_id": "wor_0123456789abcdef0123456789abcdef",
            "organization_id": "root",
            "matrix_visible_columns": [ReportMatrixColumn.LABEL.value, ReportMatrixColumn.DISTRIBUTION.value],
            "target_block_order": [],
            "matrix_synthesis_groups": [],
        }
    )

    # Payload with float string keys and integer counts (testing float key normalization)
    payload = {
        "raw_score": 2.0,
        "normalized_score": 40.0,
        "evaluated_atoms": {},
        "level_breakdown": {
            "1.0": {"hits": 1, "total": 1, "dlqs": 0},
            "2.0": {"hits": 0, "total": 1, "dlqs": 0},
        },
    }

    class MockStepResult:
        def __init__(self, step_id: str, block_id: str, payload: dict) -> None:
            self.step_id = step_id
            self.block_id = block_id
            self.payload = payload

    step_res = MockStepResult(step_id="step_eval", block_id=pb_id, payload=payload)

    parsed = MatrixDomainParser.parse_matrices(
        results=[step_res],
        locale="fi",
        blocks_by_id={pb_id: pb},
        workflow_steps={},
        profile=profile,
        row_explanations_cache={},
        workflow_ext_values=[],
        row_curated_quotes_cache={},
    )

    row = parsed.all_parsed_matrices[f"step_eval_{pb_id}"]
    assert row.level_breakdown is not None
    # Must format as "1/1" and "0/1", NOT "1.0/1.0" or "0.0/1.0"
    assert row.level_breakdown == {"1": "1/1", "2": "0/1"}


@pytest.mark.asyncio
async def test_track_b_matrix_hook_level_breakdown_non_zero_denominator() -> None:
    """RED TEST: Track B diagnostic matrix (Toulmin) MUST NOT report '0/0' denominator.

    In Toulmin's model, Scale 1 has 3 inverse assertions and Scale 2 has 5 inverse assertions.
    The empirical distribution in level_breakdown MUST reflect the total configured assertions
    (N=3 for Scale 1, N=5 for Scale 2), NOT total=0.
    """
    from backend_v2.hooks.scoring.matrix_hook import matrix_scoring_hook

    pb_id = "blk_440a5fef9331451b"
    tda_ids_lvl1 = [f"tda_11{i:030x}" for i in range(1, 4)]  # 3 assertions
    tda_ids_lvl2 = [f"tda_22{i:030x}" for i in range(1, 6)]  # 5 assertions

    claims_lvl1 = [
        MatrixClaim(
            label=I18nText(translations={"fi": f"Virhedetektori 1.{i}", "en": f"Error detector 1.{i}"}),
            tda_assertions=[
                TDAAssertion(
                    tda_id=tid,
                    concept_description=f"Defect 1.{i}",
                    inverse_evidence=True,
                    aggregation_mode="EXISTS",
                )
            ],
        )
        for i, tid in enumerate(tda_ids_lvl1, 1)
    ]

    claims_lvl2 = [
        MatrixClaim(
            label=I18nText(translations={"fi": f"Virhedetektori 2.{i}", "en": f"Error detector 2.{i}"}),
            tda_assertions=[
                TDAAssertion(
                    tda_id=tid,
                    concept_description=f"Defect 2.{i}",
                    inverse_evidence=True,
                    aggregation_mode="EXISTS",
                )
            ],
        )
        for i, tid in enumerate(tda_ids_lvl2, 1)
    ]

    scales = [
        MatrixScale(
            score=1,
            ai_label="Level 1",
            name=I18nText(translations={"fi": "Heikko", "en": "Poor"}),
            claims=claims_lvl1,
        ),
        MatrixScale(
            score=2,
            ai_label="Level 2",
            name=I18nText(translations={"fi": "Välttävä", "en": "Fair"}),
            claims=claims_lvl2,
        ),
    ]

    pb = MatrixPromptBlock.model_validate(
        {
            "id": pb_id,
            "slug": "matrix_toulmin",
            "label": {"translations": {"fi": "Toulminin Argumentaatiomalli", "en": "Toulmin Argumentation Model"}},
            "description": {"translations": {"fi": "Toulmin kuvaus", "en": "Toulmin description"}},
            "type": "float",
            "category_id": PromptBlockCategory.MATRIX.value,
            "ai_description": "Toulmin audit.",
            "scales": scales,
        }
    )

    wf_id = "wor_1111222233334444"
    step_id = "stp_1111222233334444"
    profile_id = "prof_1111222233334444"
    execution_id = "exe_1111222233334444"

    step = Step.model_validate(
        {
            "id": step_id,
            "slug": "toulmin_step",
            "name": {"translations": {"en": "Toulmin Step", "fi": "Toulmin vaihe"}},
            "type": "logic",
            "hook": "matrix_scoring_hook",
            "criteria_block_ids": [pb_id],
        }
    )

    wf = Workflow.model_validate(
        {
            "id": wf_id,
            "slug": "toulmin_wf",
            "name": {"translations": {"en": "Toulmin WF", "fi": "Toulmin WF"}},
            "description": {"translations": {"en": "Toulmin workflow", "fi": "Toulmin työnkulku"}},
            "status": "active",
            "version": 1,
            "default_profile_id": profile_id,
            "default_strictness_level": 50,
            "enable_contextual_overrides": True,
            "model_registry_id": "cfg_model_registry_01",
            "historical_context_mode": "DISABLED",
        }
    )

    now = datetime.now(timezone.utc)
    exec_rec = ExecutionRecord.model_validate(
        {
            "id": execution_id,
            "workflow_id": wf_id,
            "organization_id": "org_1111222233334444",
            "created_by": "usr_1111222233334444",
            "output_profile_id": profile_id,
            "status": "RUNNING",
            "target_locale": "fi",
            "created_at": now,
            "updated_at": now,
        }
    )

    profile = OutputProfile.model_validate(
        {
            "id": profile_id,
            "slug": "toulmin_profile",
            "workflow_id": wf_id,
            "name": {"translations": {"en": "Toulmin Profile", "fi": "Toulmin profiili"}},
            "matrix_synthesis_groups": [
                {
                    "id": "grp_1111222233334444",
                    "title": {"translations": {"en": "Toulmin Group", "fi": "Toulmin ryhmä"}},
                    "target_blocks": [pb_id],
                }
            ],
            "display_scale": "original",
        }
    )

    repo = InMemoryUnifiedWorkflowRepository()
    repo._workflows._steps[step_id] = step
    repo._workflows._save_isolated(wf_id, wf)
    repo._prompt_blocks._save_isolated(pb_id, pb)
    repo._executions._save_isolated(execution_id, exec_rec)
    repo._output_profiles._save_isolated(profile_id, profile)

    deps = HookDependencies(
        exec_repo=repo,
        workflow_repo=repo,
        comp_repo=repo,
        prompt_block_repo=repo,
        output_profile_repo=repo,
        identity_repo=repo,
        system_repo=repo,
    )

    # Simulate evaluation: all 3 in Level 1 passed (no defects), all 5 in Level 2 passed (no defects)
    evaluations = [
        AtomResultDTO(
            tda_id=tid,
            status=ExecutionStatus.PASSED,
            evaluation_reasoning=f"Clean for {tid}",
            is_inverse_evidence=True,
        )
        for tid in tda_ids_lvl1 + tda_ids_lvl2
    ]

    state = HookState(
        execution_id=execution_id,
        workflow_id=wf_id,
        step_id=step_id,
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"results": evaluations}),
        global_context_vars=GlobalContextVarsDTO(),
    )

    res = await matrix_scoring_hook(state, deps)
    assert res.success is True
    delta = res.state_delta.delta
    assert delta is not None
    matrix_output = delta.matrix_outputs[pb_id]

    assert matrix_output.level_breakdown is not None
    # Level 1 breakdown must reflect N=3 configured assertions, NOT total=0
    l1_stats = matrix_output.level_breakdown["1"]
    assert l1_stats is not None
    assert l1_stats.total == 3, f"Level 1 configured total should be 3, but got {l1_stats.total} (causing 0/0 in UI)"

    # Level 2 breakdown must reflect N=5 configured assertions, NOT total=0
    l2_stats = matrix_output.level_breakdown["2"]
    assert l2_stats is not None
    assert l2_stats.total == 5, f"Level 2 configured total should be 5, but got {l2_stats.total} (causing 0/0 in UI)"


def test_level_stats_dto_rejects_floats() -> None:
    """ISTQB Gate: LevelStatsDTO MUST strictly reject float counts under ConfigDict(strict=True)."""
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        LevelStatsDTO.model_validate({"hits": 1.0, "total": 1})

    with pytest.raises(ValidationError):
        LevelStatsDTO.model_validate({"hits": 1, "total": 1.0})

    with pytest.raises(ValidationError):
        LevelStatsDTO.model_validate({"hits": 1.5, "total": 2})

    with pytest.raises(ValidationError):
        LevelStatsDTO.model_validate({"hits": 1, "total": 2.0})


def test_defect_warning_formatting_singular_vs_plural() -> None:
    """Model B Rule 2: Pure Error Radar formatting with singular/plural defect inflection."""
    # Clean radar (0 defects)
    clean_stat = LevelStatsDTO(hits=3, total=3, dlqs=0, pos_hits=0, pos_total=0, inv_clean=3, inv_total=3)
    assert MatrixDomainParser._format_level_distribution(clean_stat, "fi") == "puhtaus 3/3"
    assert MatrixDomainParser._format_level_distribution(clean_stat, "en") == "purity 3/3"

    # 1 defect (singular)
    one_defect = LevelStatsDTO(hits=2, total=3, dlqs=0, pos_hits=0, pos_total=0, inv_clean=2, inv_total=3)
    assert MatrixDomainParser._format_level_distribution(one_defect, "fi") == "puhtaus 2/3 (⚠️ 1 virhe)"
    assert MatrixDomainParser._format_level_distribution(one_defect, "en") == "purity 2/3 (⚠️ 1 defect)"

    # 2 defects (plural)
    two_defects = LevelStatsDTO(hits=1, total=3, dlqs=0, pos_hits=0, pos_total=0, inv_clean=1, inv_total=3)
    assert MatrixDomainParser._format_level_distribution(two_defects, "fi") == "puhtaus 1/3 (⚠️ 2 virhettä)"
    assert MatrixDomainParser._format_level_distribution(two_defects, "en") == "purity 1/3 (⚠️ 2 defects)"


def test_hybrid_and_capability_level_formatting() -> None:
    """Model B Rules 1, 3, 5: Pure Capability, Hybrid, and Unpartitioned formatting."""
    # Rule 1: Pure capability multi-criterion (N_pos > 1)
    multi_cap = LevelStatsDTO(hits=3, total=4, dlqs=0, pos_hits=3, pos_total=4, inv_clean=0, inv_total=0)
    assert MatrixDomainParser._format_level_distribution(multi_cap, "fi") == "3/4 taitoa"
    assert MatrixDomainParser._format_level_distribution(multi_cap, "en") == "3/4 skills"

    # Rule 1: Pure capability single-criterion (N_pos == 1, BARS threshold)
    single_cap = LevelStatsDTO(hits=1, total=1, dlqs=0, pos_hits=1, pos_total=1, inv_clean=0, inv_total=0)
    assert MatrixDomainParser._format_level_distribution(single_cap, "fi") == "1/1"
    assert MatrixDomainParser._format_level_distribution(single_cap, "en") == "1/1"

    # Rule 3: Hybrid level clean
    hybrid_clean = LevelStatsDTO(hits=4, total=4, dlqs=0, pos_hits=2, pos_total=2, inv_clean=2, inv_total=2)
    assert MatrixDomainParser._format_level_distribution(hybrid_clean, "fi") == "2/2 taitoa, puhtaus 2/2"
    assert MatrixDomainParser._format_level_distribution(hybrid_clean, "en") == "2/2 skills, purity 2/2"

    # Rule 3: Hybrid level with 1 defect and single positive skill
    hybrid_defect = LevelStatsDTO(hits=2, total=3, dlqs=0, pos_hits=1, pos_total=1, inv_clean=1, inv_total=2)
    assert MatrixDomainParser._format_level_distribution(hybrid_defect, "fi") == "1/1, puhtaus 1/2 (⚠️ 1 virhe)"
    assert MatrixDomainParser._format_level_distribution(hybrid_defect, "en") == "1/1, purity 1/2 (⚠️ 1 defect)"

    # Rule 5: Unpartitioned counts
    unpartitioned = LevelStatsDTO(hits=1, total=2, dlqs=0, pos_hits=0, pos_total=0, inv_clean=0, inv_total=0)
    assert MatrixDomainParser._format_level_distribution(unpartitioned, "fi") == "1/2"
    assert MatrixDomainParser._format_level_distribution(unpartitioned, "en") == "1/2"


def test_matrix_domain_parser_rejects_invalid_level_key() -> None:
    """Fail-Fast: MatrixDomainParser MUST raise AppException on non-numeric level keys."""
    from backend_v2.exceptions import AppException, ErrorCodes

    pb_id = "blk_c0a1e50000000001"
    pb = MatrixPromptBlock.model_validate(
        {
            "id": pb_id,
            "slug": "test_matrix",
            "label": {"translations": {"en": "Test", "fi": "Testi"}},
            "description": {"translations": {"en": "Desc", "fi": "Kuvaus"}},
            "type": "float",
            "category_id": PromptBlockCategory.MATRIX.value,
            "ai_description": "Test.",
            "scales": [
                {"score": 1, "ai_label": "L1", "name": {"translations": {"en": "L1", "fi": "L1"}}, "claims": []}
            ],
        }
    )
    profile = OutputProfile.model_validate(
        {
            "id": "prof_0123456789abcdef0123456789abcdef",
            "slug": "test_profile",
            "name": {"translations": {"en": "Test Profile"}},
            "workflow_id": "wor_0123456789abcdef0123456789abcdef",
            "organization_id": "root",
            "matrix_visible_columns": [ReportMatrixColumn.LABEL.value, ReportMatrixColumn.DISTRIBUTION.value],
            "target_block_order": [],
            "matrix_synthesis_groups": [],
        }
    )

    class MockStepResult:
        def __init__(self, step_id: str, block_id: str, payload: dict) -> None:
            self.step_id = step_id
            self.block_id = block_id
            self.payload = payload

    step_res = MockStepResult(
        step_id="step_eval",
        block_id=pb_id,
        payload={
            "raw_score": 1.0,
            "level_breakdown": {"invalid_level_str": {"hits": 1, "total": 1, "dlqs": 0}},
        },
    )

    with pytest.raises(AppException) as exc_info:
        MatrixDomainParser.parse_matrices(
            results=[step_res],
            locale="fi",
            blocks_by_id={pb_id: pb},
            workflow_steps={},
            profile=profile,
            row_explanations_cache={},
            workflow_ext_values=[],
            row_curated_quotes_cache={},
        )
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
