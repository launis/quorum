import pytest
from pydantic import TypeAdapter, ValidationError

from backend_v2.models.core_base import I18nText
from backend_v2.models.dtos.studio import (
    GCPLocationDTO,
    LLMPlatformDTO,
    MCPGatewayDeleteResponse,
    ModelRegistryDeleteResponse,
    OutputProfileListResponse,
    PromptBlockCreateDTO,
    PromptBlockDeleteResponse,
    PromptBlockResponseDTO,
    PromptBlockSimulationRequest,
    PromptBlockSimulationResponse,
    StepCreateDTO,
    StepDeleteResponse,
    StepResponseDTO,
    StepSimulationRequest,
    StepSimulationResponse,
    StepSimulationTraceDTO,
    StepUpdateDTO,
    WorkflowAvailableExtensionsResponse,
    WorkflowCreateDTO,
    WorkflowDeleteResponse,
    WorkflowResponseDTO,
    WorkflowSimulationResponse,
    WorkflowUpdateDTO,
)
from backend_v2.models.enums import PromptBlockCategory


def test_mcp_gateway_delete_response_strictness() -> None:
    dto = MCPGatewayDeleteResponse(status="success", deleted_id="mcp_123")
    assert dto.status == "success"
    assert dto.deleted_id == "mcp_123"

    with pytest.raises(ValidationError):
        MCPGatewayDeleteResponse.model_validate({"status": "success", "deleted_id": "mcp_123", "extra_field": "fail"})


def test_model_registry_delete_response_strictness() -> None:
    dto = ModelRegistryDeleteResponse(status="deleted", deleted_id="mdl_123")
    assert dto.status == "deleted"
    assert dto.deleted_id == "mdl_123"

    with pytest.raises(ValidationError):
        ModelRegistryDeleteResponse.model_validate({"status": "deleted", "deleted_id": "mdl_123", "extra": "fail"})


def test_prompt_block_responses_strictness() -> None:
    dto1 = PromptBlockSimulationResponse(trace=StepSimulationTraceDTO(execution_time_ms=5.0, estimated_tokens=10))
    assert dto1.trace.execution_time_ms == 5.0
    assert dto1.trace.estimated_tokens == 10

    dto2 = PromptBlockDeleteResponse(status="ok", deleted_id="blk_1")
    assert dto2.status == "ok"

    with pytest.raises(ValidationError):
        PromptBlockSimulationResponse.model_validate({"trace": StepSimulationTraceDTO(), "extra": "fail"})


def test_step_responses_strictness() -> None:
    dto1 = StepSimulationResponse(trace=StepSimulationTraceDTO(execution_time_ms=12.5, estimated_tokens=100))
    assert dto1.trace.execution_time_ms == 12.5
    assert dto1.trace.estimated_tokens == 100

    dto2 = StepDeleteResponse(status="ok", deleted_id="stp_1")
    assert dto2.status == "ok"

    with pytest.raises(ValidationError):
        StepSimulationResponse.model_validate({"trace": StepSimulationTraceDTO(), "extra": "fail"})


def test_workflow_responses_strictness() -> None:
    dto1 = WorkflowSimulationResponse(trace=StepSimulationTraceDTO(execution_time_ms=10.0, estimated_tokens=50))
    assert dto1.trace.execution_time_ms == 10.0
    assert dto1.trace.estimated_tokens == 50

    dto2 = WorkflowDeleteResponse(status="ok", deleted_id="wf_1")
    assert dto2.status == "ok"

    with pytest.raises(ValidationError):
        WorkflowSimulationResponse.model_validate({"trace": StepSimulationTraceDTO(), "extra": "fail"})


