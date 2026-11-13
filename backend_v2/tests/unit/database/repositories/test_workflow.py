"""Unit tests for WorkflowRepositoryImpl over EntityPersistencePort."""

from __future__ import annotations

import pytest

from backend_v2.database.postgres.pool import PostgresPoolManager
from backend_v2.database.postgres.uow import PostgresUnitOfWork
from backend_v2.database.repositories.workflow import WorkflowRepositoryImpl
from backend_v2.exceptions import (
    AppException,
    ErrorCodes,
    ResourceNotFoundError,
    WorkflowNotFoundError,
)
from backend_v2.models.auth import SystemOrganizations
from backend_v2.models.domain.step import Step, StepRule
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.studio import (
    StepCreateDTO,
    StepUpdateDTO,
    WorkflowCreateDTO,
    WorkflowUpdateDTO,
)
from backend_v2.models.enums import (
    CognitiveTier,
    HistoricalContextMode,
    StepType,
    StorageBackend,
)
from backend_v2.settings import Settings
from backend_v2.tests.factories.model_factories import I18nTextFactory, WorkflowFactory
from backend_v2.tests.fakes.in_memory_uow import InMemoryAsyncPgPool, InMemoryUnitOfWork

_WF_ID = "wf_0195f3a0000070018234567890abcdef"
_WF_OTHER = "wf_0195f3a0000070028234567890abcdef"
_WF_MISSING = "wf_0195f3a0000070008000000000000099"
_STP_ID = "stp_0195f3a0000070018234567890abcdef"
_STP_MISSING = "stp_0195f3a0000070008000000000000099"
_BLK_ID = "blk_0195f3a0000070018234567890abcdef"
_PRF_ID = "prf_0195f3a0000070018234567890abcdef"
_SYS_ID = "mrg_0195f3a00000700e826807f3bfa3454d"
_ORG_A = "org_0195f3a0000070018234567890abcdef"
_ORG_B = "org_0195f3a0000070028234567890abcdef"


@pytest.fixture
def base_uow() -> InMemoryUnitOfWork:
    """Provide a shared InMemoryUnitOfWork store for stateful repository tests."""
    return InMemoryUnitOfWork()


@pytest.fixture
def repo(base_uow: InMemoryUnitOfWork) -> WorkflowRepositoryImpl:
    """Provide a WorkflowRepositoryImpl backed by the stateful InMemoryUnitOfWork store."""
    return WorkflowRepositoryImpl(uow_factory=lambda: InMemoryUnitOfWork(base_uow.store))


@pytest.fixture
def sample_workflow() -> Workflow:
    """Provide a valid Workflow domain model via Polyfactory."""
    return WorkflowFactory.build(
        id=_WF_ID,
        slug="wf_exec",
        organization_id=_ORG_A,
        default_profile_id=_PRF_ID,
        model_registry_id=_SYS_ID,
        steps=[],
    )


@pytest.fixture
def sample_step() -> Step:
    """Provide a valid Step domain model."""
    return Step(
        id=_STP_ID,
        slug="step_one",
        organization_id=_ORG_A,
        name=I18nTextFactory.build(translations={"en": "Step 1", "fi": "Step 1 FI"}),
        type=StepType.LLM,
        cognitive_tier=CognitiveTier.FAST,
        criteria_block_ids=[_BLK_ID],
        extraction_protocol_block_id=_BLK_ID,
        pre_hooks=[],
        post_hooks=[],
        allowed_mcp_tools=[],
        mcp_tool_params={},
        expected_inputs=[],
    )


