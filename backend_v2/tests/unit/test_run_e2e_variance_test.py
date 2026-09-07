"""Unit tests for run_e2e_variance_test script."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest
import requests

from scripts.run_e2e_variance_test import (
    check_backend,
    force_kill_services,
    load_inputs_from_path,
    main,
    make_noise_injector,
    run_variance_test,
    trigger_execution,
    validate_execution_kelvollisuus,
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


def test_pillar1_process_isolation_wmi_and_pid_protection(monkeypatch: pytest.MonkeyPatch) -> None:
    """Pillar 1: Mathematical proof of WMI process termination and PID protection."""
    executed_commands: list[str | list[str]] = []

    def mock_run(cmd: Any, *args: Any, **kwargs: Any) -> Any:
        executed_commands.append(cmd)
        return type("Res", (), {"stdout": "12345\n", "stderr": ""})()

    monkeypatch.setattr("subprocess.run", mock_run)
    monkeypatch.setattr("time.sleep", lambda s: None)

    force_kill_services()

    # Verify powershell CIM command was invoked with current PID exclusion
    current_pid = os.getpid()
    ps_calls = [c for c in executed_commands if isinstance(c, list) and "powershell" in c[0]]
    assert len(ps_calls) >= 2, "Expected at least 2 PowerShell commands (kill + verification)"

    kill_cmd_str = ps_calls[0][-1]
    assert f"$_.ProcessId -ne {current_pid}" in kill_cmd_str, "Runner's own PID must be protected"
    assert "backend_v2|run_worker|uvicorn|arq" in kill_cmd_str, "Must filter relevant background workers"

    # Verify Redis flushes
    assert any("redis-cli flushall" in str(c) for c in executed_commands)
    assert any("FLUSHALL" in str(c) for c in executed_commands)


def test_pillar2_unicode_noise_hash_perturbation() -> None:
    """Pillar 2: Mathematical proof that Unicode perturbation changes SHA-256 hash to bypass LLM cache."""
    original_text = "This is a comprehensive evaluation of cognitive reasoning."
    injector_run1 = make_noise_injector(0)
    injector_run2 = make_noise_injector(1)

    text_run1 = injector_run1(original_text)
    text_run2 = injector_run2(original_text)

    hash_run1 = hashlib.sha256(text_run1.encode("utf-8")).hexdigest()
    hash_run2 = hashlib.sha256(text_run2.encode("utf-8")).hexdigest()

    # Hashes must differ to force LLM provider cache miss
    assert hash_run1 != hash_run2, "Hashes must differ across runs to ensure fresh provider inference"

    # Semantic content must remain identical when normalized
    assert text_run1.split() == text_run2.split() == original_text.split(), "Word sequence must remain identical"
    assert "\u00a0" in text_run1
    assert "\u2002" in text_run2


def test_pillar3_dev_execution_mode_parity_propagation(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Pillar 3: Verify DEV_EXECUTION_MODE is captured and propagated to backend subprocess."""
    inputs_file = tmp_path / "inputs.json"
    with inputs_file.open("w", encoding="utf-8") as f:
        json.dump({"product_text": "Sample text"}, f)

    db_file = tmp_path / "mock_db.json"
    with db_file.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "executions": {
                    "exe_1": {"id": "exe_1", "status": "PASSED"},
                }
            },
            f,
        )

    spawned_environments: list[dict[str, str]] = []

    class MockPopen:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            if "env" in kwargs and kwargs["env"] is not None:
                spawned_environments.append(kwargs["env"])

    monkeypatch.setattr("scripts.run_e2e_variance_test.force_kill_services", lambda: None)
    monkeypatch.setattr("scripts.run_e2e_variance_test.check_backend", lambda: True)
    monkeypatch.setattr("scripts.run_e2e_variance_test.trigger_execution", lambda inp: "exe_1")
    monkeypatch.setattr("time.sleep", lambda s: None)
    monkeypatch.setattr("subprocess.Popen", MockPopen)
    monkeypatch.setattr(
        "subprocess.run",
        lambda *args, **kwargs: type("Res", (), {"stdout": "OK", "stderr": ""})(),
    )

    monkeypatch.setenv("DEV_EXECUTION_MODE", "full")
    run_variance_test(str(inputs_file), num_runs=1, timeout_seconds=10, db_path=db_file)

    assert len(spawned_environments) == 1
    assert spawned_environments[0].get("DEV_EXECUTION_MODE") == "full"


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

    db_file = tmp_path / "mock_db.json"
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
    ids = run_variance_test(None, num_runs=1, timeout_seconds=10, db_path=db_file)
    assert ids == ["exe_test_1"]


