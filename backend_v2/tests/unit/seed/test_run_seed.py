"""Unit tests for backend_v2/seed/run_seed.py."""

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import JsonValue, SecretStr, ValidationError

from backend_v2.core.telemetry import resolve_startup_logfire_token
from backend_v2.core.test_settings import get_test_settings
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.auth import SYSTEM_ROOT_USER_ID, SystemOrganizations
from backend_v2.models.enums import LLMProvider
from backend_v2.seed import run_seed
from backend_v2.services.auth.secret_service import SecretService
from backend_v2.services.auth.token_service import initialize_firebase_admin_from_secrets
from backend_v2.tests.fakes.in_memory_uow import InMemoryUnitOfWork

VALID_ORGANIZATION: dict[str, JsonValue] = {
    "id": "org_0195f3a0000070008000000000000001",
    "name": "Acme Corp",
    "is_active": True,
    "tier": "enterprise",
    "subscription_status": "active",
    "quota_limit": 500.0,
    "tpm_limit": 50000,
    "rpm_limit": 100,
}

VALID_USER: dict[str, JsonValue] = {
    "id": "usr_0195f3a00000700a83fd6b3d77c748f4",
    "email": "admin@quorum.com",
    "role": "ROOT",
    "organization_id": "org_0195f3a0000070008000000000000001",
    "is_active": True,
    "language": "fi",
    "theme_mode": "dark",
    "created_at": "2026-01-01T00:00:00Z",
}

VALID_MODEL_REGISTRY: dict[str, JsonValue] = {
    "id": "mrg_0195f3a0000070018234567890abcdef",
    "name": "Default Model Registry",
    "default_provider": "ai_studio",
    "tier_definitions": {
        "fast": {"provider": "ai_studio", "model_name": "gemini-2.5-flash"},
        "balanced": {"provider": "ai_studio", "model_name": "gemini-2.5-flash"},
        "deep": {"provider": "ai_studio", "model_name": "gemini-2.5-pro"},
        "reasoning": {"provider": "ai_studio", "model_name": "gemini-2.5-pro"},
    },
}

VALID_MCP_GATEWAY: dict[str, JsonValue] = {
    "id": "mcp_0195f3a00000700080008172bda70c86",
    "organization_id": "org_0195f3a0000070008000000000000001",
    "name": "Tavily MCP Gateway",
    "slug": "default_mcp_gateway",
    "endpoint_url": "https://mcp.tavily.com/mcp",
    "transport_type": "streamable_http",
    "auth_type": "bearer",
    "auth_env_var": None,
    "timeout_seconds": 30,
    "tools": [],
}

VALID_PROMPT_BLOCK: dict[str, JsonValue] = {
    "organization_id": "org_0195f3a0000070008000000000000001",
    "id": "blk_0195f3a0000070018234567890abcdef",
    "slug": "rule_clean",
    "label": {"translations": {"en": "Rule", "fi": "Saanto"}},
    "description": {"translations": {"en": "Description", "fi": "Kuvaus"}},
    "category_id": "system_rule",
    "type": "instruction",
    "instruction_text": "Instruction.",
}

VALID_STEP: dict[str, JsonValue] = {
    "organization_id": "org_0195f3a0000070008000000000000001",
    "id": "stp_0195f3a0000070018234567890abcdef",
    "slug": "step_guard",
    "name": {"translations": {"en": "Guard Step", "fi": "Suojavaihe"}},
    "type": "logic",
    "hook": "sample_hook",
}

VALID_WORKFLOW: dict[str, JsonValue] = {
    "organization_id": "org_0195f3a0000070008000000000000001",
    "id": "wf_0195f3a0000070018234567890abcdef",
    "slug": "test_workflow",
    "name": "Test Workflow",
    "description": "Test description",
    "status": "published",
    "version": 1,
    "is_public": True,
    "default_profile_id": "prf_0195f3a0000070018234567890abcdef",
    "historical_context_mode": "DISABLED",
    "model_registry_id": "mrg_0195f3a0000070018234567890abcdef",
    "mcp_gateway_id": "mcp_0195f3a00000700080008172bda70c86",
    "steps": [],
}