@pytest.mark.asyncio
async def test_workflow_crud_and_role_filtering(
    repo: WorkflowRepositoryImpl,
    sample_workflow: Workflow,
) -> None:
    """Positive: verify save_workflow, get_workflow aliases, tenant/ROOT filtering, update, count, and delete."""
    assert await repo.get_workflow_by_id(_WF_MISSING) is None
    assert await repo.get_workflow_definition(_WF_MISSING) is None
    assert await repo.delete_workflow(_WF_MISSING) is False

    assert await repo.save_workflow(sample_workflow) == _WF_ID
    other_wf = WorkflowFactory.build(id=_WF_OTHER, organization_id=_ORG_B, model_registry_id=_SYS_ID, steps=[])
    sys_wf = WorkflowFactory.build(
        organization_id=SystemOrganizations.ROOT_SYSTEM.value,
        model_registry_id=_SYS_ID,
        steps=[],
    )
    await repo.save_workflow(other_wf)
    await repo.save_workflow(sys_wf)

    assert await repo.get_workflow(_WF_ID) == sample_workflow
    assert await repo.get_workflow_by_id(_WF_ID) == sample_workflow
    assert await repo.count_workflows() == 3

    org_a_visible = await repo.get_all_workflows(organization_id=_ORG_A, role="MEMBER")
    assert {w.id for w in org_a_visible} == {_WF_ID, sys_wf.id}

    root_visible = await repo.get_all_workflows(organization_id=_ORG_A, role="ROOT")
    assert len(root_visible) == 3

    # Empty update returns workflow_id without mutating
    assert await repo.update_workflow(_WF_ID, WorkflowUpdateDTO()) == _WF_ID

    updated_id = await repo.update_workflow_definition(
        _WF_ID,
        WorkflowUpdateDTO(
            name=I18nTextFactory.build(translations={"en": "Updated WF"}),
            description=I18nTextFactory.build(translations={"en": "Updated Desc"}),
            slug="wf_updated",
            historical_context_mode=HistoricalContextMode.SLIDING_WINDOW_3,
            default_profile_id=None,
            default_strictness_level=85,
            default_lexical_strictness_level=85,
            security_penalty=0.5,
            post_hoc_penalty=0.5,
            passivity_penalty=0.5,
            status="draft",
            model_registry_id=_SYS_ID,
            expected_inputs=[],
            steps=[],
        ),
    )
    assert updated_id == _WF_ID
    updated_wf = await repo.get_workflow_by_id(_WF_ID)
    assert updated_wf is not None
    assert updated_wf.slug == "wf_updated"
    assert updated_wf.default_profile_id is None
    assert updated_wf.historical_context_mode == HistoricalContextMode.SLIDING_WINDOW_3

    assert await repo.delete_workflow(_WF_ID) is True
    assert await repo.get_workflow_by_id(_WF_ID) is None


@pytest.mark.asyncio
async def test_create_workflow_and_missing_registry_or_not_found_failures(
    repo: WorkflowRepositoryImpl,
) -> None:
    """Positive & Negative: create_workflow requires model_registry_id and update_workflow raises WorkflowNotFoundError."""
    wf_dto = WorkflowCreateDTO(
        slug="created_wf",
        name=I18nTextFactory.build(translations={"en": "Created"}),
        description=I18nTextFactory.build(translations={"en": "Desc"}),
        organization_id=_ORG_A,
        default_profile_id=_PRF_ID,
        historical_context_mode=HistoricalContextMode.DISABLED,
        model_registry_id=_SYS_ID,
        expected_inputs=[],
        steps=[],
    )
    created_id = await repo.create_workflow(wf_dto)
    assert created_id.startswith("wf_")

    missing_reg_dto = WorkflowCreateDTO(
        slug="missing_reg",
        name=I18nTextFactory.build(translations={"en": "Missing Reg"}),
        model_registry_id=None,
        expected_inputs=[],
        steps=[],
    )
    with pytest.raises(AppException) as reg_exc:
        await repo.create_workflow(missing_reg_dto)
    assert reg_exc.value.status_code == 422
    assert reg_exc.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

    with pytest.raises(WorkflowNotFoundError):
        await repo.update_workflow(_WF_MISSING, WorkflowUpdateDTO(slug="ghost"))


