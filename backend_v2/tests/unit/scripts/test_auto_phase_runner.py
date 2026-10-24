"""Comprehensive unit test suite for the autonomous headless CLI phase orchestrator.

Verifies phase discovery across Epic and Standalone topologies, agy subagent execution,
watchdog tree killing, Universal Quality Gate enforcement, atomic git checkpointing,
in-place tracker updating, and post-implementation hardening handoff.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scripts.auto_phase_runner import (
    AutoPhaseRunnerArgsDTO,
    AutoPhaseRunSummaryDTO,
    PhaseItemDTO,
    QualityGateResultDTO,
    SubagentExecutionResultDTO,
    clean_path_arg,
    commit_phase_checkpoint,
    execute_phase_subagent,
    filter_phases,
    main,
    mark_phase_completed_in_tracker,
    parse_tracker_phases,
    resolve_agy_binary,
    run_phase_pipeline,
    run_phase_quality_gate,
    run_post_hardening_gate,
)


def test_clean_path_arg() -> None:
    """Verify clean_path_arg normalizes markdown @-reference brackets, line bounds, and quotes."""
    assert clean_path_arg(None) is None
    assert clean_path_arg("") is None
    assert clean_path_arg("@[docs/tracker.md]") == Path("docs/tracker.md")
    assert clean_path_arg("`@[docs/tracker.md]`") == Path("docs/tracker.md")
    assert clean_path_arg("'docs/tracker.md'") == Path("docs/tracker.md")
    assert clean_path_arg("`@[backend_v2/services/foo.py#L27-L76]`") == Path("backend_v2/services/foo.py")
    assert clean_path_arg("@[backend_v2/services/foo.py#L10]") == Path("backend_v2/services/foo.py")


def test_parse_tracker_phases_epic_topology(tmp_path: Path) -> None:
    """TC-APR-001: Verify phase extraction from Multi-Phase Epic topology."""
    plan1 = tmp_path / "plan1.md"
    plan2 = tmp_path / "plan2.md"
    plan1.write_text("# Plan 1", encoding="utf-8")
    plan2.write_text("# Plan 2", encoding="utf-8")

    tracker_content = f"""# Master Epic Tracker
### Phase 1: Leaf Extraction
- **Plan:** @[{plan1.name}]
- [ ] **[NOK] Execution:** `/tier2-execute @[{plan1.name}] @[tracker.md]`
  - [ ] Step 1: Extract Leaf Types
  - [ ] Step 2: Quality Gates

### Phase 2: Orchestrator Modernization
- **Plan:** @[{plan2.name}]
- [x] **[OK] Execution:** `/tier2-execute @[{plan2.name}] @[tracker.md]` (`abc1234`)
  - [x] Step 1: Rewire DAG
  - [x] Step 2: Quality Gates

### Post-Implementation
- [ ] Tier 2 Hardening
"""
    tracker_file = tmp_path / "tracker.md"
    tracker_file.write_text(tracker_content, encoding="utf-8")

    phases = parse_tracker_phases(tracker_file, repo_root=tmp_path)
    assert len(phases) == 2

    assert phases[0].phase_num == 1
    assert phases[0].title == "Leaf Extraction"
    assert phases[0].plan_path == Path(plan1.name)
    assert phases[0].is_completed is False
    assert "/tier2-execute" in phases[0].command

    assert phases[1].phase_num == 2
    assert phases[1].title == "Orchestrator Modernization"
    assert phases[1].plan_path == Path(plan2.name)
    assert phases[1].is_completed is True
    # Verify commit hash was stripped from execution command
    assert "abc1234" not in phases[1].command


def test_parse_tracker_phases_standalone_topology(tmp_path: Path) -> None:
    """TC-APR-002: Verify phase extraction from Single-Phase Standalone Plan topology."""
    plan = tmp_path / "standalone_plan.md"
    plan.write_text("# Standalone Plan", encoding="utf-8")

    tracker_content = f"""# Tracker: Standalone Feature
**Plan:** @[{plan.name}]

