"""Unit, regression, and boundary tests for backend_v2.database.postgres.entity_adapter facade."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

import backend_v2.database.postgres.entity_adapter as entity_adapter_mod
from backend_v2.database.interfaces import EntityPersistencePort
from backend_v2.database.postgres.entity_adapter import (
    _AGGREGATE_USAGE_BASE_SQL,
    _COLLECTION_TO_TABLE_MAP,
    _DELETE_MCP_GATEWAY_SQL,
    _DELETE_MODEL_REGISTRY_SQL,
    _DELETE_TENANT_SECRET_SQL,
    _GET_EXECUTION_SQL,
    _GET_MCP_GATEWAY_SQL,
    _GET_MODEL_REGISTRY_SQL,
    _GET_ORGANIZATION_SQL,
    _GET_OUTPUT_PROFILE_SQL,
    _GET_PROMPT_BLOCK_SQL,
    _GET_REPORT_ARTIFACT_SQL,
    _GET_REPORT_BINARY_SQL,
    _GET_STEP_SQL,
    _GET_USER_SQL,
    _GET_WORKFLOW_SQL,
    _INSERT_AUDIT_LOG_SQL,
    _INSERT_USAGE_RECORD_SQL,
    _LIST_AUDIT_LOGS_SQL,
    _LIST_EXECUTIONS_SQL,
    _LIST_MCP_GATEWAYS_SQL,
    _LIST_MODEL_REGISTRIES_SQL,
    _LIST_ORGANIZATIONS_SQL,
    _LIST_OUTPUT_PROFILES_SQL,
    _LIST_PROMPT_BLOCKS_SQL,
    _LIST_REPORT_ARTIFACTS_SQL,
    _LIST_STEPS_SQL,
    _LIST_USAGE_RECORDS_SQL,
    _LIST_USERS_SQL,
    _LIST_WORKFLOWS_SQL,
    _MARK_REPORT_ARTIFACT_PDF_SQL,
    _ROOT_SYSTEM_ORG_UUID7,
    _SAVE_EXECUTION_SQL,
    _SAVE_REPORT_BINARY_SQL,
    _TABLE_TO_ENTITY_PREFIX,
    _UPSERT_MCP_GATEWAY_SQL,
    _UPSERT_MODEL_REGISTRY_SQL,
    _UPSERT_ORGANIZATION_SQL,
    _UPSERT_OUTPUT_PROFILE_SQL,
    _UPSERT_PROMPT_BLOCK_SQL,
    _UPSERT_REPORT_ARTIFACT_SQL,
    _UPSERT_STEP_SQL,
    _UPSERT_USER_SQL,
    _UPSERT_WORKFLOW_SQL,
    CANONICAL_SEED_TABLES,
    PostgresEntityAdapter,
    _coerce_float,
    _coerce_uuid_or_str,
    _decode_jsonb_column,
    _encode_optional_jsonb,
    _format_optional_uuid7,
    _format_org_uuid7,
    _parse_optional_uuid7,
    _parse_org_uuid7,
    _ReportBinaryRowDTO,
    aggregate_organization_usage_row,
    delete_mcp_gateway_row,
    delete_model_registry_row,
    delete_tenant_secret_row,
    execute_entity_delete,
    execute_entity_upsert,
    get_execution_row,
    get_mcp_gateway_row,
    get_model_registry_row,
    get_organization_row,
    get_output_profile_row,
    get_prompt_block_row,
    get_report_artifact_row,
    get_report_binary_row,
    get_step_row,
    get_user_row,
    get_workflow_row,
    hydrate_audit_log_row,
    hydrate_execution_row,
    hydrate_mcp_gateway_row,
    hydrate_model_registry_row,
    hydrate_organization_row,
    hydrate_output_profile_row,
    hydrate_prompt_block_row,
    hydrate_report_artifact_row,
    hydrate_step_row,
    hydrate_usage_record_row,
    hydrate_user_row,
    hydrate_workflow_row,
    insert_audit_log_row,
    insert_usage_record_row,
    list_mcp_gateway_rows,
    list_model_registry_rows,
    save_execution_row,
    save_report_binary_row,
    seed_collection_batch_rows,
    upsert_mcp_gateway_row,
    upsert_model_registry_row,
    upsert_organization_row,
    upsert_output_profile_row,
    upsert_prompt_block_row,
    upsert_report_artifact_row,
    upsert_step_row,
    upsert_user_row,
    upsert_workflow_row,
    verify_seed_table_counts_rows,
)
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.auth import Organization, SubscriptionStatus, TenantSecretDTO, User, UserRole
from backend_v2.models.core_base import I18nText, generate_opaque_id, parse_prefixed_uuid7
from backend_v2.models.domain.proposition_graph import ReportBinaryPayloadDTO
from backend_v2.models.domain.step import Step
from backend_v2.models.domain.system_config import (
    ModelProfile,
    SystemConfigMCPGateways,
    SystemConfigModelRegistry,
)
from backend_v2.models.enums import (
    CognitiveTier,
    EngineType,
    EntityPrefix,
    LLMProvider,
    MCPAuthType,
    MCPTransportType,
    SecretScope,
    SecretStorageMode,
    StepType,
    StepZone,
    SystemLocale,
)
from backend_v2.settings import get_settings
from backend_v2.tests.factories.model_factories import (
    AuditLogRecordFactory,
    ExecutionRecordFactory,
    OutputProfileFactory,
    ReportArtifactFactory,
    SystemRulePromptBlockFactory,
    TaskBriefFactory,
    UsageRecordFactory,
    WorkflowFactory,
)
from backend_v2.tests.fakes.in_memory_uow import InMemoryAsyncPgPool


def _build_org() -> Organization:
    """Build a valid Organization domain model for facade testing."""
    return Organization(
        id=generate_opaque_id(EntityPrefix.ORGANIZATION),
        slug="facade-org",
        name="Facade Organization",
        created_at=datetime.now(UTC),
        is_active=True,
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=100000,
        rpm_limit=1000,
    )


def _build_user(org_id: str) -> User:
    """Build a valid User domain model for facade testing."""
    return User(
        id=generate_opaque_id(EntityPrefix.USER),
        slug="facade-user",
        email="facade@quorum.ai",
        name="Facade User",
        role=UserRole.ADMIN,
        organization_id=org_id,
        is_active=True,
        language=SystemLocale.EN,
        theme_mode="dark",
        created_at=datetime.now(UTC),
        created_by="usr_0195f3a00000700a83fd6b3d77c748f4",
    )


def _build_registry_config() -> SystemConfigModelRegistry:
    """Build a valid SystemConfigModelRegistry for facade testing."""
    profile = ModelProfile(provider="ai_studio", model_name="gemini-2.5-flash")
    return SystemConfigModelRegistry(
        id=generate_opaque_id(EntityPrefix.MODEL_REGISTRY),
        name="Facade Registry",
        default_provider=LLMProvider.AI_STUDIO,
        tier_definitions={tier: profile for tier in CognitiveTier},
    )


def _build_mcp_gateway(org_id: str) -> SystemConfigMCPGateways:
    """Build a valid SystemConfigMCPGateways for facade testing."""
    return SystemConfigMCPGateways(
        id=generate_opaque_id(EntityPrefix.MCP_GATEWAY),
        organization_id=org_id,
        slug="facade_mcp_gateway",
        name="Facade MCP Gateway",
        endpoint_url="https://mcp.quorum.local/v1",
        transport_type=MCPTransportType.STREAMABLE_HTTP,
        auth_type=MCPAuthType.NONE,
        timeout_seconds=30,
        tools=[],
    )


def _build_step(block_id: str, org_id: str) -> Step:
    """Build a valid Step domain model for facade testing."""
    return Step(
        id=generate_opaque_id(EntityPrefix.STEP),
        slug="facade_step",
        organization_id=org_id,
        name=I18nText(translations={"en": "Facade Step", "fi": "Julkisivuvaihe"}),
        description=I18nText(translations={"en": "Step Description", "fi": "Kuvaus"}),
        type=StepType.LLM,
        extraction_protocol_block_id=block_id,
        criteria_block_ids=[block_id],
        mcp_tool_params={},
        cognitive_tier=CognitiveTier.FAST,
        engine_type=EngineType.PROMPT,
        zone=StepZone.ZONE_B,
    )


def test_entity_adapter_package_facade_reexports_all_symbols() -> None:
    """Verify that importing symbols from backend_v2.database.postgres.entity_adapter works identically."""
    reexported_symbols = (
        CANONICAL_SEED_TABLES,
        PostgresEntityAdapter,
        _AGGREGATE_USAGE_BASE_SQL,
        _COLLECTION_TO_TABLE_MAP,
        _DELETE_TENANT_SECRET_SQL,
        _INSERT_AUDIT_LOG_SQL,
        _INSERT_USAGE_RECORD_SQL,
        _LIST_AUDIT_LOGS_SQL,
        _LIST_USAGE_RECORDS_SQL,
        _ROOT_SYSTEM_ORG_UUID7,
        _TABLE_TO_ENTITY_PREFIX,
        _ReportBinaryRowDTO,
        _coerce_float,
        _coerce_uuid_or_str,
        _decode_jsonb_column,
        _encode_optional_jsonb,
        _format_optional_uuid7,
        _format_org_uuid7,
        _parse_optional_uuid7,
        _parse_org_uuid7,
        execute_entity_delete,
        execute_entity_upsert,
        _GET_EXECUTION_SQL,
        _GET_REPORT_ARTIFACT_SQL,
        _GET_REPORT_BINARY_SQL,
        _LIST_EXECUTIONS_SQL,
        _LIST_REPORT_ARTIFACTS_SQL,
        _MARK_REPORT_ARTIFACT_PDF_SQL,
        _SAVE_EXECUTION_SQL,
        _SAVE_REPORT_BINARY_SQL,
        _UPSERT_REPORT_ARTIFACT_SQL,
        get_execution_row,
        get_report_artifact_row,
        get_report_binary_row,
        hydrate_execution_row,
        hydrate_report_artifact_row,
        save_execution_row,
        save_report_binary_row,
        upsert_report_artifact_row,
        _DELETE_MCP_GATEWAY_SQL,
        _DELETE_MODEL_REGISTRY_SQL,
        _GET_MCP_GATEWAY_SQL,
        _GET_MODEL_REGISTRY_SQL,
        _GET_ORGANIZATION_SQL,
        _GET_USER_SQL,
        _LIST_MCP_GATEWAYS_SQL,
        _LIST_MODEL_REGISTRIES_SQL,
        _LIST_ORGANIZATIONS_SQL,
        _LIST_USERS_SQL,
        _UPSERT_MCP_GATEWAY_SQL,
        _UPSERT_MODEL_REGISTRY_SQL,
        _UPSERT_ORGANIZATION_SQL,
        _UPSERT_USER_SQL,
        aggregate_organization_usage_row,
        delete_mcp_gateway_row,
        delete_model_registry_row,
        delete_tenant_secret_row,
        get_mcp_gateway_row,
        get_model_registry_row,
        get_organization_row,
        get_user_row,
        hydrate_audit_log_row,
        hydrate_mcp_gateway_row,
        hydrate_model_registry_row,
        hydrate_organization_row,
        hydrate_usage_record_row,
        hydrate_user_row,
        insert_audit_log_row,
        insert_usage_record_row,
        list_mcp_gateway_rows,
        list_model_registry_rows,
        upsert_mcp_gateway_row,
        upsert_model_registry_row,
        upsert_organization_row,
        upsert_user_row,
        _GET_PROMPT_BLOCK_SQL,
        _GET_STEP_SQL,
        _LIST_PROMPT_BLOCKS_SQL,
        _LIST_STEPS_SQL,
        _UPSERT_PROMPT_BLOCK_SQL,
        _UPSERT_STEP_SQL,
        get_prompt_block_row,
        get_step_row,
        hydrate_prompt_block_row,
        hydrate_step_row,
        upsert_prompt_block_row,
        upsert_step_row,
        _GET_OUTPUT_PROFILE_SQL,
        _GET_WORKFLOW_SQL,
        _LIST_OUTPUT_PROFILES_SQL,
        _LIST_WORKFLOWS_SQL,
        _UPSERT_OUTPUT_PROFILE_SQL,
        _UPSERT_WORKFLOW_SQL,
        get_output_profile_row,
        get_workflow_row,
        hydrate_output_profile_row,
        hydrate_workflow_row,
        upsert_output_profile_row,
        upsert_workflow_row,
        seed_collection_batch_rows,
        verify_seed_table_counts_rows,
    )
    for sym in reexported_symbols:
        assert sym is not None
    assert PostgresEntityAdapter._hydrate_execution_row is hydrate_execution_row
    assert PostgresEntityAdapter._hydrate_organization_row is hydrate_organization_row
    assert PostgresEntityAdapter._hydrate_user_row is hydrate_user_row
    assert PostgresEntityAdapter._hydrate_model_registry_row is hydrate_model_registry_row
    assert PostgresEntityAdapter._hydrate_mcp_gateway_row is hydrate_mcp_gateway_row
    assert PostgresEntityAdapter._hydrate_prompt_block_row is hydrate_prompt_block_row
    assert PostgresEntityAdapter._hydrate_step_row is hydrate_step_row
    assert PostgresEntityAdapter._hydrate_workflow_row is hydrate_workflow_row
    assert PostgresEntityAdapter._hydrate_output_profile_row is hydrate_output_profile_row
    assert PostgresEntityAdapter._hydrate_report_artifact_row is hydrate_report_artifact_row


@pytest.mark.asyncio
async def test_entity_adapter_protocol_and_settings_propagation(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify EntityPersistencePort conformance and get_settings() timeout propagation."""
    pool = InMemoryAsyncPgPool()
    conn = await pool.acquire()
    try:
        explicit_adapter = PostgresEntityAdapter(connection=conn, command_timeout_seconds=12.5)
        assert isinstance(explicit_adapter, EntityPersistencePort)
        assert explicit_adapter.command_timeout_seconds == 12.5
        custom_settings = get_settings().model_copy(update={"postgres_command_timeout_seconds": 19.75})
        monkeypatch.setattr(entity_adapter_mod, "get_settings", lambda: custom_settings)
        default_adapter = PostgresEntityAdapter(connection=conn)
        assert isinstance(default_adapter, EntityPersistencePort)
        assert default_adapter.command_timeout_seconds == 19.75
    finally:
        await pool.release(conn)


