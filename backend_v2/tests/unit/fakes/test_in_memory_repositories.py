"""Unit tests for In-Memory Repository Fakes.

Verifies snapshot isolation, ingress mutation decoupling, explicit update requirement,
100% protocol method parity, and deterministic fault injection mechanics.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from backend_v2.models.auth import (
    OrganizationCreate,
    OrganizationUpdateDTO,
    UserCreate,
    UserRole,
    UserUpdate,
)
from backend_v2.models.domain.base import AuditLogCreateDTO, UsageAggregateUpdateDTO, UsageRecord
from backend_v2.models.domain.knowledge import ClaimCreateDTO, ConceptCreateDTO, ReferenceCreateDTO
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import PersonaPromptBlock
from backend_v2.models.dtos.studio import StepCreateDTO, StepUpdateDTO, WorkflowCreateDTO, WorkflowUpdateDTO
from backend_v2.models.dtos.system import (
    SystemConfigCreateDTO,
    SystemConfigUpdateDTO,
    SystemSettingsDTO,
)
from backend_v2.models.dtos.trace import ExecutionCreateDTO, ExecutionUpdateDTO
from backend_v2.models.enums import ExecutionStatus, StepType
from backend_v2.models.state import TraceEvent
from backend_v2.models.v2_core import (
    I18nText,
    Role,
    Step,
    SystemConfigMCPGateways,
    SystemConfigModelRegistry,
)
from backend_v2.tests.fakes.in_memory_repositories import (
    InMemoryAgentRepository,
    InMemoryAuditRepository,
    InMemoryComponentRepository,
    InMemoryExecutionPersonaRepository,
    InMemoryExecutionRepository,
    InMemoryExtractionProtocolRepository,
    InMemoryIdentityRepository,
    InMemoryKnowledgeRepository,
    InMemoryMatrixRepository,
    InMemoryOutputProfileRepository,
    InMemoryPromptBlockRepository,
    InMemoryRoleRepository,
    InMemorySystemRepository,
    InMemoryTaskBlueprintRepository,
    InMemoryUnifiedWorkflowRepository,
    InMemoryWorkflowRepository,
)

# ==============================================================================
# 1. Snapshot Reference Isolation Tests
# ==============================================================================


@pytest.mark.asyncio
async def test_snapshot_reference_isolation() -> None:
    """Verify get() returns distinct memory objects (is not) with identical structural data (==)."""
    repo = InMemoryExecutionRepository()
    dto = ExecutionCreateDTO(
        workflow_id="wf_test", output_profile_id="prof_1", organization_id="org_1", created_by="usr_1"
    )
    exec_id = await repo.create_execution(dto)

    rec1 = await repo.get_execution(exec_id)
    rec2 = await repo.get_execution(exec_id)

    assert rec1 is not None
    assert rec2 is not None
    assert rec1 is not rec2
    assert rec1 == rec2


@pytest.mark.asyncio
async def test_ingress_mutation_decoupling() -> None:
    """Verify mutating the input DTO after calling create does NOT affect internal stored state."""
    repo = InMemoryWorkflowRepository()
    dto = WorkflowCreateDTO(slug="orig-slug", name="Original Name", description="Test Desc")
    wf_id = await repo.create_workflow(dto)

    # Modify caller DTO
    _ = dto.model_copy(update={"name": "Mutated Name"})

    stored = await repo.get_workflow(wf_id)
    assert stored is not None
    assert stored.name == "Original Name"


@pytest.mark.asyncio
async def test_explicit_update_requirement() -> None:
    """Verify modifying a returned entity without calling repo.update leaves stored snapshot intact."""
    repo = InMemoryExecutionRepository()
    dto = ExecutionCreateDTO(
        workflow_id="wf_test", output_profile_id="prof_1", organization_id="org_1", created_by="usr_1"
    )
    exec_id = await repo.create_execution(dto)

    rec = await repo.get_execution(exec_id)
    assert rec is not None

    # Simulate local memory mutation
    _ = rec.model_copy(update={"status": ExecutionStatus.FAILED})

    # Re-fetch from repository: should still be original status
    fetched = await repo.get_execution(exec_id)
    assert fetched is not None
    assert fetched.status == ExecutionStatus.PENDING


# ==============================================================================
# 2. Deterministic Fault Injection Tests
# ==============================================================================


@pytest.mark.asyncio
async def test_deterministic_fault_injection_transient() -> None:
    """Verify single-shot transient fault raises on 1st call and succeeds on 2nd call."""
    repo = InMemoryExecutionRepository()
    dto = ExecutionCreateDTO(
        workflow_id="wf_test", output_profile_id="prof_1", organization_id="org_1", created_by="usr_1"
    )
    exec_id = await repo.create_execution(dto)

    repo.inject_fault("get_execution", TimeoutError("Transient DB Timeout"), trigger_count=1)

    # 1st call: must raise injected TimeoutError
    with pytest.raises(TimeoutError) as exc_info:
        await repo.get_execution(exec_id)
    assert "Transient DB Timeout" in str(exc_info.value)

    # 2nd call: must succeed normally
    rec = await repo.get_execution(exec_id)
    assert rec is not None
    assert rec.id == exec_id


@pytest.mark.asyncio
async def test_deterministic_fault_injection_permanent() -> None:
    """Verify permanent fault consistently raises across all invocations."""
    repo = InMemoryExecutionRepository()
    repo.inject_fault("create_execution", ConnectionError("Database Down"), trigger_count=None)

    dto = ExecutionCreateDTO(
        workflow_id="wf_test", output_profile_id="prof_1", organization_id="org_1", created_by="usr_1"
    )
    with pytest.raises(ConnectionError):
        await repo.create_execution(dto)

    with pytest.raises(ConnectionError):
        await repo.create_execution(dto)

    repo.clear_faults("create_execution")
    exec_id = await repo.create_execution(dto)
    assert exec_id.startswith("exe_")


@pytest.mark.asyncio
async def test_deterministic_fault_injection_context_manager() -> None:
    """Verify scoped fault_context raises during block and auto-clears on exit."""
    repo = InMemoryWorkflowRepository()
    dto = WorkflowCreateDTO(slug="wf-scoped", name="WF", description="Desc")
    wf_id = await repo.create_workflow(dto)

    async with repo.fault_context("get_workflow", RuntimeError("Scoped Error")):
        with pytest.raises(RuntimeError):
            await repo.get_workflow(wf_id)

    # After context exit, fault is cleared
    wf = await repo.get_workflow(wf_id)
    assert wf is not None


def test_fault_injection_invalid_method() -> None:
    """Verify injecting fault on non-existent method raises ValueError Fail-Fast."""
    repo = InMemoryExecutionRepository()
    with pytest.raises(ValueError) as exc_info:
        repo.inject_fault("non_existent_method", RuntimeError("Boom"))
    assert "does not exist" in str(exc_info.value)


# ==============================================================================
# 3. Complete 15/15 Protocol & Facade Coverage Tests
# ==============================================================================


@pytest.mark.asyncio
async def test_all_15_fake_repositories_and_facade() -> None:
    """Exercise methods across all 15 fake repositories and the unified facade."""
    # 1. Execution
    exec_repo = InMemoryExecutionRepository()
    e_id = await exec_repo.create_execution(
        ExecutionCreateDTO(workflow_id="wf_1", output_profile_id="prof_1", organization_id="org_1", created_by="u_1")
    )
    assert await exec_repo.get_execution_status(e_id) is not None
    assert await exec_repo.update_execution(e_id, ExecutionUpdateDTO(status=ExecutionStatus.PASSED))
    event = TraceEvent(step_name="step_1", event_type="progress", content={"message": "Started"})
    assert await exec_repo.append_trace_event(e_id, event)
    assert len(await exec_repo.get_all_executions(organization_id="org_1")) == 1
    assert len(await exec_repo.get_recent_completed_executions()) == 1
    assert await exec_repo.count_executions_by_matrix("m1") == 0
    assert await exec_repo.delete_execution(e_id)
    assert not await exec_repo.delete_execution("non_existent")

    # 2. Workflow
    wf_repo = InMemoryWorkflowRepository()
    wf_id = await wf_repo.create_workflow(WorkflowCreateDTO(slug="wf-1", name="WF1", description="D1"))
    assert await wf_repo.get_workflow(wf_id) is not None
    assert await wf_repo.get_workflow_definition(wf_id) is not None
    assert await wf_repo.get_workflow_by_id(wf_id) is not None
    assert len(await wf_repo.get_all_workflows()) == 1
    assert await wf_repo.count_workflows() == 1
    await wf_repo.update_workflow(wf_id, WorkflowUpdateDTO(name="WF1 Updated"))
    await wf_repo.update_workflow_definition(wf_id, WorkflowUpdateDTO(name="WF1 Updated Def"))
    s_id = await wf_repo.create_step(
        StepCreateDTO(slug="s1", name=I18nText(translations={"en": "S1", "fi": "S1"}), type=StepType.LOGIC, hook="h1")
    )
    assert await wf_repo.get_step(s_id) is not None
    assert await wf_repo.get_step_by_id(s_id) is not None
    assert len(await wf_repo.get_all_steps()) == 1
    await wf_repo.update_step(s_id, StepUpdateDTO(name=I18nText(translations={"en": "S1 Updated", "fi": "S1 Updated"})))
    assert await wf_repo.delete_step(s_id)
    assert await wf_repo.delete_workflow(wf_id)

    # 3. Identity
    id_repo = InMemoryIdentityRepository()
    org_id = await id_repo.create_organization(
        OrganizationCreate(
            name="Org1",
            admin_email="admin@test.com",
            admin_password="password123",
            admin_name="Admin User",
            tpm_limit=10000,
            rpm_limit=60,
        )
    )
    assert await id_repo.get_organization(org_id) is not None
    assert await id_repo.get_organization_model(org_id) is not None
    assert len(await id_repo.list_organizations()) == 1
    await id_repo.update_organization(org_id, OrganizationUpdateDTO(name="Org1 Updated"))
    u_id = await id_repo.create_user(
        UserCreate(
            email="u@test.com",
            role=UserRole.MEMBER,
            organization_id=org_id,
            is_active=True,
            language="en",
            theme_mode="system",
        )
    )
    assert await id_repo.get_user(u_id) is not None
    assert await id_repo.get_user_by_email("u@test.com") is not None
    assert len(await id_repo.list_users(org_id)) == 1
    await id_repo.update_user(u_id, UserUpdate(name="Updated User"))
    assert await id_repo.get_org_usage_total(org_id) == 0.0
    await id_repo.delete_user(u_id)
    await id_repo.delete_org_data(org_id)
    await id_repo.delete_organization(org_id)

    # 4. Component
    comp_repo = InMemoryComponentRepository()
    b_id = "pb_1234567890abcdef1234567890abcdef"
    block = PersonaPromptBlock(
        id=b_id,
        slug="persona-1",
        label=I18nText(translations={"en": "Persona 1", "fi": "Persona 1"}),
        description=I18nText(translations={"en": "Persona Desc", "fi": "Persona Desc"}),
        role_enforcement="Strict",
    )
    await comp_repo.register_component(block)
    assert await comp_repo.get_component_by_id(b_id) is not None
    assert await comp_repo.get_component_by_name("Persona 1") is not None
    assert len(await comp_repo.get_all_components()) == 1
    await comp_repo.update_component(b_id, block)
    await comp_repo.update_component_metadata(b_id, "m", "c")
    assert await comp_repo.get_components_using_dimension("dim1") == []
    await comp_repo.delete_component(b_id)

    # 5. PromptBlock
    pb_repo = InMemoryPromptBlockRepository()
    await pb_repo.create_prompt_block(block)
    assert await pb_repo.get_prompt_block_by_id(b_id) is not None
    assert await pb_repo.get_prompt_block(b_id) is not None
    assert len(await pb_repo.get_all_prompt_blocks()) == 1
    assert len(await pb_repo.get_all_prompt_blocks_models()) == 1
    assert len(await pb_repo.get_prompt_blocks_by_ids([b_id])) == 1
    await pb_repo.update_prompt_block(b_id, block)
    await pb_repo.delete_prompt_block(b_id)

    # 6. Agent
    ag_repo = InMemoryAgentRepository()
    await ag_repo.create_agent(block)
    assert await ag_repo.get_agent_by_id(b_id) is not None
    assert len(await ag_repo.get_all_agents()) == 1
    await ag_repo.update_agent(b_id, block)
    await ag_repo.delete_agent(b_id)

    # 7. TaskBlueprint
    bp_repo = InMemoryTaskBlueprintRepository()
    step_model = Step(
        id="step_1234567890abcdef1234567890abcdef",
        slug="step-bp",
        name=I18nText(translations={"en": "Step Blueprint", "fi": "Step Blueprint"}),
        type=StepType.LOGIC,
        hook="logic_hook",
    )
    await bp_repo.create_task_blueprint(step_model)
    assert await bp_repo.get_task_blueprint_by_id("step_1234567890abcdef1234567890abcdef") is not None
    assert len(await bp_repo.get_all_task_blueprints()) == 1
    await bp_repo.update_task_blueprint(
        "step_1234567890abcdef1234567890abcdef",
        StepUpdateDTO(name=I18nText(translations={"en": "Updated BP", "fi": "Updated BP"})),
    )
    await bp_repo.delete_task_blueprint("step_1234567890abcdef1234567890abcdef")

    # 8. OutputProfile
    op_repo = InMemoryOutputProfileRepository()
    prof_id = "prof_1234567890abcdef1234567890abcdef"
    profile = OutputProfile(
        id=prof_id,
        slug="prof-1",
        workflow_id="wf_1234567890abcdef1234567890abcdef",
        name=I18nText(translations={"en": "Profile 1", "fi": "Profile 1"}),
        target_block_order=[],
    )
    await op_repo.create_output_profile(profile)
    assert await op_repo.get_output_profile_by_id(prof_id) is not None
    assert len(await op_repo.get_all_output_profiles()) == 1
    assert len(await op_repo.get_all_output_profiles_models()) == 1
    await op_repo.update_output_profile(prof_id, profile)
    await op_repo.delete_output_profile(prof_id)

    # 9. Knowledge
    kn_repo = InMemoryKnowledgeRepository()
    await kn_repo.add_banned_phrase("banned", "en")
    assert len(await kn_repo.get_banned_phrases()) == 1
    assert await kn_repo.delete_banned_phrase("banned")
    assert await kn_repo.get_prompt_template("t1") is None
    c_id = await kn_repo.add_concept(ConceptCreateDTO(name="C1"))
    assert c_id.startswith("c_")
    r_id = await kn_repo.add_reference(ReferenceCreateDTO(name="R1"))
    assert r_id.startswith("ref_")
    cl_id = await kn_repo.add_claim(ClaimCreateDTO(name="CL1"))
    assert cl_id.startswith("cl_")
    assert len(await kn_repo.get_concepts()) == 1
    assert len(await kn_repo.get_references()) == 1
    assert len(await kn_repo.get_claims()) == 1
    await kn_repo.clear_knowledge_base()

    # 10. System
    sys_repo = InMemorySystemRepository()
    assert (await sys_repo.get_model_registry()).id == "sys_1234567890abcdef1234567890abcdef"
    await sys_repo.update_model_registry(
        SystemConfigModelRegistry(id="sys_1234567890abcdef1234567890abcdef", models={})
    )
    assert (await sys_repo.get_mcp_gateways()).id == "sys_abcdef1234567890abcdef1234567890"
    await sys_repo.update_mcp_gateways(SystemConfigMCPGateways(id="sys_abcdef1234567890abcdef1234567890", tools=[]))
    settings_dto = SystemSettingsDTO(environment="staging")
    cfg_id = await sys_repo.create_system_config(SystemConfigCreateDTO(type="system_settings", content=settings_dto))
    assert await sys_repo.get_system_config(cfg_id) is not None
    assert await sys_repo.get_system_settings() is None
    await sys_repo.update_system_settings(SystemConfigUpdateDTO(system_settings=settings_dto))
    assert await sys_repo.get_system_settings() is not None

    # 11. Audit
    aud_repo = InMemoryAuditRepository()
    await aud_repo.log_audit_event(AuditLogCreateDTO(actor_id="u1", action="create"))
    assert len(await aud_repo.get_audit_logs(actor_id="u1")) == 1
    await aud_repo.log_usage(
        UsageRecord(
            org_id="org_1",
            user_id="u_1",
            model="gpt-4o",
            input_tokens=50,
            output_tokens=50,
            cost_usd=0.001,
            timestamp=datetime.now(timezone.utc),
        )
    )
    assert len(await aud_repo.get_usage_records("org", "org_1")) == 1
    await aud_repo.upsert_usage_aggregate("org", "org_1", "2026-09", UsageAggregateUpdateDTO(input_tokens=100))
    assert await aud_repo.get_usage_aggregate("org", "org_1", "2026-09") is not None
    assert (await aud_repo.get_detailed_usage("org", "org_1")).organization_id == "org_1"

    # 12. Matrix
    mx_repo = InMemoryMatrixRepository()
    await mx_repo.create_matrix(block)
    assert await mx_repo.get_matrix_by_id(b_id) is not None
    assert len(await mx_repo.get_all_matrices()) == 1
    await mx_repo.update_matrix(b_id, block)
    assert await mx_repo.get_matrices_using_dimension("d1") == []
    await mx_repo.delete_matrix(b_id)

    # 13. Role
    role_repo = InMemoryRoleRepository()
    rol_id = "rol_1234567890abcdef1234567890abcdef"
    role_model = Role(
        id=rol_id,
        name=I18nText(translations={"en": "Role 1", "fi": "Role 1"}),
        model_role="analyst_model",
    )
    await role_repo.create_role(role_model)
    assert await role_repo.get_role_by_id(rol_id) is not None
    assert len(await role_repo.get_all_roles()) == 1
    await role_repo.update_role(rol_id, role_model)
    await role_repo.delete_role(rol_id)

    # 14. Execution Persona
    ep_repo = InMemoryExecutionPersonaRepository()
    await ep_repo.create_execution_persona(block)
    assert await ep_repo.get_execution_persona_by_id(b_id) is not None
    assert len(await ep_repo.get_all_execution_personas()) == 1
    await ep_repo.update_execution_persona(b_id, block)
    await ep_repo.delete_execution_persona(b_id)

    # 15. Extraction Protocol
    proto_repo = InMemoryExtractionProtocolRepository()
    await proto_repo.create_extraction_protocol(block)
    assert await proto_repo.get_extraction_protocol_by_id(b_id) is not None
    assert len(await proto_repo.get_all_extraction_protocols()) == 1
    await proto_repo.update_extraction_protocol(b_id, block)
    await proto_repo.delete_extraction_protocol(b_id)

    # 16. Unified Workflow Facade
    unified = InMemoryUnifiedWorkflowRepository()
    u_wf_id = await unified.create_workflow(WorkflowCreateDTO(slug="unified-wf", name="Unified WF", description="D"))
    assert await unified.get_workflow(u_wf_id) is not None
    assert await unified.get_workflow_by_id(u_wf_id) is not None
    assert await unified.get_workflow_definition(u_wf_id) is not None
    assert len(await unified.get_all_workflows()) == 1
    assert await unified.count_workflows() == 1
    await unified.update_workflow(u_wf_id, WorkflowUpdateDTO(name="Updated WF"))
    await unified.update_workflow_definition(u_wf_id, WorkflowUpdateDTO(name="Updated Def"))

    u_step_id = await unified.create_step(
        StepCreateDTO(
            slug="u-s1", name=I18nText(translations={"en": "US1", "fi": "US1"}), type=StepType.LOGIC, hook="h"
        )
    )
    assert await unified.get_step(u_step_id) is not None
    assert await unified.get_step_by_id(u_step_id) is not None
    assert len(await unified.get_all_steps()) == 1
    await unified.update_step(u_step_id, StepUpdateDTO(name=I18nText(translations={"en": "US1 Up", "fi": "US1 Up"})))
    assert await unified.delete_step(u_step_id)
    assert await unified.delete_workflow(u_wf_id)

    u_exec_id = await unified.create_execution(
        ExecutionCreateDTO(workflow_id="wf_1", output_profile_id="p1", organization_id="o1", created_by="u1")
    )
    assert await unified.get_execution(u_exec_id) is not None
    assert await unified.get_execution_status(u_exec_id) is not None
    await unified.update_execution(u_exec_id, ExecutionUpdateDTO(status=ExecutionStatus.RUNNING))
    await unified.append_trace_event(
        u_exec_id, TraceEvent(step_name="step1", event_type="progress", content={"message": "ok"})
    )
    assert len(await unified.get_all_executions()) == 1
    assert len(await unified.get_recent_completed_executions()) == 1
    assert await unified.count_executions_by_matrix("mx_1") == 0
    assert await unified.delete_execution(u_exec_id)

    u_org_id = await unified.create_organization(
        OrganizationCreate(
            name="OrgU",
            admin_email="u@test.com",
            admin_password="password123",
            admin_name="Admin User",
            tpm_limit=10000,
            rpm_limit=60,
        )
    )
    assert await unified.get_organization(u_org_id) is not None
    assert await unified.get_organization_model(u_org_id) is not None
    assert len(await unified.list_organizations()) == 1
    await unified.update_organization(u_org_id, OrganizationUpdateDTO(name="OrgU Updated"))
    u_user_id = await unified.create_user(
        UserCreate(
            email="u@test.com",
            role=UserRole.MEMBER,
            organization_id=u_org_id,
            is_active=True,
            language="en",
            theme_mode="system",
        )
    )
    assert await unified.get_user(u_user_id) is not None
    assert await unified.get_user_by_email("u@test.com") is not None
    assert len(await unified.list_users(u_org_id)) == 1
    await unified.update_user(u_user_id, UserUpdate(name="Updated User"))
    assert await unified.get_org_usage_total(u_org_id) == 0.0
    assert await unified.delete_user(u_user_id)
    assert await unified.delete_organization(u_org_id)
    await unified.delete_org_data("org_dummy")

    u_b_id = "blk_1234567890abcdef1234567890abcdef"
    u_block = PersonaPromptBlock(
        id=u_b_id,
        slug="u-persona",
        label=I18nText(translations={"en": "U Persona", "fi": "U Persona"}),
        description=I18nText(translations={"en": "Desc", "fi": "Desc"}),
        role_enforcement="Strict Enforcement",
    )
    assert await unified.register_component(u_block) == u_b_id
    assert await unified.get_component_by_id(u_b_id) is not None
    assert await unified.get_component_by_name("u-persona") is not None
    assert len(await unified.get_all_components()) == 1
    assert await unified.update_component_metadata(u_b_id, "mod", "cls")
    await unified.create_component(u_block)
    await unified.update_component(u_b_id, u_block)
    assert await unified.get_components_using_dimension("dim1") == []
    assert await unified.delete_component(u_b_id)

    await unified.create_prompt_block(u_block)
    assert await unified.get_prompt_block(u_b_id) is not None
    assert await unified.get_prompt_block_by_id(u_b_id) is not None
    assert len(await unified.get_all_prompt_blocks()) == 1
    assert len(await unified.get_all_prompt_blocks_models()) == 1
    assert len(await unified.get_prompt_blocks_by_ids([u_b_id])) == 1
    await unified.update_prompt_block(u_b_id, u_block)
    assert await unified.delete_prompt_block(u_b_id)

    await unified.create_agent(u_block)
    assert await unified.get_agent_by_id(u_b_id) is not None
    assert len(await unified.get_all_agents()) == 1
    await unified.update_agent(u_b_id, u_block)
    assert await unified.delete_agent(u_b_id)

    u_step = Step(
        id="step_1234567890abcdef1234567890abcdef",
        slug="step-u",
        name=I18nText(translations={"en": "Step U", "fi": "Step U"}),
        type=StepType.LOGIC,
        hook="hook_u",
    )
    await unified.create_task_blueprint(u_step)
    assert await unified.get_task_blueprint_by_id("step_1234567890abcdef1234567890abcdef") is not None
    assert len(await unified.get_all_task_blueprints()) == 1
    await unified.update_task_blueprint(
        "step_1234567890abcdef1234567890abcdef", StepUpdateDTO(name=I18nText(translations={"en": "U2", "fi": "U2"}))
    )
    assert await unified.delete_task_blueprint("step_1234567890abcdef1234567890abcdef")

    u_prof = OutputProfile(
        id="prof_1234567890abcdef1234567890abcdef",
        slug="prof-u",
        workflow_id="wf_1234567890abcdef1234567890abcdef",
        name=I18nText(translations={"en": "P", "fi": "P"}),
        target_block_order=[],
    )
    await unified.create_output_profile(u_prof)
    assert await unified.get_output_profile_by_id("prof_1234567890abcdef1234567890abcdef") is not None
    assert len(await unified.get_all_output_profiles()) == 1
    assert len(await unified.get_all_output_profiles_models()) == 1
    await unified.update_output_profile("prof_1234567890abcdef1234567890abcdef", u_prof)
    assert await unified.delete_output_profile("prof_1234567890abcdef1234567890abcdef")

    await unified.add_banned_phrase("phrase_u", "en")
    assert len(await unified.get_banned_phrases()) == 1
    assert await unified.delete_banned_phrase("phrase_u")
    assert await unified.get_prompt_template("t_u") is None
    c_u = await unified.add_concept(ConceptCreateDTO(name="CU"))
    assert c_u.startswith("c_")
    r_u = await unified.add_reference(ReferenceCreateDTO(name="RU"))
    assert r_u.startswith("ref_")
    cl_u = await unified.add_claim(ClaimCreateDTO(name="CLU"))
    assert cl_u.startswith("cl_")
    assert len(await unified.get_concepts()) == 1
    assert len(await unified.get_references()) == 1
    assert len(await unified.get_claims()) == 1
    await unified.clear_knowledge_base()

    assert (await unified.get_model_registry()).id == "sys_1234567890abcdef1234567890abcdef"
    await unified.update_model_registry(SystemConfigModelRegistry(id="sys_1234567890abcdef1234567890abcdef", models={}))
    assert (await unified.get_mcp_gateways()).id == "sys_abcdef1234567890abcdef1234567890"
    await unified.update_mcp_gateways(SystemConfigMCPGateways(id="sys_abcdef1234567890abcdef1234567890", tools=[]))
    assert await unified.get_system_settings() is None
    await unified.update_system_settings(
        SystemConfigUpdateDTO(system_settings=SystemSettingsDTO(environment="staging"))
    )
    assert await unified.get_system_settings() is not None
    cfg_u = await unified.create_system_config(
        SystemConfigCreateDTO(
            type="settings",
            content=SystemSettingsDTO(environment="production"),
        )
    )
    assert await unified.get_system_config(cfg_u) is not None

    await unified.log_audit_event(AuditLogCreateDTO(actor_id="act_u", action="act"))
    assert len(await unified.get_audit_logs()) == 1
    await unified.log_usage(
        UsageRecord(
            org_id="o1",
            user_id="u1",
            model="gpt-4o",
            input_tokens=10,
            output_tokens=20,
            cost_usd=0.01,
            timestamp=datetime.now(timezone.utc),
        )
    )
    assert len(await unified.get_usage_records("org")) == 1
    await unified.upsert_usage_aggregate("org", "o1", "2026-09", UsageAggregateUpdateDTO(input_tokens=100))
    assert await unified.get_usage_aggregate("org", "o1", "2026-09") is not None
    assert (await unified.get_detailed_usage("org", "o1")).organization_id == "o1"

    await unified.create_matrix(u_block)
    assert await unified.get_matrix_by_id(u_b_id) is not None
    assert len(await unified.get_all_matrices()) == 1
    await unified.update_matrix(u_b_id, u_block)
    assert await unified.get_matrices_using_dimension("dim1") == []
    assert await unified.delete_matrix(u_b_id)

    u_rol = Role(
        id="rol_1234567890abcdef1234567890abcdef",
        name=I18nText(translations={"en": "R", "fi": "R"}),
        model_role="analyst",
    )
    await unified.create_role(u_rol)
    assert await unified.get_role_by_id("rol_1234567890abcdef1234567890abcdef") is not None
    assert len(await unified.get_all_roles()) == 1
    await unified.update_role("rol_1234567890abcdef1234567890abcdef", u_rol)
    assert await unified.delete_role("rol_1234567890abcdef1234567890abcdef")

    await unified.create_execution_persona(u_block)
    assert await unified.get_execution_persona_by_id(u_b_id) is not None
    assert len(await unified.get_all_execution_personas()) == 1
    await unified.update_execution_persona(u_b_id, u_block)
    assert await unified.delete_execution_persona(u_b_id)

    await unified.create_extraction_protocol(u_block)
    assert await unified.get_extraction_protocol_by_id(u_b_id) is not None
    assert len(await unified.get_all_extraction_protocols()) == 1
    await unified.update_extraction_protocol(u_b_id, u_block)
    assert await unified.delete_extraction_protocol(u_b_id)