VALID_OUTPUT_PROFILE: dict[str, JsonValue] = {
    "organization_id": "org_0195f3a0000070008000000000000001",
    "id": "prf_0195f3a0000070018234567890abcdef",
    "slug": "test_profile",
    "name": {"translations": {"en": "Test Profile", "fi": "Testiprofiili"}},
    "description": {"translations": {"en": "Desc", "fi": "Kuvaus"}},
    "workflow_id": "wf_0195f3a0000070018234567890abcdef",
    "target_block_order": ["executive_summary_block"],
}

VALID_TASK_BRIEF: dict[str, JsonValue] = {
    "organization_id": "org_0195f3a0000070008000000000000001",
    "id": "tbr_0195f3a00000700d8a1b2c3d4e5f6001",
    "slug": "test_task_brief",
    "label": {"translations": {"en": "Task Brief", "fi": "Tehtavananto"}},
    "description": {"translations": {"en": "Brief desc", "fi": "Kuvaus"}},
    "instruction_text": "Complete the assignment.",
}


def _build_full_valid_seed_payload() -> run_seed.ValidatedSeedBufferDTO:
    """Return a minimal valid 10-collection seed payload as ValidatedSeedBufferDTO."""
    raw_seed_payload: dict[str, JsonValue] = {
        "organizations": [VALID_ORGANIZATION],
        "users": [VALID_USER],
        "model_registries": [VALID_MODEL_REGISTRY],
        "mcp_gateways": [VALID_MCP_GATEWAY],
        "prompt_blocks": [VALID_PROMPT_BLOCK],
        "task_briefs": [VALID_TASK_BRIEF],
        "steps": [VALID_STEP],
        "workflows": [VALID_WORKFLOW],
        "output_profiles": [VALID_OUTPUT_PROFILE],
        "executions": [],
    }
    with patch("backend_v2.services.orchestrator.dag_compiler.DAGCompilerService.validate_workflow"):
        return run_seed.validate_all_seed_collections(raw_seed_payload)


def test_run_seed_main_help(capsys: pytest.CaptureFixture[str]) -> None:
    """Test that run_seed.py can be imported and argparser works."""
    with pytest.raises(SystemExit) as excinfo:
        run_seed.main(["--help"])

    assert excinfo.value.code == 0
    captured = capsys.readouterr()
    assert "Unified V2 PostgreSQL 19 Database Seeder" in captured.out


def test_run_seed_main_postgres_default_and_local_alias() -> None:
    """Test main function with default postgres target and local alias."""
    with patch("backend_v2.seed.run_seed.seed_database", new_callable=AsyncMock) as mock_seed:
        run_seed.main([])
        mock_seed.assert_called_once_with("postgres", dry_run=False)

    with patch("backend_v2.seed.run_seed.seed_database", new_callable=AsyncMock) as mock_seed_local:
        run_seed.main(["local", "--dry-run"])
        mock_seed_local.assert_called_once_with("local", dry_run=True)


def test_run_seed_main_exception_exits() -> None:
    """Test main function handles unexpected errors with fail-fast exit."""
    with (
        patch("backend_v2.seed.run_seed.seed_database", side_effect=RuntimeError("Database down")),
        pytest.raises(SystemExit) as excinfo,
    ):
        run_seed.main(["postgres"])
    assert excinfo.value.code == 1


def test_fail_fast_logs_and_raises() -> None:
    """Test _fail_fast helper logs and returns AppException."""
    exc = run_seed._fail_fast("Critical test error", ValueError("Malformed data"))
    assert isinstance(exc, AppException)
    assert exc.error_code == ErrorCodes.VALIDATION_FAILED


@pytest.mark.asyncio
async def test_seed_database_seed_path_missing() -> None:
    """Test seed_database terminates if seed_data.json does not exist."""
    with (
        patch("backend_v2.seed.run_seed.Path.exists", return_value=False),
        pytest.raises(SystemExit) as excinfo,
    ):
        await run_seed.seed_database("postgres")
    assert excinfo.value.code == 1