def test_core_response_dto_strictness() -> None:
    # Need to pass all required fields from the base models (Workflow, Step, PromptBlock)
    # The IDs must match opaque stripe ID regex: ^([a-z]{2,5})_[a-fA-F0-9]{16,32}$
    valid_id_wf = "wf_0195f3a0000070008123456789abcdef"
    valid_id_stp = "stp_0195f3a0000070008123456789abcdef"
    valid_id_blk = "blk_0195f3a0000070008123456789abcdef"
    valid_id_prf = "prf_0195f3a0000070008123456789abcdef"
    valid_id_org = "org_0195f3a0000070008123456789abcdef"

    wf = WorkflowResponseDTO.model_validate(
        {
            "id": valid_id_wf,
            "slug": "test-wf",
            "name": {"translations": {"en": "Test Workflow", "fi": "Test Workflow"}},
            "description": {"translations": {"en": "Desc", "fi": "Desc"}},
            "version": 1,
            "status": "draft",
            "default_profile_id": valid_id_prf,
            "model_registry_id": "sys_0195f3a0000070008123456789abcdef",
            "historical_context_mode": "DISABLED",
            "organization_id": valid_id_org,
        }
    )
    assert wf.organization_id == valid_id_org
    assert wf.id == valid_id_wf
    step = StepResponseDTO.model_validate(
        {
            "id": valid_id_stp,
            "slug": "test-step",
            "name": {"translations": {"en": "Test Step", "fi": "Test Step"}},
            "type": "llm",
            "description": {"translations": {"en": "test", "fi": "testi"}},
            "cognitive_tier": "fast",
            "extraction_protocol_block_id": "blk_0195f3a0000070008123456789abcdef",
            "criteria_block_ids": ["blk_0195f3a0000070008123456789abcdef"],
            "organization_id": valid_id_org,
        }
    )
    assert step.organization_id == valid_id_org

    pb: PromptBlockResponseDTO = TypeAdapter(PromptBlockResponseDTO).validate_python(
        {
            "id": valid_id_blk,
            "slug": "test-block",
            "label": {"translations": {"en": "Test Block", "fi": "Test Block"}},
            "description": {"translations": {"en": "Test Block Desc", "fi": "Test Block Desc"}},
            "category_id": "system_rule",
            "type": "string",
            "organization_id": valid_id_org,
        }
    )
    assert pb.organization_id == valid_id_org


def test_step_simulation_response_with_actual_fields() -> None:
    # Represents the actual payload returned by studio_service.simulate_step
    # Pass arguments explicitly as keywords to avoid dictionary unpacking type variance warnings in mypy
    dto = StepSimulationResponse(
        valid=True,
        errors=[],
        rendered_prompt="--- Prompt Block: blk_1 --- \n Hello world!",
        trace=StepSimulationTraceDTO(execution_time_ms=15.0, estimated_tokens=250),
    )
    assert dto.valid is True
    assert dto.errors == []
    assert "blk_1" in dto.rendered_prompt
    assert dto.trace.execution_time_ms == 15.0
    assert dto.trace.estimated_tokens == 250


def test_prompt_block_simulation_response_with_actual_fields() -> None:
    # Represents the actual payload returned by studio_service.simulate_prompt_block
    dto = PromptBlockSimulationResponse(
        valid=True,
        errors=[],
        rendered_prompt="--- Prompt Block: blk_1 ---\nScale: 1\n",
    )
    assert dto.valid is True
    assert dto.errors == []
    assert "blk_1" in dto.rendered_prompt


def test_workflow_simulation_response_with_actual_fields() -> None:
    # Represents the actual payload returned by studio_service.simulate_workflow
    dto = WorkflowSimulationResponse(
        valid=True,
        errors=[],
        step_status={"stp_1": "OK"},
        execution_order=["stp_1"],
    )
    assert dto.valid is True
    assert dto.errors == []
    assert dto.step_status == {"stp_1": "OK"}
    assert dto.execution_order == ["stp_1"]


def test_workflow_update_dto_negative_partitions() -> None:
    """Test WorkflowUpdateDTO strictness and extra='forbid' validation."""
    # Positive test
    dto = WorkflowUpdateDTO(slug="custom_slug_123", status="DRAFT")
    assert dto.slug == "custom_slug_123"
    assert dto.status == "DRAFT"

    # Negative partition 1: Extra forbidden fields
    with pytest.raises(ValidationError) as exc:
        WorkflowUpdateDTO.model_validate({"slug": "test_slug", "extra_forbidden_key": "fail"})
    assert "extra_forbidden" in str(exc.value) or "Extra inputs are not permitted" in str(exc.value)

    # Negative partition 2: Invalid slug regex pattern
    with pytest.raises(ValidationError):
        WorkflowUpdateDTO(slug="Invalid Slug with Spaces!")


def test_step_update_dto_negative_partitions() -> None:
    """Test StepUpdateDTO strictness and extra='forbid' validation."""
    # Positive test
    dto = StepUpdateDTO(slug="step_slug", safety="safe")
    assert dto.slug == "step_slug"
    assert dto.safety == "safe"

    # Negative partition 1: Extra forbidden fields
    with pytest.raises(ValidationError) as exc:
        StepUpdateDTO.model_validate({"slug": "step_slug", "unrecognized": 123})
    assert "extra_forbidden" in str(exc.value) or "Extra inputs are not permitted" in str(exc.value)

    # Negative partition 2: Invalid safety literal value
    with pytest.raises(ValidationError):
        StepUpdateDTO.model_validate({"safety": "invalid_safety_mode"})