def test_run_variance_test_timeout(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    inputs_file = tmp_path / "inputs_timeout.json"
    with inputs_file.open("w", encoding="utf-8") as f:
        json.dump({"product_text": "Sample product text"}, f)

    db_file = tmp_path / "mock_empty_db.json"
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
        run_variance_test(str(inputs_file), num_runs=1, timeout_seconds=1, db_path=db_file)


def test_validate_execution_kelvollisuus_valid(tmp_path: Path) -> None:
    """Test that a clean passed execution without starvation is valid."""
    target_exec = {
        "id": "exe_clean_1",
        "status": "PASSED",
        "profile_syntheses": {"prf_1": {"section_syntheses": {"sec_1": "Clean summary"}, "data_starvation": None}},
    }
    trace_file = tmp_path / "execution_trace.json"
    trace_file.write_text(json.dumps([{"step_id": "stp_1", "content": {"results": []}}]), encoding="utf-8")

    is_valid, reason = validate_execution_kelvollisuus(target_exec, trace_file)
    assert is_valid is True
    assert "valid" in reason.lower()


def test_validate_execution_kelvollisuus_non_passed_status() -> None:
    """Test that failed status is rejected as invalid."""
    target_exec = {"id": "exe_failed", "status": "FAILED"}
    is_valid, reason = validate_execution_kelvollisuus(target_exec)
    assert is_valid is False
    assert "non-passed status" in reason


def test_validate_execution_kelvollisuus_data_starvation_in_profile_syntheses() -> None:
    """Test that data starvation recorded in profile_syntheses is caught and rejected."""
    target_exec = {
        "id": "exe_starved_1",
        "status": "PASSED",
        "profile_syntheses": {
            "prf_1": {
                "data_starvation": {
                    "event_type": "starvation",
                    "total_atoms": 0,
                    "reason": "Data starvation: zero atoms extracted",
                }
            }
        },
    }
    is_valid, reason = validate_execution_kelvollisuus(target_exec)
    assert is_valid is False
    assert "data starvation" in reason.lower()
    assert "prf_1" in reason


def test_validate_execution_kelvollisuus_data_starvation_in_trace(tmp_path: Path) -> None:
    """Test that data starvation event in execution_trace.json is caught and rejected."""
    target_exec = {
        "id": "exe_starved_trace",
        "status": "PASSED",
        "profile_syntheses": {},
    }
    trace_file = tmp_path / "execution_trace.json"
    trace_data = [
        {
            "step_id": "stp_synthesis",
            "content": {
                "event_type": "starvation",
                "total_atoms": 2,
                "reason": "Data starvation: sparse atoms yielded zero evaluative evidence",
            },
        }
    ]
    trace_file.write_text(json.dumps(trace_data), encoding="utf-8")

    is_valid, reason = validate_execution_kelvollisuus(target_exec, trace_file)
    assert is_valid is False
    assert "stp_synthesis" in reason
    assert "sparse atoms" in reason


def test_run_variance_test_aborts_on_data_starvation(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Test that run_variance_test aborts execution immediately when data starvation is detected."""
    inputs_file = tmp_path / "inputs_starved.json"
    with inputs_file.open("w", encoding="utf-8") as f:
        json.dump({"product_text": "Sample product text"}, f)

    db_file = tmp_path / "mock_starved_db.json"
    with db_file.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "executions": {
                    "exe_starved": {
                        "id": "exe_starved",
                        "status": "PASSED",
                        "profile_syntheses": {
                            "default": {
                                "data_starvation": {
                                    "event_type": "starvation",
                                    "total_atoms": 0,
                                    "reason": "insufficient observations",
                                }
                            }
                        },
                    }
                }
            },
            f,
        )

    monkeypatch.setattr("scripts.run_e2e_variance_test.force_kill_services", lambda: None)
    monkeypatch.setattr("scripts.run_e2e_variance_test.check_backend", lambda: True)
    monkeypatch.setattr("scripts.run_e2e_variance_test.trigger_execution", lambda inp: "exe_starved")
    monkeypatch.setattr("time.sleep", lambda s: None)

    class MockPopen:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

    monkeypatch.setattr("subprocess.Popen", MockPopen)

    with pytest.raises(SystemExit):
        run_variance_test(str(inputs_file), num_runs=1, timeout_seconds=10, db_path=db_file)


def test_multi_field_noise_perturbation() -> None:
    """Test that all string fields containing whitespace are perturbed across runs."""
    raw_inputs = {
        "chat_log": "Hello world from chat",
        "product_text": "Final product document",
        "reflection_text": "Self reflection text here",
        "number_field": 42,
        "dict_field": {"inner": "value"},
    }
    injector_0 = make_noise_injector(0)
    injector_1 = make_noise_injector(1)

    injected_0 = dict(raw_inputs)
    injected_1 = dict(raw_inputs)

    for k in ["chat_log", "product_text", "reflection_text"]:
        injected_0[k] = injector_0(str(raw_inputs[k]))
        injected_1[k] = injector_1(str(raw_inputs[k]))

    assert injected_0["number_field"] == 42
    assert injected_0["dict_field"] == {"inner": "value"}

    for k in ["chat_log", "product_text", "reflection_text"]:
        h0 = hashlib.sha256(str(injected_0[k]).encode("utf-8")).hexdigest()
        h1 = hashlib.sha256(str(injected_1[k]).encode("utf-8")).hexdigest()
        assert h0 != h1, f"Hash for {k} must differ across runs"
        assert "\u00a0" in str(injected_0[k])
        assert "\u2002" in str(injected_1[k])


def test_noise_perturbation_fail_fast_on_zero_whitespace(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Test that run_variance_test raises RuntimeError when raw_inputs has no whitespace-containing strings."""
    inputs_file = tmp_path / "inputs_nospace.json"
    with inputs_file.open("w", encoding="utf-8") as f:
        json.dump({"product_text": "NoSpacesHere", "number": 123}, f)

    db_file = tmp_path / "mock_db.json"
    with db_file.open("w", encoding="utf-8") as f:
        json.dump({"executions": {}}, f)

    monkeypatch.setattr("scripts.run_e2e_variance_test.force_kill_services", lambda: None)
    monkeypatch.setattr("scripts.run_e2e_variance_test.check_backend", lambda: True)
    monkeypatch.setattr("time.sleep", lambda s: None)

    class MockPopen:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

    monkeypatch.setattr("subprocess.Popen", MockPopen)

    with pytest.raises(RuntimeError, match="No whitespace found in any string input fields"):
        run_variance_test(str(inputs_file), num_runs=1, timeout_seconds=10, db_path=db_file)


def test_no_cache_flag_propagation(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Test that no_cache=True appends --no-cache to cmd and sets DISABLE_VERTEX_CACHE=true in env."""
    inputs_file = tmp_path / "inputs.json"
    with inputs_file.open("w", encoding="utf-8") as f:
        json.dump({"product_text": "Sample text with space"}, f)

    db_file = tmp_path / "mock_db.json"
    with db_file.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "executions": {
                    "exe_1": {
                        "id": "exe_1",
                        "status": "PASSED",
                        "profile_syntheses": {"prf_1": {"data_starvation": None}},
                    }
                }
            },
            f,
        )

    spawned_cmds: list[list[str]] = []
    spawned_envs: list[dict[str, str]] = []

    class MockPopen:
        def __init__(self, cmd: list[str], *args: Any, **kwargs: Any) -> None:
            spawned_cmds.append(cmd)
            if "env" in kwargs and kwargs["env"] is not None:
                spawned_envs.append(kwargs["env"])

    monkeypatch.setattr("scripts.run_e2e_variance_test.force_kill_services", lambda: None)
    monkeypatch.setattr("scripts.run_e2e_variance_test.check_backend", lambda: True)
    monkeypatch.setattr("scripts.run_e2e_variance_test.trigger_execution", lambda inp: "exe_1")
    monkeypatch.setattr("time.sleep", lambda s: None)
    monkeypatch.setattr("subprocess.Popen", MockPopen)
    monkeypatch.setattr(
        "subprocess.run",
        lambda *args, **kwargs: type("Res", (), {"stdout": "OK", "stderr": ""})(),
    )

    run_variance_test(str(inputs_file), num_runs=1, timeout_seconds=10, db_path=db_file, no_cache=True)

    assert len(spawned_cmds) == 1
    assert "--no-cache" in spawned_cmds[0]
    assert len(spawned_envs) == 1
    assert spawned_envs[0].get("DISABLE_VERTEX_CACHE") == "true"


def test_cooldown_seconds_and_scratch_dir(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Test that cooldown_seconds triggers time.sleep on subsequent runs and writes to scratch dir."""
    inputs_file = tmp_path / "inputs.json"
    with inputs_file.open("w", encoding="utf-8") as f:
        json.dump({"product_text": "Sample text with space"}, f)

    db_file = tmp_path / "mock_db.json"
    with db_file.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "executions": {
                    "exe_1": {
                        "id": "exe_1",
                        "status": "PASSED",
                        "profile_syntheses": {"prf_1": {"data_starvation": None}},
                    },
                    "exe_2": {
                        "id": "exe_2",
                        "status": "PASSED",
                        "profile_syntheses": {"prf_1": {"data_starvation": None}},
                    },
                }
            },
            f,
        )

    slept_durations: list[int | float] = []
    exec_counter = 0

    def mock_trigger(inp: Any) -> str:
        nonlocal exec_counter
        exec_counter += 1
        return f"exe_{exec_counter}"

    monkeypatch.setattr("scripts.run_e2e_variance_test.force_kill_services", lambda: None)
    monkeypatch.setattr("scripts.run_e2e_variance_test.check_backend", lambda: True)
    monkeypatch.setattr("scripts.run_e2e_variance_test.trigger_execution", mock_trigger)
    monkeypatch.setattr("time.sleep", lambda s: slept_durations.append(s))

    class MockPopen:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

    monkeypatch.setattr("subprocess.Popen", MockPopen)
    monkeypatch.setattr(
        "subprocess.run",
        lambda *args, **kwargs: type("Res", (), {"stdout": "OK", "stderr": ""})(),
    )

    run_variance_test(str(inputs_file), num_runs=2, timeout_seconds=10, db_path=db_file, cooldown_seconds=15)

    assert 15 in slept_durations, "Cooldown sleep of 15s must be called for Run 2"
    assert Path("scratch/variance_inputs/e2e_inputs_run1.json").exists()
    assert Path("scratch/variance_inputs/e2e_inputs_noisy.json").exists()
    assert not Path("tmp/e2e_inputs_run1.json").exists()


def test_main_cli_argparse(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that main() correctly parses CLI arguments and forwards them to run_variance_test."""
    captured_kwargs: dict[str, Any] = {}

    def mock_run_variance_test(**kwargs: Any) -> list[str]:
        captured_kwargs.update(kwargs)
        return ["exe_cli_1", "exe_cli_2"]

    monkeypatch.setattr("scripts.run_e2e_variance_test.run_variance_test", mock_run_variance_test)

    res = main(
        ["path/to/inputs", "--no-cache", "--cooldown-seconds", "30", "--num-runs", "3", "--timeout-seconds", "3600"]
    )

    assert res == ["exe_cli_1", "exe_cli_2"]
    assert captured_kwargs["inputs_target"] == "path/to/inputs"
    assert captured_kwargs["no_cache"] is True
    assert captured_kwargs["cooldown_seconds"] == 30
    assert captured_kwargs["num_runs"] == 3
    assert captured_kwargs["timeout_seconds"] == 3600
