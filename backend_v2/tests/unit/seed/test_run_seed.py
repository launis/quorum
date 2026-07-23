import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.seed import run_seed


def test_run_seed_main_help(capsys: pytest.CaptureFixture[str]) -> None:
    """Test that run_seed.py can be imported and argparser works."""
    with patch.object(sys, "argv", ["run_seed.py", "--help"]):
        with pytest.raises(SystemExit) as excinfo:
            run_seed.main()

        assert excinfo.value.code == 0
        captured = capsys.readouterr()
        assert "Unified V2 Database Seeder" in captured.out


@pytest.mark.asyncio
async def test_seed_tinydb_empty() -> None:
    """Test the TinyDB seeding process with mock empty data to gain coverage."""
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
async def test_seed_database_local_branch() -> None:
    """Test the main seed_database orchestrator for 'local' target."""
    with (
        patch("pathlib.Path.exists", return_value=True),
        patch("backend_v2.seed.run_seed.open"),
        patch("backend_v2.seed.run_seed.json.load", return_value={}),
        patch("backend_v2.seed.run_seed._seed_tinydb", new_callable=AsyncMock) as mock_seed,
    ):
        await run_seed.seed_database("local")
        mock_seed.assert_called_once_with(run_seed.LOCAL_DB_PATH, {}, "local", dry_run=False)
