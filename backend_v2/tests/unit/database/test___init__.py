"""Unit, regression, and boundary tests for backend_v2/database/__init__.py."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

import backend_v2.database as db_pkg
import backend_v2.database.repositories.components as components_pkg
from backend_v2.database import (
    CausalReasoningPort,
    EntityPersistencePort,
    Filter,
    GraphMutationPort,
    QuorumUnitOfWork,
    TopologyResolutionPort,
    UnifiedWorkflowRepository,
    close_shared_pool_manager,
    create_unit_of_work,
    get_driver,
    get_registered_uow_factory,
    get_shared_pool_manager,
    register_default_uow_factory,
)
from backend_v2.database.postgres import PostgresEntityAdapter, PostgresPoolManager
from backend_v2.exceptions import AppException, ConfigurationError, ErrorCodes
from backend_v2.models.auth import Organization, SubscriptionStatus, User, UserRole
from backend_v2.models.core_base import I18nText, generate_opaque_id
from backend_v2.models.domain.proposition_graph import ReportBinaryPayloadDTO
from backend_v2.models.domain.step import Step
from backend_v2.models.domain.system_config import (
    ModelProfile,
    ProviderExtraParamsDTO,
    SystemConfigModelRegistry,
)
from backend_v2.models.enums import (
    CognitiveTier,
    EngineType,
    EntityPrefix,
    LLMProvider,
    StepType,
    StepZone,
    StorageBackend,
    SystemLocale,
)
from backend_v2.settings import get_settings
from backend_v2.tests.factories.model_factories import (
    ExecutionRecordFactory,
    OutputProfileFactory,
    ReportArtifactFactory,
    SystemRulePromptBlockFactory,
    WorkflowFactory,
)
from backend_v2.tests.fakes.in_memory_uow import InMemoryAsyncPgPool, InMemoryUnitOfWork


def test_database_package_exports_and_uow_factory_registration() -> None:
    """Verify public __all__ exports and UnitOfWorkFactory registration roundtrip."""
    expected_exports = {
        "CausalReasoningPort",
        "EntityPersistencePort",
        "Filter",
        "GraphMutationPort",
        "IAgentRepository",
        "IAuditRepository",
        "IComponentRepository",
        "IEntityPersistenceAdapter",
        "IExecutionPersonaRepository",
        "IExecutionRepository",
        "IExtractionProtocolRepository",
        "IIdentityRepository",
        "IKnowledgeRepository",
        "IMatrixRepository",
        "IOutputProfileRepository",
        "IPromptBlockRepository",
        "IReportArtifactRepository",
        "IRoleRepository",
        "ISystemRepository",
        "ITaskBlueprintRepository",
        "IUnifiedWorkflowRepository",
        "IWorkflowRepository",
        "Operator",
        "QuorumUnitOfWork",
        "StorageDocument",
        "StorageDriver",
        "StorageValue",
        "TopologyResolutionPort",
        "UnifiedWorkflowRepository",
        "UnitOfWorkFactory",
        "close_shared_pool_manager",
        "create_unit_of_work",
        "get_driver",
        "get_registered_uow_factory",
        "get_shared_pool_manager",
        "register_default_uow_factory",
    }
    assert set(db_pkg.__all__) == expected_exports
    assert set(components_pkg.__all__) == {
        "AgentRepositoryImpl",
        "ExecutionPersonaRepositoryImpl",
        "ExtractionProtocolRepositoryImpl",
        "MatrixRepositoryImpl",
        "OutputProfileRepositoryImpl",
        "PromptBlockRepositoryImpl",
        "RoleRepositoryImpl",
        "TaskBlueprintRepositoryImpl",
    }

    flt = Filter(field="organization_id", operator="==", value=generate_opaque_id(EntityPrefix.ORGANIZATION))
    assert flt.field == "organization_id"
    assert flt.operator == "=="

    previous_factory = get_registered_uow_factory()
    try:
        register_default_uow_factory(InMemoryUnitOfWork)
        resolved_factory = get_registered_uow_factory()
        assert resolved_factory is InMemoryUnitOfWork
        uow = resolved_factory()
        assert isinstance(uow, QuorumUnitOfWork)
        assert isinstance(uow.graph, GraphMutationPort)
        assert isinstance(uow.topology, TopologyResolutionPort)
        assert isinstance(uow.reasoning, CausalReasoningPort)
        assert isinstance(uow.entities, EntityPersistencePort)
    finally:
        register_default_uow_factory(previous_factory)


@pytest.mark.asyncio
async def test_database_package_factories_and_entity_adapter_roundtrip() -> None:
    """Verify factory instantiation, UnifiedWorkflowRepository wiring, and PostgresEntityAdapter roundtrip."""
    settings = get_settings().model_copy(update={"active_backend": StorageBackend.POSTGRES})
    try:
        pool_mgr = get_shared_pool_manager(settings)
        assert isinstance(pool_mgr, PostgresPoolManager)
        driver = await get_driver(settings=settings, pool_manager=pool_mgr)
        repo = UnifiedWorkflowRepository(driver)
        assert repo.driver is driver
        uow = create_unit_of_work(settings=settings, pool_manager=pool_mgr)
        assert isinstance(uow, QuorumUnitOfWork)
    finally:
        await close_shared_pool_manager()

    pool = InMemoryAsyncPgPool()
    conn = await pool.acquire()
    try:
        adapter = PostgresEntityAdapter(connection=conn, command_timeout_seconds=5.0)
        org = Organization(
            id=generate_opaque_id(EntityPrefix.ORGANIZATION),
            slug="db-pkg-org",
            name="DB Package Org",
            created_at=datetime.now(UTC),
            is_active=True,
            tier="enterprise",
            subscription_status=SubscriptionStatus.ACTIVE,
            quota_limit=500.0,
            tpm_limit=100000,
            rpm_limit=1000,
            allowed_email_domains=[],
        )
        user = User(
            id=generate_opaque_id(EntityPrefix.USER),
            slug="db-pkg-user",
            email="pkg@quorum.ai",
            name="DB Package User",
            role=UserRole.ADMIN,
            organization_id=org.id,
            is_active=True,
            language=SystemLocale.EN,
            theme_mode="dark",
            created_at=datetime.now(UTC),
            created_by="usr_system",
        )
        profile = ModelProfile(
            provider="google",
            model_name="gemini-2.5-flash",
            allowed_tools=[],
            additional_params=ProviderExtraParamsDTO(),
        )
        cfg = SystemConfigModelRegistry(
            id=generate_opaque_id(EntityPrefix.SYSTEM_CONFIG),
            name="Pkg Registry",
            type="model_registry",
            default_provider=LLMProvider.AI_STUDIO,
            tier_definitions={tier: profile for tier in CognitiveTier},
        )
        blk = SystemRulePromptBlockFactory.build(organization_id=org.id)
        step = Step(
            id=generate_opaque_id(EntityPrefix.STEP),
            slug="pkg_step",
            organization_id=org.id,
            name=I18nText(translations={"en": "Step", "fi": "Vaihe"}),
            description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
            type=StepType.LLM,
            extraction_protocol_block_id=blk.id,
            criteria_block_ids=[blk.id],
            pre_hooks=[],
            post_hooks=[],
            allowed_mcp_tools=[],
            mcp_tool_params={},
            expected_inputs=[],
            cognitive_tier=CognitiveTier.FAST,
            engine_type=EngineType.PROMPT,
            zone=StepZone.ZONE_B,
        )
        wf = WorkflowFactory.build(organization_id=org.id, model_registry_id=cfg.id)
        prf = OutputProfileFactory.build(workflow_id=wf.id, organization_id=org.id, content_blocks=[])
        exec_rec = ExecutionRecordFactory.build(
            workflow_id=wf.id, organization_id=org.id, active_profile_id=prf.id, output_profile_id=prf.id
        )
        rep = ReportArtifactFactory.build(execution_id=exec_rec.id, workflow_id=wf.id, profile_id=prf.id)
        bin_dto = ReportBinaryPayloadDTO(
            report_id=rep.id,
            mime_type="application/pdf",
            pdf_bytes=b"%PDF-1.7 pkg",
            size_bytes=12,
            created_at=datetime.now(UTC),
        )

        assert await adapter.upsert_organization(org) == org.id
        assert (await adapter.get_organization(org.id)) is not None
        assert await adapter.upsert_user(user) == user.id
        assert (await adapter.get_user(user.id)) is not None
        assert await adapter.upsert_system_config(cfg) == cfg.id
        assert await adapter.get_system_config(cfg.id) == cfg
        assert await adapter.upsert_prompt_block(blk) == blk.id
        assert await adapter.get_prompt_block(blk.id) == blk
        assert await adapter.upsert_step(step) == step.id
        assert await adapter.get_step(step.id) == step
        assert await adapter.upsert_workflow(wf) == wf.id
        assert await adapter.get_workflow(wf.id) == wf
        assert await adapter.upsert_output_profile(prf) == prf.id
        assert await adapter.get_output_profile(prf.id) == prf
        assert await adapter.save_execution(exec_rec) == exec_rec.id
        assert (await adapter.get_execution(exec_rec.id)) is not None
        assert await adapter.upsert_report_artifact(rep) == rep.id
        assert await adapter.get_report_artifact(rep.id) == rep
        await adapter.save_report_binary(bin_dto)
        assert await adapter.get_report_binary(rep.id) == bin_dto
        assert await adapter.seed_collection_batch("organizations", [org]) == 1
        assert (await adapter.verify_seed_table_counts({"organizations": 1}))["organizations"] == 1
    finally:
        await pool.release(conn)


@pytest.mark.asyncio
async def test_database_package_negative_invalid_prefix_and_collection_validation() -> None:
    """Verify invalid prefix and unregistered collection name raise AppException(VALIDATION_FAILED)."""
    pool = InMemoryAsyncPgPool()
    conn = await pool.acquire()
    try:
        adapter = PostgresEntityAdapter(connection=conn, command_timeout_seconds=5.0)
        with pytest.raises(AppException) as bad_prefix_err:
            await adapter.get_organization("usr_0195f3a0000070008000000000000001")
        assert bad_prefix_err.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

        org = Organization(
            id=generate_opaque_id(EntityPrefix.ORGANIZATION),
            slug="neg-org",
            name="Negative Org",
            created_at=datetime.now(UTC),
            is_active=True,
            tier="enterprise",
            subscription_status=SubscriptionStatus.ACTIVE,
            quota_limit=500.0,
            tpm_limit=100000,
            rpm_limit=1000,
            allowed_email_domains=[],
        )
        with pytest.raises(AppException) as bad_col_err:
            await adapter.seed_collection_batch("unregistered_collection", [org])
        assert bad_col_err.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    finally:
        await pool.release(conn)


@pytest.mark.asyncio
async def test_database_factory_negative_invalid_pool_manager_and_binary_bva() -> None:
    """Verify get_driver rejects incompatible pool_manager and save_report_binary enforces size BVA (min-1/max+1)."""
    settings = get_settings().model_copy(update={"active_backend": StorageBackend.POSTGRES})
    with pytest.raises(ConfigurationError) as bad_pool_err:
        await get_driver(settings=settings, pool_manager=object())
    assert bad_pool_err.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR.value

    pool = InMemoryAsyncPgPool()
    conn = await pool.acquire()
    try:
        adapter = PostgresEntityAdapter(connection=conn, command_timeout_seconds=5.0)
        raw_pdf = b"%PDF-1.7"
        for invalid_size in (len(raw_pdf) - 1, len(raw_pdf) + 1):
            bad_payload = ReportBinaryPayloadDTO(
                report_id=generate_opaque_id(EntityPrefix.REPORT),
                mime_type="application/pdf",
                pdf_bytes=raw_pdf,
                size_bytes=invalid_size,
                created_at=datetime.now(UTC),
            )
            with pytest.raises(AppException) as size_err:
                await adapter.save_report_binary(bad_payload)
            assert size_err.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    finally:
        await pool.release(conn)
