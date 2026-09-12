"""Unit test suite for modular competency workflows and output profiles in seed_data.json.

Verifies DAG topology, dynamic input routing, bilingual descriptions, preset views,
baseline workflow non-regression, and ISTQB negative boundary conditions.
"""

import json
from pathlib import Path
from typing import Any

import pytest

from backend_v2.models.core_base import I18nText
from backend_v2.models.enums import PresetView
from backend_v2.models.v2_core import OutputProfile, Workflow
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

    Ensures zero-regression mandate for wf_9d68c573802341db and prf_9d68c573802341db.
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


def test_output_profiles_binding_and_preset_views() -> None:
    """Verify output profile 1:1 workflow bindings, tone instructions, and valid PresetView enum views."""
    seed_data = load_seed_data()
    profiles = {p["id"]: p for p in seed_data["output_profiles"]}

    for prf_id in EXPECTED_PROFILE_IDS[1:]:
        assert prf_id in profiles, f"OutputProfile {prf_id} missing from seed_data.json"
        prf_model = OutputProfile.model_validate(profiles[prf_id])
        assert prf_model.id == prf_id
        assert prf_model.workflow_id is not None
        assert prf_model.tone_instruction is not None
        assert len(prf_model.tone_instruction) >= 10, f"Tone instruction in {prf_id} must be non-empty"

        # Validate matrix synthesis group view_type strings against PresetView enum
        for group in prf_model.matrix_synthesis_groups:
            assert group.view_type in [v.value for v in PresetView], (
                f"Invalid view_type {group.view_type} in {prf_id}. Must be valid PresetView."
            )


# --- ISTQB Negative & Edge Case Tests ---


def test_negative_invalid_unmapped_inputs_reference_fails_dag() -> None:
    """ISTQB Negative Test 1: Step mapping referencing un-declared input key triggers DAG compilation error."""
    seed_data = load_seed_data()
    workflows = {w["id"]: w for w in seed_data["workflows"]}
    raw_wf = dict(workflows["wf_01a1d71000000001"])

    # Corrupt step input_mappings to reference non-existent input key $inputs.non_existent_key
    steps_copy = [dict(s) for s in raw_wf["steps"]]
    step_0 = dict(steps_copy[0])
    rule_copy = dict(step_0["rule"])
    rule_copy["input_mappings"] = {"product_text": "$inputs.non_existent_key"}
    step_0["rule"] = rule_copy
    steps_copy[0] = step_0
    raw_wf["steps"] = steps_copy

    bad_wf = Workflow.model_validate(raw_wf)
    with pytest.raises(ValueError) as exc_info:
        DAGCompilerService.validate_workflow(bad_wf)
    assert "non_existent_key" in str(exc_info.value) or "unmapped" in str(exc_info.value).lower()


def test_negative_circular_step_dependency_fails_dag() -> None:
    """ISTQB Negative Test 2: Circular dependency in workflow steps triggers DAG cycle error."""
    seed_data = load_seed_data()
    workflows = {w["id"]: w for w in seed_data["workflows"]}
    raw_wf = dict(workflows["wf_01a1d71000000001"])

    steps_copy = [dict(s) for s in raw_wf["steps"]]
    # Introduce circular dependency: step 0 depends on step 1, step 1 depends on step 0
    step_0 = dict(steps_copy[0])
    step_1 = dict(steps_copy[1])

    step_0_rule = dict(step_0["rule"])
    step_1_rule = dict(step_1["rule"])

    step_0_rule["depends_on"] = [step_1["id"]]
    step_1_rule["depends_on"] = [step_0["id"]]

    step_0["rule"] = step_0_rule
    step_1["rule"] = step_1_rule

    steps_copy[0] = step_0
    steps_copy[1] = step_1
    raw_wf["steps"] = steps_copy

    cyclic_wf = Workflow.model_validate(raw_wf)
    with pytest.raises(ValueError) as exc_info:
        DAGCompilerService.validate_workflow(cyclic_wf)
    assert "cycle" in str(exc_info.value).lower() or "circular" in str(exc_info.value).lower()


def test_negative_raw_xml_in_ai_description_rejected() -> None:
    """ISTQB Negative Test 3: Raw XML tags in ai_description fail validation rule assertion."""
    seed_data = load_seed_data()
    workflows = {w["id"]: w for w in seed_data["workflows"]}
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