def test_prompt_block_simulation_request_strictness() -> None:
    """Test PromptBlockSimulationRequest strictness, field validation, and extra='forbid'."""
    from backend_v2.models.domain.prompt_blocks import SystemRulePromptBlock
    from backend_v2.models.enums import BlockDataType

    block = SystemRulePromptBlock(
        id="blk_11111111111111111111111111111111",
        slug="test_rule",
        label=I18nText(translations={"en": "Rule"}),
        description=I18nText(translations={"en": "Desc"}),
        category_id=PromptBlockCategory.SYSTEM_RULE,
        type=BlockDataType.INSTRUCTION,
        instruction_text="Instruction",
    )

    # Positive test with defaults
    req1 = PromptBlockSimulationRequest(block=block)
    assert req1.mock_inputs == {}
    assert req1.target_scale_score is None
    assert req1.target_locale == "en"
    assert req1.context_text == "[SIMULATED CONTEXT DOCUMENT]"

    # Positive test with custom fields
    req2 = PromptBlockSimulationRequest(
        block=block,
        mock_inputs={"key": "val"},
        target_scale_score=3,
        target_locale="fi",
        context_text="Custom context",
    )
    assert req2.target_scale_score == 3
    assert req2.target_locale == "fi"
    assert req2.context_text == "Custom context"

    # Positive test: None and empty strings normalized to defaults via mode="before" validators
    req_null = PromptBlockSimulationRequest.model_validate(
        {
            "block": block.model_dump(mode="json"),
            "target_locale": None,
            "context_text": None,
        }
    )
    assert req_null.target_locale == "en"
    assert req_null.context_text == "[SIMULATED CONTEXT DOCUMENT]"

    req_blank = PromptBlockSimulationRequest.model_validate(
        {
            "block": block.model_dump(mode="json"),
            "target_locale": "   ",
            "context_text": "   ",
        }
    )
    assert req_blank.target_locale == "en"
    assert req_blank.context_text == "[SIMULATED CONTEXT DOCUMENT]"

    # Negative partition: Extra forbidden fields
    with pytest.raises(ValidationError):
        PromptBlockSimulationRequest.model_validate(
            {
                "block": block.model_dump(mode="json"),
                "extra_forbidden": "fail",
            }
        )


def test_step_simulation_request_strictness() -> None:
    """Test StepSimulationRequest strictness, field validation, and extra='forbid'."""
    from backend_v2.models.domain.step import Step

    step = Step(
        id="stp_0195f3a0000070018111111111111111",
        slug="test_step",
        name=I18nText(translations={"en": "Test Step"}),
        description=I18nText(translations={"en": "Desc"}),
        cognitive_tier="fast",
        extraction_protocol_block_id="blk_0195f3a0000070028222222222222222",
        criteria_block_ids=["blk_0195f3a0000070018111111111111111"],
    )

    # Positive test with defaults
    req1 = StepSimulationRequest(step=step)
    assert req1.mock_inputs == {}
    assert req1.target_locale == "en"
    assert req1.context_text == "[SIMULATED CONTEXT DOCUMENT]"

    # Positive test with custom fields
    req2 = StepSimulationRequest(
        step=step,
        mock_inputs={"user_query": "hello"},
        target_locale="fi",
        context_text="Custom source text",
    )
    assert req2.mock_inputs == {"user_query": "hello"}
    assert req2.target_locale == "fi"
    assert req2.context_text == "Custom source text"

    # Positive test: None and empty strings normalized to defaults via mode="before" validators
    step_req_null = StepSimulationRequest.model_validate(
        {
            "step": step.model_dump(mode="json"),
            "target_locale": None,
            "context_text": None,
        }
    )
    assert step_req_null.target_locale == "en"
    assert step_req_null.context_text == "[SIMULATED CONTEXT DOCUMENT]"

    step_req_blank = StepSimulationRequest.model_validate(
        {
            "step": step.model_dump(mode="json"),
            "target_locale": "   ",
            "context_text": "   ",
        }
    )
    assert step_req_blank.target_locale == "en"
    assert step_req_blank.context_text == "[SIMULATED CONTEXT DOCUMENT]"

    # Negative partition: Extra forbidden fields
    with pytest.raises(ValidationError):
        StepSimulationRequest.model_validate(
            {
                "step": step.model_dump(mode="json"),
                "extra_forbidden": "fail",
            }
        )


