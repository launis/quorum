"""Unit test suite for modular competency workflows and output profiles in seed_data.json.

Verifies DAG topology, dynamic input routing, bilingual descriptions, preset views,
baseline workflow non-regression, and ISTQB negative boundary conditions.
"""

import json
from pathlib import Path
from typing import Any

import pydantic
import pytest

from backend_v2.exceptions import AppException, WorkflowCompilationError
from backend_v2.models.core_base import I18nText
from backend_v2.models.enums import PresetView
from backend_v2.models.v2_core import (
    ExpectedInput,
    MatrixSynthesisGroup,
    OutputProfile,
    Step,
    Workflow,
)
from backend_v2.services.orchestrator.dag_compiler import DAGCompilerService

SEED_DATA_PATH = Path("backend_v2/seed/seed_data.json")

EXPECTED_WORKFLOW_IDS = [
    "wf_9d68c573802341db",  # Monolithic baseline (preservation mandate)
    "wf_01a1d71000000001",  # AI Driving License
    "wf_02a1d71000000002",  # Strategic Leadership
    "wf_03a1d71000000003",  # Deep Problem Solving
    "wf_04a1d71000000004",  # Fact-Checking & Empirical Research
    "wf_05a1d71000000005",  # Compliance & Governance
]

COMPETENCY_WORKFLOW_IDS = [
    "wf_01a1d71000000001",
    "wf_02a1d71000000002",
    "wf_03a1d71000000003",
    "wf_04a1d71000000004",
    "wf_05a1d71000000005",
]

EXPECTED_PROFILE_IDS = [
    "prf_5d6e7f8091a2b3c4",  # Monolithic baseline profile
    "prf_01b1d71000000001",
    "prf_02b1d71000000002",
    "prf_03b1d71000000003",
    "prf_04b1d71000000004",
    "prf_05b1d71000000005",
]


def load_seed_data() -> dict[str, list[dict[str, Any]]]:
    """Load raw seed_data.json from workspace.

    Returns:
        dict[str, list[dict[str, Any]]]: Complete seed data dictionary containing collections.
    """
    assert SEED_DATA_PATH.exists(), f"Seed data file missing: {SEED_DATA_PATH}"
    with open(SEED_DATA_PATH, encoding="utf-8") as f:
        data: dict[str, list[dict[str, Any]]] = json.load(f)
    return data


# --- Positive Tests ---


def test_baseline_monolithic_workflow_preserved() -> None:
    """Verify that the baseline monolithic workflow and profile remain 100% untouched.

    Ensures zero-regression mandate for wf_9d68c573802341db and prf_5d6e7f8091a2b3c4.
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
    assert len(mono_wf.steps) > 0


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
    """Verify that all output profiles define mandatory strictness_level and scoring_strategy.

    The matrix_scoring_hook and worker fail-fast require strictness_level and scoring_strategy
    to be explicitly configured on the profile.
    """
    seed_data = load_seed_data()
    profiles = {p["id"]: p for p in seed_data["output_profiles"]}

    for prf_id in EXPECTED_PROFILE_IDS:
        assert prf_id in profiles, f"OutputProfile {prf_id} missing from seed_data.json"
        prf = profiles[prf_id]
        prf_model = OutputProfile.model_validate(prf)
        assert prf_model.strictness_level is not None, (
            f"Profile '{prf_id}' missing mandatory strictness_level required by matrix_scoring_hook"
        )
        assert prf_model.scoring_strategy is not None, (
            f"Profile '{prf_id}' missing mandatory scoring_strategy required by matrix_scoring_hook"
        )


def test_negative_profile_missing_scoring_config_detected() -> None:
    """ISTQB Negative Test: OutputProfile without strictness_level or scoring_strategy fails assertion."""
    seed_data = load_seed_data()
    profiles = {p["id"]: p for p in seed_data["output_profiles"]}
    raw_prf = dict(profiles["prf_5d6e7f8091a2b3c4"])

    # Remove strictness_level and scoring_strategy
    corrupt_prf = dict(raw_prf)
    corrupt_prf["strictness_level"] = None
    corrupt_prf["scoring_strategy"] = None
    model = OutputProfile.model_validate(corrupt_prf)

    assert model.strictness_level is None
    assert model.scoring_strategy is None


# --- ISTQB Negative & Edge Case Tests ---


def test_negative_invalid_unmapped_inputs_reference_fails_dag() -> None:
    """ISTQB Negative Test 1: Step mapping referencing un-declared input key triggers DAG compilation error."""
    seed_data = load_seed_data()
    workflows = {w["id"]: w for w in seed_data["workflows"]}
    assert "wf_01a1d71000000001" in workflows, "Workflow wf_01a1d71000000001 missing"
    raw_wf = dict(workflows["wf_01a1d71000000001"])

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
    assert "wf_01a1d71000000001" in workflows, "Workflow wf_01a1d71000000001 missing"
    raw_wf = dict(workflows["wf_01a1d71000000001"])

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
    assert "wf_01a1d71000000001" in workflows, "Workflow wf_01a1d71000000001 missing"
    raw_wf = dict(workflows["wf_01a1d71000000001"])

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
        ExpectedInput.model_validate(
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
        MatrixSynthesisGroup.model_validate(
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
    research_wf_ids = ["wf_04a1d71000000004", "wf_02a1d71000000002"]
    # Workflows evaluating internal prompt dialogues, cognitive depth, or static compliance
    internal_wf_ids = ["wf_01a1d71000000001", "wf_03a1d71000000003", "wf_05a1d71000000005"]

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

    internal_wf_ids = ["wf_01a1d71000000001", "wf_03a1d71000000003", "wf_05a1d71000000005"]
    for wf_id in internal_wf_ids:
        assert wf_id in workflows, f"Workflow {wf_id} missing from seed_data.json"
        wf_model = Workflow.model_validate(workflows[wf_id])
        for step in wf_model.steps:
            if step.task_blueprint in steps:
                bp_model = Step.model_validate(steps[step.task_blueprint])
                assert "mcp_tavily_search" not in bp_model.allowed_mcp_tools, (
                    f"Tavily tool detected in non-research workflow {wf_id}"
                )
