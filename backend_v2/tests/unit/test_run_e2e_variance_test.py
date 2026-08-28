"""Unit tests for run_e2e_variance_test script."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest
import requests

from scripts.run_e2e_variance_test import (
    check_backend,
    force_kill_services,
    load_inputs_from_path,
    make_noise_injector,
    run_variance_test,
    trigger_execution,
)


def test_make_noise_injector_empty_and_no_spaces() -> None:
    injector = make_noise_injector(0)
    assert injector("") == ""
    assert injector("WordWithoutSpaces") == "WordWithoutSpaces"


def test_make_noise_injector_replaces_first_space() -> None:
    injector_0 = make_noise_injector(0)
    res_0 = injector_0("Hello world test")
    assert res_0 == "Hello\u00a0world test"

    injector_1 = make_noise_injector(1)
    res_1 = injector_1("Hello world test")
    assert res_1 == "Hello\u2002world test"


def test_load_inputs_from_path_json(tmp_path: Path) -> None:
    test_json = tmp_path / "inputs.json"
    data = {"chat_log": "Hello", "product_text": "World"}
    with test_json.open("w", encoding="utf-8") as f:
        json.dump(data, f)

    loaded = load_inputs_from_path(test_json)
    assert loaded == data


def test_load_inputs_from_path_invalid_json(tmp_path: Path) -> None:
    test_json = tmp_path / "list_inputs.json"
    with test_json.open("w", encoding="utf-8") as f:
        json.dump(["item1", "item2"], f)

    with pytest.raises(ValueError, match="JSON inputs file must contain a dictionary"):
        load_inputs_from_path(test_json)


def test_load_inputs_from_path_nonexistent() -> None:
    with pytest.raises(FileNotFoundError, match="Inputs path does not exist"):
        load_inputs_from_path("nonexistent/path/here.json")


def test_load_inputs_from_path_directory(tmp_path: Path) -> None:
    input_dir = tmp_path / "inputs"
    input_dir.mkdir()

    (input_dir / "keskusteluhistoria.md").write_text("Chat conversation content", encoding="utf-8")
    (input_dir / "lopputuote.txt").write_text("Final product content", encoding="utf-8")
    (input_dir / "reflektio.txt").write_text("Reflection text content", encoding="utf-8")
    (input_dir / "custom_key.json").write_text(json.dumps({"sub": 123}), encoding="utf-8")

    loaded = load_inputs_from_path(input_dir)
    assert loaded["chat_log"] == "Chat conversation content"
    assert loaded["product_text"] == "Final product content"
    assert loaded["reflection_text"] == "Reflection text content"
    assert loaded["custom_key"] == {"sub": 123}
    assert "document_date" in loaded


def test_load_inputs_from_path_pdf(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    input_dir = tmp_path / "pdf_inputs"
    input_dir.mkdir()
    pdf_file = input_dir / "sample.pdf"
    pdf_file.write_bytes(b"%PDF-1.4 dummy content")

    mock_doc = MagicMock()
    mock_doc.metadata = {"modDate": "D:20260625073855+03'00'"}
    monkeypatch.setattr("fitz.open", lambda stream, filetype: mock_doc)
    monkeypatch.setattr("pymupdf4llm.to_markdown", lambda doc: "Extracted PDF Markdown")

    loaded = load_inputs_from_path(input_dir)
    assert loaded["sample"] == "Extracted PDF Markdown"


def test_check_backend_success(monkeypatch: pytest.MonkeyPatch) -> None:
    class MockResponse:
        status_code = 200

    def mock_get(url: str, timeout: int = 2) -> MockResponse:
        return MockResponse()

    monkeypatch.setattr(requests, "get", mock_get)
    assert check_backend(max_retries=1) is True


def test_check_backend_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    def mock_get(url: str, timeout: int = 2) -> None:
        raise requests.ConnectionError("Connection refused")

    monkeypatch.setattr(requests, "get", mock_get)
    assert check_backend(max_retries=1) is False


def test_force_kill_services(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "subprocess.run",
        lambda *args, **kwargs: type("Res", (), {"stdout": "1234\n", "stderr": ""})(),
    )
    monkeypatch.setattr("time.sleep", lambda s: None)
    force_kill_services()


def test_trigger_execution(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    class MockWorkflowResp:
        status_code = 200
        ok = True

        def raise_for_status(self) -> None:
            pass

        def json(self) -> Any:
            return [{"id": "wf_test_123"}]

    class MockExecResp:
        status_code = 200
        ok = True

        def raise_for_status(self) -> None:
            pass

        def json(self) -> Any:
            return {
                "id": "exe_test_999",
                "execution_trace": [{"step_id": "stp_1", "content": {}}],
            }

    def mock_get(url: str, headers: Any = None, timeout: int = 10) -> MockWorkflowResp:
        return MockWorkflowResp()

    def mock_post(url: str, headers: Any = None, json: Any = None, timeout: int = 300) -> MockExecResp:
        return MockExecResp()

    monkeypatch.setattr(requests, "get", mock_get)
    monkeypatch.setattr(requests, "post", mock_post)

    exec_id = trigger_execution({"product_text": "Sample"})
    assert exec_id == "exe_test_999"


def test_trigger_execution_missing_trace(monkeypatch: pytest.MonkeyPatch) -> None:
    class MockWorkflowResp:
        status_code = 200
        ok = True

        def raise_for_status(self) -> None:
            pass

        def json(self) -> Any:
            return [{"id": "wf_test_123"}]

    class MockExecResp:
        status_code = 200
        ok = True

        def raise_for_status(self) -> None:
            pass

        def json(self) -> Any:
            return {"id": "exe_test_no_trace"}

    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: MockWorkflowResp())
    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: MockExecResp())

    with pytest.raises(SystemExit):
        trigger_execution({"product_text": "Sample"})


def test_run_variance_test_backend_fail(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    inputs_file = tmp_path / "inputs.json"
    with inputs_file.open("w", encoding="utf-8") as f:
        json.dump({"product_text": "Sample"}, f)

    monkeypatch.setattr("scripts.run_e2e_variance_test.force_kill_services", lambda: None)
    monkeypatch.setattr("scripts.run_e2e_variance_test.check_backend", lambda: False)

    class MockPopen:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

    monkeypatch.setattr("subprocess.Popen", MockPopen)

    with pytest.raises(SystemExit):
        run_variance_test(str(inputs_file), num_runs=1)


def test_run_variance_test_with_dict_fallback(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    inputs_file = tmp_path / "inputs_other.json"
    with inputs_file.open("w", encoding="utf-8") as f:
        json.dump({"custom_doc": "Test custom string", "numeric": 42}, f)

    db_file = Path("data/db_v2.json")
    db_file.parent.mkdir(parents=True, exist_ok=True)
    with db_file.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "executions": {
                    "exe_test_1": {"id": "exe_test_1", "status": "PASSED"},
                }
            },
            f,
        )

    monkeypatch.setattr("scripts.run_e2e_variance_test.force_kill_services", lambda: None)
    monkeypatch.setattr("scripts.run_e2e_variance_test.check_backend", lambda: True)
    monkeypatch.setattr("scripts.run_e2e_variance_test.trigger_execution", lambda inp: "exe_test_1")
    monkeypatch.setattr("time.sleep", lambda s: None)

    class MockPopen:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

    monkeypatch.setattr("subprocess.Popen", MockPopen)
    monkeypatch.setattr(
        "subprocess.run",
        lambda *args, **kwargs: type("Res", (), {"stdout": "OK", "stderr": ""})(),
    )

    monkeypatch.setenv("TEST_INPUTS_PATH", str(inputs_file))
    ids = run_variance_test(None, num_runs=1, timeout_seconds=10)
    assert ids == ["exe_test_1"]


def test_run_variance_test_timeout(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    inputs_file = tmp_path / "inputs_timeout.json"
    with inputs_file.open("w", encoding="utf-8") as f:
        json.dump({"product_text": "Sample"}, f)

    db_file = Path("data/db_v2.json")
    with db_file.open("w", encoding="utf-8") as f:
        json.dump({"executions": {}}, f)

    monkeypatch.setattr("scripts.run_e2e_variance_test.force_kill_services", lambda: None)
    monkeypatch.setattr("scripts.run_e2e_variance_test.check_backend", lambda: True)
    monkeypatch.setattr("scripts.run_e2e_variance_test.trigger_execution", lambda inp: "exe_timeout_1")
    monkeypatch.setattr("time.sleep", lambda s: None)

    class MockPopen:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

    monkeypatch.setattr("subprocess.Popen", MockPopen)
    monkeypatch.setattr(
        "subprocess.run",
        lambda *args, **kwargs: type("Res", (), {"stdout": "OK", "stderr": ""})(),
    )

    with pytest.raises(SystemExit):
        run_variance_test(str(inputs_file), num_runs=1, timeout_seconds=1)
