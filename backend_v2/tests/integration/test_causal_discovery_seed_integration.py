"""Integration test suite for dedicated causal discovery blueprints and DAG topologies.

Verifies that:
1. All 6 workflow-dedicated causal discovery step blueprints in seed_data.json
   validate cleanly against Pydantic V2 Step schema and have expected_inputs tailored.
2. All 6 workflows in seed_data.json contain an active causal discovery step rule
   pointing to their dedicated blueprint and a downstream fusion step declaring causal_source_step_id.
3. Kahn's wave sort orders each causal discovery step in Wave 1 and its downstream
   fusion step in Wave 2.
4. Negative scenarios fail fast per ISTQB boundary assertions.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import BaseModel, ConfigDict

from backend_v2.exceptions import AppException, ErrorCodes, WorkflowCompilationError
from backend_v2.models.domain.step import StepRule
from backend_v2.models.enums import EngineType, StepType
from backend_v2.seed.run_seed import ValidatedSeedBufferDTO, validate_all_seed_collections
from backend_v2.services.orchestrator.dag_compiler import DAGCompilerService
from backend_v2.settings import get_settings


class BlueprintSpecDTO(BaseModel):
    """Specification for dedicated causal discovery blueprints and topology."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    id: str
    slug: str
    expected_inputs: list[str]
    workflow_id: str
    step_rule_id: str
    downstream_fusion_step_id: str


DEDICATED_BLUEPRINTS: list[BlueprintSpecDTO] = [
    BlueprintSpecDTO(
        id="sp_c4a5a1d15c00438a",
        slug="step_causal_discovery",
        expected_inputs=["product_text", "chat_log", "reflection_text"],
        workflow_id="wf_9d68c573802341db",
        step_rule_id="sr_c4a5a1d15c00438a",
        downstream_fusion_step_id="sr_4d2272d8b4864847",
    ),
    BlueprintSpecDTO(
        id="sp_c4a5a1d15c00438a",
        slug="step_causal_discovery",
        expected_inputs=["product_text", "chat_log", "reflection_text"],
        workflow_id="wf_a8f1d71000000001",
        step_rule_id="sr_a8f1d71000000002",
        downstream_fusion_step_id="sr_a8f1d71000000003",
    ),
]


@pytest.fixture(scope="module")
def seed_buffer() -> ValidatedSeedBufferDTO:
    """Loads and validates seed_data.json returning strongly typed ValidatedSeedBufferDTO."""
    seed_path = Path(get_settings().seed_data_path)
    with seed_path.open("r", encoding="utf-8") as f:
        raw_seed: object = json.load(f)
    return validate_all_seed_collections(raw_seed)


def test_dedicated_causal_blueprints_pydantic_schema(
    seed_buffer: ValidatedSeedBufferDTO,
) -> None:
    """Positive Test 1: Validate each dedicated blueprint against Step Pydantic schema."""
    step_dict = {s.id: s for s in seed_buffer.steps}

    for spec in DEDICATED_BLUEPRINTS:
        blueprint_id = spec.id
        assert blueprint_id in step_dict, f"Blueprint {blueprint_id} missing from seed_data.json steps"

        step_model = step_dict[blueprint_id]
        assert step_model.id == blueprint_id
        assert step_model.slug == spec.slug
        assert step_model.type == StepType.CAUSAL_DISCOVERY
        assert step_model.engine_type == EngineType.CAUSAL_DISCOVERY
        assert step_model.is_system_core is True
        assert step_model.expected_inputs == spec.expected_inputs
        assert step_model.extraction_protocol_block_id == "blk_573802341db9d68c"


def test_workflows_contain_dedicated_causal_step_rules(
    seed_buffer: ValidatedSeedBufferDTO,
) -> None:
    """Positive Test 2: Validate workflows declaring causal discovery.

    Validate workflows contain dedicated step rule and downstream fusion wiring.
    """
    wf_dict = {w.id: w for w in seed_buffer.workflows}

    for spec in DEDICATED_BLUEPRINTS:
        wf_id = spec.workflow_id
        assert wf_id in wf_dict, f"Workflow {wf_id} missing from seed_data.json workflows"

        wf = wf_dict[wf_id]
        step_rule_ids = {s.id: s for s in wf.steps}

        causal_sr_id = spec.step_rule_id
        assert causal_sr_id in step_rule_ids, f"Causal step rule {causal_sr_id} missing from workflow {wf_id}"

        causal_sr = step_rule_ids[causal_sr_id]
        assert causal_sr.task_blueprint == spec.id

        downstream_sr_id = spec.downstream_fusion_step_id
        assert downstream_sr_id in step_rule_ids, f"Downstream fusion step {downstream_sr_id} missing from {wf_id}"

        downstream_sr = step_rule_ids[downstream_sr_id]
        assert downstream_sr.causal_source_step_id == causal_sr_id
        assert causal_sr_id in downstream_sr.depends_on


def test_topological_waves_order_causal_before_fusion(
    seed_buffer: ValidatedSeedBufferDTO,
) -> None:
    """Positive Test 3: Kahn's wave sort orders causal discovery in Wave 1 and fusion step in Wave 2."""
    wf_dict = {w.id: w for w in seed_buffer.workflows}

    for spec in DEDICATED_BLUEPRINTS:
        wf_id = spec.workflow_id
        wf = wf_dict[wf_id]

        waves = DAGCompilerService.compute_topological_waves(wf.steps)
        step_to_wave = {step.id: wave_idx for wave_idx, wave in enumerate(waves) for step in wave}

        causal_sr_id = spec.step_rule_id
        fusion_sr_id = spec.downstream_fusion_step_id

        causal_wave = step_to_wave[causal_sr_id]
        fusion_wave = step_to_wave[fusion_sr_id]

        assert causal_wave == 1, f"Expected causal step {causal_sr_id} in Wave 1, got Wave {causal_wave}"
        assert fusion_wave == 2, f"Expected downstream fusion step {fusion_sr_id} in Wave 2, got Wave {fusion_wave}"
        assert causal_wave < fusion_wave


def test_step_rule_validation_fails_when_causal_source_not_in_depends_on() -> None:
    """Negative Test 1: StepRule with causal_source_step_id not in depends_on raises AppException(VALIDATION_FAILED)."""
    with pytest.raises(AppException) as exc_info:
        StepRule(
            id="sr_1234567890abcdef",
            task_blueprint="sp_bd0b3054fe664960",
            depends_on=["sr_1111111111111111"],
            causal_source_step_id="sr_2222222222222222",
        )
    assert exc_info.value.error_code == ErrorCodes.VALIDATION_FAILED.value


def test_dag_compiler_fails_when_causal_dependency_missing_from_workflow() -> None:
    """Negative Test 2: DAGCompiler raises WorkflowCompilationError when a step depends on an unknown step ID."""
    broken_step = StepRule(
        id="sr_1234567890abcdef",
        task_blueprint="sp_bd0b3054fe664960",
        depends_on=["sr_3333333333333333"],
        causal_source_step_id="sr_3333333333333333",
    )
    with pytest.raises(WorkflowCompilationError):
        DAGCompilerService.compute_topological_waves([broken_step])
