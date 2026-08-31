"""Unit tests for StudioSimulationService."""

from typing import Any
from unittest.mock import AsyncMock, MagicMock, PropertyMock

import pytest

from backend_v2.exceptions import ResourceNotFoundError
from backend_v2.models.auth import TokenData
from backend_v2.models.domain.prompt_blocks import (
    MatrixPromptBlock,
    PersonaPromptBlock,
    ProtocolPromptBlock,
    SystemRulePromptBlock,
)
from backend_v2.models.enums import BlockDataType, HistoricalContextMode, PromptBlockCategory
from backend_v2.models.v2_core import (
    ExpectedInput,
    I18nText,
    MatrixClaim,
    MatrixScale,
    Step,
    StepRule,
    TDAAssertion,
    Workflow,
)
from backend_v2.services.studio.simulation_service import StudioSimulationService


@pytest.fixture
def mock_prompt_block_service() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def simulation_service(mock_prompt_block_service: AsyncMock) -> StudioSimulationService:
    return StudioSimulationService(prompt_block_service=mock_prompt_block_service)


@pytest.fixture
def test_token() -> TokenData:
    return TokenData(
        id="usr_1234567890abcdef1234567890abcdef",
        organization_id="org_1234567890abcdef1234567890abcdef",
        email="test@example.com",
        role="ADMIN",
    )


# ---------------------------------------------------------------------------
# Workflow Simulation Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_simulate_workflow_success(simulation_service: StudioSimulationService, test_token: TokenData) -> None:
    """Test successful DAG resolution and input mapping in workflow simulation."""
    workflow = Workflow(
        id="wor_1234567890abcdef1234567890abcdef",
        slug="test_wf",
        name=I18nText(translations={"en": "Test WF"}),
        description=I18nText(translations={"en": "Desc"}),
        status="active",
        version=1,
        default_profile_id="pro_1234567890abcdef1234567890abcdef",
        allowed_exports=[],
        historical_context_mode=HistoricalContextMode.DISABLED,
        expected_inputs=[
            ExpectedInput(
                input_key="document_text",
                label=I18nText(translations={"en": "Doc"}),
                required=True,
                description=I18nText(translations={"en": "Doc desc"}),
                input_modes=["paste"],
            )
        ],
        steps=[
            StepRule(
                id="stp_11111111111111111111111111111111",
                task_blueprint="step_extract",
                depends_on=[],
                input_mappings={"doc": "$inputs.document_text"},
            ),
            StepRule(
                id="stp_22222222222222222222222222222222",
                task_blueprint="step_evaluate",
                depends_on=["stp_11111111111111111111111111111111"],
                input_mappings={"extracted": "$steps.stp_11111111111111111111111111111111.output"},
            ),
        ],
    )

    res = await simulation_service.simulate_workflow(test_token, workflow)
    assert res.valid is True
    assert len(res.errors) == 0
    assert res.step_status["stp_11111111111111111111111111111111"] == "OK"
    assert res.step_status["stp_22222222222222222222222222222222"] == "OK"
    assert res.execution_order == [
        "stp_11111111111111111111111111111111",
        "stp_22222222222222222222222222222222",
    ]


@pytest.mark.asyncio
async def test_simulate_workflow_missing_input(
    simulation_service: StudioSimulationService, test_token: TokenData
) -> None:
    """Test workflow simulation catches missing input references."""
    workflow = Workflow(
        id="wor_1234567890abcdef1234567890abcdef",
        slug="test_wf",
        name=I18nText(translations={"en": "Test WF"}),
        description=I18nText(translations={"en": "Desc"}),
        status="active",
        version=1,
        default_profile_id="pro_1234567890abcdef1234567890abcdef",
        allowed_exports=[],
        historical_context_mode=HistoricalContextMode.DISABLED,
        expected_inputs=[
            ExpectedInput(
                input_key="doc",
                label=I18nText(translations={"en": "Doc"}),
                required=True,
                description=I18nText(translations={"en": "Doc desc"}),
                input_modes=["paste"],
            )
        ],
        steps=[
            StepRule(
                id="stp_11111111111111111111111111111111",
                task_blueprint="step_extract",
                depends_on=[],
                input_mappings={"missing": "$inputs.missing_var"},
            ),
        ],
    )

    res = await simulation_service.simulate_workflow(test_token, workflow)
    assert res.valid is False
    assert any("Missing input reference: missing_var" in err for err in res.errors)
    assert res.step_status["stp_11111111111111111111111111111111"] == "ERROR"


