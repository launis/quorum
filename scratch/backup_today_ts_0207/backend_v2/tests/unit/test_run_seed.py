from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from backend_v2.seed.run_seed import _fail_fast, main


def test_fail_fast_exits() -> None:
    """Test that _fail_fast calls sys.exit(1)."""
    with pytest.raises(SystemExit) as exc:
        _fail_fast("test message", Exception("test err"))
    assert exc.value.code == 1


@patch("backend_v2.seed.run_seed.seed_database", new_callable=AsyncMock)
@patch("sys.argv", ["run_seed.py", "local"])
def test_main_runs_local(mock_seed_database: AsyncMock) -> None:
    """Test that main() correctly parses 'local' and executes seed_database."""
    main()
    mock_seed_database.assert_called_once_with("local")


@patch("backend_v2.seed.run_seed.seed_database", new_callable=AsyncMock)
@patch("sys.argv", ["run_seed.py", "all"])
def test_main_runs_all(mock_seed_database: AsyncMock) -> None:
    """Test that main() correctly parses 'all' and executes seed_database for local and firestore."""
    main()
    assert mock_seed_database.call_count == 2

    # Verify both targets were called (order doesn't matter since they come from a set)
    calls = [call.args[0] for call in mock_seed_database.call_args_list]
    assert "local" in calls
    assert "firestore" in calls


@pytest.mark.asyncio
@patch("backend_v2.seed.run_seed.os.path.exists", return_value=True)
@patch("backend_v2.seed.run_seed._seed_tinydb", new_callable=AsyncMock)
@patch("backend_v2.seed.run_seed.json.load")
@patch("builtins.open")
async def test_seed_database_local(
    mock_open: Any, mock_json_load: Any, mock_seed_tinydb: AsyncMock, mock_exists: Any
) -> None:
    """Test seed_database with local target."""
    from backend_v2.seed.run_seed import seed_database

    mock_json_load.return_value = {"mock": "data"}
    await seed_database("local")
    mock_seed_tinydb.assert_called_once()


@pytest.mark.asyncio
@patch("backend_v2.seed.run_seed.os.path.exists", return_value=True)
@patch("backend_v2.seed.run_seed._seed_firestore", new_callable=AsyncMock)
@patch("backend_v2.seed.run_seed.json.load")
@patch("builtins.open")
async def test_seed_database_firestore(
    mock_open: Any, mock_json_load: Any, mock_seed_firestore: AsyncMock, mock_exists: Any
) -> None:
    """Test seed_database with firestore target."""
    from backend_v2.seed.run_seed import seed_database

    mock_json_load.return_value = {"mock": "data"}
    await seed_database("firestore")
    mock_seed_firestore.assert_called_once()


@pytest.mark.asyncio
@patch("backend_v2.seed.run_seed.os.path.exists", return_value=False)
@patch("backend_v2.seed.run_seed.sys.exit")
async def test_seed_database_no_file(mock_exit: Any, mock_exists: Any) -> None:
    """Test seed_database when file does not exist."""
    from backend_v2.seed.run_seed import seed_database

    mock_exit.side_effect = SystemExit(1)
    with pytest.raises(SystemExit):
        await seed_database("local")
    mock_exit.assert_called_once_with(1)


@pytest.mark.asyncio
@patch("backend_v2.seed.run_seed.TinyDB")
@patch("backend_v2.seed.run_seed.shutil")
@patch("backend_v2.seed.run_seed.os.path.exists", return_value=True)
@patch("backend_v2.seed.run_seed.os.path.getsize", return_value=123)
@patch("backend_v2.seed.run_seed.os.makedirs")
async def test_seed_tinydb_empty_data(
    mock_makedirs: Any,
    mock_getsize: Any,
    mock_exists: Any,
    mock_shutil: Any,
    mock_tinydb: Any,
) -> None:
    """Test _seed_tinydb initialization and empty data loop."""
    from backend_v2.seed.run_seed import _seed_tinydb

    mock_db_instance = mock_tinydb.return_value

    await _seed_tinydb("fake/path/db_v2.json", {}, "local")

    mock_db_instance.drop_tables.assert_called_once()
    mock_tinydb.assert_called_once_with("fake/path/db_v2.json", encoding="utf-8")
