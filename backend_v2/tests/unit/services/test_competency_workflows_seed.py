"""Unit test suite for modular competency workflows and output profiles in seed_data.json.

Verifies DAG topology, dynamic input routing, bilingual descriptions, preset views,
baseline workflow non-regression, and ISTQB negative boundary conditions.
"""

import json
import re
from pathlib import Path
from typing import Any

import pydantic
import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException, WorkflowCompilationError
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.step import ExpectedInput, Step
from backend_v2.models.domain.synthesis import MatrixSynthesisGroup
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.enums import PresetView
from backend_v2.services.orchestrator.dag_compiler import DAGCompilerService

SEED_DATA_PATH = Path("backend_v2/seed/seed_data.json")

EXPECTED_WORKFLOW_IDS = [
    "wf_9d68c573802341db",  # Monolithic baseline (preservation mandate)
    "wf_a8f1d71000000001",  # Targeted AI Steering & Argumentation Audit
    "wf_b9e2d71000000002",  # AI Steering & Cognitive Core Audit
]

COMPETENCY_WORKFLOW_IDS = [
    "wf_a8f1d71000000001",
    "wf_b9e2d71000000002",
]

EXPECTED_PROFILE_IDS = [
    "prf_5d6e7f8091a2b3c4",  # Monolithic baseline profile
    "prf_a8f1d71000000001",  # Targeted AI Steering profile
    "prf_b9e2d71000000002",  # AI Steering Cognitive Core profile
]