@pytest.mark.asyncio
async def test_seed_database_unsupported_target_raises_app_exception() -> None:
    """Negative test: unsupported target (e.g., firestore) raises AppException."""
    with pytest.raises(AppException) as excinfo:
        await run_seed.seed_database("firestore")
    assert excinfo.value.error_code == ErrorCodes.VALIDATION_FAILED


@pytest.mark.asyncio
async def test_seed_database_delegates_to_seed_postgres(tmp_path: Path) -> None:
    """Positive test: seed_database loads seed_data.json and delegates to _seed_postgres."""
    seed_file = tmp_path / "seed.json"
    payload = _build_full_valid_seed_payload()
    raw_json = payload.model_dump_json()
    seed_file.write_text(raw_json, encoding="utf-8")

    with (
        patch("backend_v2.seed.run_seed.SEED_PATH", seed_file),
        patch(
            "backend_v2.seed.run_seed._seed_postgres", new_callable=AsyncMock, return_value={"organizations": 1}
        ) as mock_pg,
    ):
        counts = await run_seed.seed_database("postgres", dry_run=False)
        assert counts == {"organizations": 1}
        mock_pg.assert_called_once_with(json.loads(raw_json), dry_run=False, uow=None)


@pytest.mark.asyncio
async def test_seed_postgres_dry_run() -> None:
    """Positive test: _seed_postgres in dry-run mode validates in-memory without touching PostgreSQL."""
    payload = _build_full_valid_seed_payload()
    with patch("backend_v2.services.orchestrator.dag_compiler.DAGCompilerService.validate_workflow"):
        counts = await run_seed._seed_postgres(payload, dry_run=True)
    assert counts["organizations"] == 1
    assert counts["workflows"] == 1


@pytest.mark.asyncio
async def test_seed_postgres_full_materialization_and_count_verification() -> None:
    """Positive test: _seed_postgres ingests all 7 collections into PostgreSQL 19 and verifies counts."""
    payload = _build_full_valid_seed_payload()
    uow = InMemoryUnitOfWork()

    with patch("backend_v2.services.orchestrator.dag_compiler.DAGCompilerService.validate_workflow"):
        counts = await run_seed._seed_postgres(payload, dry_run=False, uow=uow)

    assert counts["organizations"] == 1
    assert counts["users"] == 1
    assert counts["tenant_secrets"] == 0
    assert counts["model_registries"] == 1
    assert counts["mcp_gateways"] == 1
    assert counts["prompt_blocks"] == 1
    assert counts["task_briefs"] == 1
    assert counts["steps"] == 1
    assert counts["workflows"] == 1
    assert counts["output_profiles"] == 1
    assert counts["executions"] == 0
    assert counts["report_artifacts"] == 0
    assert counts["report_binaries"] == 0


