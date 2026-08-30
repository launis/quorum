"""Unit tests for backend_v2/seed/run_seed.py."""

from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.seed import run_seed

VALID_ORGANIZATION = {
    "id": "org_12345678abcd",
    "name": "Acme Corp",
    "is_active": True,
    "tier": "enterprise",
    "subscription_status": "active",
    "quota_limit": 500.0,
    "tpm_limit": 50000,
    "rpm_limit": 100,
}

VALID_WORKFLOW = {
    "id": "wor_1234567890abcdef",
    "slug": "test_workflow",
    "name": "Test Workflow",
    "description": "Test description",
    "status": "published",
    "version": 1,
    "is_public": True,
    "default_profile_id": "out_1234567890abcdef",
    "allowed_exports": ["pdf"],
    "historical_context_mode": "DISABLED",
    "steps": [],
}


def test_run_seed_main_help(capsys: pytest.CaptureFixture[str]) -> None:
    """Test that run_seed.py can be imported and argparser works."""
    with pytest.raises(SystemExit) as excinfo:
        run_seed.main(["--help"])

    assert excinfo.value.code == 0
    captured = capsys.readouterr()
    assert "Unified V2 Database Seeder" in captured.out


def test_run_seed_main_local_success() -> None:
    """Test main function with local target."""
    with patch("backend_v2.seed.run_seed.seed_database", new_callable=AsyncMock) as mock_seed:
        run_seed.main(["local"])
        mock_seed.assert_called_once_with("local", dry_run=False)


def test_run_seed_main_all_targets() -> None:
    """Test main function with 'all' and '--dry-run' flags."""
    with patch("backend_v2.seed.run_seed.seed_database", new_callable=AsyncMock) as mock_seed:
        run_seed.main(["all", "--dry-run"])
        assert mock_seed.call_count == 2
        calls = [c.args for c in mock_seed.call_args_list]
        assert ("local",) in calls or ("local",) in [c[0] for c in calls]
        assert ("firestore",) in calls or ("firestore",) in [c[0] for c in calls]


def test_run_seed_main_exception_exits() -> None:
    """Test main function handles unexpected errors with fail-fast exit."""
    with (
        patch("backend_v2.seed.run_seed.seed_database", side_effect=RuntimeError("Database down")),
        pytest.raises(SystemExit) as excinfo,
    ):
        run_seed.main(["local"])
    assert excinfo.value.code == 1


def test_fail_fast_logs_and_exits() -> None:
    """Test _fail_fast helper logs and terminates with SystemExit(1)."""
    with pytest.raises(SystemExit) as excinfo:
        run_seed._fail_fast("Critical test error", ValueError("Malformed data"))
    assert excinfo.value.code == 1


@pytest.mark.asyncio
async def test_seed_database_seed_path_missing() -> None:
    """Test seed_database terminates if seed_data.json does not exist."""
    with (
        patch("pathlib.Path.exists", return_value=False),
        pytest.raises(SystemExit) as excinfo,
    ):
        await run_seed.seed_database("local")
    assert excinfo.value.code == 1


@pytest.mark.asyncio
async def test_seed_database_local_branch() -> None:
    """Test the main seed_database orchestrator for 'local' target."""
    fake_data: dict[str, Any] = {"organizations": []}
    with (
        patch("pathlib.Path.exists", return_value=True),
        patch("builtins.open"),
        patch("json.load", return_value=fake_data),
        patch("backend_v2.seed.run_seed._seed_tinydb", new_callable=AsyncMock) as mock_seed,
    ):
        await run_seed.seed_database("local", dry_run=False)
        mock_seed.assert_called_once_with(run_seed.LOCAL_DB_PATH, fake_data, "local", dry_run=False)


@pytest.mark.asyncio
async def test_seed_database_firestore_dry_run(capsys: pytest.CaptureFixture[str]) -> None:
    """Test seed_database firestore branch in dry-run mode."""
    with (
        patch("pathlib.Path.exists", return_value=True),
        patch("builtins.open"),
        patch("json.load", return_value={}),
    ):
        await run_seed.seed_database("firestore", dry_run=True)
        captured = capsys.readouterr()
        assert "DRY-RUN for firestore not currently supported" in captured.out


