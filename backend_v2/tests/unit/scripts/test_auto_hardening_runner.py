"""Comprehensive unit test suite for the autonomous hardening runner CLI.

Verifies target queue discovery, audit verification loops, retry circuit breakers,
process tree termination, git commit checkpointing, and dry-run safety per TC-AHR-001 through TC-AHR-014.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from scripts.auto_hardening_runner import (
    DEFAULT_BACKEND_AGENT_TEMPLATE,
    DEFAULT_FRONTEND_AGENT_TEMPLATE,
    HardeningGate,
    HardeningIterationResultDTO,
    HardeningRunnerArgsDTO,
    HardeningRunSummaryDTO,
    HardeningStateFileDTO,
    QualityGateResultDTO,
    WorkspaceSnapshotDTO,
    capture_workspace_snapshot,
    check_tracker_has_unparsed_hardening_items,
    clean_path_arg,
    execute_circuit_breaker_rollback,
    execute_subagent_pass,
    execute_subprocess_with_tree_kill,
    fetch_unhardened_targets,
    main,
    mark_tracker_and_checkpoint,
    mark_tracker_target_done,
    parse_tracker_unhardened_targets,
    process_target_with_retries,
    run_hardening_pipeline,
    run_quality_gate,
)


def test_fetch_unhardened_targets_from_tracker_markdown(tmp_path: Path) -> None:
    """TC-AHR-001 (positive): Verify that fetch_unhardened_targets parses unchecked items from tracker markdown."""
    tracker_content = """# Tracker: Test Plan
### Post-Implementation Gates
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Execute audit loop:
  - [ ] [NEW] @[scripts/auto_hardening_runner.py]
  - [x] @[backend_v2/already_done.py]
  - [ ] @[backend_v2/services/target2.py]
  - [ ] [DELETE] @[backend_v2/services/retired_monolith.py]
- [ ] **[NOK] Tier 2 Hardening (Frontend)**:
  - [ ] @[client_app_v2/lib/features/view.dart]
"""
    backend_targets = parse_tracker_unhardened_targets(tracker_content, HardeningGate.BACKEND)
    assert backend_targets == ["scripts/auto_hardening_runner.py", "backend_v2/services/target2.py"]

    frontend_targets = parse_tracker_unhardened_targets(tracker_content, HardeningGate.FRONTEND)
    assert frontend_targets == ["client_app_v2/lib/features/view.dart"]

    tracker_file = tmp_path / "TRACKER_test.md"
    tracker_file.write_text(tracker_content, encoding="utf-8")

    args = HardeningRunnerArgsDTO(tracker=tracker_file, gate=HardeningGate.BACKEND)
    resolved = fetch_unhardened_targets(args)
    assert resolved == ["scripts/auto_hardening_runner.py", "backend_v2/services/target2.py"]


def test_fetch_explicit_targets_override(tmp_path: Path) -> None:
    """TC-AHR-002 (positive): Verify that explicit targets passed via CLI override tracker discovery."""
    tracker_file = tmp_path / "TRACKER_test.md"
    tracker_file.write_text(
        "- [ ] **[NOK] Tier 2 Hardening (Backend)**:\n  - [ ] @[from_tracker.py]\n",
        encoding="utf-8",
    )

    args = HardeningRunnerArgsDTO(
        tracker=tracker_file,
        targets=["explicit/file1.py", "explicit/file2.py"],
        gate=HardeningGate.BACKEND,
    )
    resolved = fetch_unhardened_targets(args)
    assert resolved == ["explicit/file1.py", "explicit/file2.py"]

    # Verify comma-separated target strings are cleanly split
    args_comma = HardeningRunnerArgsDTO(
        tracker=tracker_file,
        targets=["explicit/file1.py,explicit/file2.py, explicit/file3.py"],
        gate=HardeningGate.BACKEND,
    )
    resolved_comma = fetch_unhardened_targets(args_comma)
    assert resolved_comma == ["explicit/file1.py", "explicit/file2.py", "explicit/file3.py"]


def test_successful_backend_audit_marks_tracker_and_commits(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """TC-AHR-003 (positive): Verify that backend audit pass triggers mark_tracker_target_done and atomic git commit."""
    tracker_content = """# Tracker
### Post-Implementation Gates
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Execute audit:
  - [ ] @[backend_v2/target.py]