@pytest.mark.asyncio
async def test_run_seed_seeds_local_secrets_and_provisions_root_firebase_user() -> None:
    """Positive test: _seed_postgres encrypts local secrets into tenant_secrets and provisions ROOT Firebase user."""
    payload = _build_full_valid_seed_payload()
    uow = InMemoryUnitOfWork()
    secrets_settings = run_seed.LocalSeedSecretsSettings(
        _env_file=None,
        secret_ai_studio_api_key=SecretStr("AIzaSyDummyAiStudioKey1234567890"),
        secret_vertex_ai_sa_json=SecretStr('{"type":"service_account","project_id":"demo-proj"}'),
        secret_logfire_token=SecretStr("lf_tok_dummy_write_1234567890"),
        secret_root_user_email=SecretStr("root@example.com"),
        secret_root_user_password=SecretStr("QuorumRootPassword2026!"),
    )

    fb_user_record = MagicMock()
    fb_user_record.uid = SYSTEM_ROOT_USER_ID

    fake_fb_auth = MagicMock()
    fake_fb_auth.get_user_by_email.side_effect = [
        ValueError("User with email root@example.com not found"),
        fb_user_record,
    ]
    fake_fb_auth.create_user.return_value = fb_user_record
    fake_fb_auth.update_user.return_value = fb_user_record

    with patch("backend_v2.services.orchestrator.dag_compiler.DAGCompilerService.validate_workflow"):
        counts = await run_seed._seed_postgres(
            payload,
            dry_run=False,
            uow=uow,
            secrets_settings=secrets_settings,
            firebase_auth_client=fake_fb_auth,
        )

    assert counts["tenant_secrets"] == 3
    fake_fb_auth.create_user.assert_called_once_with(
        uid=SYSTEM_ROOT_USER_ID,
        email="root@example.com",
        password="QuorumRootPassword2026!",
        email_verified=True,
    )

    root_user = await uow.entities.get_user(SYSTEM_ROOT_USER_ID)
    assert root_user is not None
    assert root_user.firebase_uid == SYSTEM_ROOT_USER_ID
    assert root_user.email == "root@example.com"

    secret_service = SecretService(entity_adapter=uow.entities)
    resolved_ai_studio = await secret_service.resolve_llm_key(
        SystemOrganizations.ROOT_SYSTEM.value,
        LLMProvider.AI_STUDIO,
    )
    assert resolved_ai_studio.secret_value.get_secret_value() == "AIzaSyDummyAiStudioKey1234567890"
    resolved_logfire = await secret_service.resolve_telemetry_secret("logfire")
    assert resolved_logfire.secret_value.get_secret_value() == "lf_tok_dummy_write_1234567890"

    # Re-run to verify idempotent update-on-existing Firebase user branch
    with patch("backend_v2.services.orchestrator.dag_compiler.DAGCompilerService.validate_workflow"):
        await run_seed._seed_postgres(
            payload,
            dry_run=False,
            uow=uow,
            secrets_settings=secrets_settings,
            firebase_auth_client=fake_fb_auth,
        )
    fake_fb_auth.update_user.assert_called_once_with(
        SYSTEM_ROOT_USER_ID,
        email="root@example.com",
        password="QuorumRootPassword2026!",
        email_verified=True,
    )


def test_local_seed_secrets_settings_rejects_extra_unknown_keys(tmp_path: Path) -> None:
    """Negative test: LocalSeedSecretsSettings rejects unrecognized keys under extra='forbid'."""
    bad_env_file = tmp_path / ".env.secrets.bad"
    bad_env_file.write_text("UNKNOWN_SECRET_KEY='xyz'\n", encoding="utf-8")
    with pytest.raises(ValidationError):
        run_seed.LocalSeedSecretsSettings(_env_file=str(bad_env_file))


@pytest.mark.asyncio
async def test_provision_root_firebase_user_negative_and_boundary_cases() -> None:
    """Negative and boundary tests for _provision_root_firebase_user validation and error handling."""
    uow = InMemoryUnitOfWork()

    # 1. Incomplete credentials (email without password) raises AppException
    incomplete_secrets = run_seed.LocalSeedSecretsSettings(
        _env_file=None,
        secret_root_user_email=SecretStr("root@example.com"),
    )
    with pytest.raises(AppException) as exc_incomplete:
        await run_seed._provision_root_firebase_user(uow, incomplete_secrets)
    assert exc_incomplete.value.error_code == ErrorCodes.VALIDATION_FAILED

    # 2. Missing SECRET_VERTEX_AI_SA_JSON when ROOT email + password are set raises AppException
    missing_sa_secrets = run_seed.LocalSeedSecretsSettings(
        _env_file=None,
        secret_root_user_email=SecretStr("root@example.com"),
        secret_root_user_password=SecretStr("QuorumRootPassword2026!"),
    )
    with pytest.raises(AppException) as exc_missing_sa:
        await run_seed._provision_root_firebase_user(uow, missing_sa_secrets)
    assert exc_missing_sa.value.error_code == ErrorCodes.VALIDATION_FAILED

    # 3. Non-JSON prefix in SECRET_VERTEX_AI_SA_JSON raises AppException
    bad_prefix_secrets = run_seed.LocalSeedSecretsSettings(
        _env_file=None,
        secret_vertex_ai_sa_json=SecretStr("not-a-json-object"),
        secret_root_user_email=SecretStr("root@example.com"),
        secret_root_user_password=SecretStr("QuorumRootPassword2026!"),
    )
    with pytest.raises(AppException) as exc_bad_prefix:
        await run_seed._provision_root_firebase_user(uow, bad_prefix_secrets)
    assert exc_bad_prefix.value.error_code == ErrorCodes.VALIDATION_FAILED

    # 4. Malformed JSON syntax in SECRET_VERTEX_AI_SA_JSON raises AppException
    malformed_json_secrets = run_seed.LocalSeedSecretsSettings(
        _env_file=None,
        secret_vertex_ai_sa_json=SecretStr("{bad_json"),
        secret_root_user_email=SecretStr("root@example.com"),
        secret_root_user_password=SecretStr("QuorumRootPassword2026!"),
    )
    with pytest.raises(AppException) as exc_malformed:
        await run_seed._provision_root_firebase_user(uow, malformed_json_secrets)
    assert exc_malformed.value.error_code == ErrorCodes.VALIDATION_FAILED


