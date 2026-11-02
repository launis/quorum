"""Unit and boundary tests for PostgreSQL 19 Seed Batching and Collection CRUD stage.

Covers seed_collection_batch_rows, verify_seed_table_counts_rows, and collection
CRUD operations across all 10 canonical tables, including negative boundaries and
driver fault translation.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from backend_v2.database.postgres.entity_adapter.coercion_and_constants import (
    _TABLE_TO_ENTITY_PREFIX,
)
from backend_v2.database.postgres.entity_adapter.seed_and_collection_stage import (
    clear_collection_documents_rows,
    delete_collection_document_row,
    get_collection_document_row,
    list_collection_documents_rows,
    seed_collection_batch_rows,
    upsert_collection_document_row,
    verify_seed_table_counts_rows,
)
from backend_v2.database.postgres.pool import AsyncPgRecordProtocol
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.auth import Organization, SubscriptionStatus, User, UserRole
from backend_v2.models.core_base import I18nText, generate_opaque_id
from backend_v2.models.domain.proposition_graph import ReportBinaryPayloadDTO
from backend_v2.models.domain.step import Step
from backend_v2.models.domain.system_config import (
    AllowedMCPTool,
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
    StepType,
    StepZone,
    SystemLocale,
)
from backend_v2.tests.factories.model_factories import (
    ExecutionRecordFactory,
    OutputProfileFactory,
    ReportArtifactFactory,
    SystemRulePromptBlockFactory,
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
    profile = ModelProfile(provider="google", model_name="gemini-2.5-flash")
    return SystemConfigModelRegistry(
        id=generate_opaque_id(EntityPrefix.SYSTEM_CONFIG),
        name="Seed Registry",
        type="model_registry",
        default_provider=LLMProvider.AI_STUDIO,
        tier_definitions={tier: profile for tier in CognitiveTier},
    )


def _build_mcp_config() -> SystemConfigMCPGateways:
    """Build a valid SystemConfigMCPGateways for testing."""
    return SystemConfigMCPGateways(
        id=generate_opaque_id(EntityPrefix.SYSTEM_CONFIG),
        type="mcp_gateways",
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
    )


@pytest.mark.asyncio
async def test_execution_report_and_seed_collection_roundtrip_parity() -> None:
    """Verify seed_collection_batch_rows and verify_seed_table_counts_rows across all 10 tables."""
    pool = InMemoryAsyncPgPool()
    conn = await pool.acquire()
    try:
        org = _build_org()
        user = _build_user(org.id)
        reg_cfg = _build_registry_config()
        mcp_cfg = _build_mcp_config()
        blk = SystemRulePromptBlockFactory.build(organization_id=org.id)
        step = _build_step(blk.id, org.id)
        wf = WorkflowFactory.build(organization_id=org.id, model_registry_id=reg_cfg.id)
        prf = OutputProfileFactory.build(workflow_id=wf.id, organization_id=org.id, content_blocks=[])
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

        assert await seed_collection_batch_rows(conn, _TIMEOUT, "organizations", [org]) == 1
        assert await seed_collection_batch_rows(conn, _TIMEOUT, "users", [user]) == 1
        assert await seed_collection_batch_rows(conn, _TIMEOUT, "system_configs", [reg_cfg, mcp_cfg]) == 2
        assert await seed_collection_batch_rows(conn, _TIMEOUT, "prompt_blocks", [blk]) == 1
        assert await seed_collection_batch_rows(conn, _TIMEOUT, "steps", [step]) == 1
        assert await seed_collection_batch_rows(conn, _TIMEOUT, "workflows", [wf]) == 1
        assert await seed_collection_batch_rows(conn, _TIMEOUT, "output_profiles", [prf]) == 1
        assert await seed_collection_batch_rows(conn, _TIMEOUT, "executions", [exec_rec]) == 1
        assert await seed_collection_batch_rows(conn, _TIMEOUT, "report_artifacts", [rep]) == 1
        assert await seed_collection_batch_rows(conn, _TIMEOUT, "report_binaries", [bin_dto]) == 1

        counts = await verify_seed_table_counts_rows(
            conn,
            _TIMEOUT,
            {
                "organizations": 1,
                "users": 1,
                "system_config": 2,
                "prompt_blocks": 1,
                "steps": 1,
                "workflows": 1,
                "output_profiles": 1,
                "executions": 1,
                "report_artifacts": 1,
                "report_binaries": 1,
            },
        )
        assert counts["organizations"] == 1
        assert counts["system_configs"] == 2
        assert counts["report_binaries"] == 1
    finally:
        await pool.release(conn)


@pytest.mark.asyncio
async def test_collection_crud_across_all_canonical_tables(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify list, get, upsert, delete, and clear collection documents across all canonical tables."""
    pool = InMemoryAsyncPgPool()
    conn = await pool.acquire()
    try:
        org = _build_org()
        sys_org = _build_org("org_0195f3a0000070008000000000000001")
        user = _build_user(org.id)
        reg_cfg = _build_registry_config()
        mcp_cfg = _build_mcp_config()
        blk = SystemRulePromptBlockFactory.build(organization_id=org.id)
        step = _build_step(blk.id, org.id)
        wf = WorkflowFactory.build(organization_id=org.id, model_registry_id=reg_cfg.id)
        prf = OutputProfileFactory.build(workflow_id=wf.id, organization_id=org.id, content_blocks=[])
        exec_rec = ExecutionRecordFactory.build(
            workflow_id=wf.id,
            organization_id=org.id,
            active_profile_id=prf.id,
            output_profile_id=prf.id,
        )
        rep = ReportArtifactFactory.build(execution_id=exec_rec.id, workflow_id=wf.id, profile_id=prf.id)

        records_by_col = (
            ("organizations", org.id, org.model_dump(mode="json")),
            ("organizations", sys_org.id, sys_org.model_dump(mode="json")),
            ("users", user.id, user.model_dump(mode="json")),
            ("system_configs", reg_cfg.id, reg_cfg.model_dump(mode="json")),
            ("system_configs", mcp_cfg.id, mcp_cfg.model_dump(mode="json")),
            ("prompt_blocks", blk.id, blk.model_dump(mode="json")),
            ("steps", step.id, step.model_dump(mode="json")),
            ("workflows", wf.id, wf.model_dump(mode="json")),
            ("output_profiles", prf.id, prf.model_dump(mode="json")),
            ("executions", exec_rec.id, exec_rec.model_dump(mode="json")),
            ("report_artifacts", rep.id, rep.model_dump(mode="json")),
        )
        for col_name, doc_id, doc_payload in records_by_col:
            assert await upsert_collection_document_row(conn, _TIMEOUT, col_name, doc_id, doc_payload) is True
            fetched = await get_collection_document_row(conn, _TIMEOUT, col_name, doc_id)
            assert fetched is not None
            assert fetched["id"] == doc_id
            listed = await list_collection_documents_rows(conn, _TIMEOUT, col_name)
            assert any(d["id"] == doc_id for d in listed)

        # Verify report_binaries table (mapped in _COLLECTION_TO_TABLE_MAP but not a JSON document collection)
        assert await list_collection_documents_rows(conn, _TIMEOUT, "report_binaries") == []
        assert await get_collection_document_row(conn, _TIMEOUT, "report_binaries", rep.id) is None
        assert await upsert_collection_document_row(conn, _TIMEOUT, "report_binaries", rep.id, {}) is False

        # Verify unmapped collection_name and invalid ID/payload branches across collection CRUD
        assert await list_collection_documents_rows(conn, _TIMEOUT, "unknown_col") == []
        assert await get_collection_document_row(conn, _TIMEOUT, "unknown_col", org.id) is None
        assert await get_collection_document_row(conn, _TIMEOUT, "organizations", "org_invalid") is None
        assert await upsert_collection_document_row(conn, _TIMEOUT, "unknown_col", org.id, {}) is False
        assert await upsert_collection_document_row(conn, _TIMEOUT, "organizations", org.id, {"bad": 1}) is False
        assert (
            await upsert_collection_document_row(
                conn, _TIMEOUT, "organizations", "org_invalid", org.model_dump(mode="json")
            )
            is False
        )
        assert await delete_collection_document_row(conn, _TIMEOUT, "unknown_col", org.id) is False
        assert await delete_collection_document_row(conn, _TIMEOUT, "organizations", "org_invalid") is False
        await clear_collection_documents_rows(conn, _TIMEOUT, "unknown_col")

        # Verify missing document returns None
        missing_org_id = generate_opaque_id(EntityPrefix.ORGANIZATION)
        assert await get_collection_document_row(conn, _TIMEOUT, "organizations", missing_org_id) is None

        # Verify delete for org_system000000 and standard entities
        assert (
            await delete_collection_document_row(
                conn, _TIMEOUT, "organizations", "org_0195f3a0000070008000000000000001"
            )
            is True
        )
        assert await delete_collection_document_row(conn, _TIMEOUT, "organizations", org.id) is True
        assert await delete_collection_document_row(conn, _TIMEOUT, "organizations", org.id) is False

        # Verify delete when table_name is absent from _TABLE_TO_ENTITY_PREFIX
        reduced_prefix_map = {k: v for k, v in _TABLE_TO_ENTITY_PREFIX.items() if k != "users"}
        monkeypatch.setattr(
            "backend_v2.database.postgres.entity_adapter.seed_and_collection_stage._TABLE_TO_ENTITY_PREFIX",
            reduced_prefix_map,
        )
        assert await delete_collection_document_row(conn, _TIMEOUT, "users", user.id) is False

        # Verify clear_collection_documents_rows
        await clear_collection_documents_rows(conn, _TIMEOUT, "system_configs")
        assert await list_collection_documents_rows(conn, _TIMEOUT, "system_configs") == []
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
        # Test negative boundaries on seed_collection_batch_rows and verify_seed_table_counts_rows
        org = _build_org()
        with pytest.raises(AppException) as bad_col_err:
            await seed_collection_batch_rows(conn, _TIMEOUT, "nonexistent_col", [org])
        assert bad_col_err.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

        with pytest.raises(AppException) as bad_type_err:
            await seed_collection_batch_rows(conn, _TIMEOUT, "users", [org])
        assert bad_type_err.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

        with pytest.raises(AppException) as unknown_tbl_err:
            await verify_seed_table_counts_rows(conn, _TIMEOUT, {"unknown_tbl": 0})
        assert unknown_tbl_err.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

        with pytest.raises(AppException) as low_count_err:
            await verify_seed_table_counts_rows(conn, _TIMEOUT, {"organizations": 1})
        assert low_count_err.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value

        # Verify row is None branch in verify_seed_table_counts_rows defaults row_count to 0
        async def _return_none_row(*args: object, **kwargs: object) -> AsyncPgRecordProtocol | None:
            _ = (args, kwargs)
            return None

        monkeypatch.setattr(conn, "fetchrow", _return_none_row)
        zero_counts = await verify_seed_table_counts_rows(conn, _TIMEOUT, {"organizations": 0})
        assert zero_counts["organizations"] == 0
    finally:
        await pool.release(conn)