@pytest.mark.asyncio
async def test_entity_adapter_full_end_to_end_facade_delegation() -> None:
    """Verify end-to-end delegation across all typed PostgresEntityAdapter methods including ledgers."""
    pool = InMemoryAsyncPgPool()
    conn = await pool.acquire()
    try:
        adapter = PostgresEntityAdapter(connection=conn, command_timeout_seconds=5.0)
        org = _build_org()
        user = _build_user(org.id)
        cfg = _build_registry_config()
        extra_cfg = _build_registry_config()
        gw = _build_mcp_gateway(org.id)
        blk = SystemRulePromptBlockFactory.build(organization_id=org.id)
        tbr = TaskBriefFactory.build(organization_id=org.id, source_url="https://quorum.ai/brief")
        step = _build_step(blk.id, org.id)
        wf = WorkflowFactory.build(organization_id=org.id, model_registry_id=cfg.id)
        prf = OutputProfileFactory.build(workflow_id=wf.id, organization_id=org.id, content_blocks=[])
        exec_rec = ExecutionRecordFactory.build(
            workflow_id=wf.id, organization_id=org.id, active_profile_id=prf.id, output_profile_id=prf.id
        )
        rep = ReportArtifactFactory.build(execution_id=exec_rec.id, workflow_id=wf.id, profile_id=prf.id)
        bin_dto = ReportBinaryPayloadDTO(
            report_id=rep.id,
            mime_type="application/pdf",
            pdf_bytes=b"%PDF-1.7 facade",
            size_bytes=15,
            created_at=rep.created_at,
        )
        sec = TenantSecretDTO(
            id=generate_opaque_id(EntityPrefix.TENANT_SECRET),
            organization_id=org.id,
            scope=SecretScope.LLM_PROVIDER,
            target_identifier="ai_studio",
            storage_mode=SecretStorageMode.ENVELOPE_KMS,
            kek_version="kek-v1",
            masked_hint="****1234",
            updated_by=user.id,
            updated_at=datetime.now(UTC),
        )
        aud = AuditLogRecordFactory.build(
            organization_id=org.id,
            actor_id=user.id,
            execution_id=exec_rec.id,
            event_type="EXECUTION_CREATED",
            resource_type="execution",
            resource_id=exec_rec.id,
        )
        usg = UsageRecordFactory.build(
            org_id=org.id,
            user_id=user.id,
            execution_id=exec_rec.id,
            input_tokens=150,
            output_tokens=50,
            cost_usd=0.04,
        )

        assert await adapter.upsert_organization(org) == org.id
        fetched_org = await adapter.get_organization(org.id)
        assert fetched_org is not None and fetched_org.id == org.id and fetched_org.slug == org.slug
        assert await adapter.upsert_user(user) == user.id
        fetched_user = await adapter.get_user(user.id)
        assert fetched_user is not None and fetched_user.id == user.id and fetched_user.organization_id == org.id
        assert await adapter.upsert_tenant_secret(sec) == sec.id
        assert await adapter.delete_tenant_secret(sec.id) is True
        assert await adapter.delete_tenant_secret(sec.id) is False
        assert await adapter.upsert_model_registry(cfg) == cfg.id
        assert await adapter.get_model_registry(cfg.id) == cfg
        assert await adapter.list_model_registries() == [cfg]
        assert await adapter.upsert_model_registry(extra_cfg) == extra_cfg.id
        assert await adapter.delete_model_registry(extra_cfg.id) is True
        assert await adapter.delete_model_registry(extra_cfg.id) is False
        assert await adapter.upsert_mcp_gateway(gw) == gw.id
        assert await adapter.get_mcp_gateway(gw.id) == gw
        assert await adapter.list_mcp_gateways() == [gw]
        assert await adapter.delete_mcp_gateway(gw.id) is True
        assert await adapter.delete_mcp_gateway(gw.id) is False
        assert await adapter.upsert_prompt_block(blk) == blk.id
        assert await adapter.get_prompt_block(blk.id) == blk
        assert await adapter.upsert_task_brief(tbr) == tbr.id
        assert await adapter.get_task_brief(tbr.id) == tbr
        assert await adapter.list_task_briefs() == [tbr]
        assert await adapter.upsert_step(step) == step.id
        assert await adapter.get_step(step.id) == step
        assert await adapter.upsert_workflow(wf) == wf.id
        assert await adapter.get_workflow(wf.id) == wf
        assert await adapter.upsert_output_profile(prf) == prf.id
        assert await adapter.get_output_profile(prf.id) == prf
        assert await adapter.save_execution(exec_rec) == exec_rec.id
        fetched_exec = await adapter.get_execution(exec_rec.id)
        assert fetched_exec is not None and fetched_exec.id == exec_rec.id
        assert len(await adapter.list_executions()) == 1
        assert await adapter.upsert_report_artifact(rep) == rep.id
        assert await adapter.get_report_artifact(rep.id) == rep
        await adapter.save_report_binary(bin_dto)
        assert await adapter.get_report_binary(rep.id) == bin_dto

        assert await adapter.insert_audit_log(aud) == aud.id
        assert len(await adapter.list_audit_logs(organization_id=org.id)) == 1
        assert await adapter.insert_usage_record(usg) == usg.id
        assert len(await adapter.list_usage_records(organization_id=org.id)) == 1
        rollup = await adapter.aggregate_organization_usage(organization_id=org.id)
        assert rollup.record_count == 1
        assert rollup.total_prompt_tokens == 150
        assert rollup.total_cost_usd == pytest.approx(0.04)

        raw_org_uuid = parse_prefixed_uuid7(org.id, EntityPrefix.ORGANIZATION)
        upserted_id = await adapter._execute_upsert(
            _UPSERT_ORGANIZATION_SQL,
            raw_org_uuid,
            org.slug,
            org.name,
            org.is_active,
            org.tier,
            org.contact_email,
            org.billing_id,
            org.subscription_status.value,
            org.quota_limit,
            org.tpm_limit,
            org.rpm_limit,
            entity_label="organization",
            entity_id=org.id,
        )
        assert upserted_id == org.id
        assert await adapter.seed_collection_batch("organizations", [org]) == 1
        assert (await adapter.verify_seed_table_counts({"organizations": 1}))["organizations"] == 1
    finally:
        await pool.release(conn)


