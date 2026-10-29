"""Unit tests for backend_v2/seed/run_seed.py."""

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import JsonValue, ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.seed import run_seed
from backend_v2.tests.fakes.in_memory_uow import InMemoryUnitOfWork

VALID_ORGANIZATION: dict[str, JsonValue] = {
    "id": "org_12345678abcd",
    "name": "Acme Corp",
    "is_active": True,
    "tier": "enterprise",
    "subscription_status": "active",
    "quota_limit": 500.0,
    "tpm_limit": 50000,
    "rpm_limit": 100,
}

VALID_USER: dict[str, JsonValue] = {
    "id": "usr_0195f3a0000070018234567890abcdef",
    "email": "admin@quorum.com",
    "role": "ROOT",
    "organization_id": "org_12345678abcd",
    "is_active": True,
    "language": "fi",
    "theme_mode": "dark",
    "created_at": "2026-01-01T00:00:00Z",
}

VALID_SYSTEM_CONFIG: dict[str, JsonValue] = {
    "id": "sys_1234567890abcdef1234567890abcdef",
    "name": "Default Model Registry",
    "type": "model_registry",
    "default_provider": "ai_studio",
    "tier_definitions": {
        "fast": {"provider": "ai_studio", "model_name": "gemini-2.5-flash"},
        "balanced": {"provider": "ai_studio", "model_name": "gemini-2.5-flash"},
        "deep": {"provider": "ai_studio", "model_name": "gemini-2.5-pro"},
        "reasoning": {"provider": "ai_studio", "model_name": "gemini-2.5-pro"},
    },
}

VALID_PROMPT_BLOCK: dict[str, JsonValue] = {
    "id": "blk_0195f3a0000070018234567890abcdef",
    "slug": "rule_clean",
    "label": {"translations": {"en": "Rule", "fi": "Saanto"}},
    "description": {"translations": {"en": "Description", "fi": "Kuvaus"}},
    "category_id": "system_rule",
    "type": "instruction",
    "instruction_text": "Instruction.",
}

VALID_STEP: dict[str, JsonValue] = {
    "id": "stp_0195f3a0000070018234567890abcdef",
    "slug": "step_guard",
    "name": {"translations": {"en": "Guard Step", "fi": "Suojavaihe"}},
    "type": "logic",
    "hook": "sample_hook",
}

VALID_WORKFLOW: dict[str, JsonValue] = {
    "id": "wor_0195f3a0000070018234567890abcdef",
    "slug": "test_workflow",
    "name": "Test Workflow",
    "description": "Test description",
    "status": "published",
    "version": 1,
    "is_public": True,
    "default_profile_id": "prf_0195f3a0000070018234567890abcdef",
    "historical_context_mode": "DISABLED",
    "model_registry_id": "sys_1234567890abcdef1234567890abcdef",
    "steps": [],
}

VALID_OUTPUT_PROFILE: dict[str, JsonValue] = {
    "id": "prf_0195f3a0000070018234567890abcdef",
    "slug": "test_profile",
    "name": {"translations": {"en": "Test Profile", "fi": "Testiprofiili"}},
    "description": {"translations": {"en": "Desc", "fi": "Kuvaus"}},
    "workflow_id": "wor_0195f3a0000070018234567890abcdef",
    "target_block_order": ["executive_summary_block"],
}


def _build_full_valid_seed_payload() -> run_seed.ValidatedSeedBufferDTO:
    """Return a minimal valid 8-collection seed payload as ValidatedSeedBufferDTO."""
    return run_seed.ValidatedSeedBufferDTO.model_validate(
        {
            "organizations": [VALID_ORGANIZATION],
            "users": [VALID_USER],
            "system_config": [VALID_SYSTEM_CONFIG],
            "prompt_blocks": [VALID_PROMPT_BLOCK],
            "steps": [VALID_STEP],
            "workflows": [VALID_WORKFLOW],
            "output_profiles": [VALID_OUTPUT_PROFILE],
            "executions": [],
        }
    )


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
    assert counts["system_configs"] == 1
    assert counts["prompt_blocks"] == 1
    assert counts["steps"] == 1
    assert counts["workflows"] == 1
    assert counts["output_profiles"] == 1
    assert counts["executions"] == 0
    assert counts["report_artifacts"] == 0
    assert counts["report_binaries"] == 0


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
        "system_config": [],
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
    for col in ["users", "system_config", "prompt_blocks", "steps", "output_profiles", "executions"]:
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
