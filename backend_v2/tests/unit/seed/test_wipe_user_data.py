"""Unit tests for the wipe_user_data script."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.seed.wipe_user_data import main, wipe_dynamic_data


def test_wipe_dynamic_data_abort(monkeypatch: pytest.MonkeyPatch) -> None:
    """Tests the wipe operation is aborted when user does not confirm."""
    monkeypatch.setattr("builtins.input", lambda _: "n")

    mock_open = MagicMock()
    monkeypatch.setattr("builtins.open", mock_open)

    wipe_dynamic_data()
    mock_open.assert_not_called()


def test_wipe_dynamic_data_success(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Tests successful wipe operation when user confirms."""
    monkeypatch.setattr("builtins.input", lambda _: "y")

    # Setup mock file structure
    db_path = tmp_path / "db_v2.json"
    backup_dir = tmp_path / "backups"
    executions_dir = tmp_path / "executions"
    executions_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr("backend_v2.seed.wipe_user_data.DB_PATH", db_path)
    monkeypatch.setattr("backend_v2.seed.wipe_user_data.BACKUP_DIR", backup_dir)
    monkeypatch.setattr("backend_v2.seed.wipe_user_data.EXECUTIONS_DIR", executions_dir)

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


def test_wipe_dynamic_data_force_bypasses_prompt(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Tests force flag bypasses interactive prompt."""
    mock_input = MagicMock()
    monkeypatch.setattr("builtins.input", mock_input)

    db_path = tmp_path / "db_v2.json"
    backup_dir = tmp_path / "backups"
    executions_dir = tmp_path / "executions"

    monkeypatch.setattr("backend_v2.seed.wipe_user_data.DB_PATH", db_path)
    monkeypatch.setattr("backend_v2.seed.wipe_user_data.BACKUP_DIR", backup_dir)
    monkeypatch.setattr("backend_v2.seed.wipe_user_data.EXECUTIONS_DIR", executions_dir)

    with open(db_path, "w", encoding="utf-8") as f:
        json.dump({"workflows": {}, "executions": {}}, f)

    wipe_dynamic_data(force=True)
    mock_input.assert_not_called()


def test_wipe_dynamic_data_file_not_found(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Tests AppException is raised when database file does not exist."""
    missing_db = tmp_path / "non_existent.json"
    monkeypatch.setattr("backend_v2.seed.wipe_user_data.DB_PATH", missing_db)

    with pytest.raises(AppException) as exc_info:
        wipe_dynamic_data(force=True)

    assert exc_info.value.status_code == 404
    assert exc_info.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value


def test_wipe_dynamic_data_corrupted_json_failure(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Tests AppException is raised when database JSON is corrupted."""
    corrupted_db = tmp_path / "corrupted_db.json"
    corrupted_db.write_text("NOT_VALID_JSON", encoding="utf-8")
    backup_dir = tmp_path / "backups"

    monkeypatch.setattr("backend_v2.seed.wipe_user_data.DB_PATH", corrupted_db)
    monkeypatch.setattr("backend_v2.seed.wipe_user_data.BACKUP_DIR", backup_dir)

    with pytest.raises(AppException) as exc_info:
        wipe_dynamic_data(force=True)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value


def test_main_cli_entrypoint(monkeypatch: pytest.MonkeyPatch) -> None:
    """Tests CLI entrypoint parses args and calls wipe_dynamic_data."""
    mock_wipe = MagicMock()
    monkeypatch.setattr("backend_v2.seed.wipe_user_data.wipe_dynamic_data", mock_wipe)

    main(["--force"])
    mock_wipe.assert_called_once_with(force=True)