def test_step_simulation_response_trace_type() -> None:
    """Test StepSimulationResponse trace is strictly typed to StepSimulationTraceDTO."""
    # Negative partition: Raw dict for trace should fail strict validation
    with pytest.raises(ValidationError):
        StepSimulationResponse.model_validate({"trace": {"step": "done"}})

    # Positive partition: StepSimulationTraceDTO
    res = StepSimulationResponse(trace=StepSimulationTraceDTO(execution_time_ms=5.0, estimated_tokens=12))
    assert isinstance(res.trace, StepSimulationTraceDTO)
    assert res.trace.execution_time_ms == 5.0
    assert res.trace.estimated_tokens == 12


def test_simulation_responses_trace_strict_types() -> None:
    """Test PromptBlockSimulationResponse and WorkflowSimulationResponse trace strict typing."""
    # Negative partition: Raw dict for trace should fail strict validation
    with pytest.raises(ValidationError):
        PromptBlockSimulationResponse.model_validate({"trace": {"block": "done"}})

    with pytest.raises(ValidationError):
        WorkflowSimulationResponse.model_validate({"trace": {"wf": "done"}})

    # Positive partition: StepSimulationTraceDTO
    pb_res = PromptBlockSimulationResponse(trace=StepSimulationTraceDTO(execution_time_ms=2.0, estimated_tokens=15))
    assert isinstance(pb_res.trace, StepSimulationTraceDTO)
    assert pb_res.trace.execution_time_ms == 2.0
    assert pb_res.trace.estimated_tokens == 15

    wf_res = WorkflowSimulationResponse(trace=StepSimulationTraceDTO(execution_time_ms=8.0, estimated_tokens=80))
    assert isinstance(wf_res.trace, StepSimulationTraceDTO)
    assert wf_res.trace.execution_time_ms == 8.0
    assert wf_res.trace.estimated_tokens == 80


def test_create_dtos_and_metadata_dtos_bva_and_negative_partitions() -> None:
    """Test Create DTOs and metadata DTOs with ISTQB boundary and negative partitions."""
    platform = LLMPlatformDTO(id="vertex_ai", label="Vertex AI", has_regions=True)
    assert platform.id == "vertex_ai"
    with pytest.raises(ValidationError):
        LLMPlatformDTO.model_validate({"id": "vertex_ai", "label": "Vertex", "has_regions": "yes"})

    loc = GCPLocationDTO(id="europe-north1", label="Finland", description="EU North")
    assert loc.id == "europe-north1"
    with pytest.raises(ValidationError):
        GCPLocationDTO.model_validate({"id": "europe-north1", "label": "FI", "description": "EU", "extra": 1})

    wf_create = WorkflowCreateDTO(slug="wf_slug_1", name="Test WF", default_strictness_level=100, security_penalty=1.0)
    assert wf_create.default_strictness_level == 100
    assert wf_create.security_penalty == 1.0
    # Boundary violation: default_strictness_level > 100
    with pytest.raises(ValidationError):
        WorkflowCreateDTO(slug="wf_slug_1", name="Test WF", default_strictness_level=101)
    # Boundary violation: security_penalty < 0.0
    with pytest.raises(ValidationError):
        WorkflowCreateDTO(slug="wf_slug_1", name="Test WF", security_penalty=-0.01)

    step_create = StepCreateDTO(
        slug="stp_slug",
        name=I18nText(translations={"en": "Step"}),
        role_block_id="blk_0195f3a0000070008123456789abcdef",
    )
    assert step_create.role_block_id == "blk_0195f3a0000070008123456789abcdef"
    # Invalid Opaque Stripe ID on role_block_id
    with pytest.raises(ValidationError):
        StepCreateDTO(
            slug="stp_slug",
            name=I18nText(translations={"en": "Step"}),
            role_block_id="invalid_id",
        )

    pb_create = PromptBlockCreateDTO(
        slug="pb_slug",
        label=I18nText(translations={"en": "Label"}),
        description=I18nText(translations={"en": "Desc"}),
        category_id=PromptBlockCategory.SYSTEM_RULE,
    )
    assert pb_create.slug == "pb_slug"
    # Empty slug violates min_length=1
    with pytest.raises(ValidationError):
        PromptBlockCreateDTO(
            slug="",
            label=I18nText(translations={"en": "Label"}),
            description=I18nText(translations={"en": "Desc"}),
            category_id=PromptBlockCategory.SYSTEM_RULE,
        )

    ext_resp = WorkflowAvailableExtensionsResponse(available_extensions=["ext_a"])
    assert ext_resp.available_extensions == ["ext_a"]
    with pytest.raises(ValidationError):
        WorkflowAvailableExtensionsResponse.model_validate({"available_extensions": "not_a_list"})

    prof_list = OutputProfileListResponse(items=[])
    assert prof_list.items == []
    with pytest.raises(ValidationError):
        OutputProfileListResponse.model_validate({"items": "not_a_list"})