@pytest.mark.asyncio
async def test_entity_adapter_facade_negative_invalid_inputs_and_missing_entities() -> None:
    """Verify invalid prefixes, size boundary mismatches (BVA min-1/max+1), and missing lookups via facade."""
    pool = InMemoryAsyncPgPool()
    conn = await pool.acquire()
    try:
        adapter = PostgresEntityAdapter(connection=conn, command_timeout_seconds=5.0)
        assert await adapter.get_organization(generate_opaque_id(EntityPrefix.ORGANIZATION)) is None
        assert await adapter.get_execution(generate_opaque_id(EntityPrefix.EXECUTION)) is None
        assert await adapter.get_report_binary(generate_opaque_id(EntityPrefix.REPORT)) is None

        with pytest.raises(AppException) as bad_prefix_err:
            await adapter.get_organization("usr_0195f3a0000070008000000000000001")
        assert bad_prefix_err.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

        with pytest.raises(AppException) as bad_sec_err:
            await adapter.delete_tenant_secret("usr_0195f3a0000070008000000000000001")
        assert bad_sec_err.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

        pdf_payload = b"%PDF-1.7"
        for invalid_size in (len(pdf_payload) - 1, len(pdf_payload) + 1):
            bad_bin = ReportBinaryPayloadDTO(
                report_id=generate_opaque_id(EntityPrefix.REPORT),
                mime_type="application/pdf",
                pdf_bytes=pdf_payload,
                size_bytes=invalid_size,
                created_at=datetime.now(UTC),
            )
            with pytest.raises(AppException) as size_err:
                await adapter.save_report_binary(bad_bin)
            assert size_err.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

        with pytest.raises(AppException) as col_err:
            await adapter.seed_collection_batch("invalid_collection", [_build_org()])
        assert col_err.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    finally:
        await pool.release(conn)


@pytest.mark.asyncio
async def test_entity_adapter_facade_negative_driver_fault_and_count_boundary_violations() -> None:
    """Verify count threshold boundary (actual < expected) and injected driver faults raise AppException."""
    pool = InMemoryAsyncPgPool()
    conn = await pool.acquire()
    try:
        adapter = PostgresEntityAdapter(connection=conn, command_timeout_seconds=5.0)
        org = _build_org()
        with pytest.raises(AppException) as count_err:
            await adapter.verify_seed_table_counts({"organizations": 1})
        assert count_err.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value

        pool.inject_fault("execute", RuntimeError("simulated connection drop on execute"))
        with pytest.raises(AppException) as upsert_err:
            await adapter.upsert_organization(org)
        assert upsert_err.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value

        pool.clear_faults()
        pool.inject_fault("fetchrow", RuntimeError("simulated connection drop on fetchrow"))
        with pytest.raises(AppException) as get_err:
            await adapter.get_organization(org.id)
        assert get_err.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value
    finally:
        pool.clear_faults()
        await pool.release(conn)
