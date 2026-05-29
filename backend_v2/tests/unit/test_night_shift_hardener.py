import asyncio
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

# Add the scripts directory to the path so we can import night_shift_hardener
scripts_dir = str(Path(__file__).parents[3] / "scripts")
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

import night_shift_hardener


class MockMessage:
    """Mock the response message object returned by litellm acompletion."""

    def __init__(self, content: str) -> None:
        self.content = content


class MockChoice:
    """Mock the choice object returned inside choices array by litellm acompletion."""

    def __init__(self, content: str) -> None:
        self.message = MockMessage(content)


class MockResponse:
    """Mock the response object returned by litellm acompletion."""

    def __init__(self, content: str) -> None:
        self.choices = [MockChoice(content)]


@pytest.fixture
def temp_workspace(tmp_path: Path) -> tuple[Path, Path, Path]:
    """Fixture to set up a isolated temporary workspace for testing."""
    target_file = tmp_path / "dummy_service.py"
    target_file.write_text("def work():\n    pass\n", encoding="utf-8")

    state_file = tmp_path / "night_shift_state.json"
    system_prompt_file = tmp_path / "hardening.xml"
    system_prompt_file.write_text("<rules>Hardening Rules</rules>", encoding="utf-8")

    return target_file, state_file, system_prompt_file