"""
    tracker_file = tmp_path / "TRACKER.md"
    tracker_file.write_text(tracker_content, encoding="utf-8")

    monkeypatch.setattr(
        "scripts.auto_hardening_runner.run_quality_gate",
        lambda *args, **kwargs: QualityGateResultDTO(success=True, output="Pass", exit_code=0),
    )
    monkeypatch.setattr(
        "scripts.auto_hardening_runner.capture_workspace_snapshot",
        lambda *args, **kwargs: WorkspaceSnapshotDTO(modified_files=[], untracked_files=[]),
    )

    executed_cmds: list[list[str]] = []

    def mock_subprocess_run(cmd: list[str], *args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        executed_cmds.append(cmd)
        return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

    monkeypatch.setattr("subprocess.run", mock_subprocess_run)

    runner_args = HardeningRunnerArgsDTO(tracker=tracker_file, gate=HardeningGate.BACKEND, max_retries=0)
    iter_res = process_target_with_retries("backend_v2/target.py", runner_args, repo_root=tmp_path)

    assert iter_res.success is True
    assert iter_res.git_committed is True
    assert iter_res.tracker_marked is True

    # Verify tracker was updated in-place and parent advanced to [OK]
    updated_tracker = tracker_file.read_text(encoding="utf-8")
    assert "- [x] @[backend_v2/target.py]" in updated_tracker
    assert "- [x] **[OK] Tier 2 Hardening (Backend)**" in updated_tracker

    # Verify git add and git commit executed with correct message
    assert any(c[:2] == ["git", "add"] for c in executed_cmds)
    commit_cmd = next(c for c in executed_cmds if c[:2] == ["git", "commit"])
    assert commit_cmd == ["git", "commit", "-m", "refactor(hardening): tighten target.py"]


def test_failed_audit_triggers_retry_and_circuit_breaker(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """TC-AHR-004 (positive): Verify that audit failure across retries triggers Circuit Breaker rollback."""
    monkeypatch.setattr(
        "scripts.auto_hardening_runner.run_quality_gate",
        lambda *args, **kwargs: QualityGateResultDTO(success=False, output="Failed lint", exit_code=1),
    )
    monkeypatch.setattr(
        "scripts.auto_hardening_runner.capture_workspace_snapshot",
        lambda *args, **kwargs: WorkspaceSnapshotDTO(modified_files=[], untracked_files=[]),
    )

    rollback_calls: list[str] = []
    monkeypatch.setattr(
        "scripts.auto_hardening_runner.execute_circuit_breaker_rollback",
        lambda snapshot, target, repo_root=None: rollback_calls.append(target),
    )

    runner_args = HardeningRunnerArgsDTO(targets=["backend_v2/fail.py"], max_retries=1, gate=HardeningGate.BACKEND)
    iter_res = process_target_with_retries("backend_v2/fail.py", runner_args, repo_root=tmp_path)

    assert iter_res.success is False
    assert iter_res.attempts == 2  # 1 initial + 1 retry
    assert iter_res.git_committed is False
    assert len(rollback_calls) == 2


def test_frontend_gate_invokes_flutter_audit_loop(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """TC-AHR-005 (positive): Verify that specifying gate=FRONTEND invokes flutter_audit_loop.py."""
    invoked_cmd: list[str] = []

    def mock_tree_kill(
        cmd: list[str], timeout_seconds: int, cwd: Path | None = None
    ) -> subprocess.CompletedProcess[str]:
        invoked_cmd.extend(cmd)
        return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="Flutter OK", stderr="")

    monkeypatch.setattr("scripts.auto_hardening_runner.execute_subprocess_with_tree_kill", mock_tree_kill)

    res = run_quality_gate(
        "client_app_v2/lib/view.dart", HardeningGate.FRONTEND, timeout_seconds=120, repo_root=tmp_path
    )
    assert res.success is True
    expected_cmd = [
        "uv",
        "run",
        "python",
        "scripts/flutter_audit_loop.py",
        "client_app_v2/lib/view.dart",
        "--build",
        "--strict",
    ]
    assert invoked_cmd == expected_cmd


def test_dry_run_mode_produces_zero_side_effects(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """TC-AHR-006 (positive): Verify that --dry-run prints plan without executing subprocesses or mutating git."""
    tracker_file = tmp_path / "TRACKER.md"
    tracker_file.write_text(
        "- [ ] **[NOK] Tier 2 Hardening (Backend)**:\n  - [ ] @[scripts/target.py]\n",
        encoding="utf-8",
    )

    def fail_if_run(*args: object, **kwargs: object) -> None:
        pytest.fail("Subprocess should not be invoked during --dry-run")

    monkeypatch.setattr("subprocess.run", fail_if_run)
    monkeypatch.setattr("subprocess.Popen", fail_if_run)

    args = HardeningRunnerArgsDTO(tracker=tracker_file, dry_run=True, gate=HardeningGate.BACKEND)
    summary = run_hardening_pipeline(args, repo_root=tmp_path)

    assert summary.processed_count == 1
    assert summary.success_count == 0
    assert summary.failure_count == 0

    captured = capsys.readouterr()
    assert "DRY RUN: Target Hardening Queue" in captured.out
    assert "scripts/target.py" in captured.out

    # Tracker file must remain untouched
    assert "- [ ] @[scripts/target.py]" in tracker_file.read_text(encoding="utf-8")


def test_max_files_batch_capping(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """TC-AHR-007 (positive): Verify that --max-files 2 processes exactly 2 targets and caps queue."""
    all_targets = [f"file_{i}.py" for i in range(10)]

    processed: list[str] = []

    def mock_process(target: str, *args: object, **kwargs: object) -> HardeningIterationResultDTO:
        processed.append(target)
        return HardeningIterationResultDTO(
            target_file=target,
            gate=HardeningGate.BACKEND,
            success=True,
            attempts=1,
            duration_seconds=0.1,
            error_message=None,
            git_committed=True,
            tracker_marked=False,
        )

    monkeypatch.setattr("scripts.auto_hardening_runner.process_target_with_retries", mock_process)

    args = HardeningRunnerArgsDTO(targets=all_targets, max_files=2, gate=HardeningGate.BACKEND)
    summary = run_hardening_pipeline(args, repo_root=tmp_path)

    assert summary.total_targets == 10
    assert summary.processed_count == 2
    assert summary.skipped_count == 8
    assert summary.success_count == 2
    assert processed == ["file_0.py", "file_1.py"]


def test_nonexistent_tracker_file_fails_fast(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """TC-AHR-008 (negative): Verify that providing a nonexistent tracker file triggers exit code 1."""
    nonexistent = tmp_path / "nonexistent_tracker.md"
    exit_code = main(["--tracker", str(nonexistent)])
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "Tracker file not found" in captured.err


def test_invalid_gate_argument_rejected() -> None:
    """TC-AHR-009 (negative): Verify that passing an unsupported gate string is rejected by CLI argument parser."""
    with pytest.raises(SystemExit) as exc_info:
        main(["--gate", "unsupported_gate", "--targets", "test.py"])
    assert exc_info.value.code != 0


def test_custom_agent_command_template_formatting(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """TC-AHR-010 (positive): Verify that --agent-cmd template formats target and executes agent sub-process."""
    executed_cmd: list[str] = []

    def mock_tree_kill(
        cmd: list[str], timeout_seconds: int, cwd: Path | None = None
    ) -> subprocess.CompletedProcess[str]:
        executed_cmd.extend(cmd)
        return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="Agent Success", stderr="")

    monkeypatch.setattr("scripts.auto_hardening_runner.execute_subprocess_with_tree_kill", mock_tree_kill)
    monkeypatch.setattr("subprocess.run", lambda *args, **kwargs: subprocess.CompletedProcess(args=[], returncode=0))

    args = HardeningRunnerArgsDTO(
        agent_cmd="echo CustomAgent {target} --run",
        targets=["backend_v2/test.py"],
        gate=HardeningGate.BACKEND,
    )
    ok = execute_subagent_pass("backend_v2/test.py", args, repo_root=tmp_path)
    assert ok is True
    assert "CustomAgent" in executed_cmd
    assert "backend_v2/test.py" in executed_cmd


def test_missing_targets_fails_fast(capsys: pytest.CaptureFixture[str]) -> None:
    """TC-AHR-011 (negative): Verify that invoking runner without targets, tracker, or state file fails fast."""
    exit_code = main([])
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "No target sources specified" in captured.err


def test_subprocess_timeout_triggers_tree_kill_and_circuit_breaker(monkeypatch: pytest.MonkeyPatch) -> None:
    """TC-AHR-012 (negative): Verify that subprocess timeout terminates Windows process tree and returns exit 124."""
    mock_proc = MagicMock()
    mock_proc.pid = 9999
    mock_proc.communicate.side_effect = subprocess.TimeoutExpired(cmd=["test_cmd"], timeout=5)

    monkeypatch.setattr("subprocess.Popen", lambda *args, **kwargs: mock_proc)

    taskkill_cmds: list[list[str]] = []

    def mock_sub_run(cmd: list[str], *args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        taskkill_cmds.append(cmd)
        return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

    monkeypatch.setattr("subprocess.run", mock_sub_run)
    monkeypatch.setattr("sys.platform", "win32")

    with pytest.raises(subprocess.TimeoutExpired):
        execute_subprocess_with_tree_kill(["test_cmd"], timeout_seconds=5)

    assert mock_proc.kill.called
    assert any("taskkill" in c and "9999" in c for c in taskkill_cmds)

    # Verify quality gate translates timeout into QualityGateResultDTO with exit code 124
    res = run_quality_gate("backend_v2/timeout.py", HardeningGate.BACKEND, timeout_seconds=5)
    assert res.success is False
    assert res.exit_code == 124
    assert "timed out after 5s" in res.output


def test_workspace_snapshot_restores_collateral_modifications(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """TC-AHR-013 (positive): Verify snapshot restores collateral modifications while preserving db_v2."""
    # Create files on disk
    target_file = tmp_path / "backend_v2" / "target.py"
    target_file.parent.mkdir(parents=True, exist_ok=True)
    target_file.write_text("initial target", encoding="utf-8")

    collateral_file = tmp_path / "backend_v2" / "collateral.py"
    collateral_file.write_text("initial collateral", encoding="utf-8")

    db_file = tmp_path / "data" / "db_v2.json"
    db_file.parent.mkdir(parents=True, exist_ok=True)
    db_file.write_text('{"preserved": true}', encoding="utf-8")

    state_file = tmp_path / "hardening_state.json"
    state_file.write_text('{"TARGETS": [], "DONE": []}', encoding="utf-8")

    untracked_garbage = tmp_path / "scratch_garbage.py"
    untracked_garbage.write_text("untracked", encoding="utf-8")

    baseline_snapshot = WorkspaceSnapshotDTO(
        modified_files=[],
        untracked_files=[],
    )

    # During attempt: target, collateral, db_v2, state_file modified; untracked_garbage created
    current_snapshot = WorkspaceSnapshotDTO(
        modified_files=[
            "backend_v2/target.py",
            "backend_v2/collateral.py",
            "data/db_v2.json",
            "hardening_state.json",
        ],
        untracked_files=["scratch_garbage.py"],
    )

    monkeypatch.setattr("scripts.auto_hardening_runner.capture_workspace_snapshot", lambda root: current_snapshot)

    restored_files: list[str] = []

    def mock_git_restore(cmd: list[str], *args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        if cmd[:2] == ["git", "restore"]:
            restored_files.append(cmd[2])
        return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

    monkeypatch.setattr("subprocess.run", mock_git_restore)

    execute_circuit_breaker_rollback(baseline_snapshot, "backend_v2/target.py", repo_root=tmp_path)

    # Verify target and collateral restored
    assert "backend_v2/target.py" in restored_files
    assert "backend_v2/collateral.py" in restored_files

    # Verify db_v2.json and hardening_state.json were strictly NEVER restored
    assert "data/db_v2.json" not in restored_files
    assert "hardening_state.json" not in restored_files

    # Verify untracked garbage was deleted
    assert not untracked_garbage.exists()
    assert state_file.exists()
    assert db_file.exists()


def test_state_file_discovery_and_persistence(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """TC-AHR-014 (positive): Verify that --state-file computes REMAINING = TARGETS - DONE and updates atomically."""
    state_file = tmp_path / "hardening_state.json"
    state_file.write_text(
        '{"TARGETS": ["file1.py", "file2.py", "file3.py"], "DONE": ["file1.py"]}',
        encoding="utf-8",
    )

    args = HardeningRunnerArgsDTO(state_file=state_file, gate=HardeningGate.BACKEND)
    remaining = fetch_unhardened_targets(args)
    assert remaining == ["file2.py", "file3.py"]

    monkeypatch.setattr(
        "subprocess.run",
        lambda *a, **k: subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),
    )

    checkpoint = mark_tracker_and_checkpoint("file2.py", tracker_path=None, state_file=state_file, repo_root=tmp_path)
    assert checkpoint.state_file_updated is True
    assert checkpoint.git_committed is True

    # Verify state file was updated
    updated_state = HardeningStateFileDTO.model_validate_json(state_file.read_text(encoding="utf-8"))
    assert updated_state.done == ["file1.py", "file2.py"]
    assert updated_state.targets == ["file1.py", "file2.py", "file3.py"]


def test_mark_tracker_target_done_edge_cases(tmp_path: Path) -> None:
    """Verify mark_tracker_target_done edge cases: nonexistent tracker and target not found."""
    nonexistent = tmp_path / "no_tracker.md"
    assert mark_tracker_target_done(nonexistent, "file.py") is False

    tracker = tmp_path / "tracker.md"
    tracker.write_text("- [ ] **Tier 2 Hardening (Backend)**:\n  - [ ] @[other.py]\n", encoding="utf-8")
    assert mark_tracker_target_done(tracker, "missing.py") is False


def test_capture_workspace_snapshot_nonzero_exit(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify capture_workspace_snapshot returns empty lists if git status fails."""
    monkeypatch.setattr(
        "subprocess.run",
        lambda *a, **k: subprocess.CompletedProcess(args=[], returncode=1, stdout="", stderr=""),
    )
    snap = capture_workspace_snapshot()
    assert snap.modified_files == []
    assert snap.untracked_files == []


