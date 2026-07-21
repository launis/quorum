from unittest.mock import AsyncMock
"""Unit tests for the OpenAPI schema generation script."""

import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from backend_v2.exceptions import AppException
from backend_v2.scripts.generate_openapi import main


def test_generate_openapi_success(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Tests successful generation of the OpenAPI schema JSON file."""
    # Mock the root_dir inside generate_openapi to use tmp_path
    monkeypatch.setattr("backend_v2.scripts.generate_openapi.root_dir", tmp_path)

    # Mock the FastAPI app and its openapi method
    mock_app = MagicMock()
    mock_app.openapi.return_value = {"openapi": "3.1.0", "info": {"title": "Test API"}}

    # We need to mock the import of `app` from `backend_v2.main`
    class MockMain:
        app = mock_app

    import sys

    sys.modules["backend_v2.main"] = MockMain  # type: ignore

    main()

    output_file = tmp_path / "docs" / "swagger" / "openapi.json"
    assert output_file.exists()

    with open(output_file, encoding="utf-8") as f:
        data = json.load(f)

    assert data["openapi"] == "3.1.0"
    assert data["info"]["title"] == "Test API"

    # cleanup sys.modules
    del sys.modules["backend_v2.main"]


def test_generate_openapi_filesystem_error(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Tests the failure path when file writing fails (e.g. permissions)."""
    monkeypatch.setattr("backend_v2.scripts.generate_openapi.root_dir", tmp_path)

    mock_app = MagicMock()
    mock_app.openapi.return_value = {"openapi": "3.1.0"}

    class MockMain:
        app = mock_app

    import sys

    sys.modules["backend_v2.main"] = MockMain  # type: ignore

    # Make the target directory read-only or mock the open call
    docs_dir = tmp_path / "docs" / "swagger"
    docs_dir.mkdir(parents=True)

    def mock_open(*args: Any, **kwargs: Any) -> Any:
        raise PermissionError("Access denied")

    monkeypatch.setattr("pathlib.Path.open", mock_open)

    with pytest.raises(AppException) as exc_info:
        main()

    assert exc_info.value.status_code == 500
    assert "Failed to write OpenAPI schema file due to: Access denied" in str(exc_info.value)

    del sys.modules["backend_v2.main"]