@pytest.mark.asyncio
async def test_simulate_workflow_undeclared_dependency(
    simulation_service: StudioSimulationService, test_token: TokenData
) -> None:
    """Test workflow simulation catches undeclared step dependencies in mappings."""
    workflow = Workflow(
        id="wor_1234567890abcdef1234567890abcdef",
        slug="test_wf",
        name=I18nText(translations={"en": "Test WF"}),
        description=I18nText(translations={"en": "Desc"}),
        status="active",
        version=1,
        default_profile_id="pro_1234567890abcdef1234567890abcdef",
        allowed_exports=[],
        historical_context_mode=HistoricalContextMode.DISABLED,
        expected_inputs=[],
        steps=[
            StepRule(
                id="stp_11111111111111111111111111111111",
                task_blueprint="step_extract",
                depends_on=[],
                input_mappings={"data": "$steps.stp_22222222222222222222222222222222.out"},
            ),
        ],
    )

    res = await simulation_service.simulate_workflow(test_token, workflow)
    assert res.valid is False
    assert any("Undeclared dependency on step: stp_22222222222222222222222222222222" in err for err in res.errors)


@pytest.mark.asyncio
async def test_simulate_workflow_cycle_detected(
    simulation_service: StudioSimulationService, test_token: TokenData
) -> None:
    """Test workflow simulation detects cyclic dependencies via mock workflow."""
    mock_workflow = MagicMock()
    mock_workflow.id = "wor_1234567890abcdef1234567890abcdef"
    mock_workflow.expected_inputs = []
    mock_workflow.steps = [
        StepRule(
            id="stp_11111111111111111111111111111111",
            task_blueprint="step_1",
            depends_on=["stp_22222222222222222222222222222222"],
        ),
        StepRule(
            id="stp_22222222222222222222222222222222",
            task_blueprint="step_2",
            depends_on=["stp_11111111111111111111111111111111"],
        ),
    ]

    res = await simulation_service.simulate_workflow(test_token, mock_workflow)
    assert res.valid is False
    assert any("Cycle detected" in err for err in res.errors)


@pytest.mark.asyncio
async def test_simulate_workflow_fatal_error(
    simulation_service: StudioSimulationService, test_token: TokenData, caplog: Any
) -> None:
    """Test fatal error logging during simulation graph resolution."""
    mock_workflow = MagicMock()
    mock_workflow.id = "wf_corrupted"
    mock_workflow.expected_inputs = []

    mock_step = MagicMock()
    mock_step.id = "step_1"
    type(mock_step).depends_on = PropertyMock(side_effect=RuntimeError("Resolution failure"))
    mock_workflow.steps = [mock_step]

    res = await simulation_service.simulate_workflow(test_token, mock_workflow)
    assert res.valid is False
    assert "Fatal error resolving DAG structure." in res.errors
    assert test_token.id in caplog.text


# ---------------------------------------------------------------------------
# Prompt Block Simulation Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_simulate_prompt_block_simple(simulation_service: StudioSimulationService, test_token: TokenData) -> None:
    """Test simple prompt block simulation with template formatting."""
    block = SystemRulePromptBlock(
        id="blk_11111111111111111111111111111111",
        slug="test_instruction",
        label=I18nText(translations={"en": "Instruction"}),
        description=I18nText(translations={"en": "Desc"}),
        category_id=PromptBlockCategory.SYSTEM_RULE,
        type=BlockDataType.STRING,
        instruction_text="Analyze the document: {doc_title} and report.",
        ai_description="Analyze the document: {doc_title} and report.",
    )

    res = await simulation_service.simulate_prompt_block(
        test_token, block, mock_inputs={"doc_title": "Quarterly Report"}
    )
    assert res.valid is True
    assert "Analyze the document: Quarterly Report and report." in res.rendered_prompt
    assert res.prompt_context is not None
    assert res.prompt_context.metadata["simulated_block"] == block.id


@pytest.mark.asyncio
async def test_simulate_prompt_block_none_ai_description(
    simulation_service: StudioSimulationService, test_token: TokenData
) -> None:
    """Test prompt block simulation when ai_description and instruction_text are None."""
    block = SystemRulePromptBlock(
        id="blk_11111111111111111111111111111111",
        slug="test_none",
        label=I18nText(translations={"en": "Instruction"}),
        description=I18nText(translations={"en": "Desc"}),
        category_id=PromptBlockCategory.SYSTEM_RULE,
        type=BlockDataType.STRING,
        instruction_text=None,
        ai_description=None,
    )

    res = await simulation_service.simulate_prompt_block(test_token, block, mock_inputs={})
    assert res.valid is True
    assert res.rendered_prompt == ""