@pytest.mark.asyncio
async def test_seed_postgres_fails_fast_when_required_table_count_is_zero() -> None:
    """Negative boundary test: _seed_postgres raises AppException when any required seed table has 0 rows."""
    payload = _build_full_valid_seed_payload().model_copy(update={"organizations": []})
    uow = InMemoryUnitOfWork()

    with (
        patch("backend_v2.services.orchestrator.dag_compiler.DAGCompilerService.validate_workflow"),
        pytest.raises(AppException) as excinfo,
    ):
        await run_seed._seed_postgres(payload, dry_run=False, uow=uow)

    assert excinfo.value.error_code in (ErrorCodes.STORAGE_ACCESS_FAILED, ErrorCodes.VALIDATION_FAILED)
    assert "organizations" in excinfo.value.message


@pytest.mark.asyncio
async def test_seeder_aborts_without_truncating_tables_on_corrupt_data() -> None:
    """Contract 1: Negative test - corrupt seed data aborts during preflight without opening UoW."""
    corrupt_payload: dict[str, JsonValue] = {"organizations": [{"id": "bad_item_lacking_fields"}]}

    with (
        patch("backend_v2.seed.run_seed.create_unit_of_work") as mock_uow_fn,
        pytest.raises(AppException) as excinfo,
    ):
        await run_seed._seed_postgres(corrupt_payload, dry_run=False)

    assert excinfo.value.error_code == ErrorCodes.VALIDATION_FAILED
    mock_uow_fn.assert_not_called()


@pytest.mark.asyncio
async def test_seeder_aborts_on_invalid_workflow_dag() -> None:
    """Contract 2: Negative test - workflow with broken DAG compilation aborts before DB mutation."""
    seed_payload: dict[str, JsonValue] = {"workflows": [VALID_WORKFLOW]}

    with (
        patch("backend_v2.seed.run_seed.create_unit_of_work") as mock_uow_fn,
        patch(
            "backend_v2.services.orchestrator.dag_compiler.DAGCompilerService.validate_workflow",
            side_effect=ValueError("Broken DAG circular dependency"),
        ),
        pytest.raises(AppException) as excinfo,
    ):
        await run_seed._seed_postgres(seed_payload, dry_run=False)

    assert excinfo.value.error_code == ErrorCodes.VALIDATION_FAILED
    mock_uow_fn.assert_not_called()


