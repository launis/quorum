"""Unit tests for the wipe_user_data script."""

import json
from typing import Any
from unittest.mock import MagicMock

import pytest

from backend_v2.seed.wipe_user_data import wipe_dynamic_data


def test_wipe_dynamic_data_abort(monkeypatch: pytest.MonkeyPatch) -> None:
    """Tests the wipe operation is aborted when user does not confirm."""
    monkeypatch.setattr("builtins.input", lambda _: "n")

    # We should not hit any file operations
    mock_open = MagicMock()
    monkeypatch.setattr("builtins.open", mock_open)

    wipe_dynamic_data()
    mock_open.assert_not_called()


def test_wipe_dynamic_data_success(monkeypatch: pytest.MonkeyPatch, tmp_path: Any) -> None:
    """Tests successful wipe operation when user confirms."""
    monkeypatch.setattr("builtins.input", lambda _: "y")

    # Setup mock file structure
    db_path = tmp_path / "db_v2.json"
    backup_dir = tmp_path / "backups"

    # Mock paths in the module
    monkeypatch.setattr("backend_v2.seed.wipe_user_data.DB_PATH", str(db_path))
    monkeypatch.setattr("backend_v2.seed.wipe_user_data.BACKUP_DIR", str(backup_dir))

    # The script uses os.path.join relative to __file__ for executions_dir
    # So we'll mock os.path.dirname and join just for that part, or we can just run it
    # and mock shutil.rmtree

    db_data = {"system_config": {"item": 1}, "workflows": {"wk_1": {}}, "executions": {"ex_1": {}}}

    with open(db_path, "w", encoding="utf-8") as f:
        json.dump(db_data, f)

    mock_rmtree = MagicMock()
    monkeypatch.setattr("shutil.rmtree", mock_rmtree)

    wipe_dynamic_data()

    # Check if backup was created
    backups = list(backup_dir.glob("*.json"))
    assert len(backups) == 1

    # Check if db was updated
    with open(db_path, encoding="utf-8") as f:
        updated_data = json.load(f)

    assert updated_data["system_config"] == {"item": 1}
    assert updated_data["workflows"] == {}
    assert updated_data["executions"] == {}

    mock_rmtree.assert_called_once()