def load_seed_data() -> Any:
    """Load raw seed_data.json from workspace.

    Returns:
        Complete seed data dictionary containing collections.
    """
    assert SEED_DATA_PATH.exists(), f"Seed data file missing: {SEED_DATA_PATH}"
    with open(SEED_DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return data


# --- Positive Tests ---


def test_baseline_monolithic_workflow_preserved() -> None:
    """Verify that the baseline monolithic workflow and profile conform to the 12-step 3-zone architecture.

    Ensures mathematical topology and output profile group invariants for wf_9d68c573802341db
    and prf_5d6e7f8091a2b3c4.
    """
    seed_data = load_seed_data()
    workflows = {w["id"]: w for w in seed_data["workflows"]}
    profiles = {p["id"]: p for p in seed_data["output_profiles"]}

    assert "wf_9d68c573802341db" in workflows, "Baseline monolithic workflow wf_9d68c573802341db missing"
    assert "prf_5d6e7f8091a2b3c4" in profiles, "Baseline monolithic profile prf_5d6e7f8091a2b3c4 missing"

    mono_wf = Workflow.model_validate(workflows["wf_9d68c573802341db"])
    mono_prf = OutputProfile.model_validate(profiles["prf_5d6e7f8091a2b3c4"])

    assert mono_wf.slug == "kokonaisvaltainen_auditointi"
    assert mono_wf.default_profile_id == "prf_5d6e7f8091a2b3c4"
    assert mono_prf.workflow_id == "wf_9d68c573802341db"

    # 1. Exact 14-step topology and 7 matrix groups
    assert len(mono_wf.steps) == 14, f"Expected exactly 14 steps in monolith workflow, got {len(mono_wf.steps)}"
    assert len(mono_prf.matrix_synthesis_groups) == 7, (
        f"Expected exactly 7 matrix synthesis groups, got {len(mono_prf.matrix_synthesis_groups)}"
    )
    assert "printable_sources_block" not in mono_prf.target_block_order, (
        "printable_sources_block must be excluded from target_block_order"
    )
    assert mono_prf.show_sources_summary_box is False, "show_sources_summary_box must be False"

    # 2. Assert pruned step IDs are absent
    pruned_step_ids = {
        "sr_0f7947ec7007498c",  # OWASP LLM Guard
        "sr_99ca8c82a5aa48cd",  # Pearl & Mackenzie Profiler
        "sr_1d7e6d26b02b457b",  # ARMA Performativity Detector
        "sr_ba028623acab447a",  # Deming Judge
    }
    step_ids = {s.id for s in mono_wf.steps}
    for pruned_id in pruned_step_ids:
        assert pruned_id not in step_ids, f"Pruned step {pruned_id} must be absent from monolith workflow"

    # 3. Assert Zone B specialist dependencies and input mappings
    ingress_id = "sr_f0a26d17cc9b48a7"
    zone_b_step_ids = {
        "sr_5a8ae009eee44fe2",  # Analyst (Kahneman)
        "sr_87f408aeee64462f",  # Logician (Toulmin)
        "sr_d56fb84fbe13463a",  # Falsifier (Popper)
        "sr_4d2272d8b4864847",  # Causal Analyst (Pearl)
        "sr_02b7cc1e7c2a4a62",  # Fact-Checker (Tetlock)
        "sr_566e3209a60444d3",  # Evaluator (Bloom)
        "sr_0228db320e8f41bb",  # Coach (Goodhart)
        "sr_b4c328df1c4141c6",  # Critic (Lipton)
        "sr_f1c1d71000000002",  # AI Steering Evaluator
    }
    assert zone_b_step_ids.issubset(step_ids), f"Missing Zone B steps: {zone_b_step_ids - step_ids}"

    for step in mono_wf.steps:
        if step.id in zone_b_step_ids:
            expected_deps = (
                [ingress_id, "sr_c4a5a1d15c00438a"]
                if step.id in ("sr_4d2272d8b4864847", "sr_f1c1d71000000002")
                else [ingress_id]
            )
            assert step.depends_on == expected_deps, (
                f"Zone B step {step.id} must depend strictly on {expected_deps}, got {step.depends_on}"
            )
            assert "prior_analysis" not in step.input_mappings, f"Zone B step {step.id} must not map prior_analysis"

    # 4. Assert Zone C XAI reporter depends on all 9 Zone B steps
    xai_step = next(s for s in mono_wf.steps if s.id == "sr_5f3dd7712a7f4bb3")
    assert set(xai_step.depends_on) == zone_b_step_ids, (
        "XAI reporter sr_5f3dd7712a7f4bb3 must depend on all 9 Zone B specialists"
    )

    # 5. Assert all 7 matrix synthesis groups have valid grp_ IDs and exact cardinalities
    expected_group_cardinalities: dict[PresetView | str, int] = {
        PresetView.METRICS_1D: 1,
        PresetView.COMPARE_2D: 2,
        PresetView.MATRIX_3D: 3,
        PresetView.METRICS_1D.value: 1,
        PresetView.COMPARE_2D.value: 2,
        PresetView.MATRIX_3D.value: 3,
    }
    grp_id_pattern = re.compile(r"^grp_[a-f0-9]{16}$")
    for grp in mono_prf.matrix_synthesis_groups:
        assert grp_id_pattern.match(grp.id), f"Group ID {grp.id} does not match ^grp_[a-f0-9]{{16}}$"
        expected_count = expected_group_cardinalities[grp.view_type]
        assert len(grp.target_blocks) == expected_count, (
            f"Group {grp.id} ({grp.view_type}) requires {expected_count} target_blocks, got {len(grp.target_blocks)}"
        )


def test_all_competency_workflows_exist_and_validate() -> None:
    """Verify all 5 modular competency workflows exist in seed_data.json and validate against Pydantic V2."""
    seed_data = load_seed_data()
    workflows = {w["id"]: w for w in seed_data["workflows"]}

    for wf_id in COMPETENCY_WORKFLOW_IDS:
        assert wf_id in workflows, f"Competency workflow {wf_id} missing from seed_data.json"
        raw_wf = workflows[wf_id]
        wf_model = Workflow.model_validate(raw_wf)
        assert wf_model.id == wf_id
        assert len(wf_model.steps) >= 4, f"Workflow {wf_id} must contain at least 4 steps"
        assert len(wf_model.expected_inputs) >= 2, f"Workflow {wf_id} must specify at least 2 expected_inputs"


def test_competency_workflows_dag_acyclicity() -> None:
    """Verify Kahn's wave topological DAG compilation for all 5 competency workflows."""
    seed_data = load_seed_data()
    workflows = {w["id"]: w for w in seed_data["workflows"]}

    for wf_id in COMPETENCY_WORKFLOW_IDS:
        raw_wf = workflows[wf_id]
        wf_model = Workflow.model_validate(raw_wf)
        # Validate DAG graph topology
        DAGCompilerService.validate_workflow(wf_model)


def test_bilingual_descriptions_quality_gate() -> None:
    """Verify that all 5 competency workflows provide rich bilingual descriptions (min 50 chars)."""
    seed_data = load_seed_data()
    workflows = {w["id"]: w for w in seed_data["workflows"]}

    for wf_id in COMPETENCY_WORKFLOW_IDS:
        raw_wf = workflows[wf_id]
        wf_model = Workflow.model_validate(raw_wf)

        # Validate name translations
        assert isinstance(wf_model.name, I18nText), f"Workflow {wf_id} name must be I18nText"
        assert "fi" in wf_model.name.translations and "en" in wf_model.name.translations
        assert len(wf_model.name.translations["fi"]) >= 5
        assert len(wf_model.name.translations["en"]) >= 5

        # Validate description translations
        assert isinstance(wf_model.description, I18nText), f"Workflow {wf_id} description must be I18nText"
        assert "fi" in wf_model.description.translations and "en" in wf_model.description.translations
        fi_desc = wf_model.description.translations["fi"]
        en_desc = wf_model.description.translations["en"]
        assert len(fi_desc) >= 50, f"Workflow {wf_id} Finnish description too short (<50 chars)"
        assert len(en_desc) >= 50, f"Workflow {wf_id} English description too short (<50 chars)"


def test_ai_description_compiler_xml_sovereignty() -> None:
    """Verify that ai_description fields in expected_inputs do NOT contain raw XML tags."""
    seed_data = load_seed_data()
    workflows = {w["id"]: w for w in seed_data["workflows"]}

    for wf_id in COMPETENCY_WORKFLOW_IDS:
        wf_model = Workflow.model_validate(workflows[wf_id])
        for ei in wf_model.expected_inputs:
            assert ei.ai_description is not None, f"ExpectedInput {ei.input_key} in {wf_id} lacks ai_description"
            desc: str = ei.ai_description
            assert "<" not in desc and ">" not in desc, f"Raw XML tag detected in ai_description for {ei.input_key}"
            assert len(desc) >= 20, f"ai_description for {ei.input_key} must be descriptive (>=20 chars)"


FINNISH_PROMPT_MARKERS = [
    "Toimi ",
    " ja ",
    "tarkastajana",
    "auditoijana",
    "valmentajana",
    "sparraajana",
]


def test_output_profiles_binding_and_preset_views() -> None:
    """Verify output profile 1:1 workflow bindings, tone instructions, and valid PresetView enum views."""
    seed_data = load_seed_data()
    profiles = {p["id"]: p for p in seed_data["output_profiles"]}

    for prf_id in EXPECTED_PROFILE_IDS:
        assert prf_id in profiles, f"OutputProfile {prf_id} missing from seed_data.json"
        prf_model = OutputProfile.model_validate(profiles[prf_id])
        assert prf_model.id == prf_id
        assert prf_model.workflow_id is not None
        assert prf_model.tone_instruction is not None
        assert len(prf_model.tone_instruction) >= 10, f"Tone instruction in {prf_id} must be >=10 chars"
        for marker in FINNISH_PROMPT_MARKERS:
            assert marker.lower() not in prf_model.tone_instruction.lower(), (
                f"Finnish marker '{marker}' found in {prf_id} tone_instruction. "
                f"All prompt directives must be in English per 05_llm_architecture.md."
            )

        # Verify bilingual custom preface completeness
        assert prf_model.custom_preface is not None, f"Profile {prf_id} must define custom_preface"
        assert isinstance(prf_model.custom_preface, I18nText)
        translations = prf_model.custom_preface.translations
        assert "fi" in translations and "en" in translations, f"Profile {prf_id} preface must be bilingual"
        assert len(translations["fi"]) >= 150, f"Profile {prf_id} Finnish preface must be rich (>=150 chars)"
        assert len(translations["en"]) >= 150, f"Profile {prf_id} English preface must be rich (>=150 chars)"

        # Validate matrix synthesis group view_type strings against PresetView enum
        for group in prf_model.matrix_synthesis_groups:
            assert group.view_type in [v.value for v in PresetView], (
                f"Invalid view_type {group.view_type} in {prf_id}. Must be valid PresetView."
            )


def test_output_profiles_criteria_column_absent_in_seed_defaults() -> None:
    """Verify that 'criteria' is absent from matrix_visible_columns across all 3 default seed profiles."""
    seed_data = load_seed_data()
    profiles = {p["id"]: p for p in seed_data["output_profiles"]}

    for prf_id in EXPECTED_PROFILE_IDS:
        assert prf_id in profiles, f"OutputProfile {prf_id} missing from seed_data.json"
        prf_model = OutputProfile.model_validate(profiles[prf_id])
        assert "criteria" not in prf_model.matrix_visible_columns, (
            f"Profile '{prf_id}' must NOT contain 'criteria' in matrix_visible_columns"
        )
        assert prf_model.matrix_visible_columns == [
            "label",
            "distribution",
            "row_explanation",
            "normalized_score",
        ], f"Profile '{prf_id}' matrix_visible_columns mismatch"


def test_default_seed_profiles_baseline_uniformity() -> None:
    """Verify that all 3 default seed profiles share identical baseline configuration."""
    seed_data = load_seed_data()
    profiles = {p["id"]: p for p in seed_data["output_profiles"]}

    baseline_prf = OutputProfile.model_validate(profiles["prf_5d6e7f8091a2b3c4"])

    for prf_id in ["prf_a8f1d71000000001", "prf_b9e2d71000000002"]:
        prf = OutputProfile.model_validate(profiles[prf_id])
        assert prf.visible_metadata == baseline_prf.visible_metadata
        assert prf.visible_block_extensions == baseline_prf.visible_block_extensions
        assert prf.visible_workflow_extensions == baseline_prf.visible_workflow_extensions
        assert prf.max_extension_items == 4
        assert prf.display_scale == baseline_prf.display_scale
        assert prf.target_block_order == baseline_prf.target_block_order
        assert prf.synthesis_length_constraint == 1000
        assert prf.row_explanation_length_constraint == 250
        assert prf.xai_length_constraint == 300
        assert prf.variance_length_constraint == 500
        assert prf.matrix_graph_length_constraint == 400
        assert prf.show_sources_summary_box is False
        assert prf.sources_display_mode == "verified_evidence"
        assert prf.user_role_target_block == "blk_7d8e9f0a1b2c3d4e"
        assert prf.variance_target_block == "blk_7d8e9f0a1b2c3d4e"
        assert prf.tone_instruction == baseline_prf.tone_instruction
        assert prf.executive_summary_directive == baseline_prf.executive_summary_directive
        assert prf.matrix_1d_synthesis_directive == baseline_prf.matrix_1d_synthesis_directive
        assert prf.matrix_2d_synthesis_directive == baseline_prf.matrix_2d_synthesis_directive
        assert prf.matrix_3d_synthesis_directive == baseline_prf.matrix_3d_synthesis_directive
        assert prf.matrix_text_synthesis_directive == baseline_prf.matrix_text_synthesis_directive
        assert prf.row_explanation_directive == baseline_prf.row_explanation_directive
        assert prf.xai_synthesis_directive == baseline_prf.xai_synthesis_directive
        assert prf.variance_synthesis_directive == baseline_prf.variance_synthesis_directive


def test_dynamic_profile_configurability_invariant() -> None:
    """Verify TC-PRF-002: Dynamic Profile Configurability Invariant.

    Custom profiles may include 'criteria' and custom block orders without code-level restriction.
    """
    custom_profile_payload = {
        "id": "prf_c1d2e3f400000001",
        "slug": "custom_evaluation_profile",
        "workflow_id": "wf_9d68c573802341db",
        "name": {"translations": {"fi": "Mukautettu profiili", "en": "Custom Profile"}},
        "matrix_visible_columns": ["label", "criteria", "distribution", "normalized_score"],
        "target_block_order": ["matrix_summary_table_block"],
        "matrix_synthesis_groups": [],
    }
    custom_prf = OutputProfile.model_validate(custom_profile_payload)
    assert "criteria" in custom_prf.matrix_visible_columns
    assert custom_prf.matrix_visible_columns == ["label", "criteria", "distribution", "normalized_score"]


def test_baseline_profile_custom_preface_not_truncated() -> None:
    """Verify baseline profile prf_5d6e7f8091a2b3c4 English preface is complete without ellipsis."""
    seed_data = load_seed_data()
    profiles = {p["id"]: p for p in seed_data["output_profiles"]}
    prf = OutputProfile.model_validate(profiles["prf_5d6e7f8091a2b3c4"])
    assert prf.custom_preface is not None
    en_preface = prf.custom_preface.translations["en"]
    assert not en_preface.strip().endswith("..."), "English preface must not be truncated with ellipsis"
    assert "Insight" in en_preface
    assert "Logic & Reasoning" in en_preface or "Logic and Reasoning" in en_preface
    assert "Reliability" in en_preface
    assert len(en_preface) >= 250


def test_negative_profile_missing_custom_preface_en_rejected() -> None:
    """ISTQB Negative Test 1: OutputProfile with custom_preface missing 'en' key raises AppException."""
    seed_data = load_seed_data()
    profiles = {p["id"]: p for p in seed_data["output_profiles"]}
    raw_prf = dict(profiles["prf_5d6e7f8091a2b3c4"])
    raw_prf["custom_preface"] = {"translations": {"fi": "Pelkkä suomi"}}

    with pytest.raises((pydantic.ValidationError, AppException)) as exc_info:
        OutputProfile.model_validate(raw_prf)
    assert "English ('en') translation" in str(exc_info.value)


def test_negative_profile_finnish_tone_instruction_rejected() -> None:
    """ISTQB Negative Test 2: OutputProfile configured with Finnish prompt instruction fails language gate."""
    bad_tone = "Toimi kannustavana valmentajana."
    detected = any(marker.lower() in bad_tone.lower() for marker in FINNISH_PROMPT_MARKERS)
    assert detected is True, "Finnish prompt marker detection must catch non-English tone instruction"


def test_output_profiles_scoring_configuration() -> None:
    """Verify that all output profiles have strictness_level pruned and workflows define default_strictness_level.

    The Tripartite Phase 1 architecture mandates sovereign strictness ownership on Workflow,
    pruned from OutputProfile.
    """
    seed_data = load_seed_data()
    profiles = {p["id"]: p for p in seed_data["output_profiles"]}

    for prf_id in EXPECTED_PROFILE_IDS:
        assert prf_id in profiles, f"OutputProfile {prf_id} missing from seed_data.json"
        prf = profiles[prf_id]
        prf_model = OutputProfile.model_validate(prf)
        assert "strictness_level" not in dir(prf_model), f"Profile '{prf_id}' must not contain strictness_level"
        assert "strictness_level" not in prf, f"Raw profile '{prf_id}' must not contain strictness_level"

    workflows = {w["id"]: w for w in seed_data["workflows"]}
    for wf in workflows.values():
        wf_model = Workflow.model_validate(wf)
        assert wf_model.default_strictness_level is not None
        assert wf_model.default_strictness_level in (0, 50, 70)

    assert workflows["wf_9d68c573802341db"]["default_strictness_level"] == 0


def test_negative_profile_missing_scoring_config_detected() -> None:
    """ISTQB Negative Test: OutputProfile extra='forbid' rejects strictness_level injection."""
    seed_data = load_seed_data()
    profiles = {p["id"]: p for p in seed_data["output_profiles"]}
    raw_prf = dict(profiles["prf_5d6e7f8091a2b3c4"])

    # Test that injecting strictness_level triggers ValidationError (extra forbidden)
    corrupt_prf = dict(raw_prf)
    corrupt_prf["strictness_level"] = 50
    with pytest.raises(ValidationError):
        OutputProfile.model_validate(corrupt_prf)


# --- ISTQB Negative & Edge Case Tests ---


def test_negative_invalid_unmapped_inputs_reference_fails_dag() -> None:
    """ISTQB Negative Test 1: Step mapping referencing un-declared input key triggers DAG compilation error."""
    seed_data = load_seed_data()
    workflows = {w["id"]: w for w in seed_data["workflows"]}
    assert "wf_a8f1d71000000001" in workflows, "Workflow wf_a8f1d71000000001 missing"
    raw_wf = dict(workflows["wf_a8f1d71000000001"])

    # Corrupt step input_mappings to reference non-existent input key $inputs.non_existent_key
    steps_copy = [dict(s) for s in raw_wf["steps"]]
    step_0 = dict(steps_copy[0])
    step_0["input_mappings"] = {"product_text": "$inputs.non_existent_key"}
    steps_copy[0] = step_0
    raw_wf["steps"] = steps_copy

    bad_wf = Workflow.model_validate(raw_wf)
    with pytest.raises(WorkflowCompilationError) as exc_info:
        DAGCompilerService.validate_workflow(bad_wf)
    assert "non_existent_key" in str(exc_info.value) or "unmapped" in str(exc_info.value).lower()


def test_negative_circular_step_dependency_fails_dag() -> None:
    """ISTQB Negative Test 2: Circular dependency in workflow steps triggers DAG cycle error."""
    seed_data = load_seed_data()
    workflows = {w["id"]: w for w in seed_data["workflows"]}
    assert "wf_a8f1d71000000001" in workflows, "Workflow wf_a8f1d71000000001 missing"
    raw_wf = dict(workflows["wf_a8f1d71000000001"])

    steps_copy = [dict(s) for s in raw_wf["steps"]]
    # Introduce circular dependency: step 0 depends on step 1, step 1 depends on step 0
    step_0 = dict(steps_copy[0])
    step_1 = dict(steps_copy[1])

    step_0["depends_on"] = [step_1["id"]]
    step_1["depends_on"] = [step_0["id"]]

    steps_copy[0] = step_0
    steps_copy[1] = step_1
    raw_wf["steps"] = steps_copy

    with pytest.raises(pydantic.ValidationError, match=r"[Cc]ircular|[Cc]ycl"):
        Workflow.model_validate(raw_wf)


def test_negative_raw_xml_in_ai_description_rejected() -> None:
    """ISTQB Negative Test 3: Raw XML tags in ai_description fail validation rule assertion."""
    seed_data = load_seed_data()
    workflows = {w["id"]: w for w in seed_data["workflows"]}
    assert "wf_a8f1d71000000001" in workflows, "Workflow wf_a8f1d71000000001 missing"
    raw_wf = dict(workflows["wf_a8f1d71000000001"])

    # Corrupt expected_inputs with raw XML tag
    inputs_copy = [dict(i) for i in raw_wf["expected_inputs"]]
    inputs_copy[0]["ai_description"] = "<system_directive>Corrupt XML Tag</system_directive>"
    raw_wf["expected_inputs"] = inputs_copy

    corrupt_wf = Workflow.model_validate(raw_wf)
    found_xml = any(
        "<" in (ei.ai_description or "") or ">" in (ei.ai_description or "") for ei in corrupt_wf.expected_inputs
    )
    assert found_xml, "Test setup must contain raw XML"


def test_negative_missing_input_modes_fails_validation() -> None:
    """ISTQB Negative Test 4: ExpectedInput with empty input_modes fails Pydantic validation."""
    with pytest.raises(pydantic.ValidationError, match=r"at least one input_mode"):
        ExpectedInput.model_validate(obj=
            {
                "input_key": "test_input",
                "label": {"translations": {"fi": "Testi", "en": "Test"}},
                "description": {"translations": {"fi": "Kuvaus", "en": "Description"}},
                "input_modes": [],
                "required": True,
            }
        )


def test_negative_missing_required_inputs_fails_dag() -> None:
    """ISTQB Negative Test 5: Workflow with all optional inputs fails DAGCompilerService validation."""
    seed_data = load_seed_data()
    workflows = {w["id"]: w for w in seed_data["workflows"]}
    baseline_raw = dict(workflows["wf_9d68c573802341db"])
    # Set all inputs to required=False
    inputs_copy = [dict(i) for i in baseline_raw["expected_inputs"]]
    for inp in inputs_copy:
        inp["required"] = False
    baseline_raw["expected_inputs"] = inputs_copy

    wf = Workflow.model_validate(baseline_raw)
    with pytest.raises(AppException) as exc_info:
        DAGCompilerService.validate_workflow(wf)
    assert exc_info.value.status_code == 400
    assert "at least one input must be 'required=True'" in str(exc_info.value)


def test_negative_orphan_step_dependency_fails_dag() -> None:
    """ISTQB Negative Test 6: Step depending on non-existent step ID fails Workflow model validation."""
    seed_data = load_seed_data()
    workflows = {w["id"]: w for w in seed_data["workflows"]}
    baseline_raw = dict(workflows["wf_9d68c573802341db"])
    steps_copy = [dict(s) for s in baseline_raw["steps"]]
    steps_copy[1]["depends_on"] = ["sr_non_existent_step_id"]
    baseline_raw["steps"] = steps_copy

    with pytest.raises(pydantic.ValidationError, match=r"does not exist in this workflow"):
        Workflow.model_validate(baseline_raw)


def test_negative_matrix_group_dimensional_cardinality_mismatch() -> None:
    """ISTQB Negative Test 7: 1D MatrixSynthesisGroup with 2 target blocks fails validation."""
    with pytest.raises(pydantic.ValidationError, match=r"requires exactly 1 target block"):
        MatrixSynthesisGroup.model_validate(obj=
            {
                "id": "grp_01e1d71000000001",
                "title": {"translations": {"fi": "Testi", "en": "Test"}},
                "view_type": PresetView.METRICS_1D,
                "target_blocks": ["blk_53f32679aa514fcb", "blk_440a5fef9331451b"],
            }
        )


def test_negative_matrix_group_ids_duplicate_fails_validation() -> None:
    """ISTQB Negative Test 8: OutputProfile with duplicate matrix synthesis group IDs fails validation."""
    seed_data = load_seed_data()
    profiles = {p["id"]: p for p in seed_data["output_profiles"]}
    baseline_profile = dict(profiles["prf_5d6e7f8091a2b3c4"])

    # Duplicate first group ID in matrix_synthesis_groups
    groups_copy = [dict(g) for g in baseline_profile["matrix_synthesis_groups"]]
    if len(groups_copy) >= 2:
        groups_copy[1]["id"] = groups_copy[0]["id"]
        baseline_profile["matrix_synthesis_groups"] = groups_copy

        with pytest.raises(pydantic.ValidationError, match=r"Duplicate synthesis group IDs detected"):
            OutputProfile.model_validate(baseline_profile)


def test_tavily_search_selective_routing_governance() -> None:
    """Verify selective routing of Tavily search (mcp_tavily_search / source_verification_hook).

    Fact-Checking (wf_04...) and Strategic Leadership (wf_02...) include steps with external
    Tavily search capabilities, while non-research workflows (wf_01..., wf_03..., wf_05...)
    intentionally omit Tavily search to prevent unnecessary web latency and API costs.
    """
    seed_data = load_seed_data()
    workflows = {w["id"]: w for w in seed_data["workflows"]}
    steps = {s["id"]: s for s in seed_data["steps"]}

    # Workflows requiring empirical research & falsification
    research_wf_ids = ["wf_9d68c573802341db"]
    # Workflows evaluating internal prompt dialogues, cognitive depth, or static compliance
    internal_wf_ids = ["wf_a8f1d71000000001", "wf_b9e2d71000000002"]

    for wf_id in research_wf_ids:
        assert wf_id in workflows, f"Workflow {wf_id} missing from seed_data.json"
        raw_wf = workflows[wf_id]
        wf_model = Workflow.model_validate(raw_wf)
        # Verify at least one step in research workflows references a blueprint with Tavily tool capability
        has_tavily_step = False
        for step in wf_model.steps:
            if step.task_blueprint in steps:
                blueprint = steps[step.task_blueprint]
                tools = blueprint["allowed_mcp_tools"] if "allowed_mcp_tools" in blueprint else []
                pre_hooks = blueprint["pre_hooks"] if "pre_hooks" in blueprint else []
                if "mcp_tavily_search" in tools or "source_verification_hook" in pre_hooks:
                    has_tavily_step = True
                    break
        assert has_tavily_step, f"Research workflow {wf_id} must incorporate Tavily search verification"

    for wf_id in internal_wf_ids:
        assert wf_id in workflows, f"Workflow {wf_id} missing from seed_data.json"
        raw_wf = workflows[wf_id]
        wf_model = Workflow.model_validate(raw_wf)
        # Verify non-research workflows contain zero Tavily search steps
        for step in wf_model.steps:
            if step.task_blueprint in steps:
                blueprint = steps[step.task_blueprint]
                tools = blueprint["allowed_mcp_tools"] if "allowed_mcp_tools" in blueprint else []
                assert "mcp_tavily_search" not in tools, (
                    f"Non-research workflow {wf_id} must NOT include mcp_tavily_search in step {step.id}"
                )


def test_negative_tavily_in_non_research_workflow_rejected() -> None:
    """ISTQB Negative Test 9: Non-research workflows reject Tavily tools in their steps."""
    seed_data = load_seed_data()
    workflows = {w["id"]: w for w in seed_data["workflows"]}
    steps = {s["id"]: s for s in seed_data["steps"]}

    internal_wf_ids = ["wf_a8f1d71000000001", "wf_b9e2d71000000002"]
    for wf_id in internal_wf_ids:
        assert wf_id in workflows, f"Workflow {wf_id} missing from seed_data.json"
        wf_model = Workflow.model_validate(workflows[wf_id])
        for step in wf_model.steps:
            if step.task_blueprint in steps:
                bp_model = Step.model_validate(steps[step.task_blueprint])
                assert "mcp_tavily_search" not in bp_model.allowed_mcp_tools, (
                    f"Tavily tool detected in non-research workflow {wf_id}"
                )


def test_competency_workflow_assignment_context_governance() -> None:
    """Verify assignment_context modality governance and contextual overrides across retained workflows."""
    seed_data = load_seed_data()
    workflows = {w["id"]: w for w in seed_data["workflows"]}

    # 1. Assert all 3 retained workflows have enable_contextual_overrides=True
    for wf_id in EXPECTED_WORKFLOW_IDS:
        assert wf_id in workflows, f"Workflow {wf_id} missing from seed_data"
        wf = Workflow.model_validate(workflows[wf_id])
        assert wf.enable_contextual_overrides is True, f"Workflow {wf_id} must have enable_contextual_overrides=True"

    # 2. Verify ExpectedInput assignment governance invariants on model level
    valid_assignment = ExpectedInput.model_validate(obj=
        {
            "input_key": "assignment_context",
            "label": {"translations": {"fi": "Tehtävänanto", "en": "Assignment"}},
            "description": {"translations": {"fi": "Kuvaus", "en": "Description"}},
            "input_modes": ["assignment", "file", "paste"],
            "required": True,
        }
    )
    assert valid_assignment.is_assignment is True
    assert valid_assignment.is_chat_history is False

    # 3. Assert mutual exclusivity of assignment mode with is_chat_history=True
    with pytest.raises(ValidationError, match=r"[Aa]ssignment"):
        ExpectedInput.model_validate(obj=
            {
                "input_key": "assignment_context",
                "label": {"translations": {"fi": "Tehtävänanto", "en": "Assignment"}},
                "description": {"translations": {"fi": "Kuvaus", "en": "Description"}},
                "input_modes": ["assignment"],
                "is_chat_history": True,
                "required": True,
            }
        )

    # 4. Assert mutual exclusivity of assignment mode with is_endorsed_deliverable=True
    with pytest.raises(ValidationError, match=r"[Aa]ssignment"):
        ExpectedInput.model_validate(obj=
            {
                "input_key": "assignment_context",
                "label": {"translations": {"fi": "Tehtävänanto", "en": "Assignment"}},
                "description": {"translations": {"fi": "Kuvaus", "en": "Description"}},
                "input_modes": ["assignment"],
                "is_endorsed_deliverable": True,
                "required": True,
            }
        )