def test_seeder_preflight_validates_all_standard_collections() -> None:
    """Contract 3: Positive test - validate_all_seed_collections validates collections into ValidatedSeedBufferDTO."""
    valid_payload: dict[str, JsonValue] = {
        "organizations": [VALID_ORGANIZATION],
        "workflows": [VALID_WORKFLOW],
        "users": [],
        "model_registries": [],
        "mcp_gateways": [],
        "prompt_blocks": [],
        "steps": [],
        "output_profiles": [],
        "executions": [],
    }

    with patch("backend_v2.services.orchestrator.dag_compiler.DAGCompilerService.validate_workflow"):
        buffers = run_seed.validate_all_seed_collections(valid_payload)

    assert isinstance(buffers, run_seed.ValidatedSeedBufferDTO)
    assert "organizations" in buffers
    assert len(buffers["organizations"]) == 1
    assert buffers.organizations[0].id == VALID_ORGANIZATION["id"]
    assert "workflows" in buffers
    assert len(buffers["workflows"]) == 1
    assert buffers.workflows[0].id == VALID_WORKFLOW["id"]
    for col in [
        "users",
        "model_registries",
        "mcp_gateways",
        "prompt_blocks",
        "task_briefs",
        "steps",
        "output_profiles",
        "executions",
    ]:
        assert col in buffers
        assert buffers[col] == []
    with pytest.raises(KeyError):
        _ = buffers["unknown_collection_key"]


@pytest.mark.asyncio
async def test_seed_postgres_wraps_unexpected_uow_exception_in_app_exception() -> None:
    """Negative test: unexpected RuntimeError inside UoW transaction is wrapped via _fail_fast."""
    payload = _build_full_valid_seed_payload()
    failing_uow = MagicMock()
    failing_uow.__aenter__ = AsyncMock(side_effect=RuntimeError("Connection reset by peer"))
    failing_uow.__aexit__ = AsyncMock(return_value=None)

    with (
        patch("backend_v2.services.orchestrator.dag_compiler.DAGCompilerService.validate_workflow"),
        pytest.raises(AppException) as excinfo,
    ):
        await run_seed._seed_postgres(payload, dry_run=False, uow=failing_uow)

    assert excinfo.value.error_code == ErrorCodes.VALIDATION_FAILED


def test_validated_seed_buffer_dto_rejects_unknown_collection() -> None:
    """Test contract: ValidatedSeedBufferDTO rejects unknown collection key under extra='forbid'."""
    invalid_payload = {
        "unknown_collection": [{"id": "foo"}],
    }
    with pytest.raises(ValidationError):
        run_seed.ValidatedSeedBufferDTO.model_validate(invalid_payload)


def test_validate_all_seed_collections_unexpected_error_raises_app_exception() -> None:
    """Negative test: non-ValidationError during seed buffer validation is wrapped in AppException."""
    with (
        patch.object(
            run_seed.ValidatedSeedBufferDTO,
            "model_validate",
            side_effect=RuntimeError("Unexpected memory fault"),
        ),
        pytest.raises(AppException) as excinfo,
    ):
        run_seed.validate_all_seed_collections({})

    assert excinfo.value.error_code == ErrorCodes.VALIDATION_FAILED
    assert "Processing error during seed validation" in excinfo.value.message


@pytest.mark.asyncio
async def test_run_seed_dry_run_validates_local_secrets_without_db_mutation() -> None:
    """Verify dry-run validates seed_data.json and LocalSeedSecretsSettings in-memory without mutating PostgreSQL or Firebase."""
    payload = _build_full_valid_seed_payload()
    uow = InMemoryUnitOfWork()
    secrets_settings = run_seed.LocalSeedSecretsSettings(
        _env_file=None,
        secret_ai_studio_api_key=SecretStr("AIzaSyDummyAiStudioKey1234567890"),
        secret_vertex_ai_sa_json=SecretStr('{"type":"service_account","project_id":"demo-proj"}'),
        secret_logfire_token=SecretStr("lf_tok_dummy_write_1234567890"),
        secret_root_user_email=SecretStr("root@example.com"),
        secret_root_user_password=SecretStr("QuorumRootPassword2026!"),
    )
    fake_fb_auth = MagicMock()

    with patch("backend_v2.services.orchestrator.dag_compiler.DAGCompilerService.validate_workflow"):
        counts = await run_seed._seed_postgres(
            payload,
            dry_run=True,
            uow=uow,
            secrets_settings=secrets_settings,
            firebase_auth_client=fake_fb_auth,
        )

    assert counts["organizations"] == 1
    assert counts["users"] == 1
    assert counts["tenant_secrets"] == 3
    assert counts["workflows"] == 1
    assert await uow.entities.list_tenant_secrets(SystemOrganizations.ROOT_SYSTEM.value) == []
    assert await uow.entities.get_user(SYSTEM_ROOT_USER_ID) is None
    fake_fb_auth.create_user.assert_not_called()
    fake_fb_auth.update_user.assert_not_called()

    # Negative boundary: invalid LocalSeedSecretsSettings in dry-run raises AppException
    with (
        patch("backend_v2.services.orchestrator.dag_compiler.DAGCompilerService.validate_workflow"),
        patch.object(
            run_seed,
            "LocalSeedSecretsSettings",
            side_effect=ValidationError.from_exception_data("LocalSeedSecretsSettings", []),
        ),
        pytest.raises(AppException) as exc_invalid_secrets,
    ):
        await run_seed._seed_postgres(payload, dry_run=True, uow=None, secrets_settings=None)
    assert exc_invalid_secrets.value.error_code == ErrorCodes.VALIDATION_FAILED


