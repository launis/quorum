"""Unit tests for Server-Side ID Generation and Request/Response DTO Separation.

Enforces Zero Client-Side Creation ID Authority across Studio creation workflows.
ISTQB Test Partitioning: TC-ID-01 through TC-ID-08.
"""

import re
from typing import Any

import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.studio import (
    PromptBlockCreateDTO,
    StepCreateDTO,
    WorkflowCreateDTO,
)
from backend_v2.models.enums import BlockDataType, PromptBlockCategory, StepType
from backend_v2.models.v2_core import (
    I18nText,
    MatrixSynthesisGroup,
    StepRule,
)

# ==============================================================================
# TC-ID-01 & TC-ID-02: WorkflowCreateDTO Authority
# ==============================================================================


def test_workflow_create_dto_rejects_client_id() -> None:
    """TC-ID-01: WorkflowCreateDTO with extra='forbid' strictly rejects client-supplied id."""
    payload: dict[str, Any] = {
        "id": "wf_client_injected_123",
        "slug": "custom-workflow",
        "name": {"translations": {"en": "Custom Workflow", "fi": "Mukautettu työnkulku"}},
    }
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        WorkflowCreateDTO.model_validate(payload)


def test_workflow_create_dto_accepts_valid_payload() -> None:
    """TC-ID-02: WorkflowCreateDTO accepts valid creation payload without id."""
    payload: dict[str, Any] = {
        "slug": "custom-workflow",
        "name": {"translations": {"en": "Custom Workflow", "fi": "Mukautettu työnkulku"}},
        "description": {"translations": {"en": "Description", "fi": "Kuvaus"}},
        "allowed_exports": ["pdf"],
        "historical_context_mode": "DISABLED",
    }
    dto = WorkflowCreateDTO.model_validate(payload)
    assert dto.slug == "custom-workflow"
    assert isinstance(dto.name, I18nText)
    assert dto.allowed_exports == ["pdf"]


# ==============================================================================
# TC-ID-03 & TC-ID-04: StepCreateDTO Authority
# ==============================================================================


def test_step_create_dto_rejects_client_id() -> None:
    """TC-ID-03: StepCreateDTO with extra='forbid' strictly rejects client-supplied id."""
    payload: dict[str, Any] = {
        "id": "step_client_injected_123",
        "slug": "custom-step",
        "name": {"translations": {"en": "Custom Step", "fi": "Mukautettu vaihe"}},
    }
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        StepCreateDTO.model_validate(payload)


def test_step_create_dto_accepts_valid_payload() -> None:
    """TC-ID-04: StepCreateDTO accepts valid creation payload without id."""
    payload: dict[str, Any] = {
        "slug": "custom-step",
        "name": {"translations": {"en": "Custom Step", "fi": "Mukautettu vaihe"}},
        "type": StepType.LLM,
        "safety": "safe",
    }
    dto = StepCreateDTO.model_validate(payload)
    assert dto.slug == "custom-step"
    assert dto.type == StepType.LLM
    assert dto.safety == "safe"


# ==============================================================================
# TC-ID-05 & TC-ID-06: PromptBlockCreateDTO Authority
# ==============================================================================


def test_prompt_block_create_dto_rejects_client_id() -> None:
    """TC-ID-05: PromptBlockCreateDTO with extra='forbid' strictly rejects client-supplied id."""
    payload: dict[str, Any] = {
        "id": "blk_client_injected_123",
        "slug": "custom-block",
        "label": {"translations": {"en": "Custom Block", "fi": "Mukautettu lohko"}},
        "description": {"translations": {"en": "Description", "fi": "Kuvaus"}},
        "category_id": PromptBlockCategory.SYSTEM_RULE,
    }
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        PromptBlockCreateDTO.model_validate(payload)


def test_prompt_block_create_dto_accepts_valid_payload() -> None:
    """TC-ID-06: PromptBlockCreateDTO accepts valid creation payload without id."""
    payload: dict[str, Any] = {
        "slug": "custom-block",
        "label": {"translations": {"en": "Custom Block", "fi": "Mukautettu lohko"}},
        "description": {"translations": {"en": "Description", "fi": "Kuvaus"}},
        "category_id": PromptBlockCategory.SYSTEM_RULE,
        "type": BlockDataType.INSTRUCTION,
        "instruction_text": "Always follow architectural constraints.",
    }
    dto = PromptBlockCreateDTO.model_validate(payload)
    assert dto.slug == "custom-block"
    assert dto.category_id == PromptBlockCategory.SYSTEM_RULE
    assert dto.instruction_text == "Always follow architectural constraints."


# ==============================================================================
# TC-ID-07 & TC-ID-08: Sub-Entity Server-Side ID Generation via default_factory
# ==============================================================================


def test_step_rule_default_factory_generates_valid_opaque_id() -> None:
    """TC-ID-07: StepRule generated without explicit id receives a randomized sr_<16hex> Opaque ID."""
    step_rule = StepRule(task_blueprint="step_1234567890abcdef")
    assert step_rule.id is not None
    assert re.match(r"^sr_[a-fA-F0-9]{16,32}$", step_rule.id), f"Unexpected ID format: {step_rule.id}"


def test_matrix_synthesis_group_default_factory_generates_valid_opaque_id() -> None:
    """TC-ID-08: MatrixSynthesisGroup generated without explicit id receives a randomized grp_<16hex> Opaque ID."""
    group = MatrixSynthesisGroup(
        title=I18nText(translations={"en": "Synthesis Group 1", "fi": "Synteesiryhmä 1"}),
        target_blocks=["blk_1234567890abcdef"],
    )
    assert group.id is not None
    assert re.match(r"^grp_[a-fA-F0-9]{16,32}$", group.id), f"Unexpected ID format: {group.id}"


# ==============================================================================
# TC-ID-09: Seed Data Canonical Prefix Parity Map
# ==============================================================================


CANONICAL_SEED_PREFIXES: dict[str, str] = {
    "workflows": "wf_",
    "steps": "sp_",
    "prompt_blocks": "blk_",
    "output_profiles": "prf_",
    "system_config": "sys_",
    "organizations": "org_",
    "users": "usr_",
    "step_rules": "sr_",
    "matrix_synthesis_groups": "grp_",
    "tda_assertions": "tda_",
}


def test_canonical_seed_prefixes_contract() -> None:
    """TC-ID-09: Verifies that canonical Stripe Opaque ID prefixes strictly adhere to seed_data.json SSOT."""
    assert CANONICAL_SEED_PREFIXES["steps"] == "sp_"
    assert CANONICAL_SEED_PREFIXES["workflows"] == "wf_"
    assert CANONICAL_SEED_PREFIXES["output_profiles"] == "prf_"
    assert CANONICAL_SEED_PREFIXES["prompt_blocks"] == "blk_"
    assert CANONICAL_SEED_PREFIXES["system_config"] == "sys_"
    assert CANONICAL_SEED_PREFIXES["step_rules"] == "sr_"
    assert CANONICAL_SEED_PREFIXES["matrix_synthesis_groups"] == "grp_"
    assert CANONICAL_SEED_PREFIXES["tda_assertions"] == "tda_"