@pytest.mark.asyncio
async def test_successful_hardening(temp_workspace: tuple[Path, Path, Path], monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify that a successful LLM hardening run formats the code and updates the state atomically."""
    target_file, state_file, _ = temp_workspace

    # Mock litellm acompletion to return valid hardened python code with exactly the configured audit items
    async def mock_acompletion(*args: tuple[Any, ...], **kwargs: dict[str, Any]) -> MockResponse:
        mock_checks = [
            {"rule_id": i, "rule_name": f"rule_{i}", "status": "Pass", "finding": "Ok"}
            for i in range(1, night_shift_hardener.RuleLimits.TOTAL_RULES.value + 1)
        ]
        json_data = json.dumps(
            {
                "audit_matrix": mock_checks,
                "is_rewritten": True,
                "hardened_code": ('def work() -> None:\n    """Execute work with strict validation."""\n    pass\n'),
            }
        )
        return MockResponse(json_data)

    import litellm

    monkeypatch.setattr(litellm, "acompletion", mock_acompletion)

    # Mock subprocess.run to simulate successful Ruff and MyPy runs
    def mock_run(*args: tuple[Any, ...], **kwargs: dict[str, Any]) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(args=args[0], returncode=0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", mock_run)

    semaphore = asyncio.Semaphore(1)
    success = await night_shift_hardener.process_file_with_retry(
        system_prompt="Rule 1", target_file=target_file, semaphore=semaphore, state_file_path=state_file
    )

    # Confirm processing returned success and state is saved as DONE
    assert success is True
    assert "strict validation" in target_file.read_text(encoding="utf-8")

    with open(state_file, encoding="utf-8") as f:
        state = json.load(f)
    assert state[target_file.as_posix()] == "DONE"


@pytest.mark.asyncio
async def test_syntax_validation_failure_triggers_rollback(
    temp_workspace: tuple[Path, Path, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that syntactically broken code is rejected and the original code is rolled back."""
    target_file, state_file, _ = temp_workspace
    original_content = target_file.read_text(encoding="utf-8")

    # Mock litellm acompletion to return invalid python syntax with correct number of checks
    async def mock_acompletion(*args: tuple[Any, ...], **kwargs: dict[str, Any]) -> MockResponse:
        mock_checks = [
            {"rule_id": i, "rule_name": f"rule_{i}", "status": "Pass", "finding": "Ok"}
            for i in range(1, night_shift_hardener.RuleLimits.TOTAL_RULES.value + 1)
        ]
        json_data = json.dumps(
            {"audit_matrix": mock_checks, "is_rewritten": True, "hardened_code": "def work( -> None:\n    pass"}
        )
        return MockResponse(json_data)

    import litellm

    monkeypatch.setattr(litellm, "acompletion", mock_acompletion)

    semaphore = asyncio.Semaphore(1)
    success = await night_shift_hardener.process_file_with_retry(
        system_prompt="Rule 1", target_file=target_file, semaphore=semaphore, state_file_path=state_file
    )

    # Confirm processing failed and original file content was fully restored
    assert success is False
    assert target_file.read_text(encoding="utf-8") == original_content

    with open(state_file, encoding="utf-8") as f:
        state = json.load(f)
    assert state[target_file.as_posix()] == "FAILED_VERIFICATION"


@pytest.mark.asyncio
async def test_quality_gate_failure_triggers_rollback(
    temp_workspace: tuple[Path, Path, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that code which compiles but fails Ruff or MyPy strict checks is rolled back."""
    target_file, state_file, _ = temp_workspace
    original_content = target_file.read_text(encoding="utf-8")

    # Mock litellm acompletion to return compilable but bad code with correct number of checks
    async def mock_acompletion(*args: tuple[Any, ...], **kwargs: dict[str, Any]) -> MockResponse:
        mock_checks = [
            {"rule_id": i, "rule_name": f"rule_{i}", "status": "Pass", "finding": "Ok"}
            for i in range(1, night_shift_hardener.RuleLimits.TOTAL_RULES.value + 1)
        ]
        json_data = json.dumps(
            {"audit_matrix": mock_checks, "is_rewritten": True, "hardened_code": "def work() -> None:\n    x = 10\n"}
        )
        return MockResponse(json_data)

    import litellm

    monkeypatch.setattr(litellm, "acompletion", mock_acompletion)

    # Mock subprocess.run to raise CalledProcessError (simulating a MyPy type-checking failure)
    def mock_run(*args: tuple[Any, ...], **kwargs: dict[str, Any]) -> None:
        raise subprocess.CalledProcessError(
            returncode=1, cmd=args[0], stderr="error: Function is missing type annotation"
        )

    monkeypatch.setattr(subprocess, "run", mock_run)

    semaphore = asyncio.Semaphore(1)
    success = await night_shift_hardener.process_file_with_retry(
        system_prompt="Rule 1", target_file=target_file, semaphore=semaphore, state_file_path=state_file
    )

    # Confirm processing failed, original file content was rolled back, and state was marked accordingly
    assert success is False
    assert target_file.read_text(encoding="utf-8") == original_content

    with open(state_file, encoding="utf-8") as f:
        state = json.load(f)
    assert state[target_file.as_posix()] == "FAILED_VERIFICATION"


@pytest.mark.asyncio
async def test_atomic_state_locking(temp_workspace: tuple[Path, Path, Path]) -> None:
    """Verify that multiple concurrent operations on the state file are thread-safe and atomic."""
    _, state_file, _ = temp_workspace

    # Trigger 10 concurrent state updates to simulate high concurrency
    tasks = [night_shift_hardener.safe_update_state(f"file_{i}.py", f"STATUS_{i}", state_file) for i in range(10)]

    await asyncio.gather(*tasks)

    # Confirm all 10 updates were successfully saved in the JSON state file without any data corruption
    with open(state_file, encoding="utf-8") as f:
        state_data = json.load(f)

    assert len(state_data) == 10
    for i in range(10):
        assert state_data[f"file_{i}.py"] == f"STATUS_{i}"


@pytest.mark.asyncio
async def test_self_healing_success_on_second_attempt(
    temp_workspace: tuple[Path, Path, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that a compilation failure on the first run is successfully self-healed on the second try."""
    target_file, state_file, _ = temp_workspace

    call_count = 0

    # Mock litellm acompletion to return syntax error on first call and success on second call
    async def mock_acompletion(*args: tuple[Any, ...], **kwargs: dict[str, Any]) -> MockResponse:
        nonlocal call_count
        call_count += 1
        mock_checks = [
            {"rule_id": i, "rule_name": f"rule_{i}", "status": "Pass", "finding": "Ok"}
            for i in range(1, night_shift_hardener.RuleLimits.TOTAL_RULES.value + 1)
        ]
        if call_count == 1:
            # Return syntactically broken code on the first attempt
            json_data = json.dumps(
                {"audit_matrix": mock_checks, "is_rewritten": True, "hardened_code": "def work( -> None:\n    pass"}
            )
            return MockResponse(json_data)
        else:
            # Return correct, hardened code on the second attempt
            json_data = json.dumps(
                {
                    "audit_matrix": mock_checks,
                    "is_rewritten": True,
                    "hardened_code": (
                        'def work() -> None:\n    """Execute work with strict validation."""\n    pass\n'
                    ),
                }
            )
            return MockResponse(json_data)

    import litellm

    monkeypatch.setattr(litellm, "acompletion", mock_acompletion)

    # Mock subprocess.run to simulate successful Ruff/MyPy runs on the second attempt
    def mock_run(*args: tuple[Any, ...], **kwargs: dict[str, Any]) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(args=args[0], returncode=0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", mock_run)

    semaphore = asyncio.Semaphore(1)
    success = await night_shift_hardener.process_file_with_retry(
        system_prompt="Rule 1", target_file=target_file, semaphore=semaphore, state_file_path=state_file
    )

    # Confirm processing eventually succeeded, called LLM twice, and saved the result
    assert success is True
    assert call_count == 2
    assert "strict validation" in target_file.read_text(encoding="utf-8")

    with open(state_file, encoding="utf-8") as f:
        state = json.load(f)
    assert state[target_file.as_posix()] == "DONE"


def test_error_trace_slimming() -> None:
    """Verify that slim_error_feedback correctly limits extremely long terminal traces."""
    short_error = "short compile error"
    assert night_shift_hardener.slim_error_feedback(short_error) == short_error

    long_error = "\n".join([f"line_{i}" for i in range(100)])
    slimmed = night_shift_hardener.slim_error_feedback(long_error)
    assert "[TRUNCATED FOR BREVITY]" in slimmed
    lines = slimmed.splitlines()
    assert len(lines) <= 45  # 20 + 1 (truncated msg) + 20 lines


@pytest.mark.asyncio
async def test_dual_tier_model_escalation(
    temp_workspace: tuple[Path, Path, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that the engine uses Flash on first attempt and Pro on subsequent healing attempts."""
    target_file, state_file, _ = temp_workspace

    models_used = []

    # Mock litellm acompletion to capture the model name used for each call
    async def mock_acompletion(*args: tuple[Any, ...], **kwargs: dict[str, Any]) -> MockResponse:
        model = kwargs.get("model")
        models_used.append(model)
        mock_checks = [
            {"rule_id": i, "rule_name": f"rule_{i}", "status": "Pass", "finding": "Ok"}
            for i in range(1, night_shift_hardener.RuleLimits.TOTAL_RULES.value + 1)
        ]
        if len(models_used) == 1:
            # First attempt fails syntax compilation
            json_data = json.dumps(
                {"audit_matrix": mock_checks, "is_rewritten": True, "hardened_code": "def work( -> None:\n    pass"}
            )
        else:
            # Second attempt succeeds
            json_data = json.dumps(
                {
                    "audit_matrix": mock_checks,
                    "is_rewritten": True,
                    "hardened_code": "def work() -> None:\n    pass\n",
                }
            )
        return MockResponse(json_data)

    import litellm

    monkeypatch.setattr(litellm, "acompletion", mock_acompletion)

    # Mock subprocess.run to succeed
    def mock_run(*args: tuple[Any, ...], **kwargs: dict[str, Any]) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(args=args[0], returncode=0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", mock_run)

    semaphore = asyncio.Semaphore(1)
    success = await night_shift_hardener.process_file_with_retry(
        system_prompt="Rule 1", target_file=target_file, semaphore=semaphore, state_file_path=state_file
    )

    assert success is True
    assert len(models_used) == 2
    # Verify primary model on 1st run, healing model on retry
    assert models_used[0] == night_shift_hardener.PRIMARY_MODEL
    assert models_used[1] == night_shift_hardener.HEALING_MODEL


@pytest.mark.asyncio
async def test_audit_report_saving(temp_workspace: tuple[Path, Path, Path], monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify that validated audit matrix data is saved under tmp/audit_reports/."""
    target_file, state_file, _ = temp_workspace

    # Mock litellm acompletion to return valid hardened python code with correct number of audit items
    async def mock_acompletion(*args: tuple[Any, ...], **kwargs: dict[str, Any]) -> MockResponse:
        mock_checks = [
            {"rule_id": i, "rule_name": f"rule_{i}", "status": "Pass", "finding": "Ok"}
            for i in range(1, night_shift_hardener.RuleLimits.TOTAL_RULES.value + 1)
        ]
        json_data = json.dumps(
            {
                "audit_matrix": mock_checks,
                "is_rewritten": True,
                "hardened_code": "def work() -> None:\n    pass\n",
            }
        )
        return MockResponse(json_data)

    import litellm

    monkeypatch.setattr(litellm, "acompletion", mock_acompletion)

    # Mock subprocess.run to succeed
    def mock_run(*args: tuple[Any, ...], **kwargs: dict[str, Any]) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(args=args[0], returncode=0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", mock_run)

    report_file = Path("tmp/audit_reports") / f"{target_file.stem}_audit_report.json"
    if report_file.exists():
        report_file.unlink()

    semaphore = asyncio.Semaphore(1)
    success = await night_shift_hardener.process_file_with_retry(
        system_prompt="Rule 1", target_file=target_file, semaphore=semaphore, state_file_path=state_file
    )

    assert success is True
    # Confirm report is saved
    assert report_file.exists()
    with open(report_file, encoding="utf-8") as rf:
        report_data = json.load(rf)
    assert len(report_data["audit_matrix"]) == night_shift_hardener.RuleLimits.TOTAL_RULES.value
    assert report_data["is_rewritten"] is True


def test_git_modified_files_retrieval(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify that get_git_modified_files correctly processes git diff and porcelain status outputs."""
    call_cmds = []

    def mock_run(args: list[str], **kwargs: dict[str, Any]) -> subprocess.CompletedProcess[str]:
        call_cmds.append(" ".join(args))
        if "diff" in args:
            stdout_content = "backend_v2/services/execution.py\nbackend_v2/models/user.py\n"
        elif "status" in args:
            stdout_content = (
                " M backend_v2/models/user.py\n"
                "?? backend_v2/api/routers/studio.py\n"
                "R  backend_v2/old_name.py -> backend_v2/new_name.py\n"
            )
        else:
            stdout_content = ""
        return subprocess.CompletedProcess(args=args, returncode=0, stdout=stdout_content, stderr="")

    monkeypatch.setattr(subprocess, "run", mock_run)

    files = night_shift_hardener.get_git_modified_files()

    # Confirm correct commands are executed
    assert any("git diff" in cmd for cmd in call_cmds)
    assert any("git status" in cmd for cmd in call_cmds)

    # Verify retrieved paths (should be unique, sorted and under backend_v2/)
    assert len(files) == 4
    assert files[0] == Path("backend_v2/api/routers/studio.py")
    assert files[1] == Path("backend_v2/models/user.py")
    assert files[2] == Path("backend_v2/new_name.py")
    assert files[3] == Path("backend_v2/services/execution.py")
