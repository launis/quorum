import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.studio import (
    MCPGatewayDeleteResponse,
    ModelRegistryDeleteResponse,
    PromptBlockDeleteResponse,
    PromptBlockSimulationRequest,
    PromptBlockSimulationResponse,
    StepDeleteResponse,
    StepSimulationRequest,
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

    wf = WorkflowResponseDTO(
        id=valid_id_wf,
        slug="test-wf",
        name="Test Workflow",
        description="Desc",
        version=1,
        status="draft",
        default_profile_id=valid_id_prf,
        organization_id=valid_id_org
    )
    assert wf.organization_id == valid_id_org
    assert wf.id == valid_id_wf

    step = StepResponseDTO(
        id=valid_id_stp,
        slug="test-step",
        name={"default_locale": "en", "translations": {"en": "Test Step"}},
        type="llm",
        description={"default_locale": "en", "translations": {"en": "test", "fi": "testi"}},
        model_strategy="fast",
        prompt_blocks=["blk_0123456789abcdef"],
        organization_id=valid_id_org
    )
    assert step.organization_id == valid_id_org

    pb = PromptBlockResponseDTO(
        id=valid_id_blk,
        slug="test-block",
        label={"default_locale": "en", "translations": {"en": "Test Block"}},
        description={"default_locale": "en", "translations": {"en": "Test Block Desc"}},
        category_id="test_cat",
        type="string",
        organization_id=valid_id_org
    )
    assert pb.organization_id == valid_id_org

