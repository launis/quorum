"""Unit and boundary tests for PostgreSQL 19 Seed Batching, Ledger Persistence, and Tenant Secret Deletion.

Covers seed_collection_batch_rows across all 16 batchable collections (including audit_logs and usage_records),
verify_seed_table_counts_rows, append-only audit_logs and usage_records operations, SQL FinOps rollups,
delete_tenant_secret_row, negative boundaries, and driver fault translation.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from backend_v2.database.postgres.entity_adapter.iam_and_system_stage import (
    aggregate_organization_usage_row,
    delete_tenant_secret_row,
    insert_audit_log_row,
    insert_usage_record_row,
    list_audit_log_rows,
    list_mcp_gateway_rows,
    list_model_registry_rows,
    list_usage_record_rows,
    upsert_tenant_secret_row,
)
from backend_v2.database.postgres.entity_adapter.seed_and_collection_stage import (
    seed_collection_batch_rows,
    verify_seed_table_counts_rows,
)
from backend_v2.database.postgres.pool import AsyncPgRecordProtocol
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.auth import (
    ExecutionAssignment,
    Invitation,
    Organization,
    SubscriptionStatus,
    TenantSecretDTO,
    User,
    UserRole,
)
from backend_v2.models.core_base import I18nText, generate_opaque_id
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.domain.proposition_graph import ReportBinaryPayloadDTO
from backend_v2.models.domain.step import Step
from backend_v2.models.domain.system_config import (
    AllowedMCPTool,
    ModelProfile,
    SystemConfigMCPGateways,
    SystemConfigModelRegistry,
)
from backend_v2.models.enums import (
    AssignmentResultVisibility,
    AssignmentStatus,
    CognitiveTier,
    EmailDeliveryStatus,
    EngineType,
    EntityPrefix,
    InvitationStatus,
    LLMProvider,
    MCPAuthType,
    MCPTransportType,
    SecretScope,
    SecretStorageMode,
    StepType,
    StepZone,
    SystemLocale,
)
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

_TIMEOUT: float = 5.0


def _build_org(org_id: str | None = None) -> Organization:
    """Build a valid Organization domain model for testing."""
    return Organization(
        id=org_id if org_id is not None else generate_opaque_id(EntityPrefix.ORGANIZATION),
        slug="seed-org",
        name="Seed Organization",
        created_at=datetime.now(UTC),
        is_active=True,
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=100000,
        rpm_limit=1000,
        allowed_email_domains=[],
    )


def _build_user(org_id: str) -> User:
    """Build a valid User domain model for testing."""
    return User(
        id=generate_opaque_id(EntityPrefix.USER),
        slug="seed-user",
        email="seed@quorum.ai",
        name="Seed User",
        role=UserRole.ADMIN,
        organization_id=org_id,
        is_active=True,
        language=SystemLocale.EN,
        theme_mode="dark",
        created_at=datetime.now(UTC),
        created_by="usr_0195f3a00000700a83fd6b3d77c748f4",
    )


def _build_registry_config() -> SystemConfigModelRegistry:
    """Build a valid SystemConfigModelRegistry for testing."""
    profile = ModelProfile(provider="ai_studio", model_name="gemini-2.5-flash")
    return SystemConfigModelRegistry(
        id=generate_opaque_id(EntityPrefix.MODEL_REGISTRY),
        name="Seed Registry",
        default_provider=LLMProvider.AI_STUDIO,
        tier_definitions={tier: profile for tier in CognitiveTier},
    )


def _build_mcp_config(org_id: str) -> SystemConfigMCPGateways:
    """Build a valid SystemConfigMCPGateways for testing."""
    return SystemConfigMCPGateways(
        id=generate_opaque_id(EntityPrefix.MCP_GATEWAY),
        organization_id=org_id,
        name="Seed MCP Gateway",
        slug="seed_mcp_gateway",
        endpoint_url="https://mcp.quorum.local/v1",
        transport_type=MCPTransportType.STREAMABLE_HTTP,
        auth_type=MCPAuthType.NONE,
        timeout_seconds=30,
        tools=[
            AllowedMCPTool(
                tool_id="search_docs",
                name=I18nText(translations={"en": "Search Docs", "fi": "Hae Dokumentit"}),
                description="Search documentation.",
            )
        ],
    )


def _build_step(block_id: str, org_id: str) -> Step:
    """Build a valid Step domain model for testing."""
    return Step(
        id=generate_opaque_id(EntityPrefix.STEP),
        slug="seed_step",
        organization_id=org_id,
        name=I18nText(translations={"en": "Seed Step", "fi": "Siemenvaihe"}),
        description=I18nText(translations={"en": "Step Description", "fi": "Kuvaus"}),
        type=StepType.LLM,
        extraction_protocol_block_id=block_id,
        criteria_block_ids=[block_id],
        cognitive_tier=CognitiveTier.FAST,
        engine_type=EngineType.PROMPT,
        zone=StepZone.ZONE_B,
        mcp_tool_params={},
    )


def _build_invitation(org_id: str, invited_by: str) -> Invitation:
    """Build a valid Invitation domain model for testing."""
    now = datetime.now(UTC)
    return Invitation(
        id=generate_opaque_id(EntityPrefix.INVITATION),
        organization_id=org_id,
        email="invitee@quorum.ai",
        role=UserRole.MEMBER,
        token_hash="a" * 64,
        status=InvitationStatus.PENDING,
        email_delivery_status=EmailDeliveryStatus.SENT,
        invited_by=invited_by,
        expires_at=now + timedelta(days=7),
        created_at=now,
    )


def _build_tenant_secret(org_id: str) -> TenantSecretDTO:
    """Build a valid TenantSecretDTO domain model for testing."""
    return TenantSecretDTO(
        id=generate_opaque_id(EntityPrefix.TENANT_SECRET),
        organization_id=org_id,
        scope=SecretScope.LLM_PROVIDER,
        target_identifier="ai_studio",
        storage_mode=SecretStorageMode.ENVELOPE_KMS,
        encrypted_dek=b"wrapped-dek",
        ciphertext=b"encrypted-secret",
        nonce=b"12byte-nonce",
        kek_version="projects/quorum/locations/europe-north1/keyRings/byok/cryptoKeys/master/cryptoKeyVersions/1",
        masked_hint="AIza...9999",
        updated_by=generate_opaque_id(EntityPrefix.USER),
        updated_at=datetime.now(UTC),
    )


def _build_assignment(org_id: str, created_by: str, wf_id: str, prf_id: str) -> ExecutionAssignment:
    """Build a valid ExecutionAssignment domain model for testing."""
    now = datetime.now(UTC)
    return ExecutionAssignment(
        id=generate_opaque_id(EntityPrefix.ASSIGNMENT),
        batch_id=generate_opaque_id(EntityPrefix.ASSIGNMENT),
        organization_id=org_id,
        assigned_email="candidate@quorum.ai",
        assigned_user_id=None,
        invited_role=UserRole.MEMBER,
        workflow_id=wf_id,
        output_profile_id=prf_id,
        target_locale=SystemLocale.FI,
        locked_inputs=WorkflowInputs(dynamic_inputs={"role_context": "Architect"}),
        assignee_input_keys=["essay"],
        draft_inputs=WorkflowInputs(dynamic_inputs={"essay": "Draft"}),
        token_hash="b" * 64,
        status=AssignmentStatus.PENDING,
        email_delivery_status=EmailDeliveryStatus.SENT,
        result_visibility=AssignmentResultVisibility.CONFIRMATION_ONLY,
        hard_deadline_at=now + timedelta(days=3),
        relative_duration_seconds=3600,
        activated_at=None,
        submitted_at=None,
        execution_id=None,
        created_by=created_by,
        created_at=now,
    )


@pytest.mark.asyncio
async def test_seed_collection_batch_and_verify_counts_roundtrip_parity() -> None:
    """Verify seed_collection_batch_rows and verify_seed_table_counts_rows across all 16 batchable tables."""
    pool = InMemoryAsyncPgPool()
    conn = await pool.acquire()
    try:
        org = _build_org()
        user = _build_user(org.id)
        inv = _build_invitation(org.id, user.id)
        sec = _build_tenant_secret(org.id)
        reg_cfg = _build_registry_config()
        mcp_cfg = _build_mcp_config(org.id)
        blk = SystemRulePromptBlockFactory.build(organization_id=org.id)
        tbr = TaskBriefFactory.build(organization_id=org.id)
        step = _build_step(blk.id, org.id)
        wf = WorkflowFactory.build(organization_id=org.id, model_registry_id=reg_cfg.id)
        prf = OutputProfileFactory.build(workflow_id=wf.id, organization_id=org.id, content_blocks=[])
        asg = _build_assignment(org.id, user.id, wf.id, prf.id)
        exec_rec = ExecutionRecordFactory.build(
            workflow_id=wf.id,
            organization_id=org.id,
            active_profile_id=prf.id,
            output_profile_id=prf.id,
        )
        rep = ReportArtifactFactory.build(execution_id=exec_rec.id, workflow_id=wf.id, profile_id=prf.id)
        bin_dto = ReportBinaryPayloadDTO(
            report_id=rep.id,
            mime_type="application/pdf",
            pdf_bytes=b"%PDF-1.7",
            size_bytes=8,
            created_at=datetime.now(UTC),
        )
        aud_rec = AuditLogRecordFactory.build(
            organization_id=org.id,
            actor_id=user.id,
            execution_id=exec_rec.id,
            event_type="EXECUTION_STARTED",
            resource_type="execution",
            resource_id=exec_rec.id,
        )
        usg_rec = UsageRecordFactory.build(
            org_id=org.id,
            user_id=user.id,
            execution_id=exec_rec.id,
            input_tokens=120,
            output_tokens=60,
            cached_tokens=30,
            cost_usd=0.05,
        )

        assert await seed_collection_batch_rows(conn, _TIMEOUT, "organizations", [org]) == 1
        assert await seed_collection_batch_rows(conn, _TIMEOUT, "users", [user]) == 1
        assert await seed_collection_batch_rows(conn, _TIMEOUT, "invitations", [inv]) == 1
        assert await seed_collection_batch_rows(conn, _TIMEOUT, "tenant_secrets", [sec]) == 1
        assert await seed_collection_batch_rows(conn, _TIMEOUT, "execution_assignments", [asg]) == 1
        assert await seed_collection_batch_rows(conn, _TIMEOUT, "model_registries", [reg_cfg]) == 1
        assert await seed_collection_batch_rows(conn, _TIMEOUT, "mcp_gateways", [mcp_cfg]) == 1
        assert await seed_collection_batch_rows(conn, _TIMEOUT, "prompt_blocks", [blk]) == 1
        assert await seed_collection_batch_rows(conn, _TIMEOUT, "task_briefs", [tbr]) == 1
        assert await seed_collection_batch_rows(conn, _TIMEOUT, "steps", [step]) == 1
        assert await seed_collection_batch_rows(conn, _TIMEOUT, "workflows", [wf]) == 1
        assert await seed_collection_batch_rows(conn, _TIMEOUT, "output_profiles", [prf]) == 1
        assert await seed_collection_batch_rows(conn, _TIMEOUT, "executions", [exec_rec]) == 1
        assert await seed_collection_batch_rows(conn, _TIMEOUT, "report_artifacts", [rep]) == 1
        assert await seed_collection_batch_rows(conn, _TIMEOUT, "report_binaries", [bin_dto]) == 1
        assert await seed_collection_batch_rows(conn, _TIMEOUT, "audit_logs", [aud_rec]) == 1
        assert await seed_collection_batch_rows(conn, _TIMEOUT, "usage_records", [usg_rec]) == 1

        counts = await verify_seed_table_counts_rows(
            conn,
            _TIMEOUT,
            {
                "organizations": 1,
                "users": 1,
                "model_registries": 1,
                "mcp_gateways": 1,
                "prompt_blocks": 1,
                "task_briefs": 1,
                "steps": 1,
                "workflows": 1,
                "output_profiles": 1,
                "executions": 1,
                "report_artifacts": 1,
                "report_binaries": 1,
            },
        )
        assert counts["organizations"] == 1
        assert counts["model_registries"] == 1
        assert counts["mcp_gateways"] == 1
        assert len(await list_audit_log_rows(conn, _TIMEOUT)) == 1
        assert len(await list_usage_record_rows(conn, _TIMEOUT)) == 1
        assert len(await list_model_registry_rows(conn, _TIMEOUT)) == 1
        assert len(await list_mcp_gateway_rows(conn, _TIMEOUT)) == 1
    finally:
        await pool.release(conn)


@pytest.mark.asyncio
async def test_audit_usage_ledgers_rollup_and_delete_tenant_secret() -> None:
    """Verify append-only audit_logs, usage_records, SQL SUM/COUNT rollup, and delete_tenant_secret_row."""
    pool = InMemoryAsyncPgPool()
    conn = await pool.acquire()
    try:
        org = _build_org()
        user = _build_user(org.id)
        sec = _build_tenant_secret(org.id)
        await seed_collection_batch_rows(conn, _TIMEOUT, "organizations", [org])
        await seed_collection_batch_rows(conn, _TIMEOUT, "users", [user])
        await upsert_tenant_secret_row(conn, _TIMEOUT, sec)

        assert await delete_tenant_secret_row(conn, _TIMEOUT, sec.id) is True
        assert await delete_tenant_secret_row(conn, _TIMEOUT, sec.id) is False

        sys_audit = AuditLogRecordFactory.build(
            organization_id="system",
            actor_id="system",
            event_type="SYSTEM_BOOT",
            resource_type="system",
            resource_id="bootstrap",
        )
        org_audit = AuditLogRecordFactory.build(
            organization_id=org.id,
            actor_id=user.id,
            event_type="SECRET_ROTATED",
            resource_type="tenant_secret",
            resource_id=sec.id,
        )
        assert await insert_audit_log_row(conn, _TIMEOUT, sys_audit) == sys_audit.id
        assert await insert_audit_log_row(conn, _TIMEOUT, org_audit) == org_audit.id

        filtered_audits = await list_audit_log_rows(
            conn,
            _TIMEOUT,
            organization_id=org.id,
            actor_id=user.id,
            event_type="SECRET_ROTATED",
        )
        assert len(filtered_audits) == 1
        assert filtered_audits[0].id == org_audit.id

        now = datetime.now(UTC)
        u1 = UsageRecordFactory.build(
            org_id=org.id,
            user_id=user.id,
            input_tokens=100,
            output_tokens=40,
            cached_tokens=20,
            reasoning_tokens=10,
            cache_creation_input_tokens=5,
            cost_usd=0.12,
            estimated_savings_usd=0.03,
            timestamp=now,
        )
        u2 = UsageRecordFactory.build(
            org_id=org.id,
            user_id="system",
            input_tokens=200,
            output_tokens=60,
            cached_tokens=50,
            reasoning_tokens=15,
            cache_creation_input_tokens=0,
            cost_usd=0.18,
            estimated_savings_usd=0.07,
            timestamp=now,
        )
        assert await insert_usage_record_row(conn, _TIMEOUT, u1) == u1.id
        assert await insert_usage_record_row(conn, _TIMEOUT, u2) == u2.id

        listed_usage = await list_usage_record_rows(conn, _TIMEOUT, organization_id=org.id)
        assert len(listed_usage) == 2

        rollup = await aggregate_organization_usage_row(
            conn,
            _TIMEOUT,
            organization_id=org.id,
            since=now - timedelta(hours=1),
        )
        assert rollup.record_count == 2
        assert rollup.total_prompt_tokens == 300
        assert rollup.total_completion_tokens == 100
        assert rollup.total_cached_tokens == 70
        assert rollup.total_reasoning_tokens == 25
        assert rollup.total_cache_creation_input_tokens == 5
        assert rollup.total_cost_usd == pytest.approx(0.30)
        assert rollup.total_estimated_savings_usd == pytest.approx(0.10)
    finally:
        await pool.release(conn)


@pytest.mark.asyncio
async def test_verify_seed_table_counts_handles_null_fetchrow_and_boundaries_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify verify_seed_table_counts_rows handles None from fetchrow and raises on invalid boundaries."""
    pool = InMemoryAsyncPgPool()
    conn = await pool.acquire()
    try:
        org = _build_org()
        with pytest.raises(AppException) as bad_col_err:
            await seed_collection_batch_rows(conn, _TIMEOUT, "nonexistent_col", [org])
        assert bad_col_err.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

        with pytest.raises(AppException) as bad_type_err:
            await seed_collection_batch_rows(conn, _TIMEOUT, "users", [org])
        assert bad_type_err.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

        with pytest.raises(AppException) as bad_audit_type_err:
            await seed_collection_batch_rows(conn, _TIMEOUT, "audit_logs", [org])
        assert bad_audit_type_err.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

        with pytest.raises(AppException) as bad_usage_type_err:
            await seed_collection_batch_rows(conn, _TIMEOUT, "usage_records", [org])
        assert bad_usage_type_err.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

        with pytest.raises(AppException) as unknown_tbl_err:
            await verify_seed_table_counts_rows(conn, _TIMEOUT, {"unknown_tbl": 0})
        assert unknown_tbl_err.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

        with pytest.raises(AppException) as low_count_err:
            await verify_seed_table_counts_rows(conn, _TIMEOUT, {"organizations": 1})
        assert low_count_err.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value

        async def _return_none_row(*args: object, **kwargs: object) -> AsyncPgRecordProtocol | None:
            _ = (args, kwargs)
            return None

        monkeypatch.setattr(conn, "fetchrow", _return_none_row)
        zero_counts = await verify_seed_table_counts_rows(conn, _TIMEOUT, {"organizations": 0})
        assert zero_counts["organizations"] == 0
    finally:
        await pool.release(conn)