@pytest.mark.asyncio
async def test_collection_crud_and_report_artifact_fault_translation_failure() -> None:
    """Verify driver faults in verify_seed_table_counts, list, upsert, delete, and clear raise AppException."""
    pool = InMemoryAsyncPgPool()
    org = _build_org()
    org_payload = org.model_dump(mode="json")
    direct_app_err = AppException(
        message="pre-existing storage error",
        status_code=500,
        details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
    )
    conn = await pool.acquire()
    try:
        # 1. Fault in list_collection_documents_rows (fetch)
        pool.inject_fault("fetch", RuntimeError("simulated fetch failure"))
        with pytest.raises(AppException) as list_exc:
            await list_collection_documents_rows(conn, _TIMEOUT, "organizations")
        assert list_exc.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value

        pool.inject_fault("fetch", direct_app_err)
        with pytest.raises(AppException) as direct_list_exc:
            await list_collection_documents_rows(conn, _TIMEOUT, "organizations")
        assert direct_list_exc.value is direct_app_err

        # 2. Fault in verify_seed_table_counts_rows (fetchrow)
        pool.clear_faults()
        pool.inject_fault("fetchrow", RuntimeError("simulated fetchrow failure"))
        with pytest.raises(AppException) as count_exc:
            await verify_seed_table_counts_rows(conn, _TIMEOUT, {"organizations": 0})
        assert count_exc.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value

        pool.inject_fault("fetchrow", direct_app_err)
        with pytest.raises(AppException) as direct_count_exc:
            await verify_seed_table_counts_rows(conn, _TIMEOUT, {"organizations": 0})
        assert direct_count_exc.value is direct_app_err

        # 3. Fault in upsert_collection_document_row, delete_collection_document_row, clear_collection_documents_rows
        pool.clear_faults()
        pool.inject_fault("execute", RuntimeError("simulated execute failure"))
        with pytest.raises(AppException) as upsert_exc:
            await upsert_collection_document_row(conn, _TIMEOUT, "organizations", org.id, org_payload)
        assert upsert_exc.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value

        with pytest.raises(AppException) as del_exc:
            await delete_collection_document_row(conn, _TIMEOUT, "organizations", org.id)
        assert del_exc.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value

        with pytest.raises(AppException) as clear_exc:
            await clear_collection_documents_rows(conn, _TIMEOUT, "organizations")
        assert clear_exc.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value

        pool.inject_fault("execute", direct_app_err)
        with pytest.raises(AppException) as direct_del_exc:
            await delete_collection_document_row(conn, _TIMEOUT, "organizations", org.id)
        assert direct_del_exc.value is direct_app_err

        with pytest.raises(AppException) as direct_clear_exc:
            await clear_collection_documents_rows(conn, _TIMEOUT, "organizations")
        assert direct_clear_exc.value is direct_app_err

        validation_app_err = AppException(
            message="validation error during upsert",
            status_code=400,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )
        pool.inject_fault("execute", validation_app_err)
        assert await upsert_collection_document_row(conn, _TIMEOUT, "organizations", org.id, org_payload) is False
    finally:
        pool.clear_faults()
        await pool.release(conn)