@pytest.mark.asyncio
async def test_simulate_prompt_block_matrix_scales(
    simulation_service: StudioSimulationService, test_token: TokenData
) -> None:
    """Test matrix prompt block simulation rendering scales, claims, and TDA concept descriptions."""
    block = MatrixPromptBlock(
        id="blk_22222222222222222222222222222222",
        slug="test_matrix",
        label=I18nText(translations={"en": "Matrix Block"}),
        description=I18nText(translations={"en": "Desc"}),
        category_id=PromptBlockCategory.MATRIX,
        type=BlockDataType.FLOAT,
        ai_description="Perform matrix evaluation.",
        scales=[
            MatrixScale(
                score=1,
                ai_label="POOR",
                claims=[
                    MatrixClaim(
                        label=I18nText(translations={"en": "Claim Label", "fi": "Väite"}),
                        tda_assertions=[
                            TDAAssertion(
                                concept_description="Verify that evidence exists",
                                inverse_evidence=False,
                                aggregation_mode="EXISTS",
                            )
                        ],
                    )
                ],
            )
        ],
    )

    res = await simulation_service.simulate_prompt_block(test_token, block, mock_inputs={})
    assert res.valid is True
    rendered = res.rendered_prompt
    assert "--- EVALUATION SCALES ---" in rendered
    assert "Score 1:" in rendered
    assert "- Claim Label" in rendered
    assert "Rule: Verify that evidence exists" in rendered


@pytest.mark.asyncio
async def test_simulate_prompt_block_polymorphic_subtypes(
    simulation_service: StudioSimulationService, test_token: TokenData
) -> None:
    """Test rendering of all concrete polymorphic PromptBlock sub-types."""
    # 1. PersonaPromptBlock with role_enforcement
    persona_block = PersonaPromptBlock(
        id="blk_11111111111111111111111111111111",
        slug="persona_test",
        label=I18nText(translations={"en": "Persona"}),
        description=I18nText(translations={"en": "Desc"}),
        category_id=PromptBlockCategory.EXECUTION_PERSONA,
        type=BlockDataType.INSTRUCTION,
        role_enforcement="Act as an expert auditor.",
    )
    res_persona = await simulation_service.simulate_prompt_block(test_token, persona_block, mock_inputs={})
    assert res_persona.valid is True
    assert res_persona.rendered_prompt == "Act as an expert auditor."

    # 2. ProtocolPromptBlock with protocol_instructions
    protocol_block = ProtocolPromptBlock(
        id="blk_22222222222222222222222222222222",
        slug="protocol_test",
        label=I18nText(translations={"en": "Protocol"}),
        description=I18nText(translations={"en": "Desc"}),
        category_id=PromptBlockCategory.PROTOCOL,
        type=BlockDataType.INSTRUCTION,
        protocol_instructions="Extract exact quotes only.",
    )
    res_proto = await simulation_service.simulate_prompt_block(test_token, protocol_block, mock_inputs={})
    assert res_proto.valid is True
    assert res_proto.rendered_prompt == "Extract exact quotes only."

    # 3. SystemRulePromptBlock with instruction_text
    sys_block = SystemRulePromptBlock(
        id="blk_33333333333333333333333333333333",
        slug="sys_rule_test",
        label=I18nText(translations={"en": "System Rule"}),
        description=I18nText(translations={"en": "Desc"}),
        category_id=PromptBlockCategory.SYSTEM_RULE,
        type=BlockDataType.INSTRUCTION,
        instruction_text="Strict JSON only.",
    )
    res_sys = await simulation_service.simulate_prompt_block(test_token, sys_block, mock_inputs={})
    assert res_sys.valid is True
    assert res_sys.rendered_prompt == "Strict JSON only."


# ---------------------------------------------------------------------------
# Step Simulation Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_simulate_step_success(
    simulation_service: StudioSimulationService,
    mock_prompt_block_service: AsyncMock,
    test_token: TokenData,
) -> None:
    """Test step simulation resolving role, protocol, and criteria blocks."""
    mock_block = PersonaPromptBlock(
        id="blk_11111111111111111111111111111111",
        slug="role_block",
        label=I18nText(translations={"en": "Role"}),
        description=I18nText(translations={"en": "Desc"}),
        category_id=PromptBlockCategory.AGENT_ROLE,
        type=BlockDataType.STRING,
        role_enforcement="You are a senior analyst.",
        ai_description="You are a senior analyst.",
    )
    mock_prompt_block_service.get_prompt_block.return_value = mock_block

    step = Step(
        id="stp_11111111111111111111111111111111",
        slug="step_analyze",
        name=I18nText(translations={"en": "Analyze Step"}),
        description=I18nText(translations={"en": "Desc"}),
        type="llm",
        model_strategy="fast",
        role_block_id="blk_11111111111111111111111111111111",
        extraction_protocol_block_id="blk_11111111111111111111111111111111",
        criteria_block_ids=["blk_11111111111111111111111111111111"],
        hook="scoring_hook",
    )

    res = await simulation_service.simulate_step(test_token, step, mock_inputs={})
    assert res.valid is True
    assert "--- Prompt Block: blk_11111111111111111111111111111111 ---" in res.rendered_prompt
    assert "[Execution Hook: scoring_hook]" in res.rendered_prompt
    assert res.prompt_context is not None
    assert res.prompt_context.metadata["simulated_step"] == step.id