@pytest.mark.asyncio
async def test_live_e2e_real_llm_execution_with_seeded_tenant_secrets(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify seeded tenant_secrets satisfy startup telemetry, Firebase Admin initialization, and LLM key resolution."""
    payload = _build_full_valid_seed_payload()
    uow = InMemoryUnitOfWork()
    secrets_settings = run_seed.LocalSeedSecretsSettings(
        _env_file=None,
        secret_ai_studio_api_key=SecretStr("AIzaSyDummyAiStudioKey1234567890"),
        secret_vertex_ai_sa_json=SecretStr('{"type":"service_account","project_id":"demo-proj"}'),
        secret_logfire_token=SecretStr("lf_tok_dummy_write_1234567890"),
        secret_root_user_email=SecretStr("root@example.com"),
        secret_root_user_password=SecretStr("QuorumRootPassword2026!"),
    )
    fb_user_record = MagicMock()
    fb_user_record.uid = SYSTEM_ROOT_USER_ID
    fake_fb_auth = MagicMock()
    fake_fb_auth.get_user_by_email.side_effect = ValueError("User not found")
    fake_fb_auth.create_user.return_value = fb_user_record

    with patch("backend_v2.services.orchestrator.dag_compiler.DAGCompilerService.validate_workflow"):
        counts = await run_seed._seed_postgres(
            payload,
            dry_run=False,
            uow=uow,
            secrets_settings=secrets_settings,
            firebase_auth_client=fake_fb_auth,
        )

    assert counts["tenant_secrets"] == 3
    secret_service = SecretService(entity_adapter=uow.entities)
    test_settings = get_test_settings(otel_enabled=True, logfire_token=None, use_firebase_auth=True)

    resolved_token = await resolve_startup_logfire_token(test_settings, secret_service)
    assert resolved_token == "lf_tok_dummy_write_1234567890"

    fake_fb_admin = MagicMock()
    fake_fb_admin._apps = {}
    fake_creds_mod = MagicMock()
    fake_cert = MagicMock()
    fake_creds_mod.Certificate.return_value = fake_cert

    monkeypatch.setattr("backend_v2.services.auth.token_service.firebase_admin", fake_fb_admin)
    monkeypatch.setattr("backend_v2.services.auth.token_service.firebase_credentials_module", fake_creds_mod)

    await initialize_firebase_admin_from_secrets(secret_service, test_settings)
    fake_creds_mod.Certificate.assert_called_once_with({"type": "service_account", "project_id": "demo-proj"})
    fake_fb_admin.initialize_app.assert_called_once_with(fake_cert)

    ai_studio_cred = await secret_service.resolve_llm_key(
        SystemOrganizations.ROOT_SYSTEM.value,
        LLMProvider.AI_STUDIO,
    )
    assert ai_studio_cred.secret_value.get_secret_value() == "AIzaSyDummyAiStudioKey1234567890"