@pytest.mark.asyncio
async def test_seed_and_ledger_fault_translation_failure() -> None:
    """Verify driver faults in verify_seed_table_counts, list_system_configs, insert, and delete raise AppException."""
    pool = InMemoryAsyncPgPool()
    sec_id = generate_opaque_id(EntityPrefix.TENANT_SECRET)
    aud_rec = AuditLogRecordFactory.build()
    direct_app_err = AppException(
        message="pre-existing storage error",
        status_code=500,
        details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
    )
    conn = await pool.acquire()
    try:
        pool.inject_fault("fetch", RuntimeError("simulated fetch failure"))
        with pytest.raises(AppException) as list_exc:
            await list_model_registry_rows(conn, _TIMEOUT)
        assert list_exc.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value

        pool.inject_fault("fetch", direct_app_err)
        with pytest.raises(AppException) as direct_list_exc:
            await list_mcp_gateway_rows(conn, _TIMEOUT)
        assert direct_list_exc.value is direct_app_err

        pool.clear_faults()
        pool.inject_fault("fetchrow", RuntimeError("simulated fetchrow failure"))
        with pytest.raises(AppException) as count_exc:
            await verify_seed_table_counts_rows(conn, _TIMEOUT, {"organizations": 0})
        assert count_exc.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value

        pool.inject_fault("fetchrow", direct_app_err)
        with pytest.raises(AppException) as direct_count_exc:
            await verify_seed_table_counts_rows(conn, _TIMEOUT, {"organizations": 0})
        assert direct_count_exc.value is direct_app_err

        pool.clear_faults()
        pool.inject_fault("execute", RuntimeError("simulated execute failure"))
        with pytest.raises(AppException) as insert_exc:
            await insert_audit_log_row(conn, _TIMEOUT, aud_rec)
        assert insert_exc.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value

        with pytest.raises(AppException) as del_exc:
            await delete_tenant_secret_row(conn, _TIMEOUT, sec_id)
        assert del_exc.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value

        pool.inject_fault("execute", direct_app_err)
        with pytest.raises(AppException) as direct_del_exc:
            await delete_tenant_secret_row(conn, _TIMEOUT, sec_id)
        assert direct_del_exc.value is direct_app_err
    finally:
        pool.clear_faults()
        await pool.release(conn)