@pytest.mark.asyncio
async def test_step_crud_delete_blocked_by_usage_and_not_found_failures(
    repo: WorkflowRepositoryImpl,
    sample_step: Step,
    sample_workflow: Workflow,
) -> None:
    """Verify Step CRUD, empty update short-circuit, missing step errors, and workflow-usage delete guard."""
    assert await repo.get_step_by_id(_STP_MISSING) is None
    assert await repo.delete_step(_STP_MISSING) is False
    with pytest.raises(ResourceNotFoundError):
        await repo.update_step(_STP_MISSING, StepUpdateDTO(slug="ghost"))

    assert await repo.save_step(sample_step) == _STP_ID
    assert await repo.get_step(_STP_ID) == sample_step
    assert len(await repo.get_all_steps()) == 1

    # Empty StepUpdateDTO returns step_id unchanged
    assert await repo.update_step(_STP_ID, StepUpdateDTO()) == _STP_ID

    assert (
        await repo.update_step(
            _STP_ID,
            StepUpdateDTO(
                name=I18nTextFactory.build(translations={"en": "Renamed Step"}),
                description=I18nTextFactory.build(translations={"en": "Step Desc"}),
                slug="step_renamed",
                type=StepType.LLM,
                role_block_id=_BLK_ID,
                extraction_protocol_block_id=_BLK_ID,
                execution_persona_block_id=_BLK_ID,
                criteria_block_ids=[_BLK_ID],
                pre_hooks=[],
                post_hooks=[],
                safety="safe",
                allowed_mcp_tools=[],
                mcp_tool_params={},
                cognitive_tier=CognitiveTier.BALANCED,
                expected_inputs=[],
            ),
        )
        == _STP_ID
    )

    created_step_id = await repo.create_step(
        StepCreateDTO(
            slug="created_step",
            organization_id=_ORG_A,
            name=I18nTextFactory.build(translations={"en": "Created Step"}),
            type=StepType.LLM,
            cognitive_tier=CognitiveTier.FAST,
            criteria_block_ids=[_BLK_ID],
            extraction_protocol_block_id=_BLK_ID,
            pre_hooks=[],
            post_hooks=[],
            allowed_mcp_tools=[],
            mcp_tool_params={},
            expected_inputs=[],
        )
    )
    assert created_step_id.startswith("stp_")

    # Workflow referencing _STP_ID blocks deletion unconditionally via workflow_step_refs ON DELETE RESTRICT
    wf_using_step = sample_workflow.model_copy(
        update={
            "steps": [
                StepRule(
                    task_blueprint=_STP_ID,
                    depends_on=[],
                )
            ]
        }
    )
    await repo.save_workflow(wf_using_step)

    with pytest.raises(AppException) as blocked_exc:
        await repo.delete_step(_STP_ID, force_delete=False)
    assert blocked_exc.value.status_code == 400
    assert blocked_exc.value.details["error_code"] == ErrorCodes.DELETE_BLOCKED_BY_USAGE.value

    with pytest.raises(AppException) as forced_blocked_exc:
        await repo.delete_step(_STP_ID, force_delete=True)
    assert forced_blocked_exc.value.status_code == 400
    assert forced_blocked_exc.value.details["error_code"] == ErrorCodes.DELETE_BLOCKED_BY_USAGE.value

    # Removing the referencing workflow unlocks step deletion
    assert await repo.delete_workflow(wf_using_step.id) is True
    assert await repo.delete_step(_STP_ID, force_delete=True) is True
    assert await repo.get_step_by_id(_STP_ID) is None

    # Verify save_workflow SQL OCC increments version on update and rejects stale version with 409 CONFLICT
    occ_wf = sample_workflow.model_copy(update={"version": 1})
    await repo.save_workflow(occ_wf)
    loaded_v1 = await repo.get_workflow_by_id(occ_wf.id)
    assert loaded_v1 is not None
    assert loaded_v1.version == 1

    await repo.save_workflow(loaded_v1.model_copy(update={"status": "ACTIVE"}))
    loaded_v2 = await repo.get_workflow_by_id(occ_wf.id)
    assert loaded_v2 is not None
    assert loaded_v2.version == 2

    with pytest.raises(AppException) as stale_occ_exc:
        await repo.save_workflow(occ_wf)
    assert stale_occ_exc.value.status_code == 409
    assert stale_occ_exc.value.details["error_code"] == ErrorCodes.CONFLICT.value


@pytest.mark.asyncio
async def test_workflow_postgres_invalid_prefix_and_storage_fault_failure() -> None:
    """Negative: invalid ID prefix raises VALIDATION_FAILED and SQL fault raises STORAGE_ACCESS_FAILED."""
    pool = InMemoryAsyncPgPool()
    settings = Settings(
        storage_backend=StorageBackend.POSTGRES,
        postgres_host="db.internal",
        postgres_port=5432,
        postgres_user="quorum",
        postgres_db="quorum",
        postgres_command_timeout_seconds=5.0,
    )
    pool_mgr = PostgresPoolManager(settings=settings, pool=pool)
    pg_repo = WorkflowRepositoryImpl(uow_factory=lambda: PostgresUnitOfWork(pool_mgr))

    with pytest.raises(AppException) as invalid_exc:
        await pg_repo.get_workflow_by_id(_STP_ID)
    assert invalid_exc.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

    try:
        pool.inject_fault("fetch", RuntimeError("simulated list failure"))
        with pytest.raises(AppException) as fault_exc:
            await pg_repo.get_all_steps()
        assert fault_exc.value.status_code == 500
        assert fault_exc.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value
    finally:
        pool.clear_faults()