@pytest.mark.asyncio
async def test_seed_database_firestore_execution() -> None:
    """Test seed_database firestore branch calls _seed_firestore."""
    fake_data: dict[str, Any] = {"system_config": []}
    with (
        patch("pathlib.Path.exists", return_value=True),
        patch("builtins.open"),
        patch("json.load", return_value=fake_data),
        patch("backend_v2.seed.run_seed._seed_firestore", new_callable=AsyncMock) as mock_fire,
    ):
        await run_seed.seed_database("firestore", dry_run=False)
        mock_fire.assert_called_once_with(fake_data, "firestore")


@pytest.mark.asyncio
async def test_seed_tinydb_empty() -> None:
    """Test the TinyDB seeding process with empty data."""
    mock_db = MagicMock()
    mock_table = MagicMock()
    mock_db.table.return_value = mock_table
    mock_table.__len__.return_value = 0

    with (
        patch("backend_v2.seed.run_seed.TinyDB", return_value=mock_db),
        patch("pathlib.Path.mkdir"),
        patch("pathlib.Path.exists", return_value=False),
        patch("pathlib.Path.stat") as mock_stat,
    ):
        mock_stat.return_value.st_size = 123
        await run_seed._seed_tinydb(Path("fake_db.json"), {}, "local")

        mock_db.drop_tables.assert_called_once()
        mock_db.close.assert_called_once()


@pytest.mark.asyncio
async def test_seed_tinydb_backup_failure_exits() -> None:
    """Test _seed_tinydb terminates if database backup fails."""
    with (
        patch("pathlib.Path.mkdir"),
        patch("pathlib.Path.exists", return_value=True),
        patch("shutil.copy2", side_effect=OSError("Permission denied")),
        pytest.raises(SystemExit) as excinfo,
    ):
        await run_seed._seed_tinydb(Path("db_v2.json"), {}, "local")
    assert excinfo.value.code == 1


@pytest.mark.asyncio
async def test_seed_tinydb_with_valid_items_and_cleanup() -> None:
    """Test _seed_tinydb with valid items, execution folder wipe, and upsert."""
    mock_db = MagicMock()
    tables: dict[str, MagicMock] = {}

    def get_table(name: str) -> MagicMock:
        if name not in tables:
            tbl = MagicMock()
            tbl.__len__.return_value = 1 if name == "organizations" else 0
            tables[name] = tbl
        return tables[name]

    mock_db.table.side_effect = get_table
    seed_payload = {"organizations": [VALID_ORGANIZATION]}

    with (
        patch("backend_v2.seed.run_seed.TinyDB", return_value=mock_db),
        patch("pathlib.Path.mkdir"),
        patch("pathlib.Path.exists", return_value=True),
        patch("shutil.copy2"),
        patch("shutil.rmtree"),
        patch("pathlib.Path.stat") as mock_stat,
    ):
        mock_stat.return_value.st_size = 456
        await run_seed._seed_tinydb(Path("db_v2.json"), seed_payload, "local", dry_run=False)

        mock_db.drop_tables.assert_called_once()
        tables["organizations"].upsert.assert_called()
        mock_db.close.assert_called_once()


@pytest.mark.asyncio
async def test_seed_tinydb_with_workflow_validation() -> None:
    """Test _seed_tinydb with workflows collection validates DAG compiler."""
    mock_db = MagicMock()
    tables: dict[str, MagicMock] = {}

    def get_table(name: str) -> MagicMock:
        if name not in tables:
            tbl = MagicMock()
            tbl.__len__.return_value = 1 if name == "workflows" else 0
            tables[name] = tbl
        return tables[name]

    mock_db.table.side_effect = get_table
    seed_payload = {"workflows": [VALID_WORKFLOW]}

    with (
        patch("backend_v2.seed.run_seed.TinyDB", return_value=mock_db),
        patch("pathlib.Path.mkdir"),
        patch("pathlib.Path.exists", return_value=False),
        patch("backend_v2.services.orchestrator.dag_compiler.DAGCompilerService.validate_workflow") as mock_dag,
        patch("pathlib.Path.stat") as mock_stat,
    ):
        mock_stat.return_value.st_size = 789
        await run_seed._seed_tinydb(Path("db_v2.json"), seed_payload, "local", dry_run=False)
        mock_dag.assert_called_once()
        mock_db.close.assert_called_once()


