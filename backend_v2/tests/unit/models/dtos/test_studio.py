import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.studio import (
    MCPGatewayDeleteResponse,
    ModelRegistryDeleteResponse,
    PromptBlockDeleteResponse,
    PromptBlockSimulationResponse,
    StepDeleteResponse,
    StepSimulationResponse,
    WorkflowDeleteResponse,
    WorkflowSimulationResponse,
)


def test_mcp_gateway_delete_response_strictness() -> None:
    dto = MCPGatewayDeleteResponse(status="success", deleted_id="mcp_123")
    assert dto.status == "success"
    assert dto.deleted_id == "mcp_123"

    with pytest.raises(ValidationError):
        MCPGatewayDeleteResponse(status="success", deleted_id="mcp_123", extra_field="fail")  # type: ignore


def test_model_registry_delete_response_strictness() -> None:
    dto = ModelRegistryDeleteResponse(status="deleted", deleted_id="mdl_123")
    assert dto.status == "deleted"
    assert dto.deleted_id == "mdl_123"

    with pytest.raises(ValidationError):
        ModelRegistryDeleteResponse(status="deleted", deleted_id="mdl_123", extra="fail")  # type: ignore


def test_prompt_block_responses_strictness() -> None:
    dto1 = PromptBlockSimulationResponse(trace={"key": "val"})
    assert dto1.trace == {"key": "val"}

    dto2 = PromptBlockDeleteResponse(status="ok", deleted_id="blk_1")
    assert dto2.status == "ok"

    with pytest.raises(ValidationError):
        PromptBlockSimulationResponse(trace={"key": "val"}, extra="fail")  # type: ignore


def test_step_responses_strictness() -> None:
    dto1 = StepSimulationResponse(trace={"step": "done"})
    assert dto1.trace == {"step": "done"}

    dto2 = StepDeleteResponse(status="ok", deleted_id="stp_1")
    assert dto2.status == "ok"

    with pytest.raises(ValidationError):
        StepSimulationResponse(trace={"step": "done"}, extra="fail")  # type: ignore


def test_workflow_responses_strictness() -> None:
    dto1 = WorkflowSimulationResponse(trace={"wf": "done"})
    assert dto1.trace == {"wf": "done"}

    dto2 = WorkflowDeleteResponse(status="ok", deleted_id="wf_1")
    assert dto2.status == "ok"

    with pytest.raises(ValidationError):
        WorkflowSimulationResponse(trace={"wf": "done"}, extra="fail")  # type: ignore


def test_core_response_dto_strictness() -> None:
    from backend_v2.models.dtos.studio import PromptBlockResponseDTO, StepResponseDTO, WorkflowResponseDTO

    # Need to pass all required fields from the base models (Workflow, Step, PromptBlock)
    # The IDs must match opaque stripe ID regex: ^([a-z]{2,5})_[a-fA-F0-9]{16,32}$
    valid_id_wf = "wf_0123456789abcdef"
    valid_id_stp = "stp_0123456789abcdef"
    valid_id_blk = "blk_0123456789abcdef"
    valid_id_prf = "prf_0123456789abcdef"
    valid_id_org = "org_0123456789abcdef"

    wf = WorkflowResponseDTO.model_validate(
        {
            "id": valid_id_wf,
            "slug": "test-wf",
            "name": {"default_locale": "en", "translations": {"en": "Test Workflow"}},
            "description": {"default_locale": "en", "translations": {"en": "Desc"}},
            "version": 1,
            "status": "draft",
            "default_profile_id": valid_id_prf,
            "organization_id": valid_id_org,
        }
    )
    assert wf.organization_id == valid_id_org
    assert wf.id == valid_id_wf

    step = StepResponseDTO.model_validate(
        {
            "id": valid_id_stp,
            "slug": "test-step",
            "name": {"default_locale": "en", "translations": {"en": "Test Step"}},
            "type": "llm",
            "description": {"default_locale": "en", "translations": {"en": "test", "fi": "testi"}},
            "model_strategy": "fast",
            "prompt_blocks": ["blk_0123456789abcdef"],
            "organization_id": valid_id_org,
        }
    )
    assert step.organization_id == valid_id_org

    pb = PromptBlockResponseDTO.model_validate(
        {
            "id": valid_id_blk,
            "slug": "test-block",
            "label": {"default_locale": "en", "translations": {"en": "Test Block"}},
            "description": {"default_locale": "en", "translations": {"en": "Test Block Desc"}},
            "category_id": "test_cat",
            "type": "string",
            "organization_id": valid_id_org,
        }
    )
    assert pb.organization_id == valid_id_org


def test_step_simulation_response_with_actual_fields() -> None:
    # Represents the actual payload returned by studio_service.simulate_step
    actual_payload = {
        "valid": True,
        "errors": [],
        "rendered_prompt": "--- Prompt Block: blk_1 --- \n Hello world!"
    }
    # Currently, this will fail because Pydantic forbids extra fields
    dto = StepSimulationResponse(**actual_payload)
    assert dto.valid is True
    assert dto.errors == []
    assert "blk_1" in dto.rendered_prompt


def test_prompt_block_simulation_response_with_actual_fields() -> None:
    # Represents the actual payload returned by studio_service.simulate_prompt_block
    actual_payload = {
        "valid": True,
        "errors": [],
        "rendered_prompt": "--- Prompt Block: blk_1 ---\nScale: 1\n"
    }
    dto = PromptBlockSimulationResponse(**actual_payload)
    assert dto.valid is True
    assert dto.errors == []
    assert "blk_1" in dto.rendered_prompt


def test_workflow_simulation_response_with_actual_fields() -> None:
    # Represents the actual payload returned by studio_service.simulate_workflow
    actual_payload = {
        "valid": True,
        "errors": [],
        "step_status": {"stp_1": "OK"},
        "execution_order": ["stp_1"]
    }
    dto = WorkflowSimulationResponse(**actual_payload)
    assert dto.valid is True
    assert dto.errors == []
    assert dto.step_status == {"stp_1": "OK"}
    assert dto.execution_order == ["stp_1"]