@pytest.mark.asyncio
async def test_simulate_step_prompt_block_not_found(
    simulation_service: StudioSimulationService,
    mock_prompt_block_service: AsyncMock,
    test_token: TokenData,
) -> None:
    """Test step simulation gracefully handles missing prompt block reference."""
    mock_prompt_block_service.get_prompt_block.side_effect = ResourceNotFoundError("Block not found")

    step = Step(
        id="stp_11111111111111111111111111111111",
        slug="step_missing_block",
        name=I18nText(translations={"en": "Step"}),
        description=I18nText(translations={"en": "Desc"}),
        type="llm",
        model_strategy="fast",
        role_block_id="blk_11111111111111111111111111111111",
        extraction_protocol_block_id="blk_22222222222222222222222222222222",
        criteria_block_ids=["blk_33333333333333333333333333333333"],
    )

    res = await simulation_service.simulate_step(test_token, step, mock_inputs={})
    assert res.valid is False
    assert any("Missing referenced Prompt Block" in err for err in res.errors)
    assert "[NOT FOUND]" in res.rendered_prompt


@pytest.mark.asyncio
async def test_simulate_workflow_missing_depends_on_reference(
    simulation_service: StudioSimulationService, test_token: TokenData
) -> None:
    """Test workflow simulation when step depends on a non-existent step id."""
    mock_workflow = MagicMock()
    mock_workflow.id = "wor_1234567890abcdef1234567890abcdef"
    mock_workflow.expected_inputs = []
    mock_workflow.steps = [
        StepRule(
            id="stp_11111111111111111111111111111111",
            task_blueprint="step_extract",
            depends_on=["stp_non_existent"],
        ),
    ]
    res = await simulation_service.simulate_workflow(test_token, mock_workflow)
    assert "stp_11111111111111111111111111111111" in res.execution_order


@pytest.mark.asyncio
async def test_studio_simulation_returns_strict_dtos(
    simulation_service: StudioSimulationService,
    mock_prompt_block_service: AsyncMock,
    test_token: TokenData,
) -> None:
    """Test Contract 1: Verify simulation service methods return strictly typed DTO models."""
    from backend_v2.models.dtos.studio import (
        PromptBlockSimulationResponse,
        StepSimulationResponse,
        WorkflowSimulationResponse,
    )

    block = SystemRulePromptBlock(
        id="blk_11111111111111111111111111111111",
        slug="test_instruction",
        label=I18nText(translations={"en": "Instruction"}),
        description=I18nText(translations={"en": "Desc"}),
        category_id=PromptBlockCategory.SYSTEM_RULE,
        type=BlockDataType.STRING,
        instruction_text="Static text",
    )
    mock_prompt_block_service.get_prompt_block.return_value = block

    step = Step(
        id="stp_11111111111111111111111111111111",
        slug="step_analyze",
        name=I18nText(translations={"en": "Analyze Step"}),
        description=I18nText(translations={"en": "Desc"}),
        type="llm",
        model_strategy="fast",
        role_block_id="blk_11111111111111111111111111111111",
        extraction_protocol_block_id="blk_11111111111111111111111111111111",
        criteria_block_ids=["blk_11111111111111111111111111111111"],
    )

    workflow = Workflow(
        id="wor_1234567890abcdef1234567890abcdef",
        slug="test_wf",
        name=I18nText(translations={"en": "Test WF"}),
        description=I18nText(translations={"en": "Desc"}),
        status="active",
        version=1,
        default_profile_id="pro_1234567890abcdef1234567890abcdef",
        allowed_exports=[],
        historical_context_mode=HistoricalContextMode.DISABLED,
        expected_inputs=[],
        steps=[],
    )

    pb_res = await simulation_service.simulate_prompt_block(test_token, block, {})
    assert isinstance(pb_res, PromptBlockSimulationResponse)

    step_res = await simulation_service.simulate_step(test_token, step, {})
    assert isinstance(step_res, StepSimulationResponse)

    wf_res = await simulation_service.simulate_workflow(test_token, workflow)
    assert isinstance(wf_res, WorkflowSimulationResponse)