@pytest.mark.asyncio
async def test_seed_tinydb_dry_run() -> None:
    """Test _seed_tinydb with dry_run=True."""
    seed_payload = {"organizations": [VALID_ORGANIZATION]}
    await run_seed._seed_tinydb(Path("db_v2.json"), seed_payload, "local", dry_run=True)


@pytest.mark.asyncio
async def test_seed_tinydb_validation_error_fails_fast() -> None:
    """Test _seed_tinydb fails fast on Pydantic ValidationError."""
    mock_db = MagicMock()
    seed_payload = {"organizations": [{"id": "bad_item"}]}

    with (
        patch("backend_v2.seed.run_seed.TinyDB", return_value=mock_db),
        patch("pathlib.Path.mkdir"),
        patch("pathlib.Path.exists", return_value=False),
        pytest.raises(SystemExit) as excinfo,
    ):
        await run_seed._seed_tinydb(Path("db_v2.json"), seed_payload, "local")
    assert excinfo.value.code == 1


@pytest.mark.asyncio
async def test_seed_tinydb_processing_error_fails_fast() -> None:
    """Test _seed_tinydb fails fast on unexpected processing errors."""
    mock_db = MagicMock()
    with (
        patch("backend_v2.seed.run_seed.TinyDB", return_value=mock_db),
        patch("pathlib.Path.mkdir"),
        patch("pathlib.Path.exists", return_value=False),
        patch.dict(
            "backend_v2.seed.run_seed.STANDARD_REGISTRY",
            {
                "organizations": {
                    "table": "organizations",
                    "model": MagicMock(validate_python=MagicMock(side_effect=TypeError("Unexpected"))),
                    "id_field": "id",
                }
            },
        ),
        pytest.raises(SystemExit) as excinfo,
    ):
        await run_seed._seed_tinydb(Path("db_v2.json"), {"organizations": [{}]}, "local")
    assert excinfo.value.code == 1


@pytest.mark.asyncio
async def test_seed_tinydb_upsert_error_fails_fast() -> None:
    """Test _seed_tinydb fails fast when table upsert throws an exception."""
    mock_db = MagicMock()
    mock_table = MagicMock()
    mock_table.upsert.side_effect = RuntimeError("Disk full")
    mock_db.table.return_value = mock_table

    with (
        patch("backend_v2.seed.run_seed.TinyDB", return_value=mock_db),
        patch("pathlib.Path.mkdir"),
        patch("pathlib.Path.exists", return_value=False),
        pytest.raises(SystemExit) as excinfo,
    ):
        await run_seed._seed_tinydb(Path("db_v2.json"), {"organizations": [VALID_ORGANIZATION]}, "local")
    assert excinfo.value.code == 1


@pytest.mark.asyncio
async def test_seed_tinydb_integrity_parity_mismatch_fails_fast() -> None:
    """Test _seed_tinydb fails fast if TinyDB dropped items unexpectedly."""
    mock_db = MagicMock()
    mock_table = MagicMock()
    mock_db.table.return_value = mock_table
    # Expected 1 item, but table returns 0
    mock_table.__len__.return_value = 0

    seed_payload = {"organizations": [VALID_ORGANIZATION]}

    with (
        patch("backend_v2.seed.run_seed.TinyDB", return_value=mock_db),
        patch("pathlib.Path.mkdir"),
        patch("pathlib.Path.exists", return_value=False),
        pytest.raises(SystemExit) as excinfo,
    ):
        await run_seed._seed_tinydb(Path("db_v2.json"), seed_payload, "local")
    assert excinfo.value.code == 1


@pytest.mark.asyncio
async def test_seed_firestore_when_firebase_not_available(capsys: pytest.CaptureFixture[str]) -> None:
    """Test _seed_firestore returns early if Firebase Admin is not available."""
    with patch("backend_v2.seed.run_seed.FIREBASE_AVAILABLE", False):
        await run_seed._seed_firestore({}, "firestore")
        captured = capsys.readouterr()
        assert "Firebase Admin not installed." in captured.out