def test_fetch_unhardened_targets_nonexistent_files(tmp_path: Path) -> None:
    """Verify fetch_unhardened_targets raises FileNotFoundError when tracker or state file is missing."""
    with pytest.raises(FileNotFoundError, match="Tracker file not found"):
        fetch_unhardened_targets(HardeningRunnerArgsDTO(tracker=tmp_path / "absent.md"))

    with pytest.raises(FileNotFoundError, match="State file not found"):
        fetch_unhardened_targets(HardeningRunnerArgsDTO(state_file=tmp_path / "absent.json"))


def test_main_cli_execution_success(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify main returns 0 when pipeline succeeds."""
    state_file = tmp_path / "hardening_state.json"
    state_file.write_text('{"TARGETS": ["file.py"], "DONE": []}', encoding="utf-8")

    monkeypatch.setattr(
        "scripts.auto_hardening_runner.run_hardening_pipeline",
        lambda args: HardeningRunSummaryDTO(
            total_targets=1,
            processed_count=1,
            success_count=1,
            failure_count=0,
            skipped_count=0,
            iterations=[],
        ),
    )

    exit_code = main(["--state-file", str(state_file)])
    assert exit_code == 0


def test_main_cli_execution_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify main returns 1 when pipeline experiences failures."""
    state_file = tmp_path / "hardening_state.json"
    state_file.write_text('{"TARGETS": ["file.py"], "DONE": []}', encoding="utf-8")

    monkeypatch.setattr(
        "scripts.auto_hardening_runner.run_hardening_pipeline",
        lambda args: HardeningRunSummaryDTO(
            total_targets=1,
            processed_count=1,
            success_count=0,
            failure_count=1,
            skipped_count=0,
            iterations=[],
        ),
    )

    exit_code = main(["--state-file", str(state_file)])
    assert exit_code == 1


def test_parse_tracker_missing_gate_section() -> None:
    """Verify parse_tracker_unhardened_targets returns empty list when gate section is absent."""
    content = "# Empty Tracker\nNo gate section here\n"
    assert parse_tracker_unhardened_targets(content, HardeningGate.BACKEND) == []
    assert parse_tracker_unhardened_targets(content, HardeningGate.FRONTEND) == []


def test_fetch_unhardened_targets_no_source_raises() -> None:
    """Verify fetch_unhardened_targets raises ValueError when no sources are provided."""
    args = HardeningRunnerArgsDTO()
    with pytest.raises(ValueError, match="No target source provided"):
        fetch_unhardened_targets(args)


def test_execute_subprocess_with_tree_kill_taskkill_oserror(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify execute_subprocess_with_tree_kill handles taskkill failure gracefully."""
    mock_proc = MagicMock()
    mock_proc.pid = 1234
    mock_proc.communicate.side_effect = [
        subprocess.TimeoutExpired(cmd=["test"], timeout=1),
        subprocess.TimeoutExpired(cmd=["test"], timeout=1),
    ]

    monkeypatch.setattr("subprocess.Popen", lambda *a, **k: mock_proc)

    def mock_taskkill(*a: object, **k: object) -> subprocess.CompletedProcess[str]:
        raise OSError("Taskkill unavailable")

    monkeypatch.setattr("subprocess.run", mock_taskkill)
    monkeypatch.setattr("sys.platform", "win32")

    with pytest.raises(subprocess.TimeoutExpired):
        execute_subprocess_with_tree_kill(["test"], timeout_seconds=1)

    assert mock_proc.kill.called


def test_execute_subagent_pass_agent_cmd_failure_and_timeout(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify execute_subagent_pass returns False when agent_cmd returns non-zero or times out."""
    # Non-zero exit code
    monkeypatch.setattr(
        "scripts.auto_hardening_runner.execute_subprocess_with_tree_kill",
        lambda *a, **k: subprocess.CompletedProcess(args=[], returncode=1, stdout="", stderr="Error"),
    )
    args = HardeningRunnerArgsDTO(agent_cmd="test {target}", targets=["f.py"], gate=HardeningGate.BACKEND)
    assert execute_subagent_pass("f.py", args, repo_root=tmp_path) is False

    # TimeoutExpired
    def raise_timeout(*a: object, **k: object) -> subprocess.CompletedProcess[str]:
        raise subprocess.TimeoutExpired(cmd=["test"], timeout=1)

    monkeypatch.setattr("scripts.auto_hardening_runner.execute_subprocess_with_tree_kill", raise_timeout)
    assert execute_subagent_pass("f.py", args, repo_root=tmp_path) is False


def test_execute_subagent_pass_frontend_dart_format(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify execute_subagent_pass executes dart format for frontend dart files."""
    called_cmds: list[list[str]] = []

    def mock_run(cmd: list[str], *a: object, **k: object) -> subprocess.CompletedProcess[str]:
        called_cmds.append(cmd)
        return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

    monkeypatch.setattr("subprocess.run", mock_run)
    args = HardeningRunnerArgsDTO(gate=HardeningGate.FRONTEND, targets=["lib/view.dart"], no_auto_fix=False)
    assert execute_subagent_pass("lib/view.dart", args, repo_root=tmp_path) is True
    assert any("dart" in c and "format" in c for c in called_cmds)


def test_execute_circuit_breaker_rollback_untracked_directory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify execute_circuit_breaker_rollback removes newly created untracked directory."""
    untracked_dir = tmp_path / "scratch_dir"
    untracked_dir.mkdir(parents=True, exist_ok=True)
    (untracked_dir / "junk.txt").write_text("junk", encoding="utf-8")

    baseline = WorkspaceSnapshotDTO(modified_files=[], untracked_files=[])
    current = WorkspaceSnapshotDTO(modified_files=[], untracked_files=["scratch_dir"])

    monkeypatch.setattr("scripts.auto_hardening_runner.capture_workspace_snapshot", lambda root: current)
    monkeypatch.setattr("subprocess.run", lambda *a, **k: subprocess.CompletedProcess(args=[], returncode=0))

    execute_circuit_breaker_rollback(baseline, "target.py", repo_root=tmp_path)
    assert not untracked_dir.exists()


def test_run_hardening_pipeline_failure_verbose_and_continue_on_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Verify run_hardening_pipeline logs error with verbose=True and continues when continue_on_failure=True."""

    def mock_process(target: str, *a: object, **k: object) -> HardeningIterationResultDTO:
        return HardeningIterationResultDTO(
            target_file=target,
            gate=HardeningGate.BACKEND,
            success=False,
            attempts=1,
            duration_seconds=0.1,
            error_message="Detailed failure traceback line",
            git_committed=False,
            tracker_marked=False,
        )

    monkeypatch.setattr("scripts.auto_hardening_runner.process_target_with_retries", mock_process)

    args = HardeningRunnerArgsDTO(
        targets=["fail1.py", "fail2.py"],
        verbose=True,
        continue_on_failure=True,
        gate=HardeningGate.BACKEND,
    )
    summary = run_hardening_pipeline(args, repo_root=tmp_path)
    assert summary.failure_count == 2
    assert summary.processed_count == 2

    captured = capsys.readouterr()
    assert "Detailed failure traceback line" in captured.out


def test_main_cli_nonexistent_state_file_and_validation_error(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Verify main returns 1 when state file does not exist or arguments fail validation."""
    nonexistent_state = tmp_path / "absent_state.json"
    assert main(["--state-file", str(nonexistent_state)]) == 1
    assert "State file not found" in capsys.readouterr().err

    # Invalid max-retries (negative value triggers Field(ge=0) validation error)
    state = tmp_path / "valid_state.json"
    state.write_text('{"TARGETS": [], "DONE": []}', encoding="utf-8")
    assert main(["--state-file", str(state), "--max-retries", "-5"]) == 1
    assert "Argument Validation Error" in capsys.readouterr().err


def test_clean_path_arg_formats() -> None:
    """Verify clean_path_arg normalizes markdown links, quotes, and bare paths."""
    assert clean_path_arg(None) is None
    assert clean_path_arg("") is None
    assert clean_path_arg("   ") is None
    assert clean_path_arg("@[docs/epic/tracker.md]") == Path("docs/epic/tracker.md")
    assert clean_path_arg("`@[docs/epic/tracker.md]`") == Path("docs/epic/tracker.md")
    assert clean_path_arg('"@[docs/epic/tracker.md]"') == Path("docs/epic/tracker.md")
    assert clean_path_arg("'docs/epic/tracker.md'") == Path("docs/epic/tracker.md")
    assert clean_path_arg(Path("docs/epic/tracker.md")) == Path("docs/epic/tracker.md")


def test_main_cli_markdown_wrapped_tracker_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify main accepts markdown @[...] formatted tracker paths."""
    tracker_file = tmp_path / "tracker.md"
    tracker_file.write_text(
        "- [ ] **[NOK] Tier 2 Hardening (Backend)**:\n  - [ ] @[file.py]\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "scripts.auto_hardening_runner.run_hardening_pipeline",
        lambda args: HardeningRunSummaryDTO(
            total_targets=1,
            processed_count=1,
            success_count=1,
            failure_count=0,
            skipped_count=0,
            iterations=[],
        ),
    )

    exit_code = main(["--tracker", f"@[{tracker_file}]"])
    assert exit_code == 0


def test_execute_subagent_pass_retry_on_transient_model_glitch(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """TC-AHR-030: Verify execute_subagent_pass retries on transient model unrecognized error and succeeds."""
    call_count = 0

    def mock_tree_kill(cmd: list[str], timeout_seconds: int, cwd: Path) -> subprocess.CompletedProcess[str]:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return subprocess.CompletedProcess(
                args=cmd,
                returncode=1,
                stdout="",
                stderr='error: invalid model selection (--model "gemini-4-argon-high" --effort ""): model gemini-4-argon-high is not recognized as a known model or custom model in settings',
            )
        return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="Hardened successfully.", stderr="")

    monkeypatch.setattr("scripts.auto_hardening_runner.execute_subprocess_with_tree_kill", mock_tree_kill)
    monkeypatch.setattr("time.sleep", lambda s: None)

    args = HardeningRunnerArgsDTO(
        agent_cmd="agy {target}", targets=["f.py"], gate=HardeningGate.BACKEND, no_auto_fix=True
    )
    assert execute_subagent_pass("f.py", args, repo_root=tmp_path) is True
    assert call_count == 2


def test_execute_subagent_pass_retry_exhaustion_on_persistent_transient_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """TC-AHR-031: Verify execute_subagent_pass exhausts retries on persistent connection refused errors."""
    call_count = 0

    def mock_tree_kill(cmd: list[str], timeout_seconds: int, cwd: Path) -> subprocess.CompletedProcess[str]:
        nonlocal call_count
        call_count += 1
        return subprocess.CompletedProcess(
            args=cmd,
            returncode=1,
            stdout="",
            stderr="error: connection refused",
        )

    monkeypatch.setattr("scripts.auto_hardening_runner.execute_subprocess_with_tree_kill", mock_tree_kill)
    monkeypatch.setattr("time.sleep", lambda s: None)

    args = HardeningRunnerArgsDTO(
        agent_cmd="agy {target}", targets=["f.py"], gate=HardeningGate.BACKEND, no_auto_fix=True
    )
    assert execute_subagent_pass("f.py", args, repo_root=tmp_path) is False
    assert call_count == 3


def test_parse_tracker_unhardened_targets_with_backticks_and_anchors() -> None:
    """TC-AHR-032: Verify tracker target parsing handles backtick-wrapped links and line-bound anchors."""
    tracker_content = """# Master Tracker
### Post-Implementation Gates
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run auto_hardening_runner
  - [ ] `@[backend_v2/services/orchestrator/anchor_validation/lexical_normalizer.py#L27-L76]`
  - [ ] `@[backend_v2/services/orchestrator/anchor_validation/lexical_matcher.py#L27-L270]`
  - [ ] [NEW] `@[backend_v2/services/orchestrator/anchor_validation/evidence_validator.py]`
  - [ ] [DELETE] `@[backend_v2/services/orchestrator/anchor_validation_service.py]`
  - [x] `@[backend_v2/services/orchestrator/already_done.py#L1-L10]`
- [x] **[SKIPPED] Tier 2 Hardening (Frontend)**: Pure backend.
"""
    targets = parse_tracker_unhardened_targets(tracker_content, HardeningGate.BACKEND)
    assert targets == [
        "backend_v2/services/orchestrator/anchor_validation/lexical_normalizer.py",
        "backend_v2/services/orchestrator/anchor_validation/lexical_matcher.py",
        "backend_v2/services/orchestrator/anchor_validation/evidence_validator.py",
    ]


def test_mark_tracker_target_done_with_backticks_and_anchors(tmp_path: Path) -> None:
    """TC-AHR-033: Verify mark_tracker_target_done updates backtick-wrapped items with line anchors in-place."""
    tracker_file = tmp_path / "tracker.md"
    tracker_file.write_text(
        """# Master Tracker
### Post-Implementation Gates
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run auto_hardening_runner
  - [ ] `@[backend_v2/services/orchestrator/anchor_validation/lexical_normalizer.py#L27-L76]`
  - [ ] `@[backend_v2/services/orchestrator/anchor_validation/lexical_matcher.py#L27-L270]`
""",
        encoding="utf-8",
    )

    success = mark_tracker_target_done(
        tracker_file,
        "backend_v2/services/orchestrator/anchor_validation/lexical_normalizer.py",
    )
    assert success is True

    updated_content = tracker_file.read_text(encoding="utf-8")
    assert (
        "- [x] `@[backend_v2/services/orchestrator/anchor_validation/lexical_normalizer.py#L27-L76]`" in updated_content
    )
    assert (
        "- [ ] `@[backend_v2/services/orchestrator/anchor_validation/lexical_matcher.py#L27-L270]`" in updated_content
    )
    # Parent gate remains [NOK] because lexical_matcher is still pending
    assert "- [ ] **[NOK] Tier 2 Hardening (Backend)**" in updated_content

    # Mark second target
    success_2 = mark_tracker_target_done(
        tracker_file,
        "backend_v2/services/orchestrator/anchor_validation/lexical_matcher.py",
    )
    assert success_2 is True

    final_content = tracker_file.read_text(encoding="utf-8")
    assert "- [x] `@[backend_v2/services/orchestrator/anchor_validation/lexical_matcher.py#L27-L270]`" in final_content
    # All children checked: parent gate automatically advances to [OK]
    assert "- [x] **[OK] Tier 2 Hardening (Backend)**" in final_content


def test_check_tracker_has_unparsed_hardening_items() -> None:
    """TC-AHR-034: Verify check_tracker_has_unparsed_hardening_items identifies pending checklist children."""
    unchecked_content = """# Master Tracker
### Post-Implementation Gates
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run auto_hardening_runner
  - [ ] Some pending item
"""
    assert check_tracker_has_unparsed_hardening_items(unchecked_content, HardeningGate.BACKEND) is True
    assert check_tracker_has_unparsed_hardening_items(unchecked_content, HardeningGate.FRONTEND) is False

    checked_content = """# Master Tracker
### Post-Implementation Gates
- [x] **[OK] Tier 2 Hardening (Backend)**: Run auto_hardening_runner
  - [x] Completed item
"""
    assert check_tracker_has_unparsed_hardening_items(checked_content, HardeningGate.BACKEND) is False

    skipped_gate_content = """# Master Tracker
### Post-Implementation Gates
- [ ] **[SKIPPED] Tier 2 Hardening (Backend)**: N/A
"""
    assert check_tracker_has_unparsed_hardening_items(skipped_gate_content, HardeningGate.BACKEND) is False


def test_fetch_unhardened_targets_unparsed_items_fail_fast(tmp_path: Path) -> None:
    """TC-AHR-035: Verify fetch_unhardened_targets raises ValueError when unchecked items fail to parse."""
    tracker_file = tmp_path / "tracker.md"
    tracker_file.write_text(
        """# Master Tracker
### Post-Implementation Gates
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run auto_hardening_runner
  - [ ] Unparseable non-path markdown line here
""",
        encoding="utf-8",
    )

    args = HardeningRunnerArgsDTO(tracker=tracker_file, gate=HardeningGate.BACKEND)
    with pytest.raises(ValueError, match="has pending Tier 2 Hardening \\(Backend\\) checklist items"):
        fetch_unhardened_targets(args)


def test_fetch_unhardened_targets_gate_all(tmp_path: Path) -> None:
    """TC-AHR-036: Verify HardeningGate.ALL discovers both backend and frontend targets seamlessly."""
    tracker_file = tmp_path / "tracker.md"
    tracker_file.write_text(
        """# Master Tracker
### Post-Implementation Gates
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run auto_hardening_runner
  - [ ] @[backend_v2/services/foo.py]
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run auto_hardening_runner
  - [ ] @[client_app_v2/lib/features/bar.dart]
""",
        encoding="utf-8",
    )

    args = HardeningRunnerArgsDTO(tracker=tracker_file, gate=HardeningGate.ALL)
    targets = fetch_unhardened_targets(args)
    assert targets == ["backend_v2/services/foo.py", "client_app_v2/lib/features/bar.dart"]


def test_run_hardening_pipeline_gate_all(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """TC-AHR-037: Verify run_hardening_pipeline delegates across backend and frontend under HardeningGate.ALL."""
    tracker_file = tmp_path / "tracker.md"
    tracker_file.write_text(
        """# Master Tracker
### Post-Implementation Gates
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run auto_hardening_runner
  - [ ] @[backend_v2/services/foo.py]
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run auto_hardening_runner
  - [ ] @[client_app_v2/lib/features/bar.dart]
""",
        encoding="utf-8",
    )

    processed_gates: list[HardeningGate] = []
    processed_agent_cmds: list[str | None] = []

    def mock_process(
        target: str, args: HardeningRunnerArgsDTO, repo_root: Path | None = None
    ) -> HardeningIterationResultDTO:
        processed_gates.append(args.gate)
        processed_agent_cmds.append(args.agent_cmd)
        return HardeningIterationResultDTO(
            target_file=target,
            gate=args.gate,
            success=True,
            attempts=1,
            duration_seconds=0.1,
            git_committed=True,
            tracker_marked=True,
        )

    monkeypatch.setattr("scripts.auto_hardening_runner.process_target_with_retries", mock_process)

    args = HardeningRunnerArgsDTO(tracker=tracker_file, gate=HardeningGate.ALL)
    summary = run_hardening_pipeline(args, repo_root=tmp_path)

    assert summary.total_targets == 2
    assert summary.success_count == 2
    assert summary.failure_count == 0
    assert processed_gates == [HardeningGate.BACKEND, HardeningGate.FRONTEND]
    assert processed_agent_cmds == [DEFAULT_BACKEND_AGENT_TEMPLATE, DEFAULT_FRONTEND_AGENT_TEMPLATE]


def test_main_cli_default_subagent_template_resolution(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """TC-AHR-038: Verify main CLI resolves strict default subagent templates unless --no-agent is passed."""
    tracker_file = tmp_path / "tracker.md"
    tracker_file.write_text(
        """# Master Tracker
### Post-Implementation Gates
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run auto_hardening_runner
  - [ ] @[backend_v2/services/foo.py]
""",
        encoding="utf-8",
    )

    captured_dtos: list[HardeningRunnerArgsDTO] = []

    def mock_pipeline(dto: HardeningRunnerArgsDTO, repo_root: Path | None = None) -> HardeningRunSummaryDTO:
        captured_dtos.append(dto)
        return HardeningRunSummaryDTO(
            total_targets=1,
            processed_count=1,
            success_count=1,
            failure_count=0,
            skipped_count=0,
            iterations=[],
        )

    monkeypatch.setattr("scripts.auto_hardening_runner.run_hardening_pipeline", mock_pipeline)

    # 1. Gate backend default -> DEFAULT_BACKEND_AGENT_TEMPLATE
    code = main(["--tracker", str(tracker_file), "--gate", "backend"])
    assert code == 0
    assert captured_dtos[-1].no_agent is False
    assert captured_dtos[-1].agent_cmd == DEFAULT_BACKEND_AGENT_TEMPLATE

    # 2. Gate frontend default -> DEFAULT_FRONTEND_AGENT_TEMPLATE
    code = main(["--tracker", str(tracker_file), "--gate", "frontend"])
    assert code == 0
    assert captured_dtos[-1].no_agent is False
    assert captured_dtos[-1].agent_cmd == DEFAULT_FRONTEND_AGENT_TEMPLATE

    # 3. Explicit --no-agent disables subagent
    code = main(["--tracker", str(tracker_file), "--gate", "backend", "--no-agent"])
    assert code == 0
    assert captured_dtos[-1].no_agent is True
    assert captured_dtos[-1].agent_cmd is None

    # 4. Gate all defaults to no_agent=False
    code = main(["--tracker", str(tracker_file)])
    assert code == 0
    assert captured_dtos[-1].no_agent is False
    assert captured_dtos[-1].gate == HardeningGate.ALL