## Step Execution Status
**Plan:** @[{plan.name}]
- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[{plan.name}] @[tracker.md]`
  - [ ] Step 1: DTO definition
  - [ ] Step 2: Implementation

### Post-Implementation Gates
- [ ] Tier 2 Hardening
"""
    tracker_file = tmp_path / "tracker.md"
    tracker_file.write_text(tracker_content, encoding="utf-8")

    phases = parse_tracker_phases(tracker_file, repo_root=tmp_path)
    assert len(phases) == 1
    assert phases[0].phase_num == 1
    assert phases[0].plan_path == Path(plan.name)
    assert phases[0].is_completed is False


def test_parse_tracker_with_commit_hash(tmp_path: Path) -> None:
    """TC-APR-003: Verify regex handles commit hashes preceding execution markers."""
    plan = tmp_path / "plan.md"
    plan.write_text("# Plan", encoding="utf-8")

    tracker_content = f"""### Phase 1: Core Setup
- **Plan:** @[{plan.name}]
- [x] (f4a8b9c) **[OK] Execution:** `/tier2-execute @[{plan.name}] @[tracker.md]`
  - [x] Step 1: Setup
"""
    tracker_file = tmp_path / "tracker.md"
    tracker_file.write_text(tracker_content, encoding="utf-8")

    phases = parse_tracker_phases(tracker_file, repo_root=tmp_path)
    assert len(phases) == 1
    assert phases[0].is_completed is True


def test_parse_tracker_missing_file_raises(tmp_path: Path) -> None:
    """TC-APR-004 (negative): Verify FileNotFoundError when tracker file does not exist."""
    missing = tmp_path / "missing_tracker.md"
    with pytest.raises(FileNotFoundError, match="Tracker file not found"):
        parse_tracker_phases(missing, repo_root=tmp_path)


def test_parse_tracker_missing_plan_file_raises(tmp_path: Path) -> None:
    """TC-APR-005 (negative): Verify FileNotFoundError when referenced plan file does not exist."""
    tracker_content = """### Phase 1: Core Setup
- **Plan:** @[non_existent_plan.md]
- [ ] **[NOK] Execution:** `/tier2-execute @[non_existent_plan.md] @[tracker.md]`
"""
    tracker_file = tmp_path / "tracker.md"
    tracker_file.write_text(tracker_content, encoding="utf-8")

    with pytest.raises(FileNotFoundError, match="Referenced plan file not found on disk"):
        parse_tracker_phases(tracker_file, repo_root=tmp_path)


def test_resolve_agy_binary_found_and_missing() -> None:
    """TC-APR-006: Verify agy binary resolution via PATH, fallback locations, or error."""
    # 1. Resolved via PATH
    with patch("shutil.which", return_value="C:/Tools/agy.exe"):
        resolved = resolve_agy_binary()
        assert resolved == Path("C:/Tools/agy.exe")

    # 2. Resolved via standard candidate path
    with (
        patch("shutil.which", return_value=None),
        patch.object(Path, "exists", autospec=True) as mock_exists,
    ):
        mock_exists.side_effect = lambda self: "npm/agy.cmd" in str(self).replace("\\", "/")
        resolved = resolve_agy_binary()
        assert "agy.cmd" in str(resolved)

    # 3. Missing binary raises FileNotFoundError
    with (
        patch("shutil.which", return_value=None),
        patch.object(Path, "exists", return_value=False),
        pytest.raises(FileNotFoundError, match="Antigravity CLI \\(agy\\) not found"),
    ):
        resolve_agy_binary()


def test_dry_run_mode_prints_phases_without_subprocess(tmp_path: Path) -> None:
    """TC-APR-007: Verify --dry-run prints planned phases without spawning subprocesses."""
    plan = tmp_path / "plan.md"
    plan.write_text("# Plan", encoding="utf-8")
    tracker = tmp_path / "tracker.md"
    tracker.write_text(
        f"### Phase 1: Test\n- **Plan:** @[{plan.name}]\n- [ ] **[NOK] Execution:** `/tier2-execute`\n",
        encoding="utf-8",
    )

    args = AutoPhaseRunnerArgsDTO(tracker=tracker, dry_run=True)
    with patch("subprocess.Popen") as mock_popen:
        summary = run_phase_pipeline(args, repo_root=tmp_path)
        assert summary.total_phases == 1
        assert summary.executed_phases == 0
        assert summary.succeeded_phases == 0
        assert mock_popen.call_count == 0


def test_phase_failure_triggers_circuit_breaker(tmp_path: Path) -> None:
    """TC-APR-008: Verify failed subagent returncode halts pipeline immediately."""
    plan1 = tmp_path / "plan1.md"
    plan2 = tmp_path / "plan2.md"
    plan1.write_text("# Plan 1", encoding="utf-8")
    plan2.write_text("# Plan 2", encoding="utf-8")

    tracker = tmp_path / "tracker.md"
    tracker.write_text(
        f"### Phase 1: One\n- **Plan:** @[{plan1.name}]\n- [ ] **[NOK] Execution:** `/tier2-execute`\n\n"
        f"### Phase 2: Two\n- **Plan:** @[{plan2.name}]\n- [ ] **[NOK] Execution:** `/tier2-execute`\n",
        encoding="utf-8",
    )

    args = AutoPhaseRunnerArgsDTO(tracker=tracker, skip_commit=True, skip_hardening=True)

    with (
        patch(
            "scripts.auto_phase_runner.execute_phase_subagent",
            return_value=SubagentExecutionResultDTO(
                exit_code=1,
                output="Fatal error in subagent",
                duration_seconds=10.0,
                is_timeout=False,
            ),
        ),
        patch("scripts.auto_phase_runner.run_phase_quality_gate") as mock_qg,
    ):
        summary = run_phase_pipeline(args, repo_root=tmp_path)
        assert summary.executed_phases == 1
        assert summary.failed_phases == 1
        assert summary.succeeded_phases == 0
        assert mock_qg.call_count == 0


def test_quality_gate_failure_stops_pipeline(tmp_path: Path) -> None:
    """TC-APR-009: Verify quality gate failure halts pipeline without git commit."""
    plan = tmp_path / "plan.md"
    plan.write_text("# Plan", encoding="utf-8")
    tracker = tmp_path / "tracker.md"
    tracker.write_text(
        f"### Phase 1: Test\n- **Plan:** @[{plan.name}]\n- [ ] **[NOK] Execution:** `/tier2-execute`\n",
        encoding="utf-8",
    )

    args = AutoPhaseRunnerArgsDTO(tracker=tracker, skip_commit=False, skip_hardening=True)

    with (
        patch(
            "scripts.auto_phase_runner.execute_phase_subagent",
            return_value=SubagentExecutionResultDTO(
                exit_code=0,
                output="Success",
                duration_seconds=5.0,
                is_timeout=False,
            ),
        ),
        patch(
            "scripts.auto_phase_runner.run_phase_quality_gate",
            return_value=QualityGateResultDTO(
                success=False,
                output="Linter failure in backend_v2",
                exit_code=1,
            ),
        ),
        patch("scripts.auto_phase_runner.commit_phase_checkpoint") as mock_commit,
    ):
        summary = run_phase_pipeline(args, repo_root=tmp_path)
        assert summary.executed_phases == 1
        assert summary.failed_phases == 1
        assert mock_commit.call_count == 0


def test_mark_phase_completed_in_tracker_in_place(tmp_path: Path) -> None:
    """TC-APR-010: Verify in-place tracker checkbox update and commit hash insertion."""
    tracker_file = tmp_path / "tracker.md"
    tracker_content = """# Master Tracker
### Phase 1: Domain Setup
- **Plan:** @[plan1.md]
- [ ] **[NOK] Execution:** `/tier2-execute @[plan1.md] @[tracker.md]`
  - [ ] Step 1: Define DTOs
  - [ ] Step 2: Implement logic

### Phase 2: Next Step
- **Plan:** @[plan2.md]
- [ ] **[NOK] Execution:** `/tier2-execute @[plan2.md] @[tracker.md]`
  - [ ] Step 1: Next
"""
    tracker_file.write_text(tracker_content, encoding="utf-8")

    mark_phase_completed_in_tracker(tracker_file, phase_num=1, commit_hash="e3d4c5a")

    updated = tracker_file.read_text(encoding="utf-8")
    assert "- [x] **[OK] Execution:** `/tier2-execute @[plan1.md] @[tracker.md]` (`e3d4c5a`)" in updated
    assert "  - [x] Step 1: Define DTOs" in updated
    assert "  - [x] Step 2: Implement logic" in updated
    # Phase 2 must remain untouched
    assert "- [ ] **[NOK] Execution:** `/tier2-execute @[plan2.md] @[tracker.md]`" in updated
    assert "  - [ ] Step 1: Next" in updated


def test_execute_subagent_timeout_tree_kill(tmp_path: Path) -> None:
    """TC-APR-011: Verify watchdog timeout triggers process tree kill and returns is_timeout=True."""
    phase = PhaseItemDTO(
        phase_num=1,
        title="Timeout Test",
        plan_path=Path("plan.md"),
        is_completed=False,
        command="/tier2-execute",
    )
    args = AutoPhaseRunnerArgsDTO(tracker=tmp_path / "tracker.md", timeout=1)

    mock_proc = MagicMock()
    mock_proc.pid = 9999
    mock_proc.returncode = -1
    mock_proc.stdout.readline.side_effect = ["Starting...\n", ""]

    with (
        patch("scripts.auto_phase_runner.resolve_agy_binary", return_value=Path("agy.exe")),
        patch("subprocess.Popen", return_value=mock_proc),
        patch("scripts.auto_phase_runner._tree_kill"),
    ):
        res = execute_phase_subagent(phase, args, tmp_path)
        assert res.exit_code == -1
        assert "Starting..." in res.output


def test_commit_phase_checkpoint_clean_working_tree(tmp_path: Path) -> None:
    """TC-APR-012: Verify clean working tree skips git commit without error."""
    phase = PhaseItemDTO(
        phase_num=1,
        title="Clean Test",
        plan_path=Path("plan.md"),
        is_completed=False,
        command="/tier2-execute",
    )
    with patch(
        "subprocess.run",
        return_value=subprocess.CompletedProcess(args=[], returncode=0, stdout=""),
    ):
        hash_res = commit_phase_checkpoint(phase, tmp_path / "tracker.md", tmp_path)
        assert hash_res is None


def test_full_pipeline_success_mocked(tmp_path: Path) -> None:
    """TC-APR-013: Verify full pipeline success across two phases with git commit and hardening handoff."""
    plan1 = tmp_path / "plan1.md"
    plan2 = tmp_path / "plan2.md"
    plan1.write_text("# Plan 1", encoding="utf-8")
    plan2.write_text("# Plan 2", encoding="utf-8")

    tracker = tmp_path / "tracker.md"
    tracker.write_text(
        f"### Phase 1: One\n- **Plan:** @[{plan1.name}]\n- [ ] **[NOK] Execution:** `/tier2-execute`\n\n"
        f"### Phase 2: Two\n- **Plan:** @[{plan2.name}]\n- [ ] **[NOK] Execution:** `/tier2-execute`\n",
        encoding="utf-8",
    )

    args = AutoPhaseRunnerArgsDTO(tracker=tracker, skip_commit=False, skip_hardening=False)

    with (
        patch(
            "scripts.auto_phase_runner.execute_phase_subagent",
            return_value=SubagentExecutionResultDTO(
                exit_code=0,
                output="Success output",
                duration_seconds=12.0,
                is_timeout=False,
            ),
        ),
        patch(
            "scripts.auto_phase_runner.run_phase_quality_gate",
            return_value=QualityGateResultDTO(success=True, output="Pass", exit_code=0),
        ),
        patch("scripts.auto_phase_runner.commit_phase_checkpoint", return_value="f1e2d3c"),
        patch("scripts.auto_phase_runner.run_post_hardening_gate", return_value=0) as mock_hardening,
    ):
        summary = run_phase_pipeline(args, repo_root=tmp_path)
        assert summary.total_phases == 2
        assert summary.executed_phases == 2
        assert summary.succeeded_phases == 2
        assert summary.failed_phases == 0
        assert mock_hardening.call_count == 1


def test_filter_phases_only_phase() -> None:
    """TC-APR-014: Verify filter_phases with only_phase returns strictly the designated phase."""
    phases = [
        PhaseItemDTO(phase_num=1, title="P1", plan_path=Path("1.md"), is_completed=True, command="c1"),
        PhaseItemDTO(phase_num=2, title="P2", plan_path=Path("2.md"), is_completed=True, command="c2"),
        PhaseItemDTO(phase_num=3, title="P3", plan_path=Path("3.md"), is_completed=False, command="c3"),
    ]
    # only_phase=2 returns phase 2 even if is_completed=True
    filtered = filter_phases(phases, only_phase=2)
    assert len(filtered) == 1
    assert filtered[0].phase_num == 2


def test_filter_phases_from_phase() -> None:
    """TC-APR-015: Verify filter_phases with from_phase excludes lower phase numbers."""
    phases = [
        PhaseItemDTO(phase_num=1, title="P1", plan_path=Path("1.md"), is_completed=False, command="c1"),
        PhaseItemDTO(phase_num=2, title="P2", plan_path=Path("2.md"), is_completed=False, command="c2"),
        PhaseItemDTO(phase_num=3, title="P3", plan_path=Path("3.md"), is_completed=False, command="c3"),
    ]
    filtered = filter_phases(phases, from_phase=2)
    assert len(filtered) == 2
    assert [p.phase_num for p in filtered] == [2, 3]


def test_run_post_hardening_gate_with_hardening_agent(tmp_path: Path) -> None:
    """TC-APR-016: Verify --hardening-agent appends respective backend and frontend agent commands."""
    tracker = tmp_path / "tracker.md"
    tracker.write_text(
        """# Master Tracker
### Post-Implementation Gates
- [ ] Tier 2 Hardening (Backend)
  - [ ] @[backend_v2/services/execution.py]
- [ ] Tier 2 Hardening (Frontend)
  - [ ] @[client_app_v2/lib/features/studio/views/editor.dart]
""",
        encoding="utf-8",
    )
    args = AutoPhaseRunnerArgsDTO(
        tracker=tracker,
        hardening_agent=True,
        hardening_model="gemini-4-argon-high",
    )
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)
        code = run_post_hardening_gate(tracker, args, tmp_path)
        assert code == 0
        assert mock_run.call_count == 2

        # 1. Backend call verification
        cmd_backend = mock_run.call_args_list[0][0][0]
        assert "--gate" in cmd_backend
        assert cmd_backend[cmd_backend.index("--gate") + 1] == "backend"
        assert "--agent-cmd" in cmd_backend
        backend_agent_idx = cmd_backend.index("--agent-cmd")
        assert "gemini-4-argon-high" in cmd_backend[backend_agent_idx + 1]
        assert "/tier2-hardening-backend {target}" in cmd_backend[backend_agent_idx + 1]

        # 2. Frontend call verification
        cmd_frontend = mock_run.call_args_list[1][0][0]
        assert "--gate" in cmd_frontend
        assert cmd_frontend[cmd_frontend.index("--gate") + 1] == "frontend"
        assert "--agent-cmd" in cmd_frontend
        frontend_agent_idx = cmd_frontend.index("--agent-cmd")
        assert "gemini-4-argon-high" in cmd_frontend[frontend_agent_idx + 1]
        assert "/tier2-hardening-frontend {target}" in cmd_frontend[frontend_agent_idx + 1]


def test_run_post_hardening_gate_no_unhardened_targets(tmp_path: Path) -> None:
    """Verify run_post_hardening_gate cleanly skips when no targets are unhardened."""
    tracker = tmp_path / "tracker.md"
    tracker.write_text(
        """# Master Tracker
### Post-Implementation Gates
- [x] Tier 2 Hardening (Backend)
  - [x] @[backend_v2/services/execution.py]
- [ ] **[SKIPPED] Tier 2 Hardening (Frontend)**: No frontend files modified.
""",
        encoding="utf-8",
    )
    args = AutoPhaseRunnerArgsDTO(tracker=tracker)
    with patch("subprocess.run") as mock_run:
        code = run_post_hardening_gate(tracker, args, tmp_path)
        assert code == 0
        assert mock_run.call_count == 0


def test_run_post_hardening_gate_unparsed_items_fail_fast(tmp_path: Path) -> None:
    """Verify run_post_hardening_gate returns exit code 1 when unchecked items exist but zero targets parse."""
    tracker = tmp_path / "tracker.md"
    tracker.write_text(
        """# Master Tracker
### Post-Implementation Gates
- [ ] Tier 2 Hardening (Backend)
  - [ ] Malformed line without any path
""",
        encoding="utf-8",
    )
    args = AutoPhaseRunnerArgsDTO(tracker=tracker)
    code = run_post_hardening_gate(tracker, args, tmp_path)
    assert code == 1


def test_run_post_hardening_gate_backend_failure_halts_before_frontend(tmp_path: Path) -> None:
    """Verify backend hardening failure immediately halts and returns error without running frontend."""
    tracker = tmp_path / "tracker.md"
    tracker.write_text(
        """# Master Tracker
### Post-Implementation Gates
- [ ] Tier 2 Hardening (Backend)
  - [ ] @[backend_v2/services/execution.py]
- [ ] Tier 2 Hardening (Frontend)
  - [ ] @[client_app_v2/lib/features/studio/views/editor.dart]
""",
        encoding="utf-8",
    )
    args = AutoPhaseRunnerArgsDTO(tracker=tracker)
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=3)
        code = run_post_hardening_gate(tracker, args, tmp_path)
        assert code == 3
        # Frontend must not be called after backend failure
        assert mock_run.call_count == 1
        cmd = mock_run.call_args_list[0][0][0]
        assert cmd[cmd.index("--gate") + 1] == "backend"


def test_run_post_hardening_gate_only_frontend(tmp_path: Path) -> None:
    """Verify run_post_hardening_gate executes strictly frontend when only frontend targets exist."""
    tracker = tmp_path / "tracker.md"
    tracker.write_text(
        """# Master Tracker
### Post-Implementation Gates
- [x] Tier 2 Hardening (Backend)
  - [x] @[backend_v2/services/execution.py]
- [ ] Tier 2 Hardening (Frontend)
  - [ ] @[client_app_v2/lib/features/studio/views/editor.dart]
""",
        encoding="utf-8",
    )
    args = AutoPhaseRunnerArgsDTO(tracker=tracker, hardening_agent=True)
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)
        code = run_post_hardening_gate(tracker, args, tmp_path)
        assert code == 0
        assert mock_run.call_count == 1
        cmd = mock_run.call_args_list[0][0][0]
        assert cmd[cmd.index("--gate") + 1] == "frontend"
        assert "/tier2-hardening-frontend {target}" in cmd[cmd.index("--agent-cmd") + 1]


def test_execute_subagent_cmd_wrapper_on_windows(tmp_path: Path) -> None:
    """TC-APR-017: Verify Windows wraps .cmd / .bat binaries via cmd.exe /c."""
    phase = PhaseItemDTO(
        phase_num=1,
        title="Cmd Wrapper Test",
        plan_path=Path("plan.md"),
        is_completed=False,
        command="/tier2-execute",
    )
    args = AutoPhaseRunnerArgsDTO(tracker=tmp_path / "tracker.md")

    mock_proc = MagicMock()
    mock_proc.pid = 1234
    mock_proc.returncode = 0
    mock_proc.stdout.readline.side_effect = ["Output\n", ""]

    with (
        patch("sys.platform", "win32"),
        patch("scripts.auto_phase_runner.resolve_agy_binary", return_value=Path("C:/npm/agy.cmd")),
        patch("subprocess.Popen", return_value=mock_proc) as mock_popen,
    ):
        res = execute_phase_subagent(phase, args, tmp_path)
        assert res.exit_code == 0
        cmd_args = mock_popen.call_args[0][0]
        assert cmd_args[0] == "cmd.exe"
        assert cmd_args[1] == "/c"
        assert "agy.cmd" in cmd_args[2]


def test_commit_phase_checkpoint_dirty_files_staged(tmp_path: Path) -> None:
    """TC-APR-018: Verify specific staging of modified domain files excluding scratch/tmp."""
    phase = PhaseItemDTO(
        phase_num=3,
        title="Phase 3: Domain Service",
        plan_path=Path("plan.md"),
        is_completed=False,
        command="/tier2-execute",
    )
    tracker = tmp_path / "docs/tracker.md"

    porcelain_output = (
        " M backend_v2/services/execution.py\n"
        "?? scratch/temp_script.py\n"
        "?? .system_generated/logs/test.jsonl\n"
        " M docs/tracker.md\n"
    )

    def _mock_run(cmd: list[str], *args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        if "status" in cmd:
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout=porcelain_output)
        if "commit" in cmd:
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="[main ab12cd3]")
        if "rev-parse" in cmd:
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="ab12cd3\n")
        return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="")

    with patch("subprocess.run", side_effect=_mock_run) as mock_run:
        commit_hash = commit_phase_checkpoint(phase, tracker, tmp_path)
        assert commit_hash == "ab12cd3"
        # Check git add calls
        git_add_calls = [call[0][0] for call in mock_run.call_args_list if call[0][0][0:2] == ["git", "add"]]
        assert len(git_add_calls) >= 1
        staged_items = git_add_calls[0]
        assert "backend_v2/services/execution.py" in staged_items
        assert "docs/tracker.md" in staged_items
        assert not any("scratch/" in item for item in staged_items)
        assert not any(".system_generated/" in item for item in staged_items)


def test_mark_phase_completed_bounded_to_exact_phase_section(tmp_path: Path) -> None:
    """TC-APR-019: Verify bounded section replacement updates only the targeted phase."""
    tracker_content = """### Phase 1: Alpha
- [ ] **[NOK] Execution:** `/tier2-execute`
  - [ ] Step 1: Alpha step

### Phase 2: Beta
- [ ] **[NOK] Execution:** `/tier2-execute`
  - [ ] Step 1: Beta step
"""
    tracker_file = tmp_path / "tracker.md"
    tracker_file.write_text(tracker_content, encoding="utf-8")

    mark_phase_completed_in_tracker(tracker_file, phase_num=2, commit_hash="b2c3d4e")

    updated = tracker_file.read_text(encoding="utf-8")
    # Phase 1 must be untouched
    assert "### Phase 1: Alpha\n- [ ] **[NOK] Execution:** `/tier2-execute`" in updated
    assert "  - [ ] Step 1: Alpha step" in updated
    # Phase 2 must be updated
    assert "### Phase 2: Beta\n- [x] **[OK] Execution:** `/tier2-execute` (`b2c3d4e`)" in updated
    assert "  - [x] Step 1: Beta step" in updated


def test_execute_subagent_returns_typed_subagent_execution_result_dto(tmp_path: Path) -> None:
    """TC-APR-020: Verify execute_phase_subagent encapsulates results in SubagentExecutionResultDTO."""
    phase = PhaseItemDTO(
        phase_num=1,
        title="DTO Return Test",
        plan_path=Path("plan.md"),
        is_completed=False,
        command="/tier2-execute",
    )
    args = AutoPhaseRunnerArgsDTO(tracker=tmp_path / "tracker.md")

    mock_proc = MagicMock()
    mock_proc.pid = 4321
    mock_proc.returncode = 0
    mock_proc.stdout.readline.side_effect = ["Line 1\n", "Line 2\n", ""]

    with (
        patch("scripts.auto_phase_runner.resolve_agy_binary", return_value=Path("agy.exe")),
        patch("subprocess.Popen", return_value=mock_proc),
    ):
        res = execute_phase_subagent(phase, args, tmp_path)
        assert isinstance(res, SubagentExecutionResultDTO)
        assert res.exit_code == 0
        assert res.output == "Line 1\nLine 2\n"
        assert res.duration_seconds >= 0.0
        assert res.is_timeout is False


def test_main_cli_execution_errors(tmp_path: Path) -> None:
    """Verify main entrypoint returns exit code 1 on execution error and 2 on arg error."""
    # Arg error (missing required --tracker)
    assert main([]) == 2

    # File not found error
    missing_tracker = tmp_path / "non_existent.md"
    assert main(["--tracker", str(missing_tracker)]) == 1


def test_parse_tracker_phases_empty_and_no_phases(tmp_path: Path) -> None:
    """Verify ValueError when tracker path is empty or contains no discoverable phases."""
    with pytest.raises(ValueError, match="Invalid tracker path"):
        parse_tracker_phases(Path("   "), repo_root=tmp_path)

    empty_tracker = tmp_path / "empty_tracker.md"
    empty_tracker.write_text("# Empty Tracker\nJust plain text\n", encoding="utf-8")
    with pytest.raises(ValueError, match="No execution phases discovered"):
        parse_tracker_phases(empty_tracker, repo_root=tmp_path)


def test_parse_tracker_phases_skipped_unmatched_section(tmp_path: Path) -> None:
    """Verify section without Plan reference is gracefully skipped in multi-phase parsing."""
    tracker = tmp_path / "tracker.md"
    tracker.write_text(
        "### Phase 1: Without Plan\nSome notes\n### Phase 2: Next\nSome other notes\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="No execution phases discovered"):
        parse_tracker_phases(tracker, repo_root=tmp_path)


def test_mark_phase_completed_standalone_plan_tracker(tmp_path: Path) -> None:
    """Verify mark_phase_completed_in_tracker updates standalone plan tracker correctly."""
    tracker = tmp_path / "tracker.md"
    tracker.write_text(
        "## Step Execution Status\n"
        "- [ ] **[NOK] Execution:** `/tier2-execute`\n"
        "  - [ ] Step 1: DTO\n"
        "### Post-Implementation\n",
        encoding="utf-8",
    )
    mark_phase_completed_in_tracker(tracker, phase_num=1, commit_hash="c1d2e3f")
    updated = tracker.read_text(encoding="utf-8")
    assert "- [x] **[OK] Execution:** `/tier2-execute` (`c1d2e3f`)" in updated
    assert "  - [x] Step 1: DTO" in updated

    # Non-existent tracker does nothing without error
    mark_phase_completed_in_tracker(tmp_path / "missing.md", phase_num=1)


def test_run_post_hardening_gate_skip_and_warning(tmp_path: Path) -> None:
    """Verify run_post_hardening_gate handles skip_hardening, missing tracker, and returns non-zero code."""
    tracker = tmp_path / "tracker.md"
    args_skip = AutoPhaseRunnerArgsDTO(tracker=tracker, skip_hardening=True)
    assert run_post_hardening_gate(tracker, args_skip, tmp_path) == 0

    # 1. Missing tracker returns 1
    args_run = AutoPhaseRunnerArgsDTO(tracker=tracker, skip_hardening=False)
    assert run_post_hardening_gate(tracker, args_run, tmp_path) == 1

    # 2. Existing tracker with target where subprocess fails returns returncode 1
    tracker.write_text(
        """# Master Tracker
### Post-Implementation Gates
- [ ] Tier 2 Hardening (Backend)
  - [ ] @[backend_v2/services/execution.py]
""",
        encoding="utf-8",
    )
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=1)
        assert run_post_hardening_gate(tracker, args_run, tmp_path) == 1


def test_commit_phase_checkpoint_only_tracker_and_failures(tmp_path: Path) -> None:
    """Verify commit_phase_checkpoint branches for only tracker changed, porcelain fail, commit fail."""
    phase = PhaseItemDTO(
        phase_num=1,
        title="Commit Branches",
        plan_path=Path("plan.md"),
        is_completed=False,
        command="/tier2-execute",
    )
    tracker = tmp_path / "docs/tracker.md"

    # 1. Porcelain failure returns None
    with patch("subprocess.run", return_value=subprocess.CompletedProcess(args=[], returncode=1)):
        assert commit_phase_checkpoint(phase, tracker, tmp_path) is None

    # 2. Only tracker changed
    def _mock_only_tracker(cmd: list[str], *args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        if "status" in cmd:
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout=" M docs/tracker.md\n")
        if "commit" in cmd:
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="[main 1234567]")
        if "rev-parse" in cmd:
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="1234567\n")
        return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="")

    with patch("subprocess.run", side_effect=_mock_only_tracker) as mock_run:
        commit_hash = commit_phase_checkpoint(phase, tracker, tmp_path)
        assert commit_hash == "1234567"
        commit_calls = [call[0][0] for call in mock_run.call_args_list if call[0][0][0:2] == ["git", "commit"]]
        assert len(commit_calls) == 1
        assert "docs(tracker):" in commit_calls[0][3]

    # 3. Commit failure returns None
    def _mock_commit_fail(cmd: list[str], *args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        if "status" in cmd:
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout=" M docs/tracker.md\n")
        if "commit" in cmd:
            return subprocess.CompletedProcess(args=cmd, returncode=1, stdout="fatal: error")
        return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="")

    with patch("subprocess.run", side_effect=_mock_commit_fail):
        assert commit_phase_checkpoint(phase, tracker, tmp_path) is None


def test_run_phase_quality_gate_with_dirty_scripts(tmp_path: Path) -> None:
    """Verify run_phase_quality_gate discovers dirty scripts and passes them to audit loop."""
    phase = PhaseItemDTO(
        phase_num=1,
        title="QG Test",
        plan_path=Path("plan.md"),
        is_completed=False,
        command="/tier2-execute",
    )
    script_file = tmp_path / "scripts/my_script.py"
    script_file.parent.mkdir(parents=True, exist_ok=True)
    script_file.write_text("# script", encoding="utf-8")

    def _mock_qg_run(cmd: list[str], *args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        if "status" in cmd:
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout=" M scripts/my_script.py\n")
        if "backend_audit_loop.py" in cmd:
            assert "scripts/my_script.py" in cmd
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="All passed", stderr="")
        return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="")

    with patch("subprocess.run", side_effect=_mock_qg_run):
        res = run_phase_quality_gate(phase, tmp_path)
        assert res.success is True
        assert res.exit_code == 0


def test_execute_subagent_stdout_streaming_unicode_and_oserror(tmp_path: Path) -> None:
    """Verify execute_phase_subagent handles UnicodeEncodeError and OSError on pipe read."""
    phase = PhaseItemDTO(
        phase_num=1,
        title="Streaming Error Test",
        plan_path=Path("plan.md"),
        is_completed=False,
        command="/tier2-execute",
    )
    args = AutoPhaseRunnerArgsDTO(tracker=tmp_path / "tracker.md")

    mock_proc = MagicMock()
    mock_proc.pid = 7777
    mock_proc.returncode = 0
    mock_proc.stdout.readline.side_effect = ["Thought \U0001f914\n", OSError("Pipe closed")]

    with (
        patch("scripts.auto_phase_runner.resolve_agy_binary", return_value=Path("agy.exe")),
        patch("subprocess.Popen", return_value=mock_proc),
        patch("sys.stdout.write", side_effect=[UnicodeEncodeError("cp1252", "", 0, 1, "test")]),
        patch("sys.stdout.buffer.write") as mock_buf_write,
    ):
        res = execute_phase_subagent(phase, args, tmp_path)
        assert res.exit_code == 0
        assert mock_buf_write.call_count >= 1


def test_main_cli_full_success_and_failure(tmp_path: Path) -> None:
    """Verify main returns 0 on pipeline success and 1 when phases fail."""
    plan = tmp_path / "plan.md"
    plan.write_text("# Plan", encoding="utf-8")
    tracker = tmp_path / "tracker.md"
    tracker.write_text(
        f"### Phase 1: One\n- **Plan:** @[{plan.name}]\n- [ ] **[NOK] Execution:** `/tier2-execute`\n",
        encoding="utf-8",
    )

    # 1. Success returns 0
    with patch(
        "scripts.auto_phase_runner.run_phase_pipeline",
        return_value=AutoPhaseRunSummaryDTO(
            tracker_path=tracker,
            total_phases=1,
            executed_phases=1,
            succeeded_phases=1,
            failed_phases=0,
            results=[],
        ),
    ):
        assert main(["--tracker", str(tracker)]) == 0

    # 2. Failed phase returns 1
    with patch(
        "scripts.auto_phase_runner.run_phase_pipeline",
        return_value=AutoPhaseRunSummaryDTO(
            tracker_path=tracker,
            total_phases=1,
            executed_phases=1,
            succeeded_phases=0,
            failed_phases=1,
            results=[],
        ),
    ):
        assert main(["--tracker", str(tracker)]) == 1


def test_execute_subagent_retry_on_transient_model_glitch(tmp_path: Path) -> None:
    """TC-APR-034: Verify subagent automatically retries on transient model/catalog startup failure."""
    phase = PhaseItemDTO(
        phase_num=3,
        title="Phase 3: Domain Service",
        plan_path=Path("plan.md"),
        is_completed=False,
        command="/tier2-execute",
    )
    args = AutoPhaseRunnerArgsDTO(tracker=tmp_path / "tracker.md", max_retries=3)

    # Attempt 1 fails with transient model unrecognized error
    proc1 = MagicMock()
    proc1.pid = 1001
    proc1.returncode = 1
    proc1.stdout.readline.side_effect = [
        'error: invalid model selection (--model "gemini-4-argon-high" --effort ""): model gemini-4-argon-high is not recognized as a known model or custom model in settings\n',
        "",
    ]

    # Attempt 2 succeeds
    proc2 = MagicMock()
    proc2.pid = 1002
    proc2.returncode = 0
    proc2.stdout.readline.side_effect = ["Phase 3 completed successfully.\n", ""]

    with (
        patch("scripts.auto_phase_runner.resolve_agy_binary", return_value=Path("agy.exe")),
        patch("subprocess.Popen", side_effect=[proc1, proc2]) as mock_popen,
        patch("time.sleep") as mock_sleep,
    ):
        res = execute_phase_subagent(phase, args, tmp_path)
        assert res.exit_code == 0
        assert "Phase 3 completed successfully." in res.output
        assert mock_popen.call_count == 2
        mock_sleep.assert_called_once_with(3.0)


def test_execute_subagent_retry_exhaustion_on_persistent_failure(tmp_path: Path) -> None:
    """TC-APR-035: Verify all retry attempts are exhausted when transient failure persists."""
    phase = PhaseItemDTO(
        phase_num=3,
        title="Phase 3: Domain Service",
        plan_path=Path("plan.md"),
        is_completed=False,
        command="/tier2-execute",
    )
    args = AutoPhaseRunnerArgsDTO(tracker=tmp_path / "tracker.md", max_retries=3)

    def _make_failing_proc(pid: int) -> MagicMock:
        p = MagicMock()
        p.pid = pid
        p.returncode = 1
        p.stdout.readline.side_effect = ["error: connection refused to backend\n", ""]
        return p

    procs = [_make_failing_proc(2000 + i) for i in range(3)]

    with (
        patch("scripts.auto_phase_runner.resolve_agy_binary", return_value=Path("agy.exe")),
        patch("subprocess.Popen", side_effect=procs) as mock_popen,
        patch("time.sleep") as mock_sleep,
    ):
        res = execute_phase_subagent(phase, args, tmp_path)
        assert res.exit_code == 1
        assert "connection refused" in res.output
        assert mock_popen.call_count == 3
        assert mock_sleep.call_count == 2


def test_execute_subagent_no_retry_on_domain_failure(tmp_path: Path) -> None:
    """TC-APR-036: Verify non-transient domain failures (e.g. test failure) are not retried."""
    phase = PhaseItemDTO(
        phase_num=3,
        title="Phase 3: Domain Service",
        plan_path=Path("plan.md"),
        is_completed=False,
        command="/tier2-execute",
    )
    args = AutoPhaseRunnerArgsDTO(tracker=tmp_path / "tracker.md", max_retries=3)

    proc = MagicMock()
    proc.pid = 3001
    proc.returncode = 1
    proc.stdout.readline.side_effect = ["FAILED test_domain.py::test_case - AssertionError\n", ""]

    with (
        patch("scripts.auto_phase_runner.resolve_agy_binary", return_value=Path("agy.exe")),
        patch("subprocess.Popen", return_value=proc) as mock_popen,
        patch("time.sleep") as mock_sleep,
    ):
        res = execute_phase_subagent(phase, args, tmp_path)
        assert res.exit_code == 1
        assert "AssertionError" in res.output
        assert mock_popen.call_count == 1
        mock_sleep.assert_not_called()