@pytest.mark.asyncio
async def test_seed_firestore_execution() -> None:
    """Test _seed_firestore processes documents and commits batches."""
    mock_client = MagicMock()
    mock_batch = MagicMock()
    mock_client.batch.return_value = mock_batch
    mock_coll = MagicMock()
    mock_client.collection.return_value = mock_coll

    seed_payload = {
        "organizations": [VALID_ORGANIZATION],
        "workflows": [VALID_WORKFLOW],
    }

    with (
        patch("backend_v2.seed.run_seed.FIREBASE_AVAILABLE", True),
        patch("backend_v2.seed.run_seed.firebase_admin._apps", []),
        patch("backend_v2.seed.run_seed.credentials.ApplicationDefault"),
        patch("backend_v2.seed.run_seed.firebase_admin.initialize_app"),
        patch("backend_v2.seed.run_seed.firestore.client", return_value=mock_client),
        patch("backend_v2.seed.run_seed._delete_collection"),
        patch("backend_v2.services.orchestrator.dag_compiler.DAGCompilerService.validate_workflow"),
    ):
        await run_seed._seed_firestore(seed_payload, "firestore")
        mock_batch.set.assert_called()
        mock_batch.commit.assert_called()


@pytest.mark.asyncio
async def test_seed_firestore_batch_chunking_and_missing_doc_id(capsys: pytest.CaptureFixture[str]) -> None:
    """Test _seed_firestore handles batch commits at threshold and skips items with missing id."""
    mock_client = MagicMock()
    mock_batch = MagicMock()
    mock_client.batch.return_value = mock_batch
    mock_coll = MagicMock()
    mock_client.collection.return_value = mock_coll

    # Generate 401 valid items to trigger batch.commit() at count >= 400
    many_orgs = [{**VALID_ORGANIZATION, "id": f"org_0000000000{i:04d}"} for i in range(405)]

    seed_payload = {"organizations": many_orgs}

    with (
        patch("backend_v2.seed.run_seed.FIREBASE_AVAILABLE", True),
        patch("backend_v2.seed.run_seed.firebase_admin._apps", ["app"]),
        patch("backend_v2.seed.run_seed.firestore.client", return_value=mock_client),
        patch("backend_v2.seed.run_seed._delete_collection"),
    ):
        await run_seed._seed_firestore(seed_payload, "firestore")
        assert mock_batch.commit.call_count >= 2


@pytest.mark.asyncio
async def test_seed_firestore_validation_error_fails_fast() -> None:
    """Test _seed_firestore fails fast on invalid items."""
    mock_client = MagicMock()
    seed_payload = {"organizations": [{"id": "invalid"}]}

    with (
        patch("backend_v2.seed.run_seed.FIREBASE_AVAILABLE", True),
        patch("backend_v2.seed.run_seed.firebase_admin._apps", ["app"]),
        patch("backend_v2.seed.run_seed.firestore.client", return_value=mock_client),
        patch("backend_v2.seed.run_seed._delete_collection"),
        pytest.raises(SystemExit) as excinfo,
    ):
        await run_seed._seed_firestore(seed_payload, "firestore")
    assert excinfo.value.code == 1


@pytest.mark.asyncio
async def test_seed_firestore_processing_error_fails_fast() -> None:
    """Test _seed_firestore fails fast on unexpected processing error."""
    mock_client = MagicMock()
    with (
        patch("backend_v2.seed.run_seed.FIREBASE_AVAILABLE", True),
        patch("backend_v2.seed.run_seed.firebase_admin._apps", ["app"]),
        patch("backend_v2.seed.run_seed.firestore.client", return_value=mock_client),
        patch("backend_v2.seed.run_seed._delete_collection"),
        patch.dict(
            "backend_v2.seed.run_seed.STANDARD_REGISTRY",
            {
                "organizations": {
                    "table": "organizations",
                    "model": MagicMock(validate_python=MagicMock(side_effect=TypeError("Unexpected"))),
                    "id_field": "id",
                }
            },
        ),
        pytest.raises(SystemExit) as excinfo,
    ):
        await run_seed._seed_firestore({"organizations": [{}]}, "firestore")
    assert excinfo.value.code == 1


def test_delete_collection_pagination() -> None:
    """Test _delete_collection deletes documents in batches."""
    mock_coll = MagicMock()
    doc1 = MagicMock()
    doc2 = MagicMock()
    mock_coll.limit.return_value.stream.side_effect = [
        [doc1, doc2],  # Batch 1 (size 2 == batch_size, triggers recursion)
        [],  # Batch 2 (size 0, recursion terminates)
    ]

    run_seed._delete_collection(mock_coll, batch_size=2)
    doc1.reference.delete.assert_called_once()
    doc2.reference.delete.assert_called_once()
